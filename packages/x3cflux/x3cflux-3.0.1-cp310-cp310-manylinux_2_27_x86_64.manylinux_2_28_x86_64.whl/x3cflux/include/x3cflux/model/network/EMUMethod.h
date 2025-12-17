#ifndef X3CFLUX_EMUMETHOD_H
#define X3CFLUX_EMUMETHOD_H

#include "CascadeIterator.h"
#include "CascadeOrdering.h"

namespace x3cflux {

/// \brief EMU modeling method
///
/// This struct provides implementations to use LabelingNetwork
/// with the EMU modeling method. It provides an iterator
/// for on-the-fly generation of EMU network levels and
/// reactions as well as sequential EMU level ordering.
struct EMUMethod {
    using StateType = boost::dynamic_bitset<>;
    using IteratorType = CascadeIterator;
    using OrderingType = CascadeOrdering;
};

} // namespace x3cflux

#endif // X3CFLUX_EMUMETHOD_H
