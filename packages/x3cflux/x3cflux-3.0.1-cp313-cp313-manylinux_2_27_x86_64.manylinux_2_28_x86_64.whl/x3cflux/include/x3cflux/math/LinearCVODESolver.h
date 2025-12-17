#ifndef X3CFLUX_LINEARCVODESOLVER_H
#define X3CFLUX_LINEARCVODESOLVER_H

#include <cvode/cvode.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_nonlinearsolver.h>
#include <sundials/sundials_types.h>
#include <sunlinsol/sunlinsol_dense.h>
#include <sunmatrix/sunmatrix_sparse.h>
#include <sunnonlinsol/sunnonlinsol_newton.h>

#include "IVPSolver.h"
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename RhsState> class LinearCVODESolver : public LinearIVPSolver<RhsState, RealSparseMatrix> {
    using typename LinearIVPSolver<RhsState, RealSparseMatrix>::ProblemBase;
    using typename LinearIVPSolver<RhsState, RealSparseMatrix>::Solution;
    using typename LinearIVPSolver<RhsState, RealSparseMatrix>::State;

    struct UserData {
      public:
        const ProblemBase &problem;

      public:
        explicit UserData(const ProblemBase &problem);
    };

  public:
    std::size_t numMaxStepAttempts_;

  public:
    /// Create an IVP solver based on SUNDIALS CVODE (BDF method with step size ond order control).
    /// \param numMaxStepAttempts maximum number of unaccepted steps
    /// \param relativeTolerance absolute local error tolerance
    /// \param absoluteTolerance absolute local error tolerance
    /// \param numMaxSteps maximum number of steps allowed
    explicit LinearCVODESolver(std::size_t numMaxStepAttempts = 100, Real relativeTolerance = 1e-6,
                               Real absoluteTolerance = 1e-9, std::size_t numMaxSteps = 100'000);

    Solution solve(const ProblemBase &problem) const override;

    /// \return maximum number of unaccepted steps
    std::size_t getNumMaxStepAttempts() const;

    /// \param numMaxStepAttempts maximum number of unaccepted steps
    void setNumMaxStepAttempts(std::size_t numMaxStepAttempts);

    std::unique_ptr<LinearIVPSolver<State, RealSparseMatrix>> copy() const override;

  private:
    static SUNNonlinearSolver createNonlinearSolver(SUNContext context);

    static void convertToSerial(const RealVector &state, N_Vector copyState);

    static void convertToSerial(const RealMatrix &state, N_Vector copyState);

    static void convertToEigen(N_Vector state, RealVector &copyState);

    static void convertToEigen(N_Vector state, RealMatrix &copyState);

    static State initializeEigen(Index rows, Index cols);

    static int evaluateGenericRhsFunction(realtype time, N_Vector state, N_Vector stateDerivative, void *userData);
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "LinearCVODESolver.tpp"
#endif

#endif // X3CFLUX_LINEARCVODESOLVER_H
