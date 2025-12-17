#ifndef X3CFLUX_ISOTOPOMERTRANSFORMATION_H
#define X3CFLUX_ISOTOPOMERTRANSFORMATION_H

#include <math/NumericTypes.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>

namespace x3cflux {

template <typename Method> struct IsotopomerTransformation;

template <> struct IsotopomerTransformation<CumomerMethod> {
    static RealVector apply(const RealVector &fractions, bool toIsotopomer = true);
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERTRANSFORMATION_H
