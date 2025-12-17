#ifndef X3CFLUX_SRC_MATH_IVPSOLVER_H
#define X3CFLUX_SRC_MATH_IVPSOLVER_H

#include "CubicHermiteSpline.h"
#include "IVPBase.h"
#include "NumericTypes.h"

namespace x3cflux {

/// \brief Base for initial value problem solvers
/// \tparam StateType Eigen3 matrix or vector
template <typename StateType> class IVPSolver {
  public:
    using State = StateType;
    using Solution = CubicHermiteSpline<State>;
    using ProblemBase = IVPBase<State>;

  private:
    Real relativeTolerance_, absoluteTolerance_;
    std::size_t numMaxSteps_;

  public:
    /// Creates initial value problem solver.
    /// \param relativeTolerance relative local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit IVPSolver(Real relativeTolerance, Real absoluteTolerance, std::size_t numMaxSteps);

    virtual ~IVPSolver();

    /// Solves initial value problem.
    /// \param problem initial value problem to solve
    /// \return interpolated solution and derivative
    inline virtual Solution solve(const ProblemBase &problem) const = 0;

    /// \return relative local error tolerance
    Real getRelativeTolerance() const;

    /// \return absolute local error tolerance
    Real getAbsoluteTolerance() const;

    /// \return maximum number of steps allowed
    std::size_t getNumMaxSteps() const;

    /// \param relativeTolerance local error tolerance
    void setRelativeTolerance(Real relativeTolerance);

    /// \param relativeTolerance local error tolerance
    void setAbsoluteTolerance(Real absoluteTolerance);

    /// \param maximum number of steps allowed
    void setNumMaxSteps(std::size_t numMaxSteps);

    /// \return deep copy of solver
    virtual std::unique_ptr<IVPSolver<State>> copy() const = 0;
};

/// \brief Base for linear initial value problem solvers
/// \tparam StateType Eigen3 matrix or vector
/// \tparam MatrixType Eigen3 matrix
template <typename StateType, typename MatrixType> class LinearIVPSolver {
  public:
    using State = StateType;
    using Matrix = MatrixType;
    using Solution = CubicHermiteSpline<State>;
    using ProblemBase = LinearIVPBase<State, Matrix>;

  private:
    Real relativeTolerance_, absoluteTolerance_;
    std::size_t numMaxSteps_;

  public:
    /// Creates solver for linear initial value problems.
    /// \param relativeTolerance relative local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit LinearIVPSolver(Real relativeTolerance, Real absoluteTolerance, std::size_t numMaxSteps);

    virtual ~LinearIVPSolver();

    /// Solves linear initial value problem.
    /// \param problem linear initial value problem to solve
    /// \return interpolated solution and derivative
    inline virtual Solution solve(const ProblemBase &problem) const = 0;

    /// \return relative local error tolerance
    Real getRelativeTolerance() const;

    /// \return absolute local error tolerance
    Real getAbsoluteTolerance() const;

    /// \return maximum number of steps allowed
    std::size_t getNumMaxSteps() const;

    /// \param relativeTolerance local error tolerance
    void setRelativeTolerance(Real relativeTolerance);

    /// \param relativeTolerance local error tolerance
    void setAbsoluteTolerance(Real absoluteTolerance);

    /// \param maximum number of steps allowed
    void setNumMaxSteps(std::size_t numMaxSteps);

    /// \return deep copy of solver
    virtual std::unique_ptr<LinearIVPSolver<State, Matrix>> copy() const = 0;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "IVPSolver.tpp"
#endif

#endif // X3CFLUX_SRC_MATH_IVPSOLVER_H
