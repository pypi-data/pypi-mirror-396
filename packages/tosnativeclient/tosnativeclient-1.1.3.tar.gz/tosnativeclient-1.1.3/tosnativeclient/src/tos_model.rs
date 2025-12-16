use pyo3::types::PyTuple;
use pyo3::{pyclass, pymethods, Bound, IntoPyObject, PyRef, PyResult};
use ve_tos_rust_sdk::object::ListObjectsType2Output;

#[pyclass(name = "ListObjectsResult", module = "tosnativeclient")]
pub struct ListObjectsResult {
    #[pyo3(get)]
    pub(crate) contents: Vec<TosObject>,
    #[pyo3(get)]
    pub(crate) common_prefixes: Vec<String>,
}

impl ListObjectsResult {
    pub(crate) fn new(output: ListObjectsType2Output) -> Self {
        let mut contents = Vec::with_capacity(output.contents().len());
        for content in output.contents() {
            contents.push(TosObject {
                bucket: output.name().to_string(),
                key: content.key().to_string(),
                size: content.size() as isize,
                etag: content.etag().to_string(),
            });
        }

        let mut common_prefixes = Vec::with_capacity(output.common_prefixes().len());
        for common_prefix in output.common_prefixes() {
            common_prefixes.push(common_prefix.prefix().to_string());
        }
        Self {
            contents,
            common_prefixes,
        }
    }
}

#[derive(Clone)]
#[pyclass(name = "TosObject", module = "tosnativeclient")]
pub struct TosObject {
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) key: String,
    #[pyo3(get)]
    pub(crate) size: isize,
    #[pyo3(get)]
    pub(crate) etag: String,
}
#[pymethods]
impl TosObject {
    #[new]
    #[pyo3(signature = (bucket, key, size, etag))]
    pub fn new(bucket: String, key: String, size: isize, etag: String) -> Self {
        Self {
            bucket,
            key,
            size,
            etag,
        }
    }
    pub fn __getnewargs__(slf: PyRef<'_, Self>) -> PyResult<Bound<'_, PyTuple>> {
        let py = slf.py();
        let state = [
            slf.bucket.clone().into_pyobject(py)?.into_any(),
            slf.key.clone().into_pyobject(py)?.into_any(),
            slf.size.into_pyobject(py)?.into_any(),
            slf.etag.clone().into_pyobject(py)?.into_any(),
        ];
        PyTuple::new(py, state)
    }
}
