use std::fmt::{self, Display};

use pyo3::exceptions::PyValueError;
use pyo3::PyErr;
use serde::{de, ser};

#[derive(Clone, Debug, PartialEq)]
pub enum Error {
    Message(String),
}

impl ser::Error for Error {
    fn custom<T: Display>(msg: T) -> Self {
        Error::Message(msg.to_string())
    }
}

impl de::Error for Error {
    fn custom<T: Display>(msg: T) -> Self {
        Error::Message(msg.to_string())
    }
}

impl Display for Error {
    fn fmt(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Error::Message(msg) => formatter.write_str(msg),
        }
    }
}

impl std::error::Error for Error {}

impl From<Error> for PyErr {
    fn from(error: Error) -> Self {
        PyValueError::new_err(error.to_string())
    }
}

pub(crate) struct JSONError(pub serde_json::Error);

impl From<JSONError> for PyErr {
    fn from(error: JSONError) -> Self {
        PyValueError::new_err(error.0.to_string())
    }
}
