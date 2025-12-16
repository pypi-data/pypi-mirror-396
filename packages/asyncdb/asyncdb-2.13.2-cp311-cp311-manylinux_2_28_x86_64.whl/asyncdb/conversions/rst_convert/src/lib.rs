use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyList, PyTuple};
use rayon::prelude::*;
use serde::Serialize;
use std::collections::HashMap;
use std::sync::Arc;

/// Struct to hold record data dynamically
#[derive(Serialize, Clone)]
struct RecordData {
    fields: HashMap<String, serde_json::Value>,
}

/// Convert `asyncpg.Record` to Python dicts using Rayon for parallel data extraction
#[pyfunction]
fn todict(py: Python, records: &PyAny) -> PyResult<Vec<Py<PyDict>>> {
    // Ensure that records is iterable and collect into a Vec<PyObject>
    let records_vec: Vec<PyObject> = records
        .iter()?
        .map(|record_result| record_result.map(|record| record.into_py(py)))
        .collect::<PyResult<Vec<_>>>()?;

    eprintln!("Collected {} records", records_vec.len());

    // Wrap the records_vec in an Arc to share across threads safely
    let records_ref = Arc::new(records_vec);

    // Parallel extraction of data into Rust-native structs
    let extracted_data: Vec<RecordData> = (0..records_ref.len())
        .into_par_iter()
        .map(|index| -> PyResult<RecordData> {
            // Each thread needs to acquire the GIL to interact with Python objects
            Python::with_gil(|py| {
                eprintln!("Processing record {}", index);
                let record = records_ref[index].as_ref(py);

                // Initialize a HashMap to store field data
                let mut fields = HashMap::new();

                // Retrieve (key, value) pairs using the 'items' method
                let items_obj = match record.call_method0("items") {
                    Ok(items) => items.downcast::<PyList>()?.to_object(py),
                    Err(_) => pyo3::types::PyList::empty(py).to_object(py),
                };

                // Downcast back to PyList for iteration
                let items = items_obj.downcast::<PyList>(py)?;
                eprintln!("Record {} has {} items", index, items.len());

                // Iterate over each item to extract key-value pairs
                for item_result in items.iter::<&PyAny>() {
                    let item: &PyAny = item_result?;
                    // Each item should be a tuple of (key, value)
                    let tuple = match item.downcast::<PyTuple>() {
                        Ok(t) => t,
                        Err(_) => {
                            eprintln!("Failed to downcast item to PyTuple in record {}", index);
                            continue;
                        },
                    };
                    if tuple.len() != 2 {
                        eprintln!("Tuple length mismatch in record {}", index);
                        continue; // Skip if not a (key, value) pair
                    }
                    let key: String = match tuple.get_item(0).extract::<String>() {
                        Ok(k) => k,
                        Err(_) => {
                            eprintln!("Failed to extract key in record {}", index);
                            continue;
                        },
                    };
                    let value_py = tuple.get_item(1);
                    let value_json = match py_to_serde_value(py, value_py) {
                        Ok(v) => v,
                        Err(e) => {
                            eprintln!("Failed to convert value for key '{}' in record {}: {}", key, index, e);
                            serde_json::Value::Null
                        },
                    };
                    fields.insert(key, value_json);
                }

                Ok(RecordData { fields })
            })
        })
        .filter_map(Result::ok)
        .collect();

    eprintln!("Extracted data for {} records", extracted_data.len());

    // Create PyDicts serially from the extracted data
    let mut dicts = Vec::with_capacity(extracted_data.len());
    for (i, data) in extracted_data.into_iter().enumerate() {
        eprintln!("Creating PyDict for record {}", i);
        let dict = PyDict::new(py);
        for (key, value) in data.fields {
            // Convert serde_json::Value back to PyObject
            let py_value = serde_value_to_py_value(py, &value)?;
            dict.set_item(key, py_value)?;
        }
        dicts.push(dict.into());
    }

    Ok(dicts)
}

// Helper function to convert PyAny to serde_json::Value
fn py_to_serde_value(_py: Python, value_py: &PyAny) -> PyResult<serde_json::Value> {
    if value_py.is_none() {
        Ok(serde_json::Value::Null)
    } else if let Ok(v) = value_py.extract::<bool>() {
        Ok(serde_json::Value::Bool(v))
    } else if let Ok(v) = value_py.extract::<i64>() {
        Ok(serde_json::Value::Number(serde_json::Number::from(v)))
    } else if let Ok(v) = value_py.extract::<f64>() {
        Ok(serde_json::Value::Number(serde_json::Number::from_f64(v)
            .unwrap_or(serde_json::Number::from(0))))
    } else if let Ok(v) = value_py.extract::<String>() {
        Ok(serde_json::Value::String(v))
    } else {
        // Convert other types to string representation
        let str_value = value_py.str()?.to_string();
        Ok(serde_json::Value::String(str_value))
    }
}

// Helper function to convert serde_json::Value back to PyObject
fn serde_value_to_py_value(py: Python, value: &serde_json::Value) -> PyResult<PyObject> {
    match value {
        serde_json::Value::Null => Ok(py.None()),
        serde_json::Value::Bool(b) => Ok(b.to_object(py)),
        serde_json::Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.to_object(py))
            } else if let Some(f) = n.as_f64() {
                Ok(f.to_object(py))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Number could not be converted to i64 or f64",
                ))
            }
        }
        serde_json::Value::String(s) => Ok(s.to_object(py)),
        _ => Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "Unsupported serde_json::Value type",
        )),
    }
}

/// Python module definition
#[pymodule]
fn rst_convert(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(todict, m)?)?;
    Ok(())
}
