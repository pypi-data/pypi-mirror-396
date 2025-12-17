use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_error::map_tos_error;
use crate::tos_model::TosObject;
use crate::write_stream::WriteStream;
use pyo3::types::PyTuple;
use pyo3::{pyclass, pymethods, Bound, IntoPyObject, IntoPyObjectExt, PyRef, PyResult};
use std::sync::{Arc, RwLock};

#[pyclass(name = "TosClient", module = "tosnativeclient")]
pub struct TosClient {
    pub(crate) client: Arc<tosnativeclient_core::tos_client::TosClient>,
    #[pyo3(get)]
    pub(crate) region: String,
    #[pyo3(get)]
    pub(crate) endpoint: String,
    #[pyo3(get)]
    pub(crate) ak: String,
    #[pyo3(get)]
    pub(crate) sk: String,
    #[pyo3(get)]
    pub(crate) part_size: isize,
    #[pyo3(get)]
    pub(crate) max_retry_count: isize,
    #[pyo3(get)]
    pub(crate) max_prefetch_tasks: isize,
    #[pyo3(get)]
    pub(crate) shared_prefetch_tasks: isize,
    #[pyo3(get)]
    pub(crate) enable_crc: bool,
}

#[pymethods]
impl TosClient {
    #[new]
    #[pyo3(signature = (region, endpoint, ak=String::from(""), sk=String::from(""), part_size=8388608, max_retry_count=3, max_prefetch_tasks=3,
    shared_prefetch_tasks=32, enable_crc=true, max_upload_part_tasks=3, shared_upload_part_tasks=32))]
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
    ) -> PyResult<Self> {
        match tosnativeclient_core::tos_client::TosClient::new(
            region.clone(),
            endpoint.clone(),
            ak.clone(),
            sk.clone(),
            part_size,
            max_retry_count,
            max_prefetch_tasks,
            shared_prefetch_tasks,
            enable_crc,
            max_upload_part_tasks,
            shared_upload_part_tasks,
            0,
        ) {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(client) => Ok(Self {
                client: Arc::new(client),
                region,
                endpoint,
                ak,
                sk,
                part_size,
                max_retry_count,
                max_prefetch_tasks,
                shared_prefetch_tasks,
                enable_crc,
            }),
        }
    }

    #[pyo3(signature = (bucket, prefix=String::from(""), max_keys=1000, delimiter=String::from(""),
    continuation_token=String::from(""), start_after=String::from(""), list_background_buffer_count=1))]
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
        let list_stream = self.client.list_objects(
            bucket.to_string(),
            prefix.to_string(),
            max_keys,
            delimiter.to_string(),
            continuation_token.to_string(),
            start_after.to_string(),
            list_background_buffer_count,
        );

        ListStream {
            list_stream: Arc::new(RwLock::new(list_stream)),
            bucket,
            prefix,
            delimiter,
            max_keys,
            continuation_token,
            start_after,
            list_background_buffer_count,
        }
    }
    #[pyo3(signature = (bucket, key))]
    pub fn head_object(slf: PyRef<'_, Self>, bucket: String, key: String) -> PyResult<TosObject> {
        let client = slf.client.clone();
        slf.py()
            .allow_threads(|| match client.head_object(bucket, key) {
                Err(ex) => Err(map_tos_error(ex)),
                Ok(output) => Ok(TosObject::new(
                    output.bucket().to_string(),
                    output.key().to_string(),
                    output.size(),
                    output.etag().to_string(),
                )),
            })
    }
    #[pyo3(signature = (bucket, key, etag, size))]
    pub fn get_object(&self, bucket: String, key: String, etag: String, size: isize) -> ReadStream {
        let read_stream = self
            .client
            .get_object(bucket.clone(), key.clone(), etag.clone(), size);
        ReadStream {
            read_stream: Arc::new(read_stream),
            bucket,
            key,
            etag,
            size,
        }
    }

    #[pyo3(signature = (bucket, key, storage_class=None))]
    pub fn put_object(
        slf: PyRef<'_, Self>,
        bucket: String,
        key: String,
        storage_class: Option<String>,
    ) -> PyResult<WriteStream> {
        let client = slf.client.clone();
        slf.py().allow_threads(|| {
            match client.put_object(bucket.clone(), key.clone(), storage_class.clone()) {
                Err(ex) => Err(map_tos_error(ex)),
                Ok(write_stream) => Ok(WriteStream {
                    write_stream: Arc::new(write_stream),
                    bucket,
                    key,
                    storage_class,
                }),
            }
        })
    }

    pub fn close(slf: PyRef<'_, Self>) {
        let client = slf.client.clone();
        slf.py().allow_threads(|| client.close());
    }

    pub fn __getnewargs__(slf: PyRef<'_, Self>) -> PyResult<Bound<'_, PyTuple>> {
        let py = slf.py();
        let state = [
            slf.region.clone().into_pyobject(py)?.into_any(),
            slf.endpoint.clone().into_pyobject(py)?.into_any(),
            slf.ak.clone().into_pyobject(py)?.into_any(),
            slf.sk.clone().into_pyobject(py)?.into_any(),
            slf.part_size.into_pyobject(py)?.into_any(),
            slf.max_retry_count.into_pyobject(py)?.into_any(),
            slf.max_prefetch_tasks.into_pyobject(py)?.into_any(),
            slf.shared_prefetch_tasks.into_pyobject(py)?.into_any(),
            slf.enable_crc.into_py_any(py)?.bind(py).to_owned(),
        ];
        PyTuple::new(py, state)
    }
}
