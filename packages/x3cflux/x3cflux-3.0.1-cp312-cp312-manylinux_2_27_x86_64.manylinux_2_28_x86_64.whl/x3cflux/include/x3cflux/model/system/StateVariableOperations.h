#ifndef X3CFLUX_STATEVARIABLEOPERATIONS_H
#define X3CFLUX_STATEVARIABLEOPERATIONS_H

#include "SystemTraits.h"

namespace x3cflux {

/// \brief Base operations on state variables
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi> struct StateVariableOperations;

template <bool Multi> struct StateVariableOperations<IsotopomerMethod, Multi> {
    using SystemState = typename SystemTraits<IsotopomerMethod, Multi>::SystemStateType;
    using Fraction = typename SystemTraits<IsotopomerMethod, Multi>::FractionType;

    static auto blockwiseIfMulti(const RealVector &state, Index numMulti) -> SystemState;

    static auto assign(SystemState &state, Index place, const Fraction &value) -> void;

    static auto get(const SystemState &state, Index place) -> Fraction;

    static auto get(const Fraction &fraction, Index multiPlace) -> Real;

    static auto computeProduct(const Fraction &fraction0, const Fraction &fraction1, Index) -> Fraction;
};

template <bool Multi> struct StateVariableOperations<CumomerMethod, Multi> {
    using SystemState = typename SystemTraits<CumomerMethod, Multi>::SystemStateType;
    using Fraction = typename SystemTraits<CumomerMethod, Multi>::FractionType;

    static auto blockwiseIfMulti(const RealVector &state, Index numMulti) -> SystemState;

    static void assign(SystemState &state, Index place, const Fraction &value);

    static auto get(const SystemState &state, Index place) -> Fraction;

    static auto get(const Fraction &fraction, Index multiPlace, Index) -> Real;

    static auto computeProduct(const Fraction &fraction0, const Fraction &fraction1, Index) -> Fraction;
};

template <bool Multi> struct StateVariableOperations<EMUMethod, Multi> {
    using SystemState = typename SystemTraits<EMUMethod, Multi>::SystemStateType;
    using Fraction = typename SystemTraits<EMUMethod, Multi>::FractionType;

    static auto blockwiseIfMulti(const RealMatrix &state, Index numMulti) -> SystemState;

    static void assign(SystemState &state, Index place, const Fraction &value);

    static auto get(const SystemState &state, Index place) -> Fraction;

    static auto get(const Fraction &fraction, Index multiPlace, Index levelIndex) -> Fraction;

    static Fraction computeProduct(const Fraction &fraction0, const Fraction &fraction1, Index level);
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "StateVariableOperations.tpp"
#endif

#endif // X3CFLUX_STATEVARIABLEOPERATIONS_H
