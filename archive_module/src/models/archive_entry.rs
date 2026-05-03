use std::path::PathBuf;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ArsivGirdisi {
    pub ic_yol: PathBuf,
    pub bayt_boyutu: u64,
    pub baslangic_ofseti: u64,
    pub sikistirma: Option<String>,
}
