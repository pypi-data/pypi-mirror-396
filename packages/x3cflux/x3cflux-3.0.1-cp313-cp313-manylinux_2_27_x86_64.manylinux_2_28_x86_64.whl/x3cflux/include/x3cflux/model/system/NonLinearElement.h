#ifndef X3CFLUX_NONLINEARELEMENT_H
#define X3CFLUX_NONLINEARELEMENT_H

#include <utility>

#include "LabelingSystem.h"
#include "NonLinearity.h"
#include "ParameterAccessor.h"

namespace x3cflux {

/// \brief Base class for numerical non-linear elements
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElementBase {
  public:
    using Fraction = typename SystemTraits<Method, Multi>::FractionType;
    using SystemState = typename SystemTraits<Method, Multi>::SystemStateType;
    using NonLinearFunction = NonLinearity<Method, Stationary, Multi>;
    using Input = typename NonLinearFunction::Input;

  private:
    Index rowIndex_;
    std::vector<Real> coefficients_;
    std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions_;

  public:
    /// Create base for numerical non-linear elements
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementBase(Index rowIndex, std::vector<Real> coefficients,
                                std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions);

    /// \return row index of the element
    auto getRowIndex() const -> Index;

    /// \return coefficients of the linear combination
    auto getCoefficients() const -> const std::vector<Real> &;

    /// \return non-linear functions to combine
    auto getNonLinearFunctions() const -> const std::vector<std::shared_ptr<NonLinearFunction>> &;
};

/// \brief Numerical non-linear element
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElement;

/// \brief Numerical non-linear element for IST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElement<Method, true, Multi> : public NumericNonLinearElementBase<Method, true, Multi> {
  public:
    using Base = NumericNonLinearElementBase<Method, true, Multi>;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    using Input = typename NonLinearFunction::Input;

  public:
    /// Create IST MFA non-linear element
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElement(Index rowIndex, const std::vector<Real> &coefficients,
                            const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions);

    /// Evaluate linear combination of non-linearities
    /// \param input evaluation input
    /// \return element value
    auto evaluate(const Input &input) const -> Fraction;
};

/// \brief Numerical non-linear element for INST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElement<Method, false, Multi> : public NumericNonLinearElementBase<Method, false, Multi> {
  public:
    using Base = NumericNonLinearElementBase<Method, false, Multi>;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    using Input = typename NonLinearFunction::Input;

  public:
    /// Create IST MFA non-linear element
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElement(Index rowIndex, const std::vector<Real> &coefficients,
                            const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions);

    /// Evaluate linear combination of non-linearities
    /// \param time time point at which to evaluate
    /// \param input evaluation input
    /// \return element value
    auto evaluate(Real time, const Input &input) const -> Fraction;
};

/// \brief Base class for numerical non-linear element derivatives
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElementDerivativeBase {
  public:
    using Fraction = typename SystemTraits<Method, Multi>::FractionType;
    using SystemState = typename SystemTraits<Method, Multi>::SystemStateType;
    using NonLinearFunction = NonLinearity<Method, Stationary, Multi>;
    using Input = typename NonLinearFunction::Input;

  private:
    Index rowIndex_;
    std::vector<Real> coefficients_;
    std::vector<Real> coefficientDerivatives_;
    std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions_;

  public:
    /// Create base of numerical non-linear element derivative
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param coefficientDerivatives partial derivative of the coefficients
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementDerivativeBase(Index rowIndex, std::vector<Real> coefficients,
                                          std::vector<Real> coefficientDerivatives,
                                          std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions);

    /// \return row index of the element
    auto getRowIndex() const -> Index;

    /// \return coefficient of the linear combination
    auto getCoefficients() const -> const std::vector<Real> &;

    /// \return partial derivative of the coefficients
    auto getCoefficientDerivatives() const -> const std::vector<Real> &;

    /// \return non-linear functions to combine
    auto getNonLinearFunctions() const -> const std::vector<std::shared_ptr<NonLinearFunction>> &;
};

/// \brief Numerical non-linear element derivative
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class NumericNonLinearElementDerivative;

/// \brief Numerical non-linear element derivative for IST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElementDerivative<Method, true, Multi>
    : public NumericNonLinearElementDerivativeBase<Method, true, Multi> {
  public:
    using Base = NumericNonLinearElementDerivativeBase<Method, true, Multi>;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    using Input = typename NonLinearFunction::Input;

  public:
    /// Create numerical IST MFA non-linear element derivate
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param coefficientDerivatives partial derivative of the coefficients
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementDerivative(Index rowIndex, const std::vector<Real> &coefficients,
                                      const std::vector<Real> &coefficientDerivatives,
                                      const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions);

    /// Evaluate linear combination of non-linearities and their derivatives
    /// \param input evaluation input
    /// \param inputDerivative derivative of evaluation input
    /// \return element partial derivate value
    auto evaluate(const Input &input, const Input &inputDerivative) const -> Fraction;
};

/// \brief Numerical non-linear element derivative for INST MFA
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class NumericNonLinearElementDerivative<Method, false, Multi>
    : public NumericNonLinearElementDerivativeBase<Method, false, Multi> {
  public:
    using Base = NumericNonLinearElementDerivativeBase<Method, false, Multi>;
    using typename Base::Fraction;
    using typename Base::NonLinearFunction;
    using typename Base::SystemState;
    using Input = typename NonLinearFunction::Input;

  public:
    /// Create numerical INST MFA non-linear element derivate
    /// \param rowIndex row index of the element
    /// \param coefficients coefficient of the linear combination
    /// \param coefficientDerivatives partial derivative of the coefficients
    /// \param nonLinearFunctions non-linear functions to combine
    NumericNonLinearElementDerivative(Index rowIndex, const std::vector<Real> &coefficients,
                                      const std::vector<Real> &coefficientDerivatives,
                                      const std::vector<std::shared_ptr<NonLinearFunction>> &nonLinearFunctions);

    /// Evaluate linear combination of non-linearities and their derivatives
    /// \param input evaluation input
    /// \param inputDerivative derivative of evaluation input
    /// \return element partial derivate value
    auto evaluate(Real time, const Input &input, const Input &inputDerivative) const -> Fraction;
};

/// \brief Symbolic element that is non-linear
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi> class SymbolicNonLinearElement {
  public:
    using NonLinearFunction = NonLinearity<Method, Stationary, Multi>;
    using EvaluatedNonLinearElement = NumericNonLinearElement<Method, Stationary, Multi>;
    using EvaluatedNonLinearElementDerivative = NumericNonLinearElementDerivative<Method, Stationary, Multi>;

  private:
    Index rowIndex_;
    Index poolSizeIndex_;
    std::vector<std::pair<std::size_t, bool>> fluxCoefficients_;
    std::vector<std::shared_ptr<NonLinearFunction>> nonLinearFunctions_;

  public:
    /// Create non-linear symbolic element
    /// \param rowIndex row index of element
    /// \param poolSizeIndex index of metabolic pool size corresponding to the row
    explicit SymbolicNonLinearElement(Index rowIndex, Index poolSizeIndex);

    /// Add non-linearity with flux coefficient to the element
    /// \param reactionIndex index of metabolic reaction associated with flux
    /// \param forward forward or backward flux
    /// \param nonLinearFunction non-linear function
    auto addNonLinearity(std::size_t reactionIndex, bool forward,
                         const std::shared_ptr<NonLinearFunction> &nonLinearFunction) -> void;

    /// \return row index of element
    auto getRowIndex() const -> Index;

    /// \return index of metabolic pool size corresponding to the row
    auto getPoolSizeIndex() const -> Index;

    /// \return list of index and type representation of metabolic fluxes
    auto getFluxCoefficients() const -> const std::vector<std::pair<std::size_t, bool>> &;

    /// \return list of non-linear functions
    auto getNonLinearFunctions() const -> const std::vector<std::shared_ptr<NonLinearFunction>> &;

    /// Semi-evaluate the symbolic summation of non-linearities
    /// \param accessor accessor of metabolic fluxes
    /// \return linear combination of non-linearities
    auto evaluate(const ParameterAccessor &accessor) const -> EvaluatedNonLinearElement;

    /// Semi-evaluate the partial derivative of the symbolic summation of non-linearities
    /// \param accessor accessor of metabolic fluxes and partial derivatives
    /// \return linear combination of non-linearities and their partial derivatives
    auto evaluateDerivative(const DerivativeParameterAccessor &accessor) const -> EvaluatedNonLinearElementDerivative;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "NonLinearElement.tpp"
#endif

#endif // X3CFLUX_NONLINEARELEMENT_H
