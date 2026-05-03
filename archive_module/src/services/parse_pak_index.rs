use crate::models::archive_entry::ArsivGirdisi;
use std::path::PathBuf;

pub fn pak_indeksini_ayristir(indeks_verisi: &[u8]) -> Vec<ArsivGirdisi> {
    let mut imlec = 0usize;
    let mut girdiler = Vec::new();

    // Baglanma noktasini (mount point) oku ve atla; icerik icin kullanilmaz
    if dize_atla(indeks_verisi, &mut imlec).is_none() {
        return girdiler;
    }

    let Some(dosya_sayisi) = u32_oku(indeks_verisi, &mut imlec) else {
        return girdiler;
    };

    for _ in 0..dosya_sayisi {
        let Some(dosya_adi) = dize_oku(indeks_verisi, &mut imlec) else {
            break;
        };
        let Some(ofset) = u64_oku(indeks_verisi, &mut imlec) else { break };
        let Some(boyut) = u64_oku(indeks_verisi, &mut imlec) else { break };
        // Sikistirilmamis boyut: kullanilmaz, yine de okunmali
        if u64_oku(indeks_verisi, &mut imlec).is_none() { break }
        let Some(sikistirma_yontemi) = u32_oku(indeks_verisi, &mut imlec) else { break };
        // SHA1 karma (20 bayt) atla
        if !atla(indeks_verisi, &mut imlec, 20) { break }

        // Varsa sikistirma blok tablosunu atla
        if sikistirma_yontemi != 0 {
            let Some(blok_sayisi) = u32_oku(indeks_verisi, &mut imlec) else { break };
            // Her blok: 8 baslangic + 8 bitis ofset = 16 bayt
            if !atla(indeks_verisi, &mut imlec, blok_sayisi as usize * 16) { break }
        }

        // bEncrypted (1 bayt) + CompressionBlockSize (4 bayt) her zaman var
        if !atla(indeks_verisi, &mut imlec, 5) { break }

        let sikistirma = if sikistirma_yontemi == 0 {
            None
        } else {
            Some(format!("method_{}", sikistirma_yontemi))
        };

        girdiler.push(ArsivGirdisi {
            ic_yol: PathBuf::from(&dosya_adi),
            bayt_boyutu: boyut,
            baslangic_ofseti: ofset,
            sikistirma,
        });
    }

    girdiler
}

fn u32_oku(veri: &[u8], imlec: &mut usize) -> Option<u32> {
    if *imlec + 4 > veri.len() { return None; }
    let deger = u32::from_le_bytes(veri[*imlec..*imlec + 4].try_into().ok()?);
    *imlec += 4;
    Some(deger)
}

fn u64_oku(veri: &[u8], imlec: &mut usize) -> Option<u64> {
    if *imlec + 8 > veri.len() { return None; }
    let deger = u64::from_le_bytes(veri[*imlec..*imlec + 8].try_into().ok()?);
    *imlec += 8;
    Some(deger)
}

fn atla(veri: &[u8], imlec: &mut usize, bayt_sayisi: usize) -> bool {
    if *imlec + bayt_sayisi > veri.len() { return false; }
    *imlec += bayt_sayisi;
    true
}

// Uzunluk-onekli, null-sonlu Unreal dizesini oku (i32 uzunluk, UTF-8 veya UTF-16)
fn dize_oku(veri: &[u8], imlec: &mut usize) -> Option<String> {
    if *imlec + 4 > veri.len() { return None; }
    let uzunluk_i = i32::from_le_bytes(veri[*imlec..*imlec + 4].try_into().ok()?);
    *imlec += 4;

    if uzunluk_i == 0 { return Some(String::new()); }

    if uzunluk_i < 0 {
        // UTF-16: karakter sayisi * 2 bayt; adresleme icin atla
        let bayt_boyutu = (-uzunluk_i as usize) * 2;
        if !atla(veri, imlec, bayt_boyutu) { return None; }
        return Some(format!("(utf16:{} karakter)", -uzunluk_i));
    }

    let uzunluk = uzunluk_i as usize;
    if *imlec + uzunluk > veri.len() { return None; }
    let baytlar = &veri[*imlec..*imlec + uzunluk];
    *imlec += uzunluk;
    let gecerli = baytlar.strip_suffix(&[0]).unwrap_or(baytlar);
    String::from_utf8(gecerli.to_vec()).ok()
}

// Baglanma noktasi gibi atlanacak dizeler icin okunmadan gecilir
fn dize_atla(veri: &[u8], imlec: &mut usize) -> Option<()> {
    if *imlec + 4 > veri.len() { return None; }
    let uzunluk_i = i32::from_le_bytes(veri[*imlec..*imlec + 4].try_into().ok()?);
    *imlec += 4;
    let bayt_boyutu = if uzunluk_i < 0 {
        (-uzunluk_i as usize) * 2
    } else {
        uzunluk_i as usize
    };
    if !atla(veri, imlec, bayt_boyutu) { return None; }
    Some(())
}
