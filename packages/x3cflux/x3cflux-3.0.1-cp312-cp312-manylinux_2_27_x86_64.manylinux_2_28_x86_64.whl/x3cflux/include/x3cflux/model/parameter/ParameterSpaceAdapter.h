#ifndef X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEADAPTER_H
#define X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEADAPTER_H

#include "ParameterSpace.h"

#include <boost/dynamic_bitset/dynamic_bitset.hpp>

namespace x3cflux {

class ParameterSpaceAdapterBase : public ParameterSpace {
  private:
    Real constraintViolationTolerance_;

  public:
    explicit ParameterSpaceAdapterBase(ParameterSpace &&parameterSpace, Real constraintViolationTolerance = 0.);

    /// \return Absolute tolerance of inequality constraint violation
    Real getConstraintViolationTolerance() const;

    /// \param constraintViolationTolerance Absolute tolerance of inequality constraint violation
    void setConstraintViolationTolerance(Real constraintViolationTolerance);

    static boost::dynamic_bitset<> buildFreeParameterMask(std::size_t numParams,
                                                          const ParameterClassification &paramClass,
                                                          const SolutionSpace &paramSolutionSpace);

    static RealVector buildFullParameterVector(const RealVector &freeParameters,
                                               const boost::dynamic_bitset<> &freeParamMask,
                                               const ParameterClassification &paramClass,
                                               const SolutionSpace &paramSolutionSpace);

    static RealVector buildFullParameterDerivativeVector(std::size_t freeParameterIndex,
                                                         const boost::dynamic_bitset<> &freeParamMask,
                                                         const SolutionSpace &paramSolutionSpace);
};

/// \brief Base class for ParameterSpace adapter
/// \tparam IsStationary stationary or non-stationary
///
/// Metabolic stationary parameter spaces are different for
/// isotopically stationary or isotopically non-stationary models.
/// The first class has no pool size parameters, the second has
/// them. Thus, the dimension of the vector space of which the
/// parameter space is a subset of differs as well as generell
/// inequality constraint system.
template <bool IsStationary> class ParameterSpaceAdapter;

/// \brief Adapter for isotopically stationary metabolic model
template <> class ParameterSpaceAdapter<true> : public ParameterSpaceAdapterBase {
  private:
    boost::dynamic_bitset<> freeNetFluxMask_;
    boost::dynamic_bitset<> freeExchangeFluxMask_;

  public:
    /// \brief Create adapter for stationary metabolic parameter space.
    /// \param parameterSpace Metabolic model information
    /// \param constraintViolationTolerance Absolute tolerance of inequality constraint violation
    explicit ParameterSpaceAdapter(ParameterSpace &&parameterSpace, Real constraintViolationTolerance = 0.);

    /// \return number of free stationary metabolic parameter
    Index getNumFreeParameters() const;

    /// \return number of stationary metabolic parameters
    Index getNumParameters() const;

    /// \return names of free stationary parameters
    std::vector<std::string> getFreeParameterNames() const;

    /// \return names of all stationary parameters
    std::vector<std::string> getParameterNames() const;

    /// \return inequality constraints of free stationary metabolic parameters
    InequalitySystem getInequalitySystem() const;

    /// \brief Check if free parameters fulfill inequality constraints.
    /// \param freeParameters free parameter space vector
    /// \return fulfilled or not
    bool contains(const RealVector &freeParameters) const;

    /// \brief Compute all parameters from a vector of free parameters.
    /// \param freeParameters free parameter space vector
    /// \return vector of stationary metabolic parameters
    RealVector computeParameters(const RealVector &freeParameters) const;

    /// \brief Compute derivatives of all parameters with respect to a free parameter.
    /// \param freeParameterIndex index of free parameter to derive for
    /// \return vector of stationary metabolic parameter derivatives
    RealVector computeParameterDerivatives(Index freeParameterIndex) const;

    /// Calculates \f$\mathbf{S} \cdot \mathbf{\theta_{net}}$\f where \f$\mathbf{S}$\f
    /// is the stoichiometric matrix and \f$\mathbf{\theta}_{net}$\f the net
    /// flux parameters. The produc is expected to be \f$\mathbf{0}$\f. The \f$L^2$\f
    /// norm of the result vector is thus equal to the error of the stoichiometric equations.
    ///
    /// \brief Calculate L2 error of stoichiometric equations.
    /// \param parameters vector of all stationary metabolic parameters
    /// \return L2 error
    Real computeStoichiometryError(const RealVector &parameters) const;

    /// \brief Checks if L2 error of stoichiometric equation is small enough.
    /// \param parameters vector of all stationary metabolic parameters
    /// \param precision error tolerance (default: machine epsilon)
    /// \return L2 error small enough or not
    bool isFeasible(const RealVector &parameters, Real precision = std::numeric_limits<Real>::epsilon()) const;
};

using StationaryParameterSpace = ParameterSpaceAdapter<true>;

/// \brief Adapter for isotopically non-stationary metabolic model
template <> class ParameterSpaceAdapter<false> : public ParameterSpaceAdapterBase {
  private:
    boost::dynamic_bitset<> freeNetFluxMask_;
    boost::dynamic_bitset<> freeExchangeFluxMask_;
    boost::dynamic_bitset<> freePoolSizeMask_;

  public:
    /// \brief Create adapter for non-stationary metabolic parameter space.
    /// \param parameterSpace Metabolic model information
    /// \param constraintViolationTolerance Absolute tolerance of inequality constraint violation
    explicit ParameterSpaceAdapter(ParameterSpace &&parameterSpace, Real constraintViolationTolerance = 0.);

    /// \return number of free non-stationary metabolic parameters
    Index getNumFreeParameters() const;

    /// \return number of non-stationary metabolic parameters
    Index getNumParameters() const;

    /// \return names of free non-stationary metabolic parameters
    std::vector<std::string> getFreeParameterNames() const;

    /// \return names of all non-stationary metabolic parameters
    std::vector<std::string> getParameterNames() const;

    /// \return inequality constraints of free non-stationary metabolic parameters
    InequalitySystem getInequalitySystem() const;

    /// \brief Check if free parameters fulfill inequality constraints.
    /// \param freeParameters free parameter space vector
    /// \return fulfilled or not
    bool contains(const RealVector &freeParameters) const;

    /// \brief Calculate all parameters from a vector of free parameters.
    /// \param freeParameters free parameter space vector
    /// \return vector of non-stationary metabolic parameters
    RealVector computeParameters(const RealVector &freeParameters) const;

    /// \brief Compute derivatives of all parameters with respect to a free parameter.
    /// \param freeParameterIndex index of free parameter to derive for
    /// \return vector of non-stationary metabolic parameter derivatives
    RealVector computeParameterDerivatives(Index freeParameterIndex) const;

    /// Calculates \f$\mathbf{S} \cdot \mathbf{\theta_{net}}$\f where \f$\mathbf{S}$\f
    /// is the stoichiometric matrix and \f$\mathbf{\theta}_{net}$\f the net
    /// flux parameters. The produc is expected to be \f$\mathbf{0}$\f. The \f$L^2$\f
    /// norm of the result vector is thus equal to the error of the stoichiometric equations.
    ///
    /// \brief Calculate L2 error of stoichiometric equations.
    /// \param parameters vector of all non-stationary metabolic parameters
    /// \return L2 error
    Real computeStoichiometryError(const RealVector &parameters) const;

    /// \brief Checks if L2 error of stoichiometric equation is small enough.
    /// \param parameters vector of all non-stationary metabolic parameters
    /// \param precision error tolerance (default: machine epsilon)
    /// \return L2 error small enough or not
    bool isFeasible(const RealVector &parameters, Real precision = std::numeric_limits<Real>::epsilon()) const;
};

using NonStationaryParameterSpace = ParameterSpaceAdapter<false>;

} // namespace x3cflux

#endif // X3CFLUX_SRC_MAIN_PARAMETER_PARAMETERSPACEADAPTER_H