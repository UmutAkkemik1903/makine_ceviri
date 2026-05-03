use crate::models::archive_entry::ArsivGirdisi;

// Bu uzantilar ceviri boru hattina iletilecek dosyalari temsil eder
const HEDEF_UZANTILAR: &[&str] = &["locres", "uasset"];

pub fn locres_girdileri_filtrele(girdiler: Vec<ArsivGirdisi>) -> Vec<ArsivGirdisi> {
    // PathBuf::extension() noktasiz uzantiyi dondurur; ".locres" degil "locres"
    girdiler
        .into_iter()
        .filter(|girdi| {
            girdi
                .ic_yol
                .extension()
                .and_then(|u| u.to_str())
                .map(|uzanti| HEDEF_UZANTILAR.contains(&uzanti))
                .unwrap_or(false)
        })
        .collect()
}
