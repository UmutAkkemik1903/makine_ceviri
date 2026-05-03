use crate::interfaces::archive_parser::ArsivAyrisitirici;
use crate::models::archive_scan_result::ArsivTaramaSonucu;
use crate::services::unreal_pak_parser::UnrealPakParser;
use std::path::Path;

pub fn arsiv_tara(dosya_yolu: &Path, aes_anahtari: Option<&str>) -> ArsivTaramaSonucu {
    let ayrisitirici = UnrealPakParser;

    ayrisitirici.arsiv_listele(dosya_yolu, aes_anahtari)
}
