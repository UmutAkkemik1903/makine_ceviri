use aes::{
    cipher::{generic_array::GenericArray, BlockDecrypt, KeyInit},
    Aes256,
};

// Kullanici tarafindan saglanmis hex AES-256 anahtariyla indeksi coz (ECB modu)
pub fn pak_indeksini_coz(sifreli_veri: &[u8], hex_anahtar: &str) -> Option<Vec<u8>> {
    // 64 hex karakter = 32 bayt = AES-256 anahtari
    if hex_anahtar.len() != 64 {
        eprintln!("[ERROR] AES anahtari 64 hex karakter olmali.");
        return None;
    }

    let mut anahtar_baytlari = [0u8; 32];
    for (i, cift) in hex_anahtar.as_bytes().chunks(2).enumerate() {
        let cifter = std::str::from_utf8(cift).ok()?;
        anahtar_baytlari[i] = u8::from_str_radix(cifter, 16).ok()?;
    }

    // AES-ECB geregi: veri 16 baytlik bloklara tam bolunmeli
    if sifreli_veri.len() % 16 != 0 {
        eprintln!("[ERROR] Sifreli veri boyutu 16 bayt kati degil.");
        return None;
    }

    let cipher = Aes256::new(GenericArray::from_slice(&anahtar_baytlari));
    let mut cozulmus = sifreli_veri.to_vec();
    for blok in cozulmus.chunks_mut(16) {
        cipher.decrypt_block(GenericArray::from_mut_slice(blok));
    }

    Some(cozulmus)
}
