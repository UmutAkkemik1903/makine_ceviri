#[derive(Debug, Clone, Default, PartialEq, Eq)]
#[allow(dead_code)]
pub struct PakSecenekleri {
    pub aes_anahtari: Option<String>,
    pub sadece_locres: bool,
}
