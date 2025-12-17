#ifndef X3CFLUX_SRC_MATH_LESSOLVER_H
#define X3CFLUX_SRC_MATH_LESSOLVER_H

#include "MathError.h"
#include "NumericTypes.h"
#include <util/Logging.h>

namespace x3cflux {

/// \brief Linear equation system with an optional initial guess
/// \tparam MatrixType_ Eigen3 matrix
/// \tparam RhsType_ Eigen3 vector or matrix
template <typename MatrixType_, typename RhsType_> class LinearEquationSystem {
  public:
    using MatrixType = MatrixType_;
    using RhsType = RhsType_;

  private:
    MatrixType matrix_;
    RhsType rhs_;
    RhsType initialGuess_;

  public:
    /// Creates an linear equation system from matrix and rhs.
    /// \param matrix system matrix
    /// \param rhs system right hand side
    /// \param initialGuess initially guessed solution value (default zero)
    LinearEquationSystem(MatrixType matrix, RhsType rhs, RhsType initialGuess = RhsType());

    /// \return number of equations (rows).
    Index getNumEquations() const;

    /// \return number of unknowns (columns).
    Index getNumUnknowns() const;

    /// \return number of right hand sides (if RhsType is matrix valued)
    Index getNumRhs() const;

    /// \return matrix of the linear equation system
    const MatrixType &getMatrix() const;

    /// \return right hand side of the linear equation system
    const RhsType &getRhs() const;

    /// \return initially guessed solution value (e.g. for iterative solvers)
    const RhsType &getInitialGuess() const;
};

/// \brief Base for a linear equation system solver
/// \tparam MatrixType_ Eigen3 matrix
/// \tparam RhsType_ Eigen3 vector or matrix
template <typename MatrixType_, typename RhsType_> class LESSolver {
  public:
    using MatrixType = MatrixType_;
    using RhsType = RhsType_;
    using Scalar = typename MatrixType::Scalar;
    using SolutionType = RhsType;

  private:
    Real tolerance_;

  public:
    /// \brief Creates linear equation solver.
    /// \param tolerance error tolerance
    explicit LESSolver(Real tolerance = 1e-9);

    virtual ~LESSolver();

    /// Solves a given linear equation system.
    /// \return solution vector or matrix
    inline virtual SolutionType solve(const LinearEquationSystem<MatrixType, RhsType> &) const = 0;

    /// \return error tolerance
    Real getTolerance() const;

    /// \param tolerance error tolerance
    void setTolerance(Real tolerance);

    /// \return deep copy of solver
    virtual std::unique_ptr<LESSolver<MatrixType, RhsType>> copy() const = 0;
};

/// \brief LU solver for sparse and dense linear equation systems
/// \tparam MatrixType_ Eigen3 matrix
/// \tparam RhsType_ Eigen3 vector or matrix
template <typename MatrixType_, typename RhsType_> class LUSolver : public LESSolver<MatrixType_, RhsType_> {
  public:
    using Base = LESSolver<MatrixType_, RhsType_>;
    using typename Base::MatrixType;
    using typename Base::RhsType;
    using typename Base::Scalar;
    using typename Base::SolutionType;
    typedef std::conditional_t<std::is_same<MatrixType, Matrix<Scalar>>::value, Eigen::PartialPivLU<Matrix<Scalar>>,
                               Eigen::SparseLU<SparseMatrix<Scalar>>>
        Method;

    explicit LUSolver(Real tolerance = 1e-9);

    ~LUSolver() override;

    auto solve(const LinearEquationSystem<MatrixType, RhsType> &linearEquationSystem) const -> SolutionType override;

    auto copy() const -> std::unique_ptr<LESSolver<MatrixType, RhsType>> override;

  private:
    static bool check_decomposition(const Eigen::PartialPivLU<Matrix<Scalar>> &decomposition);

    static bool check_decomposition(const Eigen::SparseLU<SparseMatrix<Scalar>> &decomposition);
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "LESSolver.tpp"
#endif

#endif // X3CFLUX_SRC_MATH_LESSOLVER_H
