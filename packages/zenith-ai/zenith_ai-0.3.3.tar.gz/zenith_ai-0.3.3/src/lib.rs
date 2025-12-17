//! Zenith AI - PyO3 Python Bindings
//!
//! This crate provides native Python bindings for the Zenith AI
//! high-performance data loading engine using PyO3.
//!
//! # Features
//! - Zero-copy data transfer via Apache Arrow
//! - High-performance ring buffer for data streaming
//! - Native Parquet reading with GIL release
//! - WASM plugin execution for preprocessing

use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyValueError, PyIOError, PyStopIteration};
use std::sync::{Arc, Mutex};
use std::path::PathBuf;
use std::collections::VecDeque;
use std::fs::File;

use arrow::array::{ArrayRef, RecordBatch};
use arrow::pyarrow::ToPyArrow;
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use parquet::file::reader::FileReader;

mod engine;
mod buffer;
mod plugin;

pub use engine::PyEngine;
pub use buffer::RingBuffer;
pub use plugin::PluginManager;

/// Zenith AI Python Module
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register classes
    m.add_class::<PyEngine>()?;
    m.add_class::<PyDataLoader>()?;
    m.add_class::<PyFastLoader>()?;
    m.add_class::<PyPluginInfo>()?;
    
    // Register functions
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(is_available, m)?)?;
    m.add_function(wrap_pyfunction!(fast_read_parquet, m)?)?;
    
    // Module metadata
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__author__", "Zenith Contributors")?;
    
    Ok(())
}

/// Get the Zenith native library version
#[pyfunction]
fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

/// Check if native acceleration is available
#[pyfunction]
fn is_available() -> bool {
    true
}

/// Fast native Parquet reader - reads all batches and returns as PyArrow
#[pyfunction]
fn fast_read_parquet(py: Python<'_>, path: &str, batch_size: usize) -> PyResult<PyObject> {
    // Release GIL while reading
    let batches: Result<Vec<RecordBatch>, _> = py.allow_threads(|| {
        let file = File::open(path).map_err(|e| e.to_string())?;
        let builder = ParquetRecordBatchReaderBuilder::try_new(file)
            .map_err(|e| e.to_string())?
            .with_batch_size(batch_size);
        
        let reader = builder.build().map_err(|e| e.to_string())?;
        
        reader.collect::<Result<Vec<_>, _>>()
            .map_err(|e| e.to_string())
    });
    
    let batches = batches.map_err(|e| PyRuntimeError::new_err(e))?;
    
    // Convert to PyArrow
    let pyarrow = py.import_bound("pyarrow")?;
    let py_batches: Vec<PyObject> = batches
        .into_iter()
        .map(|b| b.to_pyarrow(py))
        .collect::<Result<Vec<_>, _>>()?;
    
    Ok(pyarrow
        .call_method1("concat_batches", (py_batches.first().map(|b| {
            // Get schema from first batch
            b.getattr(py, "schema").ok()
        }), py_batches))?
        .into())
}

/// Plugin information exposed to Python
#[pyclass]
#[derive(Clone)]
pub struct PyPluginInfo {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub version: String,
    #[pyo3(get)]
    pub path: String,
}

#[pymethods]
impl PyPluginInfo {
    fn __repr__(&self) -> String {
        format!("<PluginInfo(name='{}', version='{}')>", self.name, self.version)
    }
}

/// High-performance DataLoader for ML training (legacy)
#[pyclass]
pub struct PyDataLoader {
    source: String,
    batch_size: usize,
    shuffle: bool,
    num_workers: usize,
    engine: Arc<Mutex<engine::EngineCore>>,
}

#[pymethods]
impl PyDataLoader {
    #[new]
    #[pyo3(signature = (source, batch_size=32, shuffle=true, num_workers=4))]
    fn new(
        source: String,
        batch_size: usize,
        shuffle: bool,
        num_workers: usize,
    ) -> PyResult<Self> {
        let engine = engine::EngineCore::new(1024)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create engine: {}", e)))?;
        
        Ok(Self {
            source,
            batch_size,
            shuffle,
            num_workers,
            engine: Arc::new(Mutex::new(engine)),
        })
    }
    
    #[getter]
    fn source(&self) -> &str {
        &self.source
    }
    
    #[getter]
    fn batch_size(&self) -> usize {
        self.batch_size
    }
    
    #[getter]
    fn shuffle(&self) -> bool {
        self.shuffle
    }
    
    #[getter]
    fn num_workers(&self) -> usize {
        self.num_workers
    }
    
    fn __repr__(&self) -> String {
        format!(
            "<DataLoader(source='{}', batch_size={}, shuffle={}, num_workers={})>",
            self.source, self.batch_size, self.shuffle, self.num_workers
        )
    }
    
    fn __len__(&self) -> usize {
        0
    }
}

/// Fast Native Loader - iterates over Parquet with GIL release
#[pyclass]
pub struct PyFastLoader {
    path: String,
    batch_size: usize,
    batches: Vec<RecordBatch>,
    current_idx: usize,
    shuffle: bool,
    indices: Vec<usize>,
}

#[pymethods]
impl PyFastLoader {
    #[new]
    #[pyo3(signature = (path, batch_size=256, shuffle=true))]
    fn new(py: Python<'_>, path: String, batch_size: usize, shuffle: bool) -> PyResult<Self> {
        // Load all batches during construction (with GIL release)
        let batches: Result<Vec<RecordBatch>, String> = py.allow_threads(|| {
            let file = File::open(&path).map_err(|e| e.to_string())?;
            let builder = ParquetRecordBatchReaderBuilder::try_new(file)
                .map_err(|e| e.to_string())?
                .with_batch_size(batch_size);
            
            let reader = builder.build().map_err(|e| e.to_string())?;
            reader.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
        });
        
        let batches = batches.map_err(|e| PyRuntimeError::new_err(e))?;
        let num_batches = batches.len();
        
        let mut indices: Vec<usize> = (0..num_batches).collect();
        if shuffle {
            use std::collections::hash_map::RandomState;
            use std::hash::{BuildHasher, Hasher};
            // Simple shuffle
            let state = RandomState::new();
            for i in (1..num_batches).rev() {
                let mut hasher = state.build_hasher();
                hasher.write_usize(i);
                let j = hasher.finish() as usize % (i + 1);
                indices.swap(i, j);
            }
        }
        
        Ok(Self {
            path,
            batch_size,
            batches,
            current_idx: 0,
            shuffle,
            indices,
        })
    }
    
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }
    
    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<PyObject>> {
        if self.current_idx >= self.batches.len() {
            return Ok(None);
        }
        
        let batch_idx = self.indices[self.current_idx];
        let batch = &self.batches[batch_idx];
        self.current_idx += 1;
        
        // Convert to PyArrow RecordBatch
        let py_batch = batch.to_pyarrow(py)?;
        Ok(Some(py_batch))
    }
    
    fn __len__(&self) -> usize {
        self.batches.len()
    }
    
    fn reset(&mut self) {
        self.current_idx = 0;
    }
    
    fn __repr__(&self) -> String {
        format!(
            "<FastLoader(path='{}', batches={}, batch_size={})>",
            self.path, self.batches.len(), self.batch_size
        )
    }
}
