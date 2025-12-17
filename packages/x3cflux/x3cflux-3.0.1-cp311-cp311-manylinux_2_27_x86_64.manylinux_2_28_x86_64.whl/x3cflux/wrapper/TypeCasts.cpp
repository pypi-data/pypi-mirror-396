#include "TypeCasts.h"

#include <boost/date_time/posix_time/time_formatters.hpp>
#include <boost/date_time/posix_time/time_parsers.hpp>

bool pybind11::detail::type_caster<ExprTree, void>::load(handle src, bool) {
    PyObject *source = src.ptr();
    PyObject *stringConverter = PyObject_GetAttrString(source, "__str__");
    PyObject *result = PyObject_CallObject(stringConverter, nullptr);
    if (!result) {
        return false;
    }
    std::string expressionString(PyUnicode_AsUTF8(result));
    value = *flux::symb::ExprTree::parse(expressionString.c_str());
    Py_DECREF(result);

    return not PyErr_Occurred();
}

pybind11::handle pybind11::detail::type_caster<ExprTree, void>::cast(const flux::symb::ExprTree &src,
                                                                     return_value_policy, handle) {
    auto expression_string = src.toString();

    PyObject *sympy = PyImport_ImportModule("sympy");
    if (!sympy) {
        PyErr_Print();
        std::cerr << "Error: could not import module 'sympy'" << std::endl;
    }
    PyObject *parseExpr = PyObject_GetAttrString(sympy, "parse_expr");
    PyObject *args = Py_BuildValue("(s)", expression_string.c_str());
    PyObject *sympyExpr = PyObject_CallObject(parseExpr, args);
    Py_DECREF(args);
    Py_DECREF(parseExpr);

    return sympyExpr;
}

bool pybind11::detail::type_caster<boost::dynamic_bitset<>, void>::load(handle src, bool) {
    PyObject *source = src.ptr();
    PyObject *stringConverter = PyObject_GetAttrString(source, "__str__");
    PyObject *result = PyObject_CallObject(stringConverter, nullptr);
    if (!result) {
        return false;
    }
    std::string bitsetString(PyUnicode_AsUTF8(result));
    value = boost::dynamic_bitset<>(bitsetString);
    Py_DECREF(result);

    return not PyErr_Occurred();
}

pybind11::handle pybind11::detail::type_caster<boost::dynamic_bitset<>, void>::cast(const boost::dynamic_bitset<> &src,
                                                                                    return_value_policy, handle) {
    std::string bitsetString;
    boost::to_string(src, bitsetString);

    PyObject *stringObject = PyUnicode_FromString(bitsetString.c_str());

    return stringObject;
}

bool pybind11::detail::type_caster<boost::posix_time::ptime, void>::load(handle src, bool) {
    PyObject *source = src.ptr();
    PyObject *stringConverter = PyObject_GetAttrString(source, "isoformat");
    PyObject *result = PyObject_CallObject(stringConverter, nullptr);
    if (!result) {
        return false;
    }
    std::string datetimeString(PyUnicode_AsUTF8(result));
    value = boost::posix_time::from_iso_extended_string(datetimeString);
    Py_DECREF(result);

    return not PyErr_Occurred();
}

pybind11::handle
pybind11::detail::type_caster<boost::posix_time::ptime, void>::cast(const boost::posix_time::ptime &src,
                                                                    return_value_policy, handle) {
    auto datetimeString = boost::posix_time::to_iso_extended_string(src);

    PyObject *datetime = PyImport_ImportModule("datetime");
    if (!datetime) {
        PyErr_Print();
        std::cerr << "Error: could not import module 'datetime'" << std::endl;
    }
    PyObject *classDatetime = PyObject_GetAttrString(datetime, "datetime");
    PyObject *parseDatetime = PyObject_GetAttrString(classDatetime, "fromisoformat");
    PyObject *args = Py_BuildValue("(s)", datetimeString.c_str());
    PyObject *datetimeObject = PyObject_CallObject(parseDatetime, args);
    Py_DECREF(args);
    Py_DECREF(classDatetime);
    Py_DECREF(parseDatetime);

    return datetimeObject;
}
