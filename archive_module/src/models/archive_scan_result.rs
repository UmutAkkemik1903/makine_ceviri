use super::archive_entry::ArsivGirdisi;
use super::archive_kind::ArsivTuru;
use std::path::PathBuf;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ArsivTaramaSonucu {
    pub dosya_yolu: PathBuf,
    pub arsiv_turu: ArsivTuru,
    pub pak_imzasi_var: bool,
    pub sifreli_mi: bool,
    pub girdiler: Vec<ArsivGirdisi>,
}
