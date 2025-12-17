use crate::common::{BufferPool, TokenAcquirer};
use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_model::TosObject;
use crate::write_stream::WriteStream;
use async_trait::async_trait;
use futures_util::future::BoxFuture;
use std::future::Future;
use std::sync::atomic::{AtomicIsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use tokio::runtime::{Builder, Handle, Runtime};
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::asynchronous::tos;
use ve_tos_rust_sdk::asynchronous::tos::{AsyncRuntime, TosClientImpl};
use ve_tos_rust_sdk::credential::{CommonCredentials, CommonCredentialsProvider};
use ve_tos_rust_sdk::error::{GenericError, TosError};
use ve_tos_rust_sdk::object::HeadObjectInput;

#[derive(Debug, Default)]
pub struct TokioRuntime {
    pub(crate) runtime: Option<Arc<Runtime>>,
}

#[async_trait]
impl AsyncRuntime for TokioRuntime {
    type JoinError = tokio::task::JoinError;
    async fn sleep(&self, duration: Duration) {
        tokio::time::sleep(duration).await;
    }

    fn spawn<'a, F>(&self, future: F) -> BoxFuture<'a, Result<F::Output, Self::JoinError>>
    where
        F: Future + Send + 'static,
        F::Output: Send + 'static,
    {
        match self.runtime.as_ref() {
            None => Box::pin(Handle::current().spawn(future)),
            Some(r) => Box::pin(r.spawn(future)),
        }
    }

    fn block_on<F: Future>(&self, future: F) -> F::Output {
        match self.runtime.as_ref() {
            None => Handle::current().block_on(future),
            Some(r) => r.block_on(future),
        }
    }
}

pub(crate) type InnerTosClient =
    TosClientImpl<CommonCredentialsProvider<CommonCredentials>, CommonCredentials, TokioRuntime>;

pub struct TosClient {
    rclient: Arc<InnerTosClient>,
    wclient: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    pcontext: Arc<SharedPrefetchContext>,
    sta: Arc<Option<TokenAcquirer>>,
    buffer_pool: BufferPool,

    region: String,
    endpoint: String,
    ak: String,
    sk: String,
    part_size: isize,
    max_retry_count: isize,
    max_prefetch_tasks: isize,
    shared_prefetch_tasks: isize,
    max_upload_part_tasks: isize,
    shared_upload_part_tasks: isize,
    enable_crc: bool,
}

impl TosClient {
    pub fn new(
        region: String,
        endpoint: String,
        ak: String,
        sk: String,
        part_size: isize,
        max_retry_count: isize,
        max_prefetch_tasks: isize,
        shared_prefetch_tasks: isize,
        enable_crc: bool,
        max_upload_part_tasks: isize,
        shared_upload_part_tasks: isize,
        max_worker_threads: isize,
    ) -> Result<Self, TosError> {
        let mut builder = Builder::new_multi_thread();
        if max_worker_threads > 0 {
            builder.worker_threads(max_worker_threads as usize);
        } else if let Ok(max_worker_threads) = thread::available_parallelism() {
            builder.worker_threads(max_worker_threads.get());
        } else {
            builder.worker_threads(16);
        }
        match builder.enable_all().build() {
            Err(ex) => Err(TosError::TosClientError {
                message: "build runtime error".to_string(),
                cause: Some(GenericError::DefaultError(ex.to_string())),
                request_url: "".to_string(),
            }),
            Ok(runtime) => {
                let runtime = Arc::new(runtime);
                let mut clients = Vec::with_capacity(2);
                for _ in 0..2 {
                    match tos::builder()
                        .connection_timeout(3000)
                        .request_timeout(120000)
                        .max_connections(10000)
                        .max_retry_count(max_retry_count)
                        .ak(ak.clone())
                        .sk(sk.clone())
                        .region(region.clone())
                        .endpoint(endpoint.clone())
                        .enable_crc(enable_crc)
                        .async_runtime(TokioRuntime {
                            runtime: Some(runtime.clone()),
                        })
                        .build()
                    {
                        Err(ex) => return Err(ex),
                        Ok(client) => {
                            clients.push(client);
                        }
                    }
                }

                let sta;
                if shared_upload_part_tasks > 0 {
                    sta = Some(TokenAcquirer::new(shared_upload_part_tasks));
                } else {
                    sta = None;
                }

                Ok(Self {
                    rclient: Arc::new(clients.pop().unwrap()),
                    wclient: Arc::new(clients.pop().unwrap()),
                    runtime,
                    pcontext: Arc::new(SharedPrefetchContext::new(shared_prefetch_tasks)),
                    sta: Arc::new(sta),
                    buffer_pool: BufferPool::new(0, 0),
                    region,
                    endpoint,
                    ak,
                    sk,
                    part_size,
                    max_retry_count,
                    max_prefetch_tasks,
                    shared_prefetch_tasks,
                    max_upload_part_tasks,
                    shared_upload_part_tasks,
                    enable_crc,
                })
            }
        }
    }

    pub fn list_objects(
        &self,
        bucket: String,
        prefix: String,
        max_keys: isize,
        delimiter: String,
        continuation_token: String,
        start_after: String,
        list_background_buffer_count: isize,
    ) -> ListStream {
        ListStream::new(
            self.rclient.clone(),
            self.runtime.clone(),
            bucket,
            prefix,
            delimiter,
            max_keys,
            continuation_token,
            start_after,
            list_background_buffer_count,
        )
    }
    pub fn head_object(&self, bucket: String, key: String) -> Result<TosObject, TosError> {
        let input = HeadObjectInput::new(bucket, key);
        self.runtime.block_on(async {
            match self.rclient.head_object(&input).await {
                Err(ex) => Err(ex),
                Ok(output) => Ok(TosObject::inner_new(input.bucket(), input.key(), output)),
            }
        })
    }

    pub async fn async_head_object(
        &self,
        bucket: String,
        key: String,
    ) -> Result<TosObject, TosError> {
        let input = HeadObjectInput::new(bucket, key);
        match self.rclient.head_object(&input).await {
            Err(ex) => Err(ex),
            Ok(output) => Ok(TosObject::inner_new(input.bucket(), input.key(), output)),
        }
    }

    pub fn get_object(&self, bucket: String, key: String, etag: String, size: isize) -> ReadStream {
        ReadStream::new(
            self.rclient.clone(),
            self.runtime.clone(),
            self.pcontext.clone(),
            bucket,
            key,
            etag,
            size,
            self.part_size,
            self.max_prefetch_tasks,
        )
    }

    pub fn put_object(
        &self,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> Result<WriteStream, TosError> {
        let client = self.wclient.clone();
        let runtime = self.runtime.clone();
        let part_size = self.part_size;
        let max_upload_part_tasks = self.max_upload_part_tasks;
        let sta = self.sta.clone();
        let buffer_pool = self.buffer_pool.clone();
        runtime.clone().block_on(async {
            WriteStream::new(
                client,
                runtime,
                bucket,
                key,
                storage_class,
                part_size,
                max_upload_part_tasks,
                sta,
                buffer_pool,
            )
            .await
        })
    }

    pub async fn async_put_object(
        &self,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> Result<WriteStream, TosError> {
        let client = self.wclient.clone();
        let runtime = self.runtime.clone();
        let part_size = self.part_size;
        let max_upload_part_tasks = self.max_upload_part_tasks;
        let sta = self.sta.clone();
        let buffer_pool = self.buffer_pool.clone();
        WriteStream::new(
            client,
            runtime,
            bucket,
            key,
            storage_class,
            part_size,
            max_upload_part_tasks,
            sta,
            buffer_pool,
        )
        .await
    }

    pub fn get_async_runtime(&self) -> Arc<Runtime> {
        self.runtime.clone()
    }

    pub async fn async_close(&self) {
        self.rclient.shutdown().await;
        self.wclient.shutdown().await;
    }

    pub fn close(&self) {
        self.runtime.block_on(async {
            self.async_close().await;
        })
    }
}

pub(crate) struct SharedPrefetchContext {
    stolen_shared_prefetch_tasks: AtomicIsize,
    shared_prefetch_tasks: isize,
}

impl SharedPrefetchContext {
    pub(crate) fn new(shared_prefetch_tasks: isize) -> Self {
        Self {
            stolen_shared_prefetch_tasks: AtomicIsize::new(0),
            shared_prefetch_tasks,
        }
    }

    pub(crate) fn try_steal_shared_prefetch_task(&self) -> bool {
        loop {
            let current = self.stolen_shared_prefetch_tasks.load(Ordering::Acquire);
            if current >= self.shared_prefetch_tasks {
                return false;
            }
            if let Ok(_) = self.stolen_shared_prefetch_tasks.compare_exchange(
                current,
                current + 1,
                Ordering::AcqRel,
                Ordering::Relaxed,
            ) {
                return true;
            }
        }
    }

    pub(crate) fn release_shared_prefetch_task(&self) {
        self.stolen_shared_prefetch_tasks
            .fetch_add(-1, Ordering::Release);
    }
}
