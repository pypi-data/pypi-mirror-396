#ifndef X3CFLUX_NATURALLABELINGINITIALIZER_H
#define X3CFLUX_NATURALLABELINGINITIALIZER_H

#include <math/NumericTypes.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/IsotopomerMethod.h>
#include <model/network/MetaboliteNetwork.h>
#include <model/network/StateTransporter.h>

namespace x3cflux {

template <typename Method> struct NaturalLabelingInitializer;

template <> struct NaturalLabelingInitializer<IsotopomerMethod> {
    using Isotopomer = StateVariableImpl<IsotopomerMethod::StateType>;

    static Real computeFraction(const Isotopomer &isotopomer, const std::map<TracerElement, std::size_t> &numIsotopes);

    template <typename Ordering>
    static RealVector computeInitialState(const MetaboliteNetwork &network, const Ordering &ordering);
};

template <> struct NaturalLabelingInitializer<CumomerMethod> {
    using Cumomer = typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType;
    using IsotopomerNaturalLabeling = NaturalLabelingInitializer<IsotopomerMethod>;
    using Isotopomer = typename IsotopomerNaturalLabeling::Isotopomer;

    static Real computeFraction(const Cumomer &cumomer, const std::map<TracerElement, std::size_t> &isotopesNumAtoms);

    template <typename Ordering>
    static RealVector computeInitialState(const MetaboliteNetwork &network, const Ordering &ordering);
};

template <> struct NaturalLabelingInitializer<EMUMethod> {
    using EMU = typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType;
    using IsotopomerNaturalLabeling = NaturalLabelingInitializer<IsotopomerMethod>;
    using Isotopomer = typename IsotopomerNaturalLabeling::Isotopomer;

    static RealVector computeFraction(const EMU &emu, const std::map<TracerElement, std::size_t> &isotopesNumAtoms);

    template <typename Ordering>
    static RealMatrix computeInitialState(const MetaboliteNetwork &network, const Ordering &ordering);
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "NaturalLabelingInitializer.tpp"
#endif

#endif // X3CFLUX_NATURALLABELINGINITIALIZER_H
