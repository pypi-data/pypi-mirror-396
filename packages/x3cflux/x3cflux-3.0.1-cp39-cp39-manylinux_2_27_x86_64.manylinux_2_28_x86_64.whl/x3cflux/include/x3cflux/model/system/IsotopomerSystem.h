#ifndef X3CFLUX_ISOTOPOMERSYSTEM_H
#define X3CFLUX_ISOTOPOMERSYSTEM_H

#include "LabelingSystem.h"
#include "MultiHelper.h"
#include "NonLinearElement.h"
#include <math/IVPBase.h>
#include <math/NumericTypes.h>
#include <model/data/Substrate.h>
#include <model/network/LabelingNetwork.h>

#include <utility>

namespace x3cflux {

template <bool Multi = false>
class IsotopomerSystem : public LabelingSystem<IsotopomerMethod, false, Multi>,
                         public IVPBase<typename SystemTraits<IsotopomerMethod, Multi>::SystemStateType> {
  public:
    using Base = LabelingSystem<IsotopomerMethod, false, Multi>;
    using typename Base::Fraction;
    using typename Base::Solution;
    using typename Base::Solver;
    using typename Base::SystemState;

    using NonLinearElement = NumericNonLinearElement<IsotopomerMethod, false, Multi>;
    using StateVarOps = StateVariableOperations<IsotopomerMethod, Multi>;

  private:
    RealSparseMatrix linearCoefficients_;
    std::vector<NonLinearElement> nonLinearities_;

  public:
    IsotopomerSystem(const RealSparseMatrix &linearCoefficients, std::vector<NonLinearElement> nonLinearities,
                     const SystemState &initialValue, Real endTime, const Solver &solver);

    const RealSparseMatrix &getLinearCoefficients() const;

    const std::vector<NonLinearElement> &getNonLinearities() const;

    auto evaluateNonLinearities(Real time, const SystemState &state) const -> SystemState;

    auto operator()(Real time, const SystemState &state) const -> SystemState override;

    auto solve() const -> Solution override;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "IsotopomerSystem.tpp"
#endif

#endif // X3CFLUX_ISOTOPOMERSYSTEM_H
