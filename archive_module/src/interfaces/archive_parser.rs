use crate::models::archive_scan_result::ArsivTaramaSonucu;
use std::path::Path;

pub trait ArsivAyrisitirici {
    fn arsiv_listele(&self, dosya_yolu: &Path, aes_anahtari: Option<&str>) -> ArsivTaramaSonucu;
}
