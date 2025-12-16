use pyo3::{pyclass, pyfunction, PyResult, Python};
use tracing_appender::non_blocking::WorkerGuard;

#[pyfunction]
#[pyo3(signature = (seconds, file_path, image_width=1200))]
pub fn async_write_profile(
    py: Python<'_>,
    seconds: i64,
    file_path: String,
    image_width: usize,
) -> PyResult<()> {
    tosnativeclient_core::common::async_write_profile(seconds, file_path.as_str(), image_width);
    Ok(())
}

#[pyclass(name = "TosLogGuard", module = "tosnativeclient")]
pub struct TosLogGuard {
    _guard: WorkerGuard,
}

#[pyfunction]
#[pyo3(signature = (directives, directory, file_name_prefix))]
pub fn init_tracing_log(
    directives: String,
    directory: String,
    file_name_prefix: String,
) -> PyResult<Option<TosLogGuard>> {
    if directory == "" {
        return Ok(None);
    }
    let guard: WorkerGuard = ve_tos_rust_sdk::common::init_tracing_log(
        directives.clone(),
        directory.clone(),
        file_name_prefix.clone(),
    );
    Ok(Some(TosLogGuard { _guard: guard }))
}
