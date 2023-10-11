use std::sync::Arc;

use mountpoint_s3_client::types::ListObjectsResult;
use pyo3::{pyclass, pymethods, PyRef, PyRefMut, PyResult, Python};

use crate::mountpoint_clients::mountpoint_s3_client_wrapper::MountpointS3ClientWrapper;
use crate::python_structs::py_list_object_result::PyListObjectResult;
use crate::python_structs::py_object_info::PyObjectInfo;

#[pyclass(name = "ListObjectStream", module = "_s3dataset")]
pub struct ListObjectStream {
    client: Arc<dyn MountpointS3ClientWrapper + Send + Sync + 'static>,
    continuation_token: Option<String>,
    complete: bool,
    #[pyo3(get)]
    bucket: String,
    #[pyo3(get)]
    prefix: String,
    #[pyo3(get)]
    delimiter: String,
    #[pyo3(get)]
    max_keys: usize,
}

impl ListObjectStream {
    pub(crate) fn new(
        client: Arc<dyn MountpointS3ClientWrapper + Send + Sync + 'static>,
        bucket: String,
        prefix: String,
        delimiter: String,
        max_keys: usize,
    ) -> Self {
        Self {
            client,
            bucket,
            prefix,
            delimiter,
            max_keys,
            continuation_token: None,
            complete: false,
        }
    }

    fn make_request(&self, py: Python) -> PyResult<ListObjectsResult> {
        py.allow_threads(|| {
            let client = &self.client;
            client.list_objects(
                &self.bucket,
                self.continuation_token.as_deref(),
                &self.delimiter,
                self.max_keys,
                &self.prefix,
            )
        })
    }
}

#[pymethods]
impl ListObjectStream {
    pub fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub fn __next__(mut slf: PyRefMut<'_, Self>) -> PyResult<Option<PyListObjectResult>> {
        if slf.complete {
            return Ok(None);
        }
        let results = slf.make_request(slf.py())?;

        slf.continuation_token = results.next_continuation_token;
        if slf.continuation_token.is_none() {
            slf.complete = true;
        }

        let objects = results
            .objects
            .into_iter()
            .map(|obj| PyObjectInfo::new(obj))
            .collect();

        Ok(Some(PyListObjectResult::new(
            objects,
            results.common_prefixes,
        )))
    }
}

#[cfg(test)]
mod tests {
    use pyo3::types::IntoPyDict;
    use pyo3::{py_run, PyResult, Python};
    use tracing_subscriber::layer::SubscriberExt;
    use tracing_subscriber::util::SubscriberInitExt;

    use crate::mountpoint_clients::mountpoint_s3_client_mock::MountpointS3ClientMock;
    use crate::mountpoint_s3_client::MountpointS3Client;

    #[test]
    fn test_list_objects() -> PyResult<()> {
        let layer = tracing_subscriber::fmt::layer().with_ansi(true);
        let registry = tracing_subscriber::registry().with(layer);
        let _ = registry.try_init();

        pyo3::prepare_freethreaded_python();

        Python::with_gil(|py| {
            let locals = [
                ("MountpointS3Client", py.get_type::<MountpointS3Client>()),
                (
                    "MountpointS3ClientMock",
                    py.get_type::<MountpointS3ClientMock>(),
                ),
            ];

            py_run!(
                py,
                *locals.into_py_dict(py),
                r#"
                expected_keys = {"test"}
                
                mock_client = MountpointS3ClientMock("us-east-1", "mock-bucket")
                client = MountpointS3Client.with_client(mock_client)
                for key in expected_keys:
                    mock_client.add_object(key, b"")
                
                stream = client.list_objects("mock-bucket")
                
                object_infos = [object_info for page in stream for object_info in page.object_info]
                keys = {object_info.key for object_info in object_infos}
                assert keys == expected_keys
                "#
            );
        });

        Ok(())
    }
}
