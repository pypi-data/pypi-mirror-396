use pyo3::prelude::*;
use sha2::{Sha256, Digest};
use hex;

// use std::any::type_name;
// fn type_of<T>(_: T) -> &'static str {
//     type_name::<T>()
// }

#[pyfunction]
fn add(a: u32, b: u32) -> PyResult<u32> {
    Ok(a.wrapping_add(b))
}
#[pyfunction]
fn add_64(a: u32, b: u32) -> PyResult<u64>{
    let c: u64 = (a as u64).wrapping_add(b as u64);
    Ok(c)
}

#[pyfunction]
fn sub(a: u32, b: u32) -> PyResult<u32> {
    Ok(a.wrapping_sub(b))
}

#[pyfunction]
fn sub_64(a: u32, b: u32) -> PyResult<u64> {
    let c: u64 = (a as u64).wrapping_sub(b as u64);
    Ok(c)
}

#[pyfunction]
fn neg(a: u32) -> PyResult<u32> {
    Ok(a.wrapping_neg())
}

#[pyfunction]
fn neg_64(a: u32) -> PyResult<u64> {
    let b: u64 = (a as u64).wrapping_neg();
    Ok(b)
}

#[pyfunction]
fn mult(a: u32, b: u32) -> PyResult<u32> {
    Ok(a.wrapping_mul(b))
}

#[pyfunction]
fn mult_64(a: u32, b: u32) -> PyResult<u64> {
    let c: u64 = (a as u64).wrapping_mul(b as u64);
    Ok(c)
}

#[pyfunction]
fn right_shift(a: u32, b: u32) -> PyResult<u32> {
    Ok(a >> b)
}

#[pyfunction]
fn float2fix(x: f64) -> PyResult<u32> {
    let factor: f64 = 2_f64.powf(12.0);
    let y: f64 = x * factor;
    let z: i32 = y as i32;
    let k: u32 = z as u32;
    Ok(k)
}

#[pyfunction]
fn fix2float(x: u32) -> PyResult<f64> {
    let y: i32 = x as i32;
    let z: f64 = y as f64;
    let factor: f64 = 2_f64.powf(-12.0);
    let k: f64 = factor * z;
    Ok(k)
}

#[pyfunction]
fn pnrg_dcf(seed: Vec<u8>) -> PyResult<Vec<u8>> {
    let lambda = seed.len(); // λ in bytes
    let output_size = 4 * lambda + 1; // Output size in bytes: 4λ + 2

    // Initialize the hash function with the seed
    let mut hasher = Sha256::new();
    hasher.update(&seed);

    // Generate the pseudorandom output deterministically
    let mut output = Vec::new();
    while output.len() < output_size {
        // Hash the current state and append the result
        let hash = hasher.finalize_reset();
        output.extend_from_slice(&hash);
        hasher.update(&hash); // Update hasher with the last hash
    }

    // Trim to the exact output size
    output.truncate(output_size);
    Ok(output)
}

#[pyfunction]
fn pnrg_dpf(seed: Vec<u8>) -> PyResult<Vec<u8>> {
    let lambda = seed.len(); // λ in bytes
    let output_size = 2 * lambda + 2; // Output size in bytes: 2λ + 2

    // Initialize the hash function with the seed
    let mut hasher = Sha256::new();
    hasher.update(&seed);

    // Generate the pseudorandom output deterministically
    let mut output = Vec::new();
    while output.len() < output_size {
        // Hash the current state and append the result
        let hash = hasher.finalize_reset();
        output.extend_from_slice(&hash);
        hasher.update(&hash); // Update hasher with the last hash
    }

    // Trim to the exact output size
    output.truncate(output_size);
    Ok(output)
}

#[pyfunction]
fn convert(input: Vec<u8>) -> PyResult<u32> {
    // input: Vec<u8> each element represent the hex's decimal representation, e.g. ed -> 237
    // println!("Integer: {:?}", (input[0], input[1], input[2], input[3]));
    let group_element = u32::from_be_bytes([input[0], input[1], input[2], input[3]]);
    Ok(group_element)
}

#[pyfunction]
fn u32_to_binary_list(num: u32) -> Vec<bool> {
    let binary_str = format!("{:032b}", num); // 将数字转换为二进制字符串
    binary_str
        .chars() // 遍历字符串中的字符
        .map(|c| c == '1') // '1' 转为 true, '0' 转为 false // .map(|c| c.to_digit(10).unwrap() as u8) // 转换为 u8
        .collect() // 收集到 Vec 中
}

#[pyfunction]
fn split_dcf(output: &str) -> PyResult<(String, String, String, String, String, String)> {
    // Split the output into the desired segments
    let part1 = output[0..32].to_string();
    let part2 = output[32..64].to_string();
    let part3 = output[64..65].to_string();
    let part4 = output[65..97].to_string();
    let part5 = output[97..129].to_string();
    let part6 = output[129..130].to_string();

    Ok((part1, part2, part3, part4, part5, part6))
}

#[pyfunction]
fn split_dpf(output: &str) -> PyResult<(String, String, String, String)> {
    // Split the output into the desired segments
    let part1 = output[0..32].to_string();
    let part2 = output[32..33].to_string();
    let part3 = output[33..65].to_string();
    let part4 = output[65..66].to_string();

    Ok((part1, part2, part3, part4))
}

#[pyfunction]
fn strhex_xor(output0: &str, output1: &str) -> PyResult<String> {
    // println!("Output: {}", type_of(output0));
    let bytes0 = hex::decode(output0).expect("Invalid hex string 0");
    let bytes1 = hex::decode(output1).expect("Invalid hex string 1");

    let xor_result: Vec<u8> = bytes0.iter()
        .zip(bytes1.iter())
        .map(|(b1, b2)| b1 ^ b2)
        .collect();

    Ok(hex::encode(xor_result))
}

#[pyfunction]
fn u32_mod_31(x: u32) -> PyResult<u32> {
    Ok(x % (1 << 31))
}

#[pyfunction]
fn u32_msb(x: u32) -> PyResult<u32> {
    let msb: u32 = if x & (1 << 31) != 0 { 1 } else { 0 };
    Ok(msb)
}

#[pyfunction]
fn truncate_12(x: u32) -> PyResult<u32> {
    Ok(x >> 12)
}

/// A Python module implemented in Rust.
#[pymodule]
fn universe(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(truncate_12, m)?)?;

    m.add_function(wrap_pyfunction!(add, m)?)?;
    m.add_function(wrap_pyfunction!(add_64, m)?)?;

    m.add_function(wrap_pyfunction!(sub, m)?)?;
    m.add_function(wrap_pyfunction!(sub_64, m)?)?;

    m.add_function(wrap_pyfunction!(neg, m)?)?;
    m.add_function(wrap_pyfunction!(neg_64, m)?)?;

    m.add_function(wrap_pyfunction!(mult, m)?)?;
    m.add_function(wrap_pyfunction!(mult_64, m)?)?;

    m.add_function(wrap_pyfunction!(right_shift, m)?)?;
    m.add_function(wrap_pyfunction!(float2fix, m)?)?;
    m.add_function(wrap_pyfunction!(fix2float, m)?)?;
    m.add_function(wrap_pyfunction!(pnrg_dcf, m)?)?;
    m.add_function(wrap_pyfunction!(pnrg_dpf, m)?)?;
    m.add_function(wrap_pyfunction!(convert, m)?)?;
    m.add_function(wrap_pyfunction!(u32_to_binary_list, m)?)?;
    m.add_function(wrap_pyfunction!(split_dcf, m)?)?;
    m.add_function(wrap_pyfunction!(split_dpf, m)?)?;
    m.add_function(wrap_pyfunction!(strhex_xor, m)?)?;
    m.add_function(wrap_pyfunction!(u32_mod_31, m)?)?;
    m.add_function(wrap_pyfunction!(u32_msb, m)?)?;
    Ok(())
}