#ifndef X3CFLUX_STATETRANSPORTER_H
#define X3CFLUX_STATETRANSPORTER_H

#include "MetaboliteNetwork.h"

#include <utility>
#include <vector>

namespace x3cflux {

/// \brief Metabolite state variable
/// \tparam State metabolite state
///
/// A metabolite state variable that is supposed to be used for
/// transportation calculation.
template <typename State> class StateVariableImpl {
  public:
    using StateType = State;

  private:
    std::size_t poolIndex_;
    State state_;

  public:
    /// Create metabolite state variable.
    /// \param poolIndex metabolite pool index
    /// \param state metabolite state
    StateVariableImpl(std::size_t poolIndex, State state);

    /// \return metabolite pool index
    std::size_t getPoolIndex() const;

    /// \return metabolite state
    State getState() const;
};

/// \brief Reaction of metabolite state variables
/// \tparam State metabolite state
///
/// A reaction of state variables that is supposed to be used
/// for transportation calculation. Therefore, there is only one
/// product whose state is then transported back to the educts.
template <typename State> class StateVariableReactionImpl {
  public:
    using StateVariableType = StateVariableImpl<State>;

  private:
    std::size_t reactionIndex_;
    bool forward_;
    StateVariableType product_;
    std::vector<StateVariableType> educts_;

  public:
    /// Create reaction of state variables.
    /// \param reactionIndex metabolic reaction index
    /// \param forward indicates if reaction is forward or backward
    /// \param product single state variable product
    /// \param educts state variable educts
    StateVariableReactionImpl(std::size_t reactionIndex, bool forward, const StateVariableType &product,
                              const std::vector<StateVariableType> &educts);

    /// \return metabolic reaction index
    std::size_t getReactionIndex() const;

    /// \return indicates if reaction is forward or backward
    bool isForward() const;

    /// \return single state variable product
    auto getProduct() const -> const StateVariableType &;

    /// \return state variable educts
    auto getEducts() const -> const std::vector<StateVariableType> &;
};

/// \brief Basic typedefs for a metabolite state variable
/// \tparam T metabolite state
template <typename T> struct StateTransporterTraits {
    using StateType = T;
    using StateVariableType = StateVariableImpl<StateType>;
    using ReactionType = StateVariableReactionImpl<StateType>;
};

/// \brief Default transporter (cannot be used)
/// \tparam T metabolite state
///
/// The transporter should be implemented for sensible
/// choices of states the correspond to existing state
/// variables. They have to implement the static function
/// "transport".
template <typename T> struct StateTransporter;

/// \brief State transporter check (default false)
/// \tparam T metabolite state
///
/// Check should be implemented for types that have a
/// sensible transporter implementation.
template <typename T> struct HasStateTransporter : public std::false_type {};

/// \brief State transporter implementation for binary number state
///
/// The implementation works for state variables with binary numbers as state
/// (e.g. Cumomer, EMU). It uses atom permutations of the given reactions
/// to permute the labeling of the product and omits all 0-labeled educts.
template <> struct StateTransporter<boost::dynamic_bitset<>> {
    using State = typename StateTransporterTraits<boost::dynamic_bitset<>>::StateType;
    using StateVariable = typename StateTransporterTraits<boost::dynamic_bitset<>>::StateVariableType;

    /// Transport labeling state of given reactant to reaction educts.
    /// \param network network information
    /// \param reactionIndex index of the reaction
    /// \param backwards indicate direction of the reaction
    /// \param reactantIndex index of reactant
    /// \param state state of the metabolite pool
    /// \return educt state variables
    static auto transport(const MetaboliteNetwork &network, std::size_t reactionIndex, bool backwards,
                          std::size_t reactantIndex, const State &state) -> std::vector<StateVariable>;
};

/// \brief State transporter check for binary number state
template <> struct HasStateTransporter<boost::dynamic_bitset<>> : public std::true_type {};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "StateTransporter.tpp"
#endif

#endif // X3CFLUX_STATETRANSPORTER_H
