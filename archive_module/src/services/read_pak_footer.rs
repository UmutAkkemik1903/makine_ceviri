use crate::models::pak_footer::PakAyakizi;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

// Unreal PAK dosyasinin ayakizindeki sihirli sayi (little-endian)
const PAK_SIHIRI: u32 = 0x5A6F12E1;

pub fn pak_ayakizi_oku(dosya_yolu: &Path) -> Option<PakAyakizi> {
    let mut dosya = File::open(dosya_yolu).ok()?;

    // En yeniden eskiye dogru ayakizi boyutlarini dene:
    // v8+: 61 bayt (GUID 16 + sifreli bayrak 1 + sihir 4 + surum 4 + ofset 8 + boyut 8 + hash 20)
    // v7:  45 bayt (sifreli bayrak 1 + sihir 4 + surum 4 + ofset 8 + boyut 8 + hash 20)
    // v1-6: 44 bayt (sihir 4 + surum 4 + ofset 8 + boyut 8 + hash 20)
    for &ayakizi_boyutu in &[61i64, 45i64, 44i64] {
        if dosya.seek(SeekFrom::End(-ayakizi_boyutu)).is_err() {
            continue;
        }
        let mut tampon = vec![0u8; ayakizi_boyutu as usize];
        if dosya.read_exact(&mut tampon).is_err() {
            continue;
        }

        // Sihirin hangi adreste oldugunu ve sifreli bayragini belirle
        let (sihir_ofseti, sifreli_mi) = match ayakizi_boyutu {
            61 => (17usize, tampon[16] != 0),
            45 => (1usize, tampon[0] != 0),
            _ => (0usize, false),
        };

        let sihir = u32::from_le_bytes(
            tampon[sihir_ofseti..sihir_ofseti + 4].try_into().ok()?,
        );
        if sihir != PAK_SIHIRI {
            continue;
        }

        let surum = u32::from_le_bytes(
            tampon[sihir_ofseti + 4..sihir_ofseti + 8].try_into().ok()?,
        );
        let indeks_ofseti = u64::from_le_bytes(
            tampon[sihir_ofseti + 8..sihir_ofseti + 16].try_into().ok()?,
        );
        let indeks_boyutu = u64::from_le_bytes(
            tampon[sihir_ofseti + 16..sihir_ofseti + 24].try_into().ok()?,
        );

        return Some(PakAyakizi {
            surum,
            indeks_ofseti,
            indeks_boyutu,
            sifreli_indeks: sifreli_mi,
        });
    }

    None
}
