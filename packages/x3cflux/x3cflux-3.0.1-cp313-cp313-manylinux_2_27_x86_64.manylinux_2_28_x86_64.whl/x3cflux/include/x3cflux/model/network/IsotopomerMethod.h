#ifndef X3CFLUX_ISOTOPOMERMETHOD_H
#define X3CFLUX_ISOTOPOMERMETHOD_H

#include "IsotopomerIterator.h"
#include "IsotopomerOrdering.h"

namespace x3cflux {

/// \brief Isotopomer modeling method
///
/// This struct provides implementations to use LabelingNetwork
/// with the isotopomer modeling method. It provides an iterator
/// for on-the-fly generation of isotopomer reactions and sequential
/// isotopomer ordering.
struct IsotopomerMethod {
    using StateType = boost::dynamic_bitset<>;
    using IteratorType = IsotopomerIterator;
    using OrderingType = IsotopomerOrdering;
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERMETHOD_H
