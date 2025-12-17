#ifndef X3CFLUX_LABELINGNETWORK_H
#define X3CFLUX_LABELINGNETWORK_H

#include "BacktrackReduction.h"
#include "MetaboliteNetwork.h"
#include "ReductionIterator.h"
#include "ReductionOrdering.h"

namespace x3cflux {

/// \brief Network of metabolite labeling states and state reactions
/// \tparam Method labeling state modeling method
///
/// The simple LabelingNetwork is derived from MetaboliteNetwork
/// and directly operates on its data. It provides iterators to iterate
/// its labeling state-based reactions and orderings that sequentially
/// order the labeling states. These features must be implemented by the
/// method and accessible as typedefs.
template <typename Method> class LabelingNetwork : public MetaboliteNetwork {
  public:
    using ModelingMethod = Method;
    using Iterator = typename ModelingMethod::IteratorType;
    using Ordering = typename ModelingMethod::OrderingType;

  public:
    /// Create labeling network.
    /// \param data raw raw metabolite and reaction data
    /// \param substrates raw substrate data
    explicit LabelingNetwork(const NetworkData &data, const std::vector<std::shared_ptr<Substrate>> substrates);

    /// \return begin network iterator
    Iterator begin() const;

    /// \return end network iterator
    Iterator end() const;
};

/// \brief Backtrack-reduced network of metabolite labeling states and state reactions
/// \tparam Method labeling state modeling method
///
/// The ReducedLabelingNetwork is derived from BacktrackReduction and directly operates
/// on its data. It provides iterators to iterate its labeling state-based reactions
/// and orderings that sequentially order the labeling states. These features are
/// implemented by the BacktrackReduction. However, the chosen labeling modeling method
/// must fulfill the criteria to be backtrack-reducible.
template <typename Method> class ReducedLabelingNetwork : public BacktrackReduction<Method> {
  public:
    using ModelingMethod = Method;
    using Reduction = BacktrackReduction<ModelingMethod>;
    using Iterator = ReductionIterator<typename Reduction::State>;
    using Ordering = ReductionOrdering<typename Reduction::State>;

  public:
    /// Create ReducedLabelingNetwork
    /// \param data raw metabolite and reaction data
    /// \param substrates raw substrate data
    /// \param measurements
    ReducedLabelingNetwork(const NetworkData &data, const std::vector<std::shared_ptr<Substrate>> &substrates,
                           const std::vector<std::shared_ptr<LabelingMeasurement>> &measurements);

    /// \return begin reduced network iterator
    Iterator begin() const;

    /// \return end reduced network iterator
    Iterator end() const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "LabelingNetwork.tpp"
#endif

#endif // X3CFLUX_LABELINGNETWORK_H
