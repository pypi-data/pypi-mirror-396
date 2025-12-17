#ifndef X3CFLUX_NONLINEARITY_H
#define X3CFLUX_NONLINEARITY_H

#include "MultiHelper.h"
#include "StateVariableOperations.h"
#include <IVPSolver.h>

namespace x3cflux {

template <typename Method, bool Stationary, bool Multi> class NonLinearity;

template <typename Method, bool Multi> class NonLinearity<Method, true, Multi> {
  public:
    using Traits = SystemTraits<Method, Multi>;
    using Fraction = typename Traits::FractionType;
    using SystemState = typename Traits::SystemStateType;
    using Input = std::vector<SystemState>;

  public:
    virtual ~NonLinearity();

    virtual Fraction evaluate(const Input &input) const = 0;

    virtual Fraction evaluateDerivative(const Input &input, const Input &inputDerivative) const = 0;
};

template <typename Method, bool Multi> class NonLinearity<Method, false, Multi> {
  public:
    using Traits = SystemTraits<Method, Multi>;
    using Fraction = typename Traits::FractionType;
    using SystemState = typename Traits::SystemStateType;
    typedef std::conditional_t<Traits::TYPE == SystemType::CASCADED,
                               std::vector<typename IVPSolver<SystemState>::Solution>, SystemState>
        Input;

  public:
    virtual ~NonLinearity();

    virtual Fraction evaluate(Real time, const Input &input) const = 0;

    virtual Fraction evaluateDerivative(Real time, const Input &input, const Input &inputDerivative) const = 0;
};

template <typename Method, bool Stationary, bool Multi> class Condensation;

template <bool Multi>
class Condensation<IsotopomerMethod, false, Multi> : public NonLinearity<IsotopomerMethod, false, Multi> {
  public:
    using Traits = SystemTraits<IsotopomerMethod, Multi>;
    using Fraction = typename Traits::FractionType;
    using SystemState = typename Traits::SystemStateType;
    using StateVarOps = StateVariableOperations<IsotopomerMethod, Multi>;

  private:
    std::vector<size_t> systemIndices_;

  public:
    explicit Condensation(std::vector<size_t> systemIndices);

    auto evaluate(Real time, const SystemState &isotopomers) const -> Fraction override;

    auto evaluateDerivative(Real time, const SystemState &isotopomers, const SystemState &isotopomerDerivatives) const
        -> Fraction override;
};

template <typename Method, bool Stationary, bool Multi>
class Condensation : public NonLinearity<Method, true, Multi>, public NonLinearity<Method, false, Multi> {
  public:
    using Traits = SystemTraits<Method, Multi>;
    using Fraction = typename Traits::FractionType;
    using SystemState = typename Traits::SystemStateType;
    using StationaryInput = typename NonLinearity<Method, true, Multi>::Input;
    using NonStationaryInput = typename NonLinearity<Method, false, Multi>::Input;
    using StateVarOps = StateVariableOperations<Method, Multi>;

  private:
    std::vector<std::size_t> cascadeIndices_;
    std::vector<std::size_t> systemIndices_;

  public:
    Condensation(std::vector<std::size_t> cascadeIndices, std::vector<std::size_t> systemIndices);

    auto evaluate(const StationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluateDerivative(const StationaryInput &baseSolution,
                            const StationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;

    auto evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                            const NonStationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;
};

template <typename Method, bool Stationary, bool Multi> class ConstantSubstrateInput;

template <bool Stationary, bool Multi>
class ConstantSubstrateInput<IsotopomerMethod, Stationary, Multi>
    : public NonLinearity<IsotopomerMethod, true, Multi>, public NonLinearity<IsotopomerMethod, false, Multi> {
  public:
    using Base = NonLinearity<IsotopomerMethod, Stationary, Multi>;
    using typename Base::Fraction;
    using typename Base::SystemState;
    using StationaryInput = typename NonLinearity<IsotopomerMethod, true, Multi>::Input;
    using NonStationaryInput = typename NonLinearity<IsotopomerMethod, false, Multi>::Input;

  private:
    Fraction concentration_;

  public:
    explicit ConstantSubstrateInput(Fraction concentration);

    auto evaluate(const StationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluateDerivative(const StationaryInput &baseSolution,
                            const StationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;

    auto evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                            const NonStationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;
};

template <bool Stationary, bool Multi>
class ConstantSubstrateInput<CumomerMethod, Stationary, Multi> : public NonLinearity<CumomerMethod, true, Multi>,
                                                                 public NonLinearity<CumomerMethod, false, Multi> {
  public:
    using Base = NonLinearity<CumomerMethod, Stationary, Multi>;
    using typename Base::Fraction;
    using typename Base::SystemState;
    using StationaryInput = typename NonLinearity<CumomerMethod, true, Multi>::Input;
    using NonStationaryInput = typename NonLinearity<CumomerMethod, false, Multi>::Input;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    Fraction concentration_;

  public:
    explicit ConstantSubstrateInput(const MultiAdapt<std::shared_ptr<ConstantSubstrate>> &substrate,
                                    const boost::dynamic_bitset<> &state);

    auto evaluate(const StationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluateDerivative(const StationaryInput &baseSolution,
                            const StationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;

    auto evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                            const NonStationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;

  private:
    static auto computeCumomer(const std::shared_ptr<ConstantSubstrate> &substrate,
                               const boost::dynamic_bitset<> &state) -> Real;
};

template <bool Stationary, bool Multi>
class ConstantSubstrateInput<EMUMethod, Stationary, Multi> : public NonLinearity<EMUMethod, true, Multi>,
                                                             public NonLinearity<EMUMethod, false, Multi> {
  public:
    using Base = NonLinearity<EMUMethod, Stationary, Multi>;
    using typename Base::Fraction;
    using typename Base::SystemState;
    using StationaryInput = typename NonLinearity<EMUMethod, true, Multi>::Input;
    using NonStationaryInput = typename NonLinearity<EMUMethod, false, Multi>::Input;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    Fraction concentration_;

  public:
    explicit ConstantSubstrateInput(const MultiAdapt<std::shared_ptr<ConstantSubstrate>> &substrate,
                                    const boost::dynamic_bitset<> &state);

    auto evaluate(const StationaryInput &input) const -> Fraction override;

    auto evaluate(Real time, const NonStationaryInput &prevLevelSolutions) const -> Fraction override;

    auto evaluateDerivative(const StationaryInput &baseSolution,
                            const StationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;

    auto evaluateDerivative(Real time, const NonStationaryInput &baseSolution,
                            const NonStationaryInput &prevLevelDerivativeSolutions) const -> Fraction override;

  private:
    static auto computeEMU(const std::shared_ptr<ConstantSubstrate> &substrate, const boost::dynamic_bitset<> &state)
        -> RealVector;

    static auto computeEMU(const std::vector<std::shared_ptr<ConstantSubstrate>> &parSubstrate,
                           const boost::dynamic_bitset<> &state) -> RealVector;
};

template <typename Method, bool Multi> class VariateSubstrateInputBase : public NonLinearity<Method, false, Multi> {
  public:
    using Base = NonLinearity<Method, false, Multi>;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    using EvaluationResult = std::conditional_t<Multi, Real, RealVector>;

  public:
    static auto evaluateSimpleInput(const VariateProfile &inputFunctions, Real time) -> Real;

    static auto evaluateSimpleInputDerivative(const VariateProfile &inputFunctions, Real time) -> Real;

  private:
    static auto evaluateExpression(const flux::symb::ExprTree &expr, Real time) -> Real;
};

template <typename Method, bool Multi> class VariateSubstrateInput;

template <bool Multi>
class VariateSubstrateInput<IsotopomerMethod, Multi> : public VariateSubstrateInputBase<IsotopomerMethod, Multi> {
  public:
    using Base = VariateSubstrateInputBase<IsotopomerMethod, Multi>;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    MultiAdapt<VariateProfile> substrate_;

  public:
    explicit VariateSubstrateInput(const MultiAdapt<VariateProfile> &inputFunctions);

    auto evaluate(Real time, const Input &input) const -> Fraction override;

    auto evaluateDerivative(Real time, const Input &input, const Input &inputDerivative) const -> Fraction override;
};

template <bool Multi>
class VariateSubstrateInput<CumomerMethod, Multi> : public VariateSubstrateInputBase<CumomerMethod, Multi> {
  public:
    using Base = VariateSubstrateInputBase<CumomerMethod, Multi>;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    MultiAdapt<std::shared_ptr<VariateSubstrate>> substrate_;
    boost::dynamic_bitset<> state_;

  public:
    explicit VariateSubstrateInput(const MultiAdapt<std::shared_ptr<VariateSubstrate>> &substrate,
                                   boost::dynamic_bitset<> state);

    auto evaluate(Real time, const Input &prevLevelSolutions) const -> Fraction override;

    auto evaluateDerivative(Real time, const Input &baseSolution, const Input &prevLevelDerivativeSolution) const
        -> Fraction override;

  private:
    static auto evaluateCumomer(const std::shared_ptr<VariateSubstrate> &substrate,
                                const boost::dynamic_bitset<> &state, Real time) -> Real;

    static auto evaluateCumomerDerivative(const std::shared_ptr<VariateSubstrate> &substrate,
                                          const boost::dynamic_bitset<> &state, Real time) -> Real;
};

template <bool Multi>
class VariateSubstrateInput<EMUMethod, Multi> : public VariateSubstrateInputBase<EMUMethod, Multi> {
  public:
    using Base = VariateSubstrateInputBase<EMUMethod, Multi>;
    using typename Base::EvaluationResult;
    using typename Base::Fraction;
    using typename Base::Input;
    using typename Base::SystemState;

    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

  private:
    MultiAdapt<std::shared_ptr<VariateSubstrate>> substrate_;
    boost::dynamic_bitset<> state_;

  public:
    explicit VariateSubstrateInput(const MultiAdapt<std::shared_ptr<VariateSubstrate>> &substrate,
                                   boost::dynamic_bitset<> state);

    auto evaluate(Real time, const Input &prevLevelSolutions) const -> Fraction override;

    auto evaluateDerivative(Real time, const Input &baseSolution, const Input &prevLevelDerivativeSolution) const
        -> Fraction override;

  private:
    static auto evaluateEMU(const std::vector<std::shared_ptr<VariateSubstrate>> &parSubstrate,
                            const boost::dynamic_bitset<> &state, Real time) -> RealVector;

    static auto evaluateEMU(const std::shared_ptr<VariateSubstrate> &substrate, const boost::dynamic_bitset<> &state,
                            Real time) -> RealVector;

    static auto evaluateEMUDerivative(const std::vector<std::shared_ptr<VariateSubstrate>> &parSubstrate,
                                      const boost::dynamic_bitset<> &state, Real time) -> RealVector;

    static auto evaluateEMUDerivative(const std::shared_ptr<VariateSubstrate> &substrate,
                                      const boost::dynamic_bitset<> &state, Real time) -> RealVector;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "NonLinearity.tpp"
#endif

#endif // X3CFLUX_NONLINEARITY_H
