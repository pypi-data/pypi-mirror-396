/// Robustification of the step size was derived from the CVODE 5.3.0 ODE solver package.
///
/// BSD 3-Clause License Copyright (c) 2002-2019, Lawrence Livermore National Security and Southern Methodist
/// University. All rights reserved. Redistribution and use in source and binary forms, with or without modification,
/// are permitted provided that the following conditions are met:
/// * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
/// disclaimer.
/// * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
/// following disclaimer
///   in the documentation and/or other materials provided with the distribution.
/// * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
/// products derived
///   from this software without specific prior written permission.
///
/// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
/// IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
/// FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
/// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
/// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
/// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
/// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
/// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#ifndef X3CFLUX_ADAPTIVEIVPSOLVER_H
#define X3CFLUX_ADAPTIVEIVPSOLVER_H

#include "IVPSolver.h"
#include "RKStepProposal.h"

namespace x3cflux {

/// \brief Adaptive IVP solver
/// \tparam IVPSolverBaseType type of the IVP (e.g. IVPBase or LinearIVPBase)
/// \tparam StepProposal method with advance and correction proposal
///
/// The adaptive IVP solver can be set up with different proposal or stepping methods
/// that calculate the advance of the iterative solution procedure. The proposals must
/// match the IVP base type and must yield a second lower order proposal for local error
/// control.
template <typename IVPSolverBaseType, typename StepProposal> class AdaptiveIVPSolver : public IVPSolverBaseType {
  public:
    using typename IVPSolverBaseType::ProblemBase;
    using typename IVPSolverBaseType::Solution;
    using typename IVPSolverBaseType::State;

    /// Accuracy order of advancing method (local error is in \f$\mathcal{O}(h^{ADVANCE\_ORDER})\f$)
    static constexpr std::size_t ADVANCE_ORDER = StepProposal::ADVANCE_ORDER;

    /// Accuracy order of correction method (local error is in \f$\mathcal{O}(h^{CORRECTION\_ORDER})\f$)
    static constexpr std::size_t CORRECTION_ORDER = StepProposal::CORRECTION_ORDER;

  public:
    std::size_t numMaxStepAttempts_;

  public:
    /// Create adaptive IVP solver.
    /// \param numMaxStepAttempts maximum number of unaccepted steps
    /// \param relativeTolerance absolute local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit AdaptiveIVPSolver(std::size_t numMaxStepAttempts = 100,
                               Real relativeTolerance = std::numeric_limits<Real>::epsilon(),
                               Real absoluteTolerance = 1e-6, std::size_t numMaxSteps = 100'000);
    Solution solve(const ProblemBase &problem) const override;

    /// \return maximum number of unaccepted steps
    std::size_t getNumMaxStepAttempts() const;

    /// \param numMaxStepAttempts maximum number of unaccepted steps
    void setNumMaxStepAttempts(std::size_t numMaxStepAttempts);

    std::unique_ptr<IVPSolverBaseType> copy() const override;

  private:
    Real getInitialStepSize(const IVPBase<State> &problem, Real tolerance) const;

    static Real estimateLocalError(const RealVector &advState, const RealVector &corrState);

    static Real estimateLocalError(const RealMatrix &advState, const RealMatrix &corrState);

    Real adjustStepSize(Real localErrorEstim, Real stepSize, Real tolerance) const;
};

/// \brief Adaptive IVP solver using the DOPRI54 method
/// \tparam StateType Eigen3 vector or matrix
template <typename StateType>
using DOPRI54Solver = AdaptiveIVPSolver<IVPSolver<StateType>, ERKFStepProposal<StateType, DOPRI54Scheme>>;

/// \brief Adaptive solver for linear IVP's using the SDIRK43 method
/// \tparam StateType Eigen3 vector or matrix
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType>
using LinearSDIRK43Solver = AdaptiveIVPSolver<LinearIVPSolver<StateType, MatrixType>,
                                              LinearSDIRKStepProposal<StateType, MatrixType, SDIRK43Scheme>>;

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "AdaptiveIVPSolver.tpp"
#endif

#endif // X3CFLUX_ADAPTIVEIVPSOLVER_H