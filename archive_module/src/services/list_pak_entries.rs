use crate::models::archive_entry::ArsivGirdisi;
use crate::services::decrypt_pak_index::pak_indeksini_coz;
use crate::services::filter_locres_entries::locres_girdileri_filtrele;
use crate::services::parse_pak_index::pak_indeksini_ayristir;
use crate::services::read_pak_footer::pak_ayakizi_oku;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

pub fn pak_girdilerini_listele(dosya_yolu: &Path, aes_anahtari: Option<&str>) -> Vec<ArsivGirdisi> {
    // Ayakizinden indeks konumunu bul; bulunamazsa dosya gecerli bir PAK degil
    let Some(ayakizi) = pak_ayakizi_oku(dosya_yolu) else {
        eprintln!("[DEBUG] Gecerli PAK ayakizi bulunamadi.");
        return Vec::new();
    };
    eprintln!(
        "[INFO] PAK surumu: {}, indeks ofseti: {}, boyut: {} bayt",
        ayakizi.surum, ayakizi.indeks_ofseti, ayakizi.indeks_boyutu
    );

    // Ham indeks verisini diskten oku
    let Ok(mut dosya) = File::open(dosya_yolu) else {
        return Vec::new();
    };
    if dosya.seek(SeekFrom::Start(ayakizi.indeks_ofseti)).is_err() {
        return Vec::new();
    }
    let mut indeks_verisi = vec![0u8; ayakizi.indeks_boyutu as usize];
    if dosya.read_exact(&mut indeks_verisi).is_err() {
        eprintln!("[ERROR] Indeks verisi okunamadi.");
        return Vec::new();
    }

    // Sifreli ise AES-256-ECB ile coz
    let cozulmus = if ayakizi.sifreli_indeks {
        let Some(anahtar) = aes_anahtari else {
            eprintln!("[WARNING] Sifreli indeks: AES anahtari saglanmadi.");
            return Vec::new();
        };
        let Some(veri) = pak_indeksini_coz(&indeks_verisi, anahtar) else {
            eprintln!("[ERROR] AES cozme basarisiz.");
            return Vec::new();
        };
        veri
    } else {
        indeks_verisi
    };

    // Indeksi ayristir ve sadece ceviri adaylarini (.locres / .uasset) dondur
    let tum_girdiler = pak_indeksini_ayristir(&cozulmus);
    locres_girdileri_filtrele(tum_girdiler)
}
