#ifndef X3CFLUX_SYSTEMBUILDER_H
#define X3CFLUX_SYSTEMBUILDER_H

#include "LabelingSystem.h"
#include "ParameterAccessor.h"
#include <math/AdaptiveIVPSolver.h>
#include <math/LinearCVODESolver.h>

namespace x3cflux {

/// \brief Base class for labeling system builders
///
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
///
/// Derived classes have to implement the function build and buildDerivative,
/// which are supposed to create labeling systems at its derivative systems
/// from a given parameter vector.
template <typename Method, bool Stationary, bool Multi = false> class SystemBuilder {
  public:
    using System = LabelingSystem<Method, Stationary, Multi>;
    using Solver = typename System::Solver;
    using SystemState = typename System::SystemState;
    using Traits = typename System::Traits;
    using Solution = typename System::Solution;

    typedef std::conditional_t<Stationary, LUSolver<RealSparseMatrix, SystemState>,
                               std::conditional_t<Traits::TYPE == SystemType::CASCADED, LinearCVODESolver<SystemState>,
                                                  DOPRI54Solver<SystemState>>>
        StandardSolver;

  private:
    Index numReactions_, numMetabolites_;
    std::unique_ptr<Solver> solver_, derivativeSolver_;

  public:
    /// Create system builder
    /// \param numReactions number of metabolic reactions
    /// \param numMetabolites number of metabolites
    SystemBuilder(Index numReactions, Index numMetabolites);

    explicit SystemBuilder(Index numReactions);

    virtual ~SystemBuilder();

    /// \return labeling system solver
    auto getSolver() const -> const Solver &;

    /// \return labeling system solver
    auto getSolver() -> Solver &;

    auto getDerivativeSolver() const -> const Solver &;

    auto getDerivativeSolver() -> Solver &;

    /// \param solver labeling system solver
    void setSolver(const Solver &solver);

    void setDerivativeSolver(const Solver &solver);

    /// \param parameters all metabolic parameters (netto and exchange)
    /// \return (forward, backward) parameter accessor
    ParameterAccessor getParameterAccessor(const RealVector &parameters) const;

    /// \param parameters all metabolic parameters (netto and exchange)
    /// \param parameterDerivatives partial derivatives of all metabolic parameters
    /// \return (forward, backward) derivative parameter accessor
    DerivativeParameterAccessor getDerivativeParameterAccessor(const RealVector &parameters,
                                                               const RealVector &parameterDerivatives) const;

    /// Build labeling system
    /// \param parameters all metabolic parameters
    /// \return labeling system
    virtual std::unique_ptr<System> build(const RealVector &parameters) const = 0;

    /// Build labeling system derivative
    /// \param parameters all metabolic parameters
    /// \param parameterDerivatives partial derivatives of all metabolic parameters
    /// \param baseSystemSolution solution of base labeling system
    /// \return labeling system derivative
    virtual std::unique_ptr<System> buildDerivative(const RealVector &parameters,
                                                    const RealVector &parameterDerivatives,
                                                    const Solution &baseSystemSolution) const = 0;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "SystemBuilder.tpp"
#endif

#endif // X3CFLUX_SYSTEMBUILDER_H
