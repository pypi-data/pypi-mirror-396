#ifndef X3CFLUX_PARAMETERACCESSOR_H
#define X3CFLUX_PARAMETERACCESSOR_H
#include "NumericTypes.h"
#include "util/Logging.h"

namespace x3cflux {

/// \brief Accessor that maps (net, xch) to (fwd, bwd) parameters
class ParameterAccessor {
  private:
    Index numReactions_;
    Index numMetabolites_;
    const RealVector &parameters_;

  public:
    /// Create parameter accessor
    /// \param numReactions number of metabolic reactions
    /// \param numMetabolites number of metabolites
    /// \param parameters vector of parameter values
    ParameterAccessor(Index numReactions, Index numMetabolites, const RealVector &parameters);

    /// \return number of metabolic reactions
    Index getNumReactions() const;

    /// \return number of metabolites
    Index getNumMetabolites() const;

    /// \return vector of parameter values
    const RealVector &getParameters() const;

    /// \param reactionIndex index of the reaction
    /// \param forward forward or backward
    /// \return flux value
    Real getFlux(Index reactionIndex, bool forward) const;

    /// \param metaboliteIndex index of metabolites
    /// \return pool size of metabolite
    Real getPoolSize(Index metaboliteIndex) const;
};

/// \brief Accessor that maps (net, xch) to (fwd, bwd) parameters including partial derivatives
class DerivativeParameterAccessor : public ParameterAccessor {
  private:
    const RealVector &parameterDerivatives_;

  public:
    /// Create derivative parameter accessor
    /// \param numReactions number of metabolic reactions
    /// \param numMetabolites number of metabolites
    /// \param parameters parameter values
    /// \param parameterDerivatives parameter partial derivative values
    DerivativeParameterAccessor(Index numReactions, Index numMetabolites, const RealVector &parameters,
                                const RealVector &parameterDerivatives);

    /// \param reactionIndex index of reaction
    /// \param forward forward or backward
    /// \return partial flux derivative value
    Real getFluxDerivative(Index reactionIndex, bool forward) const;

    /// \param metaboliteIndex index of metabolite
    /// \return partial pool size derivative value
    Real getPoolSizeDerivative(Index metaboliteIndex) const;
};

} // namespace x3cflux

#endif // X3CFLUX_PARAMETERACCESSOR_H
