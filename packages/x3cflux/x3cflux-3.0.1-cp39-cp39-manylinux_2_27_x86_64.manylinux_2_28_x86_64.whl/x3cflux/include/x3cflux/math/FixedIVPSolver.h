#ifndef X3CFLUX_FIXEDIVPSOLVER_H
#define X3CFLUX_FIXEDIVPSOLVER_H

#include "EulerStepProposal.h"
#include "IVPBase.h"

namespace x3cflux {

/// \brief Fixed step size IVP solver
/// \tparam IVPSolverBaseType type of the IVP (e.g. IVPBase or LinearIVPBase)
/// \tparam StepProposal method with advance proposal
///
/// The fixed IVP solver can be set up with different proposal or stepping methods
/// that calculate the advance of the iterative solution procedure. The proposals must
/// match the IVP base type.
template <typename IVPSolverBaseType, typename StepProposal> class FixedIVPSolver : public IVPSolverBaseType {
  public:
    using typename IVPSolverBaseType::ProblemBase;
    using typename IVPSolverBaseType::Solution;
    using typename IVPSolverBaseType::State;

    /// Accuracy order of method (local error is in \f$\mathcal{O}(h^{ADVANCE\_ORDER})\f$)
    static constexpr Index ADVANCE_ORDER = StepProposal::ADVANCE_ORDER;

  public:
    Real stepSize_;

  public:
    /// \brief Create fixed step size IVP solver.
    /// \param stepSize iteration step size
    explicit FixedIVPSolver(Real stepSize = 1e-3);

    /// \return iteration step size
    Real getStepSize() const;

    /// \param stepSize iteration step size
    void setStepSize(Real stepSize);

    Solution solve(const ProblemBase &problem) const override;

    std::unique_ptr<IVPSolverBaseType> copy() const override;
};

/// \brief Fixed IVP solver using the explicit Euler method
/// \tparam StateType Eigen3 vector or matrix
template <typename StateType>
using ExplicitEulerSolver = FixedIVPSolver<IVPSolver<StateType>, ExplicitEulerStepProposal<StateType>>;

/// \brief Fixed solver for linear IVP's using the implicit Euler method
/// \tparam StateType Eigen3 vector or matrix
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType>
using LinearImplicitEulerSolver =
    FixedIVPSolver<LinearIVPSolver<StateType, MatrixType>, LinearImplicitEulerStepProposal<StateType, MatrixType>>;

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "FixedIVPSolver.tpp"
#endif

#endif // X3CFLUX_FIXEDIVPSOLVER_H
