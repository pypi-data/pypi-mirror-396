#ifndef X3CFLUX_TYPECASTS_H
#define X3CFLUX_TYPECASTS_H

#include <FluxML.h>
#include <Python.h>
#include <boost/date_time/posix_time/ptime.hpp>
#include <boost/dynamic_bitset/dynamic_bitset.hpp>
#include <pybind11/detail/common.h>
#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace pybind11 {
namespace detail {
template <> struct type_caster<flux::symb::ExprTree> {
  public:
    PYBIND11_TYPE_CASTER(flux::symb::ExprTree, const_name("ExprTree"));

    bool load(handle src, bool);

    static handle cast(const flux::symb::ExprTree &src, return_value_policy /* policy */, handle /* parent */);
};

template <> struct type_caster<boost::dynamic_bitset<>> {
  public:
    PYBIND11_TYPE_CASTER(boost::dynamic_bitset<>, const_name("boost::dynamic_bitset<>"));

    bool load(handle src, bool);

    static handle cast(const boost::dynamic_bitset<> &src, return_value_policy /* policy */, handle /* parent */);
};

template <> struct type_caster<boost::posix_time::ptime> {
  public:
    PYBIND11_TYPE_CASTER(boost::posix_time::ptime, const_name("DateTime"));

    bool load(handle src, bool);

    static handle cast(const boost::posix_time::ptime &src, return_value_policy /* policy */, handle /* parent */);
};
} // namespace detail
} // namespace pybind11

#endif // X3CFLUX_TYPECASTS_H
