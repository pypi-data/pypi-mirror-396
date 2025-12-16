use crate::tos_error::map_tos_error;
use pyo3::types::PyBytes;
use pyo3::{pyclass, pymethods, Bound, PyRef, PyResult};
use std::sync::Arc;

const DEFAULT_PREFERRED_CHUNK_SIZE: isize = 128 * 1024;
const COMMON_IO_SIZE: isize = 1 * 1024 * 1024;

#[pyclass(name = "ReadStream", module = "tosnativeclient")]
pub struct ReadStream {
    pub(crate) read_stream: Arc<tosnativeclient_core::read_stream::ReadStream>,
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) key: String,
    #[pyo3(get)]
    pub(crate) etag: String,
    #[pyo3(get)]
    pub(crate) size: isize,
}

#[pymethods]
impl ReadStream {
    #[pyo3(signature = (offset=0, length=COMMON_IO_SIZE+DEFAULT_PREFERRED_CHUNK_SIZE))]
    pub fn read(
        slf: PyRef<'_, Self>,
        offset: isize,
        length: isize,
    ) -> PyResult<Option<Bound<'_, PyBytes>>> {
        let read_stream = slf.read_stream.clone();
        match slf
            .py()
            .allow_threads(|| read_stream.read(offset, length, true))
        {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(result) => match result {
                None => Ok(None),
                Some(data) => Ok(Some(PyBytes::new(slf.py(), data.as_ref()))),
            },
        }
    }

    pub fn close(slf: PyRef<'_, Self>) {
        let read_stream = slf.read_stream.clone();
        slf.py().allow_threads(|| read_stream.close());
    }
}
