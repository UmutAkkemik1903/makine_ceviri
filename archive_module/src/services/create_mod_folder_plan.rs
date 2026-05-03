use std::path::Path;
use std::path::PathBuf;

#[allow(dead_code)]
pub fn mod_klasoru_yolu_olustur(oyun_icerik_yolu: &Path) -> PathBuf {
    oyun_icerik_yolu.join("~mods")
}
