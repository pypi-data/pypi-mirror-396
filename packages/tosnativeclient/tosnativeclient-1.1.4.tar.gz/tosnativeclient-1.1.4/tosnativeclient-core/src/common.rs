use bytes::BytesMut;
use pprof::flamegraph::Options;
use pprof::ProfilerGuard;
use slab::Slab;
use std::fs::File;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;
use std::{fs, io, thread};
use tokio::sync::{AcquireError, OwnedSemaphorePermit, RwLock, Semaphore, TryAcquireError};
use tracing::warn;

const DEFAULT_BUFFER_SIZE: isize = 8 * 1024 * 1024;
const DEFAULT_BUFFER_COUNT: isize = 100;

pub fn async_write_profile(seconds: i64, file_path: &str, mut image_width: usize) {
    if seconds <= 0 {
        return;
    }

    let fp;
    if file_path.is_empty() {
        fp = String::from("cpu_profile.html");
    } else if !file_path.ends_with(".html") {
        fp = String::from(file_path) + ".html";
    } else {
        fp = file_path.to_string();
    }

    if let Some(p) = Path::new(fp.as_str()).parent() {
        if let Err(ex) = fs::create_dir_all(p) {
            if ex.kind() != io::ErrorKind::AlreadyExists {
                warn!("flamegraph error, {:?}", ex);
                return;
            }
        }
    }
    if image_width <= 0 {
        image_width = 1200;
    }
    match ProfilerGuard::new(100) {
        Err(ex) => {
            warn!("flamegraph new error, {:?}", ex);
        }
        Ok(guard) => {
            thread::spawn(move || {
                sleep(Duration::from_secs(seconds as u64));
                match File::create(fp) {
                    Ok(fd) => {
                        if let Ok(report) = guard.report().build() {
                            let mut options = Options::default();
                            options.image_width = Some(image_width);
                            if let Err(ex) = report.flamegraph_with_options(fd, &mut options) {
                                warn!("flamegraph error, {:?}", ex);
                            }
                        }
                    }
                    Err(ex) => {
                        warn!("flamegraph error, {:?}", ex);
                    }
                }
            });
        }
    }
}

pub(crate) struct TokenAcquirer {
    semaphore: Arc<Semaphore>,
}

impl TokenAcquirer {
    pub(crate) fn new(max_tokens: isize) -> Self {
        Self {
            semaphore: Arc::new(Semaphore::new(max_tokens as usize)),
        }
    }

    pub(crate) async fn acquire(&self) -> Result<OwnedSemaphorePermit, AcquireError> {
        self.semaphore.clone().acquire_owned().await
    }

    pub(crate) fn try_acquire(&self) -> Result<OwnedSemaphorePermit, TryAcquireError> {
        self.semaphore.clone().try_acquire_owned()
    }

    pub(crate) fn close(&self) {
        self.semaphore.close();
    }

    pub(crate) fn available_permits(&self) -> usize {
        self.semaphore.available_permits()
    }
}

pub(crate) struct BufferPool {
    inner: Arc<RwLock<Slab<BytesMut>>>,
    buffer_count: isize,
    buffer_size: isize,
}

impl Clone for BufferPool {
    fn clone(&self) -> Self {
        Self {
            inner: self.inner.clone(),
            buffer_count: self.buffer_count,
            buffer_size: self.buffer_size,
        }
    }
}

impl BufferPool {
    pub(crate) fn new(mut buffer_size: isize, total_buffer_size: isize) -> Self {
        if buffer_size <= 0 {
            buffer_size = DEFAULT_BUFFER_SIZE
        }

        let mut buffer_count = total_buffer_size / buffer_size;

        if buffer_count <= 0 {
            buffer_count = DEFAULT_BUFFER_COUNT;
        }

        let mut slab = Slab::with_capacity(buffer_count as usize);
        for _ in 0..buffer_count {
            let mut buffer = BytesMut::with_capacity(buffer_size as usize);
            buffer.resize(buffer_size as usize, 0);
            slab.insert(buffer);
        }
        Self {
            inner: Arc::new(RwLock::new(slab)),
            buffer_count,
            buffer_size,
        }
    }
    pub(crate) fn buffer_size(&self) -> isize {
        self.buffer_size
    }
    pub(crate) fn buffer_count(&self) -> isize {
        self.buffer_count
    }

    pub(crate) async fn len(&self) -> usize {
        self.inner.read().await.len()
    }

    pub(crate) async fn must_allocate(&self) -> BytesMut {
        {
            let inner = self.inner.read().await;
            if inner.len() == 0 {
                return BytesMut::with_capacity(self.buffer_size as usize);
            }
        }

        let mut inner = self.inner.write().await;
        if inner.len() == 0 {
            return BytesMut::with_capacity(self.buffer_size as usize);
        }
        let key = inner.iter().next().map(|(key, _)| key).unwrap();
        let mut buf = inner.remove(key);
        buf.clear();
        buf
    }

    pub(crate) async fn deallocate(&self, mut buffer: BytesMut) {
        if buffer.capacity() != self.buffer_size as usize {
            return;
        }

        {
            let inner = self.inner.read().await;
            if inner.vacant_key() >= self.buffer_count as usize {
                return;
            }
        }

        let mut inner = self.inner.write().await;
        if inner.vacant_key() >= self.buffer_count as usize {
            return;
        };
        buffer.clear();
        inner.insert(buffer);
    }
}

#[cfg(test)]
mod tests {
    use crate::common::{BufferPool, DEFAULT_BUFFER_SIZE};
    use bytes::{Bytes, BytesMut};
    use std::fmt::Write;

    #[test]
    fn test_buffer_pool() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        rt.block_on(async {
            let pool = BufferPool::new(0, DEFAULT_BUFFER_SIZE * 3);
            assert_eq!(pool.len().await, 3);
            let buf = pool.must_allocate().await;
            assert_eq!(pool.len().await, 2);
            let pool2 = pool.clone();
            let handler = rt.spawn(async move {
                let mut buf = pool2.must_allocate().await;
                assert_eq!(pool2.len().await, 1);
                assert_eq!(buf.len(), 0);
                buf.write_str("hello world").unwrap();
                assert_eq!(buf.len(), "hello world".len());
                buf
            });
            let buf2 = handler.await.unwrap();
            assert_eq!(pool.len().await, 1);
            let pool2 = pool.clone();
            let handler = rt.spawn(async move {
                pool2.deallocate(buf).await;
                assert_eq!(pool2.len().await, 2);
                pool2.deallocate(buf2).await;

                pool2
                    .deallocate(BytesMut::with_capacity(DEFAULT_BUFFER_SIZE as usize))
                    .await;
            });
            let _ = handler.await;
            assert_eq!(pool.len().await, 3);
        });
    }
}
