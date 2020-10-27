use pyo3::{ffi, prelude::*, types::PyAny, wrap_pyfunction, AsPyPointer};
use serde::{
    ser::Error as SerdeError,
    ser::{SerializeMap, SerializeSeq},
    Serializer,
};
use smallvec::SmallVec;

mod error;
mod string;
mod types;

pub const RECURSION_LIMIT: u8 = 255;

struct PyObjectWrapper {
    object: *mut ffi::PyObject,
    recursion_depth: u8,
}

impl PyObjectWrapper {
    fn new(object: *mut ffi::PyObject, recursion_depth: u8) -> Self {
        Self {
            object,
            recursion_depth,
        }
    }
}

impl serde::Serialize for PyObjectWrapper {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let object_type = unsafe { ffi::Py_TYPE(self.object) };
        if object_type == unsafe { types::STR_TYPE } {
            let mut str_size: ffi::Py_ssize_t = 0;
            let uni = unsafe { string::read_utf8_from_str(self.object, &mut str_size) };
            let slice = unsafe {
                std::str::from_utf8_unchecked(std::slice::from_raw_parts(uni, str_size as usize))
            };
            serializer.serialize_str(slice)
        } else if object_type == unsafe { types::INT_TYPE } {
            let value = unsafe { ffi::PyLong_AsLongLong(self.object) };
            if value == -1 && !unsafe { ffi::PyErr_Occurred() }.is_null() {
                unsafe { ffi::PyErr_Clear() }
                serializer.serialize_i64(42) //TODO. fix
            } else {
                serializer.serialize_i64(value)
            }
        } else if object_type == unsafe { types::FLOAT_TYPE } {
            let value = unsafe { ffi::PyFloat_AS_DOUBLE(self.object) };
            let integer_part = value.trunc();
            if (value - integer_part) == 0.0f64 {
                serializer.serialize_f64(integer_part)
            } else {
                serializer.serialize_f64(value)
            }
        } else if object_type == unsafe { types::BOOL_TYPE } {
            serializer.serialize_bool(self.object == unsafe { types::TRUE })
        } else if object_type == unsafe { types::NONE_TYPE } {
            serializer.serialize_unit()
        } else if object_type == unsafe { types::DICT_TYPE } {
            if self.recursion_depth == RECURSION_LIMIT {
                return Err(SerdeError::custom("Recursion limit reached"));
            }
            let length = unsafe { (*self.object.cast::<ffi::PyDictObject>()).ma_used };
            if length == 0 {
                serializer.serialize_map(Some(0))?.end()
            } else {
                let mut items: SmallVec<[(&str, *mut ffi::PyObject); 32]> =
                    SmallVec::with_capacity(length as usize);
                let mut pos = 0isize;
                let mut str_size: ffi::Py_ssize_t = 0;
                let mut key: *mut ffi::PyObject = std::ptr::null_mut();
                let mut value: *mut ffi::PyObject = std::ptr::null_mut();
                for _ in 0..length {
                    unsafe {
                        ffi::_PyDict_Next(
                            self.object,
                            &mut pos,
                            &mut key,
                            &mut value,
                            std::ptr::null_mut(),
                        )
                    };
                    let data = unsafe { string::read_utf8_from_str(key, &mut str_size) };
                    let k = unsafe {
                        std::str::from_utf8_unchecked(std::slice::from_raw_parts(
                            data,
                            str_size as usize,
                        ))
                    };
                    items.push((k, value));
                }
                items.sort_unstable_by(|a, b| a.0.cmp(b.0));

                let mut map = serializer.serialize_map(None)?;
                for (key, val) in items.iter() {
                    map.serialize_entry(
                        key,
                        &PyObjectWrapper::new(*val, self.recursion_depth + 1),
                    )?;
                }
                map.end()
            }
        } else if object_type == unsafe { types::LIST_TYPE } {
            if self.recursion_depth == RECURSION_LIMIT {
                return Err(SerdeError::custom("Recursion limit reached"));
            }
            let length = unsafe { ffi::PyList_GET_SIZE(self.object) } as usize;
            if length == 0 {
                serializer.serialize_seq(Some(0))?.end()
            } else {
                let mut sequence = serializer.serialize_seq(None)?;
                for i in 0..length {
                    let elem = unsafe { ffi::PyList_GET_ITEM(self.object, i as isize) };
                    #[allow(clippy::integer_arithmetic)]
                    sequence
                        .serialize_element(&PyObjectWrapper::new(elem, self.recursion_depth + 1))?
                }
                sequence.end()
            }
        } else {
            Err(SerdeError::custom("Unsupported object type"))
        }
    }
}

#[pyfunction]
fn dumps(object: &PyAny) -> PyResult<String> {
    let value = PyObjectWrapper::new(object.as_ptr(), 0);
    Ok(serde_json::to_string(&value).map_err(error::JSONError)?)
}

// TODO:
//  - handle recursion with a memo instead of counting recursion levels?

/// Canonicalising JSON encoder
#[pymodule]
fn canonical_json(_: Python, module: &PyModule) -> PyResult<()> {
    types::init();
    module.add_wrapped(wrap_pyfunction!(dumps))?;
    Ok(())
}
