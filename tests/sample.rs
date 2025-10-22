use pyo3::prelude::*;
use pyo3::types::{ PyBytes, PyByteArray };
use pyo3::exceptions::PyValueError;
use zeroize::Zeroize;

// Rijndaels forward s-box
fn sbox(byte: u8) -> u8 {
    let fo_sbox : [u8; 256] = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76, 
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15, 
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8, 
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73, 
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08, 
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ];

    fo_sbox[byte as usize]
}

// Rijndaels inverse s-box
fn inv_sbox(byte: u8) -> u8 {
    let ba_sbox : [u8; 256] = [
        0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb, 
        0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb, 
        0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e, 
        0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25, 
        0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92, 
        0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84, 
        0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06, 
        0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b, 
        0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73, 
        0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e, 
        0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b, 
        0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4, 
        0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f, 
        0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef, 
        0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61, 
        0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
    ];

    ba_sbox[byte as usize]
}

// Shift rows
fn shift_rows(state: &mut [[u8; 4]; 4]) {
    let mut temp: [u8; 4];

    temp = state[1];
    for i in 0..4 {
        state[1][i] = temp[(i + 1) % 4]; 
    }

    temp = state[2];
    for i in 0..4 {
        state[2][i] = temp[(i + 2) % 4]; 
    }

    temp = state[3];
    for i in 0..4 {
        state[3][i] = temp[(i + 3) % 4]; 
    }
}

// Inverse shift rows
fn inv_shift_rows(state: &mut [[u8; 4]; 4]) {
    todo!();
}

// MixColumns
// Multiplication in Galois Field (2^8)
fn gmul(a: u8, b: u8) -> u8 {
    let mut p: u8 = 0;
    let mut a_temp = a;
    let mut b_temp = b;

    for _ in 0..8 {
        if b_temp & 1 != 0 {
            p ^= a_temp;
        }

        let hi_bit_set = a_temp & 0x80 != 0;
        a_temp <<= 1;

        if hi_bit_set {
            a_temp ^= 0x1B;
        }
        b_temp >>= 1;
    }

    p
}

// Apply mix columns
fn mix_columns(state: &mut [[u8; 4]; 4]) {
    let mut temp: [u8; 4] = [0; 4];

    for c in 0..4{ 
        temp[0] = gmul(2, state[0][c]) ^ gmul(3, state[1][c]) ^ state[2][c] ^ state[3][c];
        temp[1] = state[0][c] ^ gmul(2, state[1][c]) ^ gmul(3, state[2][c]) ^ state[3][c];
        temp[2] = state[0][c] ^ state[1][c] ^ gmul(2, state[2][c]) ^ gmul(3, state[3][c]);
        temp[3] = gmul(3, state[0][c]) ^ state[1][c] ^ state[2][c] ^ gmul(2, state[3][c]);

        for i in 0..4 {
            state[i][c] = temp[i];
        }
    }
}

// Apply inverse mix columns
fn inv_mix_columns(state: &mut [[u8; 4]; 4]) {
    let mut temp: [u8; 4] = [0; 4];

    for c in 0..4 {
        temp[0] = gmul(14, state[0][c]) ^ gmul(11, state[1][c]) ^ gmul(13, state[2][c]) ^ gmul(9, state[3][c]);
        temp[1] = gmul(9, state[0][c]) ^ gmul(14, state[1][c]) ^ gmul(11, state[2][c]) ^ gmul(13, state[3][c]);
        temp[2] = gmul(13, state[0][c]) ^ gmul(9, state[1][c]) ^ gmul(14, state[2][c]) ^ gmul(11, state[3][c]);
        temp[3] = gmul(11, state[0][c]) ^ gmul(13, state[1][c]) ^ gmul(9, state[2][c]) ^ gmul(14, state[3][c]);

        for i in 0..4 {
            state[i][c] = temp[i];
        }
    }
}

// Expand Key
const RCON: [u8; 11] = [
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
];

// Shift bytes left
fn rot_word(word: u32) -> u32 {
    (word << 8 ) | (word >> 24)
}

// Apply s-box
fn sub_word(word: u32) -> u32 {
    ((sbox(((word >> 24) & 0xFF) as u8) as u32) << 24) |
    ((sbox(((word >> 16) & 0xFF) as u8) as u32) << 16) |
    ((sbox(((word >> 8) & 0xFF) as u8) as u32) << 8) |
    (sbox((word & 0xFF) as u8) as u32)
}

fn key_expansion(key: [u8; 32], round_keys: &mut [u32; 60]) {
    // Initial 8 words from key
    for i in 0..8 {
        round_keys[i] = ((key[4 * i] as u32) << 24) | 
            ((key[4 * i + 1] as u32) << 16) |
            ((key[4 * i + 2] as u32) << 8) |
            (key[4 * i + 3] as u32);
    }

    // Fill remaining 52 words
    for i in 8..60 {
        let mut temp: u32 = round_keys[i - 1];

        if i % 8 == 0 {
            temp = sub_word(rot_word(temp)) ^ ((RCON[i / 8] as u32) << 24);
        } else if i % 8 == 4 {
            temp = sub_word(temp);
        }

        round_keys[i] = round_keys[i - 8] ^ temp
    }
}

// XOR each byte of state with a round key
fn add_round_key(state: &mut [[u8; 4]; 4], round_key: [u32; 4]) {
    for c in 0..4 {
        state[0][c] = state[0][c] ^ (((round_key[c] >> 24) as u8) & 0xFF as u8);
        state[1][c] = state[1][c] ^ (((round_key[c] >> 16) as u8) & 0xFF as u8);
        state[2][c] = state[2][c] ^ (((round_key[c] >> 8) as u8) & 0xFF as u8);
        state[3][c] = state[3][c] ^ ((round_key[c] as u8) & 0xFF as u8);
    }
}

// Sub bytes
fn sub_bytes(state: &mut [[u8; 4]; 4]) {
    for i in 0..4 {
        for j in 0..4 {
            state[i][j] = sbox(state[i][j]);
        }
    }
}

// Inverse sub byte
fn inv_sub_bytes(state: &mut [[u8; 4]; 4]) {
    for i in 0..4 {
        for j in 0..4 {
            state[i][j] = inv_sbox(state[i][j]);
        }
    }
}

// AES ecryption (256bit)
fn aes_encrypt(state: &mut [[u8; 4]; 4], round_keys: &[u32; 60]) {
    // Initial round
    add_round_key(state, [round_keys[0], round_keys[1], round_keys[2], round_keys[3]]);
    // Nine rounds of sub_bytes, shift_rows, mix_columns, add_round_key
    for i in 1..14 {
        sub_bytes(state);
        shift_rows(state);
        mix_columns(state);
        add_round_key(
            state, 
            [
                round_keys[i * 4], 
                round_keys[i * 4 + 1], 
                round_keys[i * 4 + 2], 
                round_keys[i * 4 + 3]
            ] 
        );
    }

    // Final round (no mix columns)
    sub_bytes(state);
    shift_rows(state);
    add_round_key(
        state,
        [
            round_keys[56],
            round_keys[57],
            round_keys[58],
            round_keys[59]
        ]
    );
}

// AES decryption (256bit)
fn aes_decrypt(state: &mut [[u8; 4]; 4], round_keys: &[u32; 60]) {
    // Initial round
    add_round_key(state, [round_keys[56], round_keys[57], round_keys[58], round_keys[59]]);
    // Nine rounds of sub_bytes, shift_rows, mix_columns, add_round_key
    for i in (1..14).rev() {
        inv_shift_rows(state);
        inv_sub_bytes(state);
        add_round_key(
            state, 
            [
                round_keys[i * 4], 
                round_keys[i * 4 + 1], 
                round_keys[i * 4 + 2], 
                round_keys[i * 4 + 3]
            ] 
        );
        inv_mix_columns(state);
    }

    // Final round (no mix columns)
    inv_shift_rows(state);
    inv_sub_bytes(state);
    add_round_key(
        state,
        [
            round_keys[0],
            round_keys[1],
            round_keys[2],
            round_keys[3]
        ]
    );
}

fn block_to_state(block: &[u8; 16]) -> [[u8; 4]; 4] {
    let mut state = [[0u8; 4]; 4];
    for i in 0..4 {
        for j in 0..4 {
            state[j][i] =  block[i * 4 + j];
        }
    }
    state
}

fn state_to_block(state: &[[u8; 4]; 4]) -> [u8; 16] {
    let mut block = [0u8; 16];
    for i in 0..4 {
        for j in 0..4 {
            block[i * 4 + j] = state[j][i];
        }
    }
    block
}

// Incremt counter (as a big-endian integer)
fn increment_counter(counter: &mut [u8; 16]) {
    for i in (0..16).rev() {
        counter[i] = counter[i].wrapping_add(1);
        if counter[i] != 1 {
            break;
        }
    }
}

// Helperfunctions
fn print_hex(data: &[u8]) {
    for byte in data {
        print!("{:02x}", byte);
    }
    println!()
}

fn print_state(state: &[[u8; 4]; 4]) {
    todo!("#1 Undescribed by author.");
}

// AES-CTR
fn aes_ctr(data: &[u8], key: &[u8; 32], nonce: &[u8; 8]) -> Vec<u8> {
    let mut round_keys: [u32; 60] = [0; 60];
    key_expansion(*key, &mut round_keys);

    let mut counter_block = [0u8; 16];
    counter_block[0..8].copy_from_slice(nonce);

    let mut result = Vec::with_capacity(data.len());
    let mut offset = 0;

    while offset < data.len() {
        let mut counter_state = block_to_state(&counter_block);
        aes_encrypt(&mut counter_state, &round_keys);
        
        let keystream = state_to_block(&counter_state);

        let block_size = std::cmp::min(16, data.len() - offset);
        for i in 0..block_size {
            result.push(data[offset + i] ^ keystream[i]);
        }
        increment_counter(&mut counter_block);
        offset += 16;
    }

    result
}

#[pyfunction]
fn aes_ctr_py(py: Python, data: &[u8], key: &[u8], nonce: &[u8]) -> PyResult<Py<PyBytes>> {
    if key.len() != 32 {
        return Err(PyValueError::new_err("Key must be 32 bytes (256 bits)"));
    }
    if nonce.len() != 8 {
        return Err(PyValueError::new_err("Nonce must be 8 bytes (64 bits)"));
    }

    let mut key_array = [0u8; 32];
    let mut nonce_array = [0u8; 8];

    key_array.copy_from_slice(key);
    nonce_array.copy_from_slice(nonce);

    let result = aes_ctr(data, &key_array, &nonce_array);

    Ok(PyBytes::new(py, &result).into())
}

#[pyclass]
pub struct AesCtrSecret {
    key: [u8; 32],
    nonce: [u8; 8],
}

#[pymethods]
impl AesCtrSecret {
    #[new]
    fn new(key: &PyByteArray, nonce: &PyByteArray) -> PyResult<Self> {
        let key_slice = unsafe { key.as_bytes_mut() };
        let nonce_slice = unsafe { nonce.as_bytes_mut() };

        if key_slice.len() != 32 {
            return Err(PyValueError::new_err("Key must be 32 bytes (256 bits)"));
        }

        if nonce_slice.len() != 8 {
            return Err(PyValueError::new_err("Nonce must be 8 bytes (64 bits)"));
        }

        let mut key = [0u8; 32];
        let mut nonce = [0u8; 8];

        key.copy_from_slice(key_slice);
        nonce.copy_from_slice(nonce_slice);

        key_slice.fill(0);
        nonce_slice.fill(0);

        Ok(Self { key, nonce })
    }

    pub fn encrypt<'py>(&self, py: Python<'py>, data: &PyByteArray) -> PyResult<&'py PyBytes> {
        todo!("#2 Undescribed by author.");
    }
}

impl Drop for AesCtrSecret {
    fn drop(&mut self) {
        self.key.zeroize();
        self.nonce.zeroize();
    }
}

#[pymodule]
fn aes_ctr_rspy(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(aes_ctr_py, m)?)?;
    m.add_class::<AesCtrSecret>()?;
    Ok(())
}

