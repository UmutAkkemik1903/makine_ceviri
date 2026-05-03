use std::fs::File;
use std::io::Read;
use std::path::Path;

const PAK_IMZASI: [u8; 6] = [0x5B, 0x44, 0x41, 0x54, 0x41, 0x5D];

pub fn pak_imzasi_dogrula(dosya_yolu: &Path) -> bool {
    let Ok(mut dosya) = File::open(dosya_yolu) else {
        return false;
    };

    let mut tampon = [0_u8; 6];

    if dosya.read_exact(&mut tampon).is_err() {
        return false;
    }

    tampon == PAK_IMZASI
}
