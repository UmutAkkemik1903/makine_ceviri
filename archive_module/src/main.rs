mod controllers;
mod interfaces;
mod models;
mod services;

use controllers::archive_controller::arsiv_tara;
use std::env;
use std::path::PathBuf;
use std::process;

fn main() {
    let argumanlar: Vec<String> = env::args().collect();

    if argumanlar.len() < 2 {
        eprintln!("[ERROR] Kullanim: archive_module <pak_dosyasi> [aes_anahtari]");
        process::exit(1);
    }

    let dosya_yolu = PathBuf::from(&argumanlar[1]);
    let aes_anahtari = argumanlar.get(2).map(String::as_str);
    let sonuc = arsiv_tara(&dosya_yolu, aes_anahtari);

    println!("[INFO] Dosya: {}", sonuc.dosya_yolu.display());
    println!("[INFO] Tur: {:?}", sonuc.arsiv_turu);
    println!("[INFO] Unreal imzasi: {}", sonuc.pak_imzasi_var);
    println!("[INFO] Sifreli: {}", sonuc.sifreli_mi);
    println!("[INFO] Ceviri adayi girdi sayisi: {}", sonuc.girdiler.len());
    for girdi in &sonuc.girdiler {
        println!(
            "  [PROCESS] {}  ({} bayt, ofset: {})",
            girdi.ic_yol.display(),
            girdi.bayt_boyutu,
            girdi.baslangic_ofseti
        );
    }
}
