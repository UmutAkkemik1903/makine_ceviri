#[derive(Debug, Clone)]
pub struct PakAyakizi {
    pub surum: u32,
    pub indeks_ofseti: u64,
    pub indeks_boyutu: u64,
    pub sifreli_indeks: bool,
}
