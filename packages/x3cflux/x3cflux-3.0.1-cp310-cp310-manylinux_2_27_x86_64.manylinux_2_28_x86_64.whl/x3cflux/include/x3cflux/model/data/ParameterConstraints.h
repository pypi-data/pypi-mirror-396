#ifndef X3CFLUX_SRC_DATA_PARAMETERCONSTRAINTS_H
#define X3CFLUX_SRC_DATA_PARAMETERCONSTRAINTS_H

#include "NumericTypes.h"

#include <list>
#include <string>

namespace x3cflux {

/// \brief Base class for parameter constraints
class ConstraintBase {
  protected:
    std::string name_;

  public:
    /// \brief Creates constraint.
    /// \param name name of the constraint
    explicit ConstraintBase(std::string name);

    /// \return name of the constraint
    const std::string &getName() const;
};

/// \brief Constraints of type \f$parameter=value\f$
class DefinitionConstraint : public ConstraintBase {
  private:
    std::string parameterName_;
    Real parameterValue_;

  public:
    /// \brief Creates a parameter defining constraint.
    /// \param name name of the constraint
    /// \param parameterName name of the parameter
    /// \param parameterValue value of the parameter
    DefinitionConstraint(const std::string &name, std::string parameterName, Real parameterValue);

    /// \return name of the parameter
    const std::string &getParameterName() const;

    /// \return value of the parameter
    Real getParameterValue() const;
};

/// \brief Constraints of type \f$\sum a_i \cdot parameter_i + constant\f$
class LinearConstraint : public ConstraintBase {
  private:
    std::vector<std::string> parameterNames_;
    std::vector<Real> parameterCoefficients_;
    Real constant_;

  public:
    /// \brief Create a constraint for a linear combination of parameters.
    /// \param name name of the constraint
    /// \param parameterNames name of the parameters
    /// \param parameterCoefficients coefficients of the parameters
    /// \param constant additional constant value
    LinearConstraint(const std::string &name, std::vector<std::string> parameterNames,
                     std::vector<Real> parameterCoefficients, Real constant);

    /// \return name of the parameters
    const std::vector<std::string> &getParameterNames() const;

    /// \return coefficients of the parameters
    const std::vector<Real> &getParameterCoefficients() const;

    /// \return additional constant value
    Real getConstant() const;
};

/// \brief Collection of parameter constraints
///
/// A collection of constraints can be parameter definitions, equality and
/// inequality constraints for linear combinations of parameters. Equality
/// constraints are defined like
/// \f$\sum parameter_i + constant = 0\f$,
/// inequality constraints are defined like
/// \f$\sum parameter_i + constant < 0\f$.
class ParameterConstraints {
  private:
    std::vector<DefinitionConstraint> definitionConstraints_;
    std::vector<LinearConstraint> equalityConstraints_;
    std::vector<LinearConstraint> inequalityConstraints_;

  public:
    /// \brief Creates a collection of parameter constraints.
    /// \param definitionConstraints parameter defining constraints
    /// \param equalityConstraints constraining the sum of parameters and a constant equal to zero
    /// \param inequalityConstraints constraining the sum of parameters and a constant less than to zero
    ParameterConstraints(std::vector<DefinitionConstraint> definitionConstraints,
                         std::vector<LinearConstraint> equalityConstraints,
                         std::vector<LinearConstraint> inequalityConstraints);

    /// \return parameter definition constraints
    const std::vector<DefinitionConstraint> &getDefinitionConstraints() const;

    /// \return parameter equality constraints
    const std::vector<LinearConstraint> &getEqualityConstraints() const;

    /// \return parameter inequality constraints
    const std::vector<LinearConstraint> &getInequalityConstraints() const;
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_PARAMETERCONSTRAINTS_H