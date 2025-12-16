use crate::common::{BufferPool, TokenAcquirer};
use crate::tos_client::InnerTosClient;
use arc_swap::ArcSwap;
use async_channel::{Receiver, Sender};
use bytes::BytesMut;
use futures_util::future::join_all;
use std::cmp::min;
use std::collections::{HashMap, LinkedList};
use std::sync::atomic::{AtomicI8, AtomicIsize, Ordering};
use std::sync::Arc;
use tokio::runtime::Runtime;
use tokio::sync::{Mutex, Notify, RwLock};
use tokio::task::JoinHandle;
use tracing::log::{error, info};
use tracing::warn;
use ve_tos_rust_sdk::asynchronous::multipart::MultipartAPI;
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::enumeration::StorageClassType;
use ve_tos_rust_sdk::error::TosError;
use ve_tos_rust_sdk::multipart::{
    AbortMultipartUploadInput, CompleteMultipartUploadInput, CreateMultipartUploadInput,
    UploadPartFromBufferInput, UploadedPart,
};
use ve_tos_rust_sdk::object::PutObjectFromBufferInput;

const DEFAULT_PART_SIZE: isize = 8 * 1024 * 1024;
const DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT: isize = 100 * 1024 * 1024;
const DEFAULT_UPLOAD_PART_TASKS: isize = 3;
const MAX_UPLOAD_PART_SIZE: isize = 5 * 1024 * 1024 * 1024;
const MAX_PART_NUMBER: isize = 10000;
const OTHER_MU_KICK_OFF: i8 = 1;
const RELEASE_MU_KICK_OFF: i8 = 2;

pub struct WriteStream {
    object_writer: ObjectWriter,
    runtime: Arc<Runtime>,
    offset: AtomicIsize,
    bucket: String,
    key: String,
    storage_class: Option<String>,
}

impl WriteStream {
    pub fn write(&self, data: &[u8]) -> Result<isize, TosError> {
        match self
            .runtime
            .block_on(async { self.object_writer.write(data, self.offset()).await })
        {
            Err(ex) => Err(ex),
            Ok(written) => {
                self.offset.fetch_add(written, Ordering::Release);
                Ok(written)
            }
        }
    }

    pub async fn async_write(&self, data: &[u8], offset: isize) -> Result<isize, TosError> {
        self.object_writer.write(data, offset).await
    }

    pub fn close(&self) -> Result<(), TosError> {
        match self
            .runtime
            .block_on(async { self.object_writer.release().await })
        {
            Err(ex) => Err(ex),
            Ok(_) => Ok(()),
        }
    }

    pub async fn async_close(&self) -> Result<(), TosError> {
        self.object_writer.release().await
    }

    pub fn offset(&self) -> isize {
        self.offset.load(Ordering::Acquire)
    }

    pub fn bucket(&self) -> &str {
        &self.bucket
    }

    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn storage_class(&self) -> &Option<String> {
        &self.storage_class
    }
    pub(crate) async fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
        part_size: isize,
        max_upload_part_tasks: isize,
        sta: Arc<Option<TokenAcquirer>>,
        buffer_pool: BufferPool,
    ) -> Result<Self, TosError> {
        let mut part_size = part_size;
        if part_size <= 0 {
            part_size = DEFAULT_PART_SIZE;
        } else if part_size > MAX_UPLOAD_PART_SIZE {
            part_size = MAX_UPLOAD_PART_SIZE;
        }

        let _bucket = bucket.clone();
        let _key = key.clone();
        let _storage_class = storage_class.clone();
        let object_writer = ObjectWriter::new(
            client,
            runtime.clone(),
            _bucket,
            _key,
            _storage_class,
            part_size,
            max_upload_part_tasks,
            sta,
            buffer_pool,
        )
        .await?;
        Ok(Self {
            object_writer,
            runtime,
            offset: AtomicIsize::new(0),
            bucket,
            key,
            storage_class,
        })
    }
}

struct ObjectWriter {
    ctx: Mutex<(ObjectUploader, isize)>,
    closed: Arc<AtomicI8>,
}

impl ObjectWriter {
    async fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
        part_size: isize,
        max_upload_part_tasks: isize,
        sta: Arc<Option<TokenAcquirer>>,
        buffer_pool: BufferPool,
    ) -> Result<Self, TosError> {
        let wp = Arc::new(WriteParam {
            bucket,
            key,
            storage_class,
        });
        let ou = ObjectUploader::new(
            client,
            runtime,
            wp,
            part_size,
            0,
            AtomicI8::new(0),
            max_upload_part_tasks,
            sta,
            buffer_pool,
        )
        .await?;
        Ok(Self {
            ctx: Mutex::new((ou, 0)),
            closed: Arc::new(AtomicI8::new(0)),
        })
    }

    async fn write(&self, data: &[u8], offset: isize) -> Result<isize, TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            warn!("write on closed object writer");
            return Err(TosError::TosClientError {
                message: "write on closed object writer".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        let mut ctx = self.ctx.lock().await;
        if offset != ctx.1 {
            warn!(
                "unexpected start to write, expect [{}], actual [{}]",
                ctx.1, offset
            );
            return Err(TosError::TosClientError {
                message: format!(
                    "unexpected start to write, expect [{}], actual [{}]",
                    ctx.1, offset
                ),
                cause: None,
                request_url: "".to_string(),
            });
        }

        if ctx.0.is_aborted() {
            warn!("write on aborted object writer");
            return Err(TosError::TosClientError {
                message: "write on aborted object writer".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        if data.is_empty() {
            return Ok(0);
        }

        if ctx.0.is_sealed() {
            warn!("write on sealed object writer");
            return Err(TosError::TosClientError {
                message: "write on sealed object writer".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        if ctx.1 + data.len() as isize > ctx.0.max_size {
            warn!("exceed the max size, max size is [{}]", ctx.0.max_size);
            return Err(TosError::TosClientError {
                message: format!("exceed the max size, max size is [{}]", ctx.0.max_size),
                cause: None,
                request_url: "".to_string(),
            });
        }
        match ctx.0.write(data).await {
            Err(ex) => Err(ex),
            Ok(written) => {
                ctx.1 += written;
                Ok(written)
            }
        }
    }

    async fn flush(&self) -> Result<(), TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            return Err(TosError::TosClientError {
                message: "flush on closed object writer".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        let mut ctx = self.ctx.lock().await;
        ctx.0.flush(true).await
    }

    async fn fsync(&self) -> Result<(), TosError> {
        if self.closed.load(Ordering::Acquire) == 1 {
            return Err(TosError::TosClientError {
                message: "fsync on closed object writer".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }
        let mut ctx = self.ctx.lock().await;
        ctx.0.fsync().await
    }

    async fn release(&self) -> Result<(), TosError> {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            let mut ctx = self.ctx.lock().await;
            match ctx.0.release().await {
                Err(ex) => return Err(ex),
                Ok(_) => {
                    if !ctx.0.is_created() {
                        return ctx.0.put_empty_object().await;
                    }
                }
            }
        }
        Ok(())
    }
}

struct WriteParam {
    bucket: String,
    key: String,
    storage_class: Option<String>,
}

struct ObjectUploader {
    next_write_offset: isize,
    uc: Arc<UploadContext>,
    runtime: Arc<Runtime>,
    current: Option<Part>,
    part_size: isize,
    max_size: isize,
    max_upload_part_tasks: isize,
    dp: Arc<Dispatcher>,
    st: Arc<Store>,
    ta: Arc<TokenAcquirer>,
    sta: Arc<Option<TokenAcquirer>>,
    buffer_pool: BufferPool,
    wait_dispatch: Option<JoinHandle<()>>,
    wait_execute: Option<JoinHandle<()>>,
    mu_ctx: Arc<MultipartUploadContext>,
}

impl ObjectUploader {
    async fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        wp: Arc<WriteParam>,
        part_size: isize,
        next_write_offset: isize,
        created: AtomicI8,
        max_upload_part_tasks: isize,
        sta: Arc<Option<TokenAcquirer>>,
        buffer_pool: BufferPool,
    ) -> Result<Self, TosError> {
        let max_size = part_size * MAX_PART_NUMBER;
        if next_write_offset >= max_size {
            return Err(TosError::TosClientError {
                message: format!("exceed the max size, max size is [{}]", max_size),
                cause: None,
                request_url: "".to_string(),
            });
        }

        let mut max_tokens = max_upload_part_tasks;
        if max_tokens <= 0 {
            max_tokens = DEFAULT_UPLOAD_PART_TASKS;
        }
        let mut ou = Self {
            next_write_offset,
            uc: Arc::new(UploadContext::new(created, wp, client)),
            runtime,
            current: None,
            part_size,
            max_size,
            max_upload_part_tasks,
            dp: Arc::new(Dispatcher::new(calc_queue_size(part_size))),
            st: Arc::new(Store::new(part_size, next_write_offset)),
            ta: Arc::new(TokenAcquirer::new(max_tokens)),
            sta,
            buffer_pool,
            wait_dispatch: None,
            wait_execute: None,
            mu_ctx: Arc::new(MultipartUploadContext::new()),
        };
        ou.dispatch().await;
        ou.execute().await;
        Ok(ou)
    }

    pub(crate) fn available_permits(&self) -> usize {
        self.ta.available_permits()
    }

    async fn reset(&mut self) -> Result<(), TosError> {
        self.max_size = self.part_size * MAX_PART_NUMBER;
        if self.next_write_offset >= self.max_size {
            return Err(TosError::TosClientError {
                message: format!("exceed the max size, max size is [{}]", self.max_size),
                cause: None,
                request_url: "".to_string(),
            });
        }
        self.wait_dispatch = None;
        self.wait_execute = None;
        self.mu_ctx = Arc::new(MultipartUploadContext::new());
        self.dp = Arc::new(Dispatcher::new(calc_queue_size(self.part_size)));
        self.st = Arc::new(Store::new(self.part_size, self.next_write_offset));

        let mut max_tokens = self.max_upload_part_tasks;
        if max_tokens <= 0 {
            max_tokens = DEFAULT_UPLOAD_PART_TASKS;
        }

        self.ta = Arc::new(TokenAcquirer::new(max_tokens));
        self.dispatch().await;
        self.execute().await;
        Ok(())
    }

    async fn write(&mut self, data: &[u8]) -> Result<isize, TosError> {
        let mut current;
        if let Some(part) = self.current.take() {
            current = part;
        } else {
            current = Part::new(self.part_size, self.buffer_pool.clone());
        }
        let mut written = 0isize;
        loop {
            let filled = current.fill(&data[written as usize..]).await;
            written += filled;
            if current.is_full() {
                let (push_result, succeed) = self.dp.push(current).await;
                if !succeed {
                    if let Some(mut part) = push_result {
                        part.release().await;
                        self.uc.abort().await;
                    }
                    return Err(TosError::TosClientError {
                        message: "dispatch current part failed".to_string(),
                        cause: None,
                        request_url: "".to_string(),
                    });
                }
                current = Part::new(self.part_size, self.buffer_pool.clone());
            }

            if written == data.len() as isize {
                self.current = Some(current);
                return Ok(written);
            }
        }
    }

    async fn flush(&mut self, flush_to_remote: bool) -> Result<(), TosError> {
        if self.uc.is_aborted() {
            return Err(TosError::TosClientError {
                message: "uploading is aborted".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        if flush_to_remote {
            return self.write_to_remote().await;
        }

        Ok(())
    }

    async fn fsync(&mut self) -> Result<(), TosError> {
        if self.uc.is_aborted() {
            return Err(TosError::TosClientError {
                message: "uploading is aborted".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        self.write_to_remote().await
    }

    async fn write_to_remote(&mut self) -> Result<(), TosError> {
        let result = self.flush_current().await;
        self.mu_ctx.kick_off(OTHER_MU_KICK_OFF).await;
        if result.is_err() {
            return result;
        }
        self.close_dispatch_and_store().await;
        if self.uc.is_aborted() {
            return Err(TosError::TosClientError {
                message: "uploading is aborted".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        let result = self.uc.complete_multipart_upload().await;
        if result.is_ok() {
            self.uc.seal();
        }
        result
    }

    async fn release(&mut self) -> Result<(), TosError> {
        let mut result = self.flush_current().await;
        self.mu_ctx.kick_off(RELEASE_MU_KICK_OFF).await;
        self.close_dispatch_and_store().await;

        if result.is_ok() && !self.uc.is_aborted() {
            result = self.uc.complete_multipart_upload().await;
        }

        // finally release
        loop {
            match self.dp.pull().await {
                None => break,
                Some(mut part) => {
                    part.release().await;
                }
            }
        }

        loop {
            match self.st.pull().await {
                None => break,
                Some(mut si) => {
                    si.release().await;
                }
            }
        }

        self.ta.close();
        self.st.destroy();
        result
    }

    async fn flush_current(&mut self) -> Result<(), TosError> {
        if let Some(current) = self.current.take() {
            if current.size() > 0 {
                let (push_result, succeed) = self.dp.push(current).await;
                if !succeed {
                    if let Some(mut part) = push_result {
                        part.release().await;
                        self.uc.abort().await;
                    }
                    return Err(TosError::TosClientError {
                        message: "flush current part failed".to_string(),
                        cause: None,
                        request_url: "".to_string(),
                    });
                }
            }
        }
        Ok(())
    }
    async fn close_dispatch_and_store(&mut self) {
        self.dp.close();
        if let Some(wait_dispatch) = self.wait_dispatch.take() {
            let _ = wait_dispatch.await;
        }
        self.st.close();
        if let Some(wait_execute) = self.wait_execute.take() {
            let _ = wait_execute.await;
        }
    }

    async fn dispatch(&mut self) {
        let dp = self.dp.clone();
        let st = self.st.clone();
        let uc = self.uc.clone();
        self.wait_dispatch = Some(self.runtime.spawn(async move {
            loop {
                match dp.pull().await {
                    None => return,
                    Some(mut part) => {
                        if uc.is_aborted() {
                            part.release().await;
                            continue;
                        }

                        let (send_result, succeed) = st.push(part).await;
                        if !succeed {
                            error!("push part to store failed");
                            if let Some(mut part) = send_result {
                                part.release().await;
                            }
                            uc.abort().await;
                        }
                    }
                }
            }
        }));
    }

    async fn execute(&mut self) {
        let runtime = self.runtime.clone();
        let dp = self.dp.clone();
        let st = self.st.clone();
        let uc = self.uc.clone();
        let ta = self.ta.clone();
        let sta = self.sta.clone();
        let mu_ctx = self.mu_ctx.clone();
        self.wait_execute = Some(self.runtime.spawn(async move {
            let mut wait_async_uploads = LinkedList::<JoinHandle<()>>::new();
            loop {
                match st.pull().await {
                    None => break,
                    Some(mut si) => {
                        if uc.is_aborted() {
                            si.release().await;
                            continue;
                        }

                        wait_async_uploads.push_back(
                            uc.clone()
                                .async_upload(
                                    runtime.clone(),
                                    dp.clone(),
                                    st.clone(),
                                    ta.clone(),
                                    sta.clone(),
                                    mu_ctx.clone(),
                                    si,
                                )
                                .await,
                        );
                    }
                }
            }
            join_all(wait_async_uploads).await;
        }));
    }

    async fn put_empty_object(&self) -> Result<(), TosError> {
        self.uc.put_empty_object().await
    }

    fn is_aborted(&self) -> bool {
        self.uc.is_aborted()
    }

    fn is_sealed(&self) -> bool {
        self.uc.is_sealed()
    }

    fn is_created(&self) -> bool {
        self.uc.is_created()
    }
}

struct UploadContext {
    aborted: AtomicI8,
    sealed: AtomicI8,
    created: AtomicI8,
    upload_id: ArcSwap<String>,
    mum: RwLock<MultipartUploadMeta>,
    wp: Arc<WriteParam>,
    client: Arc<InnerTosClient>,
}

impl UploadContext {
    fn new(created: AtomicI8, wp: Arc<WriteParam>, client: Arc<InnerTosClient>) -> Self {
        Self {
            aborted: AtomicI8::new(0),
            sealed: AtomicI8::new(0),
            created,
            upload_id: ArcSwap::new(Arc::new("".to_string())),
            mum: RwLock::new(MultipartUploadMeta::new(16)),
            wp,
            client,
        }
    }

    fn is_aborted(&self) -> bool {
        self.aborted.load(Ordering::Acquire) == 1
    }

    fn is_sealed(&self) -> bool {
        self.sealed.load(Ordering::Acquire) == 1
    }
    fn seal(&self) {
        let _ = self
            .sealed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed);
    }
    fn is_created(&self) -> bool {
        self.created.load(Ordering::Acquire) == 1
    }

    async fn async_upload(
        self: Arc<Self>,
        runtime: Arc<Runtime>,
        dp: Arc<Dispatcher>,
        st: Arc<Store>,
        ta: Arc<TokenAcquirer>,
        sta: Arc<Option<TokenAcquirer>>,
        mu_ctx: Arc<MultipartUploadContext>,
        mut si: StoreItem,
    ) -> JoinHandle<()> {
        let permit = match sta.as_ref() {
            Some(sta) => match ta.try_acquire() {
                Ok(permit) => permit,
                Err(_) => sta.acquire().await.unwrap(),
            },
            None => ta.acquire().await.unwrap(),
        };

        runtime.spawn(async move {
            if false {
                drop(permit);
            }
            if self.aborted.load(Ordering::Acquire) == 1 {
                si.release().await;
                return;
            }

            if si.part_number() > 1 {
                mu_ctx.kick_off(OTHER_MU_KICK_OFF).await;
                mu_ctx.wait_finished().await;
                if self.aborted.load(Ordering::Acquire) == 1 {
                    si.release().await;
                    return;
                }

                // upload part
                self.upload_part(si).await;
                return;
            }

            let flag = mu_ctx.wait_kick_off().await;
            if self.aborted.load(Ordering::Acquire) == 1 {
                si.release().await;
                return;
            }

            if flag == RELEASE_MU_KICK_OFF && dp.index() == 1 && st.index() == 1 {
                mu_ctx.mark_finished().await;
                // put object directly
                if let Some((data_list, buffer_pool)) = si.take() {
                    let mut input = PutObjectFromBufferInput::new(
                        self.wp.bucket.as_str(),
                        self.wp.key.as_str(),
                    );
                    let mut len = 0;
                    let mut freeze_data_list = Vec::with_capacity(data_list.len());
                    for data in data_list {
                        len += data.len();
                        freeze_data_list.push(data.freeze());
                    }
                    let freeze_data_list2 = freeze_data_list.clone();
                    input.set_content_length(len as i64);
                    input.set_content_with_bytes_list(freeze_data_list.into_iter());
                    if let Some(sc) = self.wp.storage_class.as_ref() {
                        if let Some(sc) = trans_storage_class(sc) {
                            input.set_storage_class(sc);
                        }
                    }
                    let output = self.client.put_object_from_buffer(&input).await;
                    drop(input);
                    si.release().await;
                    for data in freeze_data_list2 {
                        let data = data.try_into_mut().unwrap();
                        buffer_pool.deallocate(data).await;
                    }
                    match output {
                        Err(ex) => {
                            error!(
                                "put object in bucket [{}] with key [{}] failed, {}",
                                self.wp.bucket,
                                self.wp.key,
                                ex.to_string()
                            );
                            self.abort().await;
                        }
                        Ok(_) => {
                            let _ = self.created.compare_exchange(
                                0,
                                1,
                                Ordering::AcqRel,
                                Ordering::Relaxed,
                            );
                        }
                    }
                }
                return;
            }

            // init multipart upload first
            let mut input =
                CreateMultipartUploadInput::new(self.wp.bucket.as_str(), self.wp.key.as_str());
            if let Some(sc) = self.wp.storage_class.as_ref() {
                if let Some(sc) = trans_storage_class(sc) {
                    input.set_storage_class(sc);
                }
            }
            match self.client.create_multipart_upload(&input).await {
                Err(ex) => {
                    error!(
                        "init multipart upload in bucket [{}] with key [{}] failed, {}",
                        self.wp.bucket,
                        self.wp.key,
                        ex.to_string()
                    );
                    self.abort().await;
                    si.release().await;
                    mu_ctx.mark_finished().await;
                }
                Ok(output) => {
                    self.upload_id
                        .store(Arc::new(output.upload_id().to_string()));
                    mu_ctx.mark_finished().await;
                    self.upload_part(si).await;
                }
            }
        })
    }

    async fn upload_part(&self, mut si: StoreItem) {
        let upload_id = self.upload_id.load();
        if upload_id.as_str() != "" {
            if let Some((data_list, buffer_pool)) = si.take() {
                let mut input = UploadPartFromBufferInput::new(
                    self.wp.bucket.as_str(),
                    self.wp.key.as_str(),
                    upload_id.as_str(),
                );
                input.set_part_number(si.part_number());
                let mut len = 0;
                let mut freeze_data_list = Vec::with_capacity(data_list.len());
                for data in data_list {
                    len += data.len();
                    freeze_data_list.push(data.freeze());
                }
                let freeze_data_list2 = freeze_data_list.clone();
                input.set_content_with_bytes_list(freeze_data_list.into_iter());
                input.set_content_length(len as i64);
                let output = self.client.upload_part_from_buffer(&input).await;
                drop(input);
                si.release().await;
                for data in freeze_data_list2 {
                    let data = data.try_into_mut().unwrap();
                    buffer_pool.deallocate(data).await;
                }
                match output {
                    Err(ex) => {
                        error!("upload part in bucket [{}] with key [{}] failed upload id [{}], part number [{}], {}", self.wp.bucket, 
                                self.wp.key, upload_id.as_str(), si.part_number(), ex.to_string());
                        self.abort().await;
                    }
                    Ok(output) => {
                        self.mum.write().await.add_object_part(
                            si.part_number(),
                            ObjectPart {
                                uploaded_part: UploadedPart::new(si.part_number(), output.etag()),
                                crc64: output.hash_crc64ecma(),
                            },
                        );
                    }
                }
            }
        }
    }

    async fn abort(&self) {
        if let Ok(_) = self
            .aborted
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            let upload_id = self.upload_id.load();
            if upload_id.as_str() != "" {
                let input = AbortMultipartUploadInput::new(
                    self.wp.bucket.as_str(),
                    self.wp.key.as_str(),
                    upload_id.as_str(),
                );
                if let Err(ex) = self.client.abort_multipart_upload(&input).await {
                    match ex {
                        TosError::TosClientError { message, .. } => {
                            warn!("abort multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}", self.wp.bucket,
                                    self.wp.key, upload_id.as_str(), message);
                        }
                        TosError::TosServerError {
                            message,
                            status_code,
                            ..
                        } => {
                            if status_code == 404 {
                                info!("abort multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}", self.wp.bucket,
                                    self.wp.key,upload_id.as_str(), message);
                            } else {
                                warn!("abort multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}", self.wp.bucket,
                                    self.wp.key, upload_id.as_str(), message);
                            }
                        }
                    }
                }
            }
        }
    }

    async fn complete_multipart_upload(&self) -> Result<(), TosError> {
        let upload_id = self.upload_id.load();
        if upload_id.as_str() != "" {
            let mut mum = self.mum.write().await;
            let mut input = CompleteMultipartUploadInput::new(
                self.wp.bucket.as_str(),
                self.wp.key.as_str(),
                upload_id.as_str(),
            );
            input.set_parts(mum.get_object_parts());
            match self.client.complete_multipart_upload(&input).await {
                Err(ex) => {
                    error!("complete multipart upload in bucket [{}] with key [{}] failed, upload id [{}], {}",
                        self.wp.bucket, self.wp.key, upload_id.as_str(), ex.to_string());
                    self.abort().await;
                    return Err(ex);
                }
                Ok(_) => {
                    let _ =
                        self.created
                            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed);
                }
            }
            self.upload_id.store(Arc::new("".to_string()));
        }
        Ok(())
    }

    async fn put_empty_object(&self) -> Result<(), TosError> {
        let mut input =
            PutObjectFromBufferInput::new(self.wp.bucket.as_str(), self.wp.key.as_str());
        input.set_content_length(0);
        if let Some(sc) = self.wp.storage_class.as_ref() {
            if let Some(sc) = trans_storage_class(sc) {
                input.set_storage_class(sc);
            }
        }
        match self.client.put_object_from_buffer(&input).await {
            Err(ex) => {
                error!(
                    "put empty object in bucket [{}] with key [{}] failed, {}",
                    self.wp.bucket,
                    self.wp.key,
                    ex.to_string()
                );
                Err(ex)
            }
            Ok(_) => Ok(()),
        }
    }
}

struct Part {
    data_list: LinkedList<BytesMut>,
    buffer_pool: BufferPool,
    filled_size: isize,
    part_size: isize,
}

impl Part {
    fn new(part_size: isize, buffer_pool: BufferPool) -> Self {
        Self {
            data_list: LinkedList::new(),
            buffer_pool,
            filled_size: 0,
            part_size,
        }
    }

    async fn fill(&mut self, data: &[u8]) -> isize {
        if data.len() == 0 {
            return 0;
        }

        if self.is_full() {
            return 0;
        }

        match self.data_list.back() {
            None => {
                let buf = self.buffer_pool.must_allocate().await;
                self.data_list.push_back(buf);
            }
            Some(last) => {
                if last.len() == DEFAULT_PART_SIZE as usize {
                    let buf = self.buffer_pool.must_allocate().await;
                    self.data_list.push_back(buf);
                }
            }
        };

        let last = self.data_list.back_mut().unwrap();
        let remaining = min(
            self.part_size - self.filled_size,
            DEFAULT_PART_SIZE - last.len() as isize,
        );

        if remaining >= data.len() as isize {
            last.extend_from_slice(data);
            let result = data.len() as isize;
            self.filled_size += result;
            return result;
        }
        last.extend_from_slice(&data[..remaining as usize]);
        self.filled_size += remaining;
        remaining
    }

    fn is_full(&self) -> bool {
        self.filled_size >= self.part_size
    }

    fn size(&self) -> isize {
        self.filled_size as isize
    }

    async fn release(&mut self) {
        while !self.data_list.is_empty() {
            let front = self.data_list.pop_front().unwrap();
            self.buffer_pool.deallocate(front).await;
        }
    }
}

struct Dispatcher {
    sender: Sender<Part>,
    receiver: Receiver<Part>,
    inner_queue_size: isize,
    inner_index: AtomicIsize,
    closed: AtomicI8,
}

impl Dispatcher {
    fn new(inner_queue_size: isize) -> Self {
        let (sender, receiver) = async_channel::bounded(inner_queue_size as usize);
        Self {
            sender,
            receiver,
            inner_queue_size,
            inner_index: AtomicIsize::new(0),
            closed: AtomicI8::new(0),
        }
    }

    async fn push(&self, part: Part) -> (Option<Part>, bool) {
        match self.sender.send(part).await {
            Ok(_) => {
                self.inner_index.fetch_add(1, Ordering::Release);
                (None, true)
            }
            Err(ex) => (Some(ex.0), false),
        }
    }

    async fn pull(&self) -> Option<Part> {
        match self.receiver.recv().await {
            Ok(part) => Some(part),
            Err(_) => None,
        }
    }

    fn index(&self) -> isize {
        self.inner_index.load(Ordering::Acquire)
    }

    fn close(&self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            self.sender.close();
        }
    }

    fn reopen(&mut self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(1, 0, Ordering::AcqRel, Ordering::Relaxed)
        {
            let (sender, receiver) = async_channel::bounded(self.inner_queue_size as usize);
            self.sender = sender;
            self.receiver = receiver;
        }
    }
}

struct Store {
    sender: Sender<StoreItem>,
    receiver: Receiver<StoreItem>,
    part_size: isize,
    next_part_number: AtomicIsize,
    next_object_start: AtomicIsize,
    closed: AtomicI8,
}

impl Store {
    fn new(part_size: isize, next_object_start: isize) -> Self {
        let (sender, receiver) = async_channel::bounded(calc_queue_size(part_size) as usize);
        Self {
            sender,
            receiver,
            part_size,
            next_part_number: AtomicIsize::new(1),
            next_object_start: AtomicIsize::new(next_object_start),
            closed: AtomicI8::new(0),
        }
    }

    fn new_store_item(&self, part: Part) -> StoreItem {
        let object_start = self.next_object_start.load(Ordering::Acquire);
        let object_end = object_start + part.size();
        StoreItem {
            part: Some(part),
            object_start,
            object_end,
            part_number: self.next_part_number.load(Ordering::Acquire),
        }
    }

    fn index(&self) -> isize {
        self.next_part_number.load(Ordering::Acquire) - 1
    }

    async fn push(&self, part: Part) -> (Option<Part>, bool) {
        let part_size = part.size();
        match self.sender.send(self.new_store_item(part)).await {
            Ok(_) => {
                self.next_object_start
                    .fetch_add(part_size, Ordering::Release);
                self.next_part_number.fetch_add(1, Ordering::Release);
                (None, true)
            }
            Err(ex) => (ex.0.part, false),
        }
    }

    async fn pull(&self) -> Option<StoreItem> {
        match self.receiver.recv().await {
            Ok(si) => Some(si),
            Err(_) => None,
        }
    }

    fn close(&self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            self.sender.close();
        }
    }

    fn destroy(&self) {
        self.close();
        // do nothing
    }

    fn reopen(&mut self) {
        if let Ok(_) = self
            .closed
            .compare_exchange(1, 0, Ordering::AcqRel, Ordering::Relaxed)
        {
            let (sender, receiver) =
                async_channel::bounded(calc_queue_size(self.part_size) as usize);
            self.sender = sender;
            self.receiver = receiver;
        }
    }
}

struct StoreItem {
    part: Option<Part>,
    object_start: isize,
    object_end: isize,
    part_number: isize,
}

impl StoreItem {
    fn part_number(&self) -> isize {
        self.part_number
    }

    fn object_start(&self) -> isize {
        self.object_start
    }

    fn object_end(&self) -> isize {
        self.object_end
    }

    fn take(&mut self) -> Option<(LinkedList<BytesMut>, BufferPool)> {
        match self.part.take() {
            None => None,
            Some(part) => Some((part.data_list, part.buffer_pool)),
        }
    }

    fn size(&self) -> isize {
        if let Some(part) = self.part.as_ref() {
            return part.size();
        }
        0
    }

    async fn release(&mut self) {
        if let Some(part) = self.part.as_mut() {
            part.release().await;
        }
    }
}

struct MultipartUploadContext {
    kick_off_lock: RwLock<i8>,
    kick_off_notify: Notify,
    finished_lock: RwLock<bool>,
    finished_notify: Notify,
}

impl MultipartUploadContext {
    fn new() -> Self {
        Self {
            kick_off_lock: RwLock::new(0),
            kick_off_notify: Notify::new(),
            finished_lock: RwLock::new(false),
            finished_notify: Notify::new(),
        }
    }

    async fn kick_off(&self, flag: i8) {
        if flag <= 0 {
            return;
        }

        {
            let val = self.kick_off_lock.read().await;
            if *val > 0 {
                return;
            }
        }

        let mut val = self.kick_off_lock.write().await;
        if *val > 0 {
            return;
        }
        *val = flag;
        self.kick_off_notify.notify_waiters();
    }

    async fn wait_kick_off(&self) -> i8 {
        loop {
            {
                let val = self.kick_off_lock.read().await;
                if *val > 0 {
                    return *val;
                }
            }
            self.kick_off_notify.notified().await;
        }
    }

    async fn mark_finished(&self) {
        {
            let val = self.finished_lock.read().await;
            if *val {
                return;
            }
        }

        let mut val = self.finished_lock.write().await;
        if *val {
            return;
        }
        *val = true;
        self.finished_notify.notify_waiters();
    }

    async fn wait_finished(&self) {
        loop {
            {
                let val = self.finished_lock.read().await;
                if *val {
                    return;
                }
            }
            self.finished_notify.notified().await;
        }
    }
}

struct MultipartUploadMeta {
    object_parts: Option<HashMap<isize, ObjectPart>>,
    cap: isize,
}

impl MultipartUploadMeta {
    fn new(cap: isize) -> Self {
        Self {
            object_parts: None,
            cap,
        }
    }

    fn add_object_part(&mut self, part_number: isize, op: ObjectPart) {
        if self.object_parts.is_none() {
            self.object_parts = Some(HashMap::with_capacity(self.cap as usize));
        }

        if let Some(object_parts) = self.object_parts.as_mut() {
            object_parts.insert(part_number, op);
        }
    }

    fn get_object_parts(&mut self) -> Vec<UploadedPart> {
        if let Some(object_parts) = self.object_parts.take() {
            let mut result = Vec::with_capacity(object_parts.len());
            for (_, op) in object_parts {
                result.push(op.uploaded_part);
            }
            return result;
        }
        Vec::new()
    }
}

struct ObjectPart {
    uploaded_part: UploadedPart,
    crc64: u64,
}

fn calc_queue_size(part_size: isize) -> isize {
    let mut queue_size = DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT / part_size;
    if DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT % part_size != 0 {
        queue_size += 1;
    }
    queue_size
}

fn trans_storage_class(value: impl AsRef<str>) -> Option<StorageClassType> {
    match value.as_ref() {
        "STANDARD" => Some(StorageClassType::StorageClassStandard),
        "IA" => Some(StorageClassType::StorageClassIa),
        "ARCHIVE_FR" => Some(StorageClassType::StorageClassArchiveFr),
        "INTELLIGENT_TIERING" => Some(StorageClassType::StorageClassIntelligentTiering),
        "COLD_ARCHIVE" => Some(StorageClassType::StorageClassColdArchive),
        "ARCHIVE" => Some(StorageClassType::StorageClassArchive),
        "DEEP_COLD_ARCHIVE" => Some(StorageClassType::StorageClassDeepColdArchive),
        _ => None,
    }
}
