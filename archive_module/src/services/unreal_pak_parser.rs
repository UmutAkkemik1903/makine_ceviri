use crate::interfaces::archive_parser::ArsivAyrisitirici;
use crate::models::archive_kind::ArsivTuru;
use crate::models::archive_scan_result::ArsivTaramaSonucu;
use crate::services::detect_pak_signature::pak_imzasi_dogrula;
use crate::services::list_pak_entries::pak_girdilerini_listele;
use crate::services::read_pak_footer::pak_ayakizi_oku;
use std::path::Path;

pub struct UnrealPakParser;

impl ArsivAyrisitirici for UnrealPakParser {
    fn arsiv_listele(&self, dosya_yolu: &Path, aes_anahtari: Option<&str>) -> ArsivTaramaSonucu {
        let pak_imzasi_var = pak_imzasi_dogrula(dosya_yolu);
        let arsiv_turu = if pak_imzasi_var {
            ArsivTuru::UnrealPak
        } else {
            ArsivTuru::Bilinmeyen
        };

        // Sifreli durumu tahmin degil; ayakizinin gercek bayragina gore belirlenir
        let sifreli_mi = pak_imzasi_var
            .then(|| pak_ayakizi_oku(dosya_yolu))
            .flatten()
            .map(|a| a.sifreli_indeks)
            .unwrap_or(false);

        let girdiler = if pak_imzasi_var {
            pak_girdilerini_listele(dosya_yolu, aes_anahtari)
        } else {
            Vec::new()
        };

        ArsivTaramaSonucu {
            dosya_yolu: dosya_yolu.to_path_buf(),
            arsiv_turu,
            pak_imzasi_var,
            sifreli_mi,
            girdiler,
        }
    }
}
