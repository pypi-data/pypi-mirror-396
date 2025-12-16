use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use sarhash_core;

// --- Python Bindings ---

/// Hash a password using the specified algorithm
///
/// # Arguments
/// * `password` - The password to hash
/// * `algorithm` - The hashing algorithm to use ("argon2", "bcrypt", or "scrypt")
///
/// # Returns
/// The hashed password as a string
///
/// # Errors
/// Returns PyValueError if the algorithm is unsupported or hashing fails
#[pyfunction]
pub fn hash_password(password: &str) -> PyResult<String> {
    sarhash_core::hash_password(password).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Verify a password against a hash
///
/// # Arguments
/// * `password` - The password to verify
/// * `hash` - The hash to verify against
///
/// # Returns
/// True if the password matches the hash, False otherwise
///
/// # Errors
/// Returns PyValueError if verification fails due to invalid hash format
#[pyfunction]
pub fn verify_password(password: &str, hash: &str) -> PyResult<bool> {
    sarhash_core::verify_password(password, hash).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// A Python module implemented in Rust for fast password hashing
#[pymodule]
fn _sarhash(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hash_password, m)?)?;
    m.add_function(wrap_pyfunction!(verify_password, m)?)?;
    Ok(())
}
