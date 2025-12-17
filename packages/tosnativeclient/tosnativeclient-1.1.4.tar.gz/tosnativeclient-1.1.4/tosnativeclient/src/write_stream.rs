use crate::tos_error::map_tos_error;
use pyo3::{pyclass, pymethods, PyRefMut, PyResult};
use std::sync::Arc;

#[pyclass(name = "WriteStream", module = "tosnativeclient")]
pub struct WriteStream {
    pub(crate) write_stream: Arc<tosnativeclient_core::write_stream::WriteStream>,
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) key: String,
    #[pyo3(get)]
    pub(crate) storage_class: Option<String>,
}

#[pymethods]
impl WriteStream {
    pub fn write(slf: PyRefMut<'_, Self>, data: &[u8]) -> PyResult<isize> {
        let write_stream = slf.write_stream.clone();
        match slf.py().allow_threads(|| write_stream.write(data)) {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(written) => Ok(written),
        }
    }

    pub fn close(slf: PyRefMut<'_, Self>) -> PyResult<()> {
        let write_stream = slf.write_stream.clone();
        match slf.py().allow_threads(|| write_stream.close()) {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(_) => Ok(()),
        }
    }
}
