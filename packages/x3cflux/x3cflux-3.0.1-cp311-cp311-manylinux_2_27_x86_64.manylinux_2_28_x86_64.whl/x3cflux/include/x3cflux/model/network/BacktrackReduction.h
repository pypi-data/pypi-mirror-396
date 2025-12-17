#ifndef X3CFLUX_BACKTRACKREDUCTION_H
#define X3CFLUX_BACKTRACKREDUCTION_H

#include "MeasurementConverter.h"
#include "MetaboliteNetwork.h"
#include "StateTransporter.h"
#include <model/data/Measurement.h>
#include <unordered_map>
#include <unordered_set>

// Add std::hash support for boost::dynamic_bitset<> (Boost Version < 1.71.0)
#if (BOOST_VERSION / 100) % 1000 < 71
#include <functional>
namespace std {
template <> struct hash<boost::dynamic_bitset<>> {
    using argument_type = boost::dynamic_bitset<>;
    using result_type = std::size_t;
    result_type operator()(const argument_type &a) const noexcept {
        std::hash<unsigned long> hasher;
        return hasher(a.to_ulong()); // todo: use hasher that works for all sizes
    }
};
} // namespace std
#endif

namespace x3cflux {

/// \brief Backtracking based network reduction algorithm
/// \tparam Method modeling method
/// \tparam Transporter transporter of the methods state
/// \tparam Converter measurement converter of the method
///
/// To reduce a labeling network this approach calculates the state variables
/// that can be identified by the given measurements. From these variables the
/// algorithm identifies all necessary state variables and reactions to form the
/// measurement state variable by tracking their states through the networks
/// reactions.
template <typename Method,
          typename Transporter = std::enable_if_t<HasStateTransporter<typename Method::StateType>::value,
                                                  StateTransporter<typename Method::StateType>>,
          typename Converter = std::enable_if_t<HasMeasurementConverter<Method>::value, MeasurementConverter<Method>>>
class BacktrackReduction : public MetaboliteNetwork {
  public:
    using TransporterTraits = StateTransporterTraits<typename Method::StateType>;
    using State = typename TransporterTraits::StateType;
    using StateVariable = typename TransporterTraits::StateVariableType;
    using Reaction = typename TransporterTraits::ReactionType;

  private:
    std::unordered_map<std::size_t, std::unordered_set<State>> stateVariables_;
    std::vector<Reaction> reactions_;
    IntegerMatrix flowDirectionTable_;

  public:
    /// Create and run backtrack reduction algorithm.
    /// \param networkData raw metabolite and reaction data
    /// \param substrates raw substrate data
    /// \param measurements raw measurement data
    BacktrackReduction(const NetworkData &networkData, const std::vector<std::shared_ptr<Substrate>> &substrates,
                       const std::vector<std::shared_ptr<LabelingMeasurement>> &measurements);

    /// \return reduced state variable
    auto getStateVariables() const -> const std::unordered_map<std::size_t, std::unordered_set<State>> &;

    /// \return reduced state variable reactions
    const std::vector<Reaction> &getReactions() const;

  private:
    Index getMeasurementPoolIndex(const std::shared_ptr<LabelingMeasurement> &measurement) const;

    void backtrackStateVariable(Index poolIndex, const State &state);
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "BacktrackReduction.tpp"
#endif

#endif // X3CFLUX_BACKTRACKREDUCTION_H
