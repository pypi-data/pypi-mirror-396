#ifndef X3CFLUX_CASCADESYSTEM_H
#define X3CFLUX_CASCADESYSTEM_H

#include "LabelingSystem.h"
#include "NonLinearElement.h"
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>

#include <utility>

namespace x3cflux {

template <typename Method, bool Stationary, bool Multi = false> class CascadeLevelSystem;

/// \brief Level system of IST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelSystem<Method, true, Multi>
    : public LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType> {
  public:
    using Base = LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType>;
    using typename Base::RhsType;

    using Solution = RhsType;
    using NonLinearElement = NumericNonLinearElement<Method, true, Multi>;
    using SystemCondition = RhsType;
    using StateVarOps = StateVariableOperations<Method, Multi>;

  private:
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<RhsType> &prevLevelSolutions_;

  public:
    /// Create level system of IST cascade
    /// \param jacobiMatrix linear part
    /// \param nonLinearities non-linear part
    /// \param initialGuess initial labeling state
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelSystem(const RealSparseMatrix &jacobiMatrix, std::vector<NonLinearElement> nonLinearities,
                       const RhsType &initialGuess, const std::vector<Solution> &prevLevelSolutions);

  private:
    static auto createRhs(Index numRows, Index numCols, const std::vector<NonLinearElement> &nonLinearities,
                          const std::vector<Solution> &prevLevelSolutions) -> RhsType;
};

/// \brief Level system of INST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelSystem<Method, false, Multi>
    : public LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix> {
  public:
    using Base = LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix>;
    using typename Base::State;
    using Solution = typename IVPSolver<State>::Solution;

    using NonLinearElement = NumericNonLinearElement<Method, false, Multi>;
    using SystemCondition = std::pair<Real, State>;
    using StateVarOps = StateVariableOperations<Method, Multi>;

  private:
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<Solution> &prevLevelSolutions_;

  public:
    /// Create level system of INST cascade
    /// \param jacobiMatrix linear part
    /// \param nonLinearities non-linear part
    /// \param condition initial labeling state
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelSystem(const RealSparseMatrix &jacobiMatrix, std::vector<NonLinearElement> nonLinearities,
                       const SystemCondition &condition, const std::vector<Solution> &prevLevelSolutions);

    State evaluateInhomogeneity(Real time) const override;
};

template <typename Method, bool Stationary, bool Multi = false> class CascadeLevelDerivativeSystem;

/// \brief Level system of IST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelDerivativeSystem<Method, true, Multi>
    : public LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType> {
  public:
    using Base = LinearEquationSystem<RealSparseMatrix, typename SystemTraits<Method, Multi>::SystemStateType>;
    using typename Base::RhsType;

    using Solution = RhsType;
    using NonLinearElement = NumericNonLinearElementDerivative<Method, true, Multi>;
    using SystemCondition = RhsType;
    using StateVarOps = StateVariableOperations<Method, Multi>;

  private:
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<RhsType> &prevLevelSolutions_;

  public:
    /// Create level system of derivative IST cascade
    /// \param jacobiMatrix linear part
    /// \param jacobiMatrixDerivative partial derivative of linear part
    /// \param nonLinearities non-linear part
    /// \param initialGuess initial labeling state
    /// \param nonDerivSolutions solution of base system
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelDerivativeSystem(const RealSparseMatrix &jacobiMatrix, const RealSparseMatrix &jacobiMatrixDerivative,
                                 std::vector<NonLinearElement> nonLinearities, const RhsType &initialGuess,
                                 const std::vector<Solution> &nonDerivSolutions,
                                 const std::vector<Solution> &prevLevelSolutions);

  private:
    static auto createRhs(Index numRows, Index numCols, const std::vector<NonLinearElement> &nonLinearities,
                          const std::vector<Solution> &nonDerivSolutions,
                          const std::vector<Solution> &prevLevelSolutions) -> RhsType;
};

/// \brief Level system of derivative INST cascade
/// \tparam Method labeling state simulation method
/// \tparam Multi multiple or single experiment
template <typename Method, bool Multi>
class CascadeLevelDerivativeSystem<Method, false, Multi>
    : public LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix> {
  public:
    using Base = LinearIVPBase<typename SystemTraits<Method, Multi>::SystemStateType, RealSparseMatrix>;
    using typename Base::State;
    using Solution = typename IVPSolver<State>::Solution;

    using NonLinearElement = NumericNonLinearElementDerivative<Method, false, Multi>;
    using SystemCondition = std::pair<Real, State>;
    using StateVarOps = StateVariableOperations<Method, Multi>;

  private:
    RealSparseMatrix jacobiMatrixDerivative_;
    std::vector<NonLinearElement> nonLinearities_;
    const std::vector<Solution> &nonDerivSolutions_;
    const std::vector<Solution> &prevLevelSolutions_;

  public:
    /// Create level system of derivative INST cascade
    /// \param jacobiMatrix linear part
    /// \param jacobiMatrixDerivative partial derivative of linear part
    /// \param nonLinearities non-linear part
    /// \param condition initial labeling state
    /// \param nonDerivSolutions solution of base system
    /// \param prevLevelSolutions solutions of previous cascade levels
    CascadeLevelDerivativeSystem(const RealSparseMatrix &jacobiMatrix, const RealSparseMatrix &jacobiMatrixDerivative,
                                 std::vector<NonLinearElement> nonLinearities, const SystemCondition &condition,
                                 const std::vector<Solution> &nonDerivSolutions,
                                 const std::vector<Solution> &prevLevelSolutions);

    auto evaluateInhomogeneity(Real time) const -> State override;
};

template <typename SystemStateType>
SystemStateType reduceSystemState(const SystemStateType &state, const std::vector<Index> &nonZeroIndices);

template <bool IsDerivative, typename NonLinearElement, typename Condition>
auto reduceSystem(const RealSparseMatrix &linearCoefficients, const std::vector<NonLinearElement> &nonLinearElements,
                  const Condition &condition, const std::vector<Index> &nonZeroIndices);

template <typename SystemStateType>
SystemStateType expandSystemState(const SystemStateType &reducedState, const std::vector<Index> &zeroIndices);
;

template <typename SolutionType>
SolutionType expandSystem(const SolutionType &reducedSolution, const std::vector<Index> &zeroIndices);

/// \brief Cascade labeling system
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<SystemTraits<Method, Multi>::TYPE == SystemType::CASCADED, bool> = true>
class CascadeSystem : public LabelingSystem<Method, Stationary, Multi> {
  public:
    using Base = LabelingSystem<Method, Stationary, Multi>;
    using typename Base::Fraction;
    using typename Base::Solution;
    using typename Base::Solver;
    using typename Base::SystemState;

    using LevelSystem = CascadeLevelSystem<Method, Stationary, Multi>;
    using SystemCondition = typename LevelSystem::SystemCondition;

    using NonLinearElement = NumericNonLinearElement<Method, Stationary, Multi>;

  private:
    std::size_t numLevels_;
    std::vector<RealSparseMatrix> levelLinearCoefficients_;
    std::vector<std::vector<NonLinearElement>> levelNonLinearities_;
    std::vector<SystemCondition> levelConditions_;
    mutable Solution solutionCache_;

  public:
    /// Create cascade labeling system
    /// \param levelLinearCoefficients linear labeling interaction terms
    /// \param levelNonLinearities non-linear labeling interaction terms
    /// \param levelConditions initial labeling states
    /// \param solver numerical solver
    CascadeSystem(const std::vector<RealSparseMatrix> &levelLinearCoefficients,
                  std::vector<std::vector<NonLinearElement>> levelNonLinearities,
                  std::vector<SystemCondition> levelConditions, const Solver &solver);

    void solveLevelSystem(std::size_t levelIndex) const;

    auto getLevelSystem(std::size_t level) const -> LevelSystem;

    /// Solve this cascade system
    /// \return solution of cascade system
    auto solve() const -> Solution override;
};

/// \brief Derivative of cascade labeling system
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<SystemTraits<Method, Multi>::TYPE == SystemType::CASCADED, bool> = true>
class CascadeDerivativeSystem : public LabelingSystem<Method, Stationary, Multi> {
  public:
    using Base = LabelingSystem<Method, Stationary, Multi>;
    using typename Base::Fraction;
    using typename Base::Solution;
    using typename Base::Solver;
    using typename Base::SystemState;

    using LevelSystem = CascadeLevelDerivativeSystem<Method, Stationary, Multi>;
    using SystemCondition = typename LevelSystem::SystemCondition;

    using NonLinearElement = NumericNonLinearElementDerivative<Method, Stationary, Multi>;

  private:
    std::size_t numLevels_;
    std::vector<RealSparseMatrix> levelLinearCoefficients_;
    std::vector<RealSparseMatrix> levelLinearDerivativeCoefficients_;
    std::vector<std::vector<NonLinearElement>> levelNonLinearities_;
    std::vector<SystemCondition> levelConditions_;
    const Solution &nonDerivSolution_;
    mutable Solution solutionCache_;

  public:
    /// Create derivative of cascade labeling system
    /// \param levelLinearCoefficients linear labeling interaction terms
    /// \param levelLinearDerivativeCoefficients partial derivative of linear interaction terms
    /// \param levelNonLinearities non-linear labeling interaction terms
    /// \param levelConditions initial labeling states
    /// \param nonDerivSolution solution of base system
    /// \param solver numerical solver
    CascadeDerivativeSystem(const std::vector<RealSparseMatrix> &levelLinearCoefficients,
                            std::vector<RealSparseMatrix> levelLinearDerivativeCoefficients,
                            std::vector<std::vector<NonLinearElement>> levelNonLinearities,
                            std::vector<SystemCondition> levelConditions, const Solution &nonDerivSolution,
                            const Solver &solver);

    void solveLevelSystem(std::size_t levelIndex) const;

    auto getLevelSystem(std::size_t level) const -> LevelSystem;

    /// Solve this cascade system
    /// \return solution of cascade system derivative
    auto solve() const -> Solution override;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "CascadeSystem.tpp"
#endif

#endif // X3CFLUX_CASCADESYSTEM_H
