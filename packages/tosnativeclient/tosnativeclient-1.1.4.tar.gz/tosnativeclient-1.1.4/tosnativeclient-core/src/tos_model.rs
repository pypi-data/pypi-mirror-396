use ve_tos_rust_sdk::object::HeadObjectOutput;

#[derive(Clone)]
pub struct TosObject {
    pub(crate) bucket: String,
    pub(crate) key: String,
    pub(crate) size: isize,
    pub(crate) etag: String,
}

impl TosObject {
    pub fn new(bucket: String, key: String, size: isize, etag: String) -> Self {
        Self {
            bucket,
            key,
            size,
            etag,
        }
    }
    pub(crate) fn inner_new(bucket: &str, key: &str, output: HeadObjectOutput) -> Self {
        Self {
            bucket: bucket.to_string(),
            key: key.to_string(),
            size: output.content_length() as isize,
            etag: output.etag().to_string(),
        }
    }

    pub fn bucket(&self) -> &str {
        &self.bucket
    }

    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn size(&self) -> isize {
        self.size
    }

    pub fn etag(&self) -> &str {
        &self.etag
    }
}
