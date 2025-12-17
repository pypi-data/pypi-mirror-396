mod pretty;

use std::io::Write;

use pyo3::prelude::*;

///A class for pretty-printing Python objects.
#[pyclass]
pub struct Pretty {
    config: pretty::Config,
}

#[pymethods]
impl Pretty {
    #[new]
    #[pyo3(signature = (indent = 4))]
    fn new(indent: usize) -> Self {
        Self {
            config: pretty::Config { indent },
        }
    }

    /// The number of spaces to use for indentation. Default is 4.
    #[getter]
    fn indent(&self) -> usize {
        self.config.indent
    }

    #[setter]
    fn set_indent(&mut self, indent: usize) {
        self.config.indent = indent;
    }

    /// Pretty-format the given object and return it as a string.
    ///
    /// Args:
    ///     obj: The object to pretty-format.
    ///
    /// Returns:
    ///     A string containing the pretty-formatted representation of the object.
    fn format(&self, obj: &Bound<'_, PyAny>) -> PyResult<String> {
        let mut buffer = Vec::new();
        pretty::print(obj, &self.config, 0, &mut buffer)?;
        buffer.push(b'\n');
        Ok(String::from_utf8(buffer).unwrap_or_default())
    }

    /// Pretty-print the given object to standard output.
    ///
    /// Args:
    ///     obj: The object to pretty-print.
    fn print(&self, obj: &Bound<'_, PyAny>) -> PyResult<()> {
        let mut stdout = std::io::stdout();
        pretty::print(obj, &self.config, 0, &mut stdout)?;
        writeln!(stdout)?;
        Ok(())
    }
}

/// Pretty-format the given object and return it as a string.
///
/// Args:
///     obj: The object to pretty-format.
///     indent: The number of spaces to use for indentation. Default is 4.
///
/// Returns:
///     A string containing the pretty-formatted representation of the object.
#[pyo3::pyfunction]
#[pyo3(signature = (obj, indent = 4))]
fn pretty_format(obj: &Bound<'_, PyAny>, indent: usize) -> PyResult<String> {
    Pretty::new(indent).format(obj)
}

/// Pretty-print the given object to standard output.
///
/// Args:
///     obj: The object to pretty-print.
///     indent: The number of spaces to use for indentation. Default is 4.
#[pyo3::pyfunction]
#[pyo3(signature = (obj, indent = 4))]
fn pretty_print(obj: &Bound<'_, PyAny>, indent: usize) -> PyResult<()> {
    Pretty::new(indent).print(obj)
}

/// A module for pretty-printing Python objects.
#[pyo3::pymodule]
mod foliar {
    #[pymodule_export]
    use super::{Pretty, pretty_format, pretty_print};
}
