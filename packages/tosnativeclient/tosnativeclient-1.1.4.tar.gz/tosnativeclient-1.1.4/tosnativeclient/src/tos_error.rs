use pyo3::exceptions::PyException;
use pyo3::types::PyTuple;
use pyo3::{create_exception, pyclass, pymethods, Bound, IntoPyObject, PyErr, PyRef, PyResult};
use std::error::Error;

#[derive(Clone)]
#[pyclass(name = "TosError", module = "tosnativeclient")]
pub struct TosError {
    #[pyo3(get)]
    message: String,
    #[pyo3(get)]
    status_code: Option<isize>,
    #[pyo3(get)]
    ec: String,
    #[pyo3(get)]
    request_id: String,
}

impl TosError {
    pub(crate) fn message(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
            status_code: None,
            ec: "".to_string(),
            request_id: "".to_string(),
        }
    }
}

#[pymethods]
impl TosError {
    #[new]
    #[pyo3(signature = (message, status_code=None, ec=String::from(""), request_id=String::from("")))]
    pub fn new(
        message: String,
        status_code: Option<isize>,
        ec: String,
        request_id: String,
    ) -> Self {
        Self {
            message,
            status_code,
            ec,
            request_id,
        }
    }

    pub fn __getnewargs__(slf: PyRef<'_, Self>) -> PyResult<Bound<'_, PyTuple>> {
        let py = slf.py();
        let state = [
            slf.message.clone().into_pyobject(py)?.into_any(),
            slf.status_code.clone().into_pyobject(py)?.into_any(),
            slf.ec.clone().into_pyobject(py)?.into_any(),
            slf.request_id.clone().into_pyobject(py)?.into_any(),
        ];
        PyTuple::new(py, state)
    }
}

create_exception!(tosnativeclient, TosException, PyException);

pub(crate) fn map_error_from_string(message: impl Into<String>) -> PyErr {
    PyErr::new::<TosException, _>(TosError::new(
        message.into(),
        None,
        "".to_string(),
        "".to_string(),
    ))
}

pub(crate) fn map_error(err: impl Error) -> PyErr {
    PyErr::new::<TosException, _>(TosError::message(err.to_string()))
}

pub(crate) fn map_string_to_error(err: impl AsRef<str>) -> PyErr {
    PyErr::new::<TosException, _>(TosError::message(err.as_ref().to_string()))
}

pub(crate) fn map_tos_error(err: ve_tos_rust_sdk::error::TosError) -> PyErr {
    match err {
        ve_tos_rust_sdk::error::TosError::TosClientError { message, .. } => {
            PyErr::new::<TosException, _>(TosError::message(message))
        }
        ve_tos_rust_sdk::error::TosError::TosServerError {
            message,
            status_code,
            ec,
            request_id,
            ..
        } => {
            PyErr::new::<TosException, _>(TosError::new(message, Some(status_code), ec, request_id))
        }
    }
}
