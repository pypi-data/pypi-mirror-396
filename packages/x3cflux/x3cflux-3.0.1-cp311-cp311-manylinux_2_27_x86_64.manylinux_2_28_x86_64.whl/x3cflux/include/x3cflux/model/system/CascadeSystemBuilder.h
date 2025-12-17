#ifndef X3CFLUX_CASCADESYSTEMBUILDER_H
#define X3CFLUX_CASCADESYSTEMBUILDER_H

#include "CascadeSystem.h"
#include "NaturalLabelingInitializer.h"
#include "SymbolicElementsBuilder.h"
#include "SymbolicLinearElement.h"
#include "SystemBuilder.h"
#include "SystemError.h"

#include <model/network/LabelingNetwork.h>

namespace x3cflux {

template <typename Method, bool Stationary> struct SymbolicSubstrateIntakeBuilder;

template <typename Method> struct SymbolicSubstrateIntakeBuilder<Method, true> {
  public:
    using StateVariable = StateVariableImpl<typename Method::StateType>;
    using State = typename StateVariable::StateType;

    using SingleNonLinearFunction = NonLinearity<Method, true, false>;
    using MultiNonLinearFunction = NonLinearity<Method, true, true>;

    static std::shared_ptr<SingleNonLinearFunction> buildSingleIntake(const std::shared_ptr<Substrate> &substrate,
                                                                      const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrate)) {
            auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
            return std::make_shared<ConstantSubstrateInput<Method, true, false>>(constSubstr, state);
        } else if (isInstanceOf<VariateSubstrate>(substrate)) {
            X3CFLUX_THROW(SystemError, "Variate substrate type cannot be used in "
                                       "stationary simulation");
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }

    static std::shared_ptr<MultiNonLinearFunction>
    buildMultiIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrates.front())) {
            std::vector<std::shared_ptr<ConstantSubstrate>> constSubstrates;
            for (const auto &substrate : substrates) {
                auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
                constSubstrates.push_back(constSubstr);
            }

            return std::make_shared<ConstantSubstrateInput<Method, true, true>>(constSubstrates, state);
        } else if (isInstanceOf<VariateSubstrate>(substrates.front())) {
            X3CFLUX_THROW(SystemError, "Variate substrate type cannot be used in "
                                       "stationary simulation");
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }
};

template <typename Method> struct SymbolicSubstrateIntakeBuilder<Method, false> {
  public:
    using StateVariable = StateVariableImpl<typename Method::StateType>;
    using State = typename StateVariable::StateType;

    using SingleNonLinearFunction = NonLinearity<Method, false, false>;
    using MultiNonLinearFunction = NonLinearity<Method, false, true>;

    static std::shared_ptr<SingleNonLinearFunction> buildSingleIntake(const std::shared_ptr<Substrate> &substrate,
                                                                      const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrate)) {
            auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
            return std::make_shared<ConstantSubstrateInput<Method, false, false>>(constSubstr, state);
        } else if (isInstanceOf<VariateSubstrate>(substrate)) {
            auto varSubstr = std::dynamic_pointer_cast<VariateSubstrate>(substrate);
            return std::make_shared<VariateSubstrateInput<Method, false>>(varSubstr, state);
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }

    static std::shared_ptr<MultiNonLinearFunction>
    buildMultiIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const State &state) {
        if (isInstanceOf<ConstantSubstrate>(substrates.front())) {
            std::vector<std::shared_ptr<ConstantSubstrate>> constSubstrates;
            for (const auto &substrate : substrates) {
                auto constSubstr = std::dynamic_pointer_cast<ConstantSubstrate>(substrate);
                constSubstrates.push_back(constSubstr);
            }

            return std::make_shared<ConstantSubstrateInput<Method, false, true>>(constSubstrates, state);
        } else if (isInstanceOf<VariateSubstrate>(substrates.front())) {
            std::vector<std::shared_ptr<VariateSubstrate>> varSubstrates;
            for (const auto &substrate : substrates) {
                auto varSubstr = std::dynamic_pointer_cast<VariateSubstrate>(substrate);
                varSubstrates.push_back(varSubstr);
            }

            return std::make_shared<VariateSubstrateInput<Method, true>>(varSubstrates, state);
        } else {
            X3CFLUX_THROW(SystemError, "Unknown substrate type supplied");
        }
    }
};

template <typename Network, bool Stationary, bool Multi> class SymbolicNonLinearityBuilder {
  public:
    using Method = typename Network::ModelingMethod;
    using Ordering = typename Network::Ordering;
    using StateVariable = StateVariableImpl<typename Method::StateType>;
    using State = typename StateVariable::StateType;

    using SymbSubstrateIntakeBuilder = SymbolicSubstrateIntakeBuilder<Method, Stationary>;
    using SingleNonLinearFunction = typename SymbSubstrateIntakeBuilder::SingleNonLinearFunction;
    using MultiNonLinearFunction = typename SymbSubstrateIntakeBuilder::MultiNonLinearFunction;
    using CascadeCondensation = Condensation<Method, Stationary, Multi>;

  private:
    const std::vector<Ordering> &orderings_;

  public:
    explicit SymbolicNonLinearityBuilder(const std::vector<Ordering> &orderings) : orderings_(orderings) {}

    std::shared_ptr<CascadeCondensation> buildCondensation(const std::vector<StateVariable> &educts) const {
        std::vector<std::size_t> levelIndices, systemIndices;
        for (const auto &educt : educts) {
            std::size_t level = educt.getState().count() - 1;
            levelIndices.push_back(level);
            systemIndices.push_back(orderings_[level].getSystemIndex(educt));
        }
        return std::make_shared<CascadeCondensation>(levelIndices, systemIndices);
    }

    std::shared_ptr<SingleNonLinearFunction>
    buildSubstrateIntake(const std::vector<std::shared_ptr<Substrate>> &substrates, const std::string &name,
                         const State &state) const {
        auto substrate = findSubstrate(substrates, name);

        // Continue if substrate does not exist
        if (not substrate) {
            return nullptr;
        }

        return SymbSubstrateIntakeBuilder::buildSingleIntake(substrate, state);
    }

    std::shared_ptr<MultiNonLinearFunction>
    buildSubstrateIntake(const std::vector<std::vector<std::shared_ptr<Substrate>>> &parSubstrates,
                         const std::string &name, const State &state) const {
        std::vector<std::shared_ptr<Substrate>> foundSubstrates;
        for (const auto &substrates : parSubstrates) {
            if (auto substrate = findSubstrate(substrates, name)) {
                foundSubstrates.push_back(substrate);
            }
        }

        // Leave out substrates that were not fed in the experiment
        if (foundSubstrates.empty()) {
            return nullptr;
        }

        // Some experiments left out the substrate - this is not supported yet
        if (foundSubstrates.size() != parSubstrates.size()) {
            X3CFLUX_THROW(SystemError, "Multi substrate intake missing");
        }

        // Substrates with different type is not supported
        checkSubstrateTypesEqual(foundSubstrates);

        return SymbSubstrateIntakeBuilder::buildMultiIntake(foundSubstrates, state);
    }

  private:
    std::shared_ptr<Substrate> findSubstrate(const std::vector<std::shared_ptr<Substrate>> &substrates,
                                             const std::string &name) const {
        auto substrIt = std::find_if(substrates.begin(), substrates.end(),
                                     [&](const std::shared_ptr<Substrate> &substrate) -> bool {
                                         return substrate->getMetaboliteName() == name;
                                     });

        if (substrIt != substrates.end()) {
            return *substrIt;
        }

        return nullptr;
    }

    static void checkSubstrateTypesEqual(const std::vector<std::shared_ptr<Substrate>> &substrates) {
        auto isConstant = [&](const std::shared_ptr<Substrate> &substrate) -> bool {
            return isInstanceOf<ConstantSubstrate>(substrate);
        };

        // Multi intake must have the same type - constant or time variate
        if (std::all_of(substrates.begin(), substrates.end(), isConstant) or
            std::none_of(substrates.begin(), substrates.end(), isConstant)) {
            return;
        }

        X3CFLUX_THROW(SystemError, "Multi substrate intake type varies between experiments");
    }
};

template <typename Method, bool Stationary, bool Multi = false,
          std::enable_if_t<SystemTraits<Method, Multi>::TYPE == SystemType::CASCADED, bool> = true>
class CascadeSystemBuilder : public SystemBuilder<Method, Stationary, Multi> {
  public:
    using Base = SystemBuilder<Method, Stationary, Multi>;
    using System = typename Base::System;
    using Solution = typename Base::Solution;
    using Fraction = typename System::Fraction;
    using SystemState = typename System::SystemState;

    using CascadeNetwork = LabelingNetwork<Method>;
    using ReducedCascadeNetwork = ReducedLabelingNetwork<Method>;
    using ProductSystem = CascadeSystem<Method, Stationary, Multi>;
    using SystemCondition = typename ProductSystem::SystemCondition;
    using ProductDerivativeSystem = CascadeDerivativeSystem<Method, Stationary, Multi>;
    using NaturalLabeling = NaturalLabelingInitializer<Method>;
    using StateVarOps = StateVariableOperations<Method, Multi>;
    template <typename T> using MultiAdapt = typename MultiHelper<Multi>::template MultiAdapt<T>;

    using SymbLinearElement = SymbolicLinearElement<Stationary>;
    using SymbNonLinearElement = SymbolicNonLinearElement<Method, Stationary, Multi>;
    using NonLinearElement = NumericNonLinearElement<Method, Stationary, Multi>;
    using NonLinearElementDerivative = NumericNonLinearElementDerivative<Method, Stationary, Multi>;

  private:
    std::vector<std::size_t> levelSizes_;
    std::vector<std::vector<SymbLinearElement>> levelSymbolicLinearElements_;
    std::vector<std::vector<SymbNonLinearElement>> levelSymbolicNonLinearities_;
    std::vector<SystemCondition> levelInitialValues_;
    std::vector<SystemCondition> levelInitialValueDerivatives_;
    Real endTime_;

    template <typename Network, std::enable_if_t<std::is_same<Network, CascadeNetwork>::value or
                                                     std::is_same<Network, ReducedCascadeNetwork>::value,
                                                 bool> = true>
    CascadeSystemBuilder(const Network &network, const MultiAdapt<std::vector<std::shared_ptr<Substrate>>> &substrates,
                         Real endTime = std::numeric_limits<Real>::infinity());

  public:
    template <typename Network, std::enable_if_t<std::is_same<Network, CascadeNetwork>::value or
                                                     std::is_same<Network, ReducedCascadeNetwork>::value,
                                                 bool> = true>
    static std::unique_ptr<CascadeSystemBuilder>
    create(const Network &network, const MultiAdapt<std::vector<std::shared_ptr<Substrate>>> &substrates,
           Real endTime = std::numeric_limits<Real>::infinity());

    Real getEndTime() const;

    auto build(const RealVector &parameters) const -> std::unique_ptr<System> override;

    auto buildDerivative(const RealVector &parameters, const RealVector &parameterDerivatives,
                         const Solution &baseSystemSolution) const -> std::unique_ptr<System> override;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "CascadeSystemBuilder.tpp"
#endif

#endif // X3CFLUX_CASCADESYSTEMBUILDER_H
