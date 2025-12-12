use kdl::{KdlDocument, KdlNode, KdlValue};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyInt, PyString};

#[pyclass]
struct Document {
    inner: KdlDocument,
}

#[pyclass]
struct Node {
    inner: KdlNode,
}

#[pymethods]
impl Document {
    #[new]
    fn new() -> Self {
        Self {
            inner: KdlDocument::new(),
        }
    }

    #[staticmethod]
    fn parse(text: &str) -> PyResult<Self> {
        parse_document(text)
    }

    #[getter]
    fn nodes(&self) -> Vec<Node> {
        self.inner.nodes().iter().cloned().map(Node::from).collect()
    }

    fn get(&self, name: &str) -> Option<Node> {
        self.inner.get(name).cloned().map(Node::from)
    }

    fn get_arg(&self, py: Python<'_>, name: &str) -> PyResult<Option<Py<PyAny>>> {
        self.inner
            .get_arg(name)
            .map(|v| value_to_py(py, v))
            .transpose()
    }

    fn iter_args(&self, py: Python<'_>, name: &str) -> PyResult<Vec<Py<PyAny>>> {
        self.inner
            .iter_args(name)
            .map(|v| value_to_py(py, v))
            .collect()
    }

    fn autoformat(&mut self) {
        self.inner.autoformat();
    }

    fn to_string(&self) -> String {
        self.inner.to_string()
    }

    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!("Document({})", self.inner)
    }
}

#[pymethods]
impl Node {
    #[getter]
    fn name(&self) -> String {
        self.inner.name().value().to_string()
    }

    #[getter]
    fn ty(&self) -> Option<String> {
        self.inner.ty().map(|ty| ty.value().to_string())
    }

    #[getter]
    fn args(&self, py: Python<'_>) -> PyResult<Vec<Py<PyAny>>> {
        self.inner
            .entries()
            .iter()
            .filter(|e| e.name().is_none())
            .map(|e| value_to_py(py, e.value()))
            .collect()
    }

    #[getter]
    fn props(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);
        for entry in self.inner.entries().iter().filter(|e| e.name().is_some()) {
            if let Some(name) = entry.name() {
                dict.set_item(name.value(), value_to_py(py, entry.value())?)?;
            }
        }

        Ok(dict.into_pyobject(py)?.unbind().into())
    }

    #[getter]
    fn children(&self) -> Option<Document> {
        self.inner
            .children()
            .cloned()
            .map(|doc| Document { inner: doc })
    }

    fn to_string(&self) -> String {
        self.inner.to_string()
    }

    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!("Node({})", self.inner)
    }
}

#[pyfunction]
fn parse(text: &str) -> PyResult<Document> {
    parse_document(text)
}

fn parse_document(text: &str) -> PyResult<Document> {
    let inner = text
        .parse::<KdlDocument>()
        .map_err(|err| PyValueError::new_err(err.to_string()))?;
    Ok(Document { inner })
}

fn value_to_py(py: Python<'_>, value: &KdlValue) -> PyResult<Py<PyAny>> {
    Ok(match value {
        KdlValue::String(v) => PyString::new(py, v).into_any().unbind(),
        KdlValue::Integer(v) => PyInt::new(py, *v).into_any().unbind(),
        KdlValue::Float(v) => PyFloat::new(py, *v).into_any().unbind(),
        KdlValue::Bool(v) => py.get_type::<PyBool>().call1((*v,))?.into_any().unbind(),
        KdlValue::Null => py.None(),
    })
}

impl From<KdlNode> for Node {
    fn from(inner: KdlNode) -> Self {
        Self { inner }
    }
}

#[pymodule]
fn kdl_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Document>()?;
    m.add_class::<Node>()?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;

    let version = env!("CARGO_PKG_VERSION");
    m.add("__version__", version)?;
    Ok(())
}
