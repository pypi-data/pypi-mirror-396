
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include "LanguageRecognizer.h"

namespace py = pybind11;

PYBIND11_MODULE(simpleLanguageRecognizer, m) {
	m.def("languageRecognizer", &languageRecognizer, py::arg("text"), py::arg("allLanguages") = true, py::arg("maxResults") = 3, py::arg("sampleRatio") = 0.25);
}