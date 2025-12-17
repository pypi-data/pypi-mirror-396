#ifndef X3CFLUX_INITIALVALUEPROBLEMBASE_H
#define X3CFLUX_INITIALVALUEPROBLEMBASE_H

#include "NumericTypes.h"

#include <util/Logging.h>

namespace x3cflux {

/// \brief Base class for initial value problems
/// \tparam StateType Eigen3 matrix or vector
template <typename StateType> class IVPBase {
  public:
    using State = StateType;

  private:
    Real startTime_;
    Real endTime_;
    State initialValue_;

  public:
    /// Creates initial value problem.
    /// \param startTime initial time point
    /// \param endTime end time point
    /// \param initialValue initial state
    IVPBase(Real startTime, Real endTime, State initialValue);

    virtual ~IVPBase();

    /// \return size of the state vector
    Index getSize() const;

    /// \return number of states to solved simultaneously
    Index getNumStates() const;

    /// \return initial time point
    const Real &getStartTime() const;

    /// \return end time point
    Real getEndTime() const;

    /// \return initial value of the initial value problem
    State getInitialValue() const;

    /// Evaluates the right hand side of the ODE.
    /// \param time point in time
    /// \param state solution function value
    /// \return derivative of the solution function
    virtual State operator()(Real time, const State &state) const = 0;
};

/// \brief Base class for linear initial value problems.
/// \tparam StateType Eigen3 matrix or vector
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType> class LinearIVPBase : public IVPBase<StateType> {
  public:
    using typename IVPBase<StateType>::State;
    using Matrix = MatrixType;

  private:
    Matrix jacobiMatrix_;

  public:
    /// Creates initial value problem.
    /// \param startTime initial time point
    /// \param endTime end time point
    /// \param initialValue initial state
    /// \param jacobiMatrix jacobi matrix of the initial value problem
    LinearIVPBase(Real startTime, Real endTime, State initialValue, Matrix jacobiMatrix);

    /// \return jacobi matrix of the initial value problem
    const Matrix &getJacobiMatrix() const;

    /// Evaluates the inhomogeneity of the linear initial value problem.
    /// \param time point in time
    /// \return inhomogenity value at time point
    virtual State evaluateInhomogeneity(Real time) const = 0;

    /// Evaluates the right hand side of the linear ODE.
    /// \param time point in time
    /// \param state solution function value
    /// \return derivative of the solution function
    State operator()(Real time, const State &state) const override;
};
} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "IVPBase.tpp"
#endif

#endif // X3CFLUX_INITIALVALUEPROBLEMBASE_H
