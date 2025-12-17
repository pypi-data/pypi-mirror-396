#ifndef X3CFLUX_ISOTOPOMERORDERING_H
#define X3CFLUX_ISOTOPOMERORDERING_H

#include "IsotopomerIterator.h"
#include <math/NumericTypes.h>

namespace x3cflux {

/// \brief Sequential ordering of isotopomer state variables
///
/// The ordering maps isotopomer state variables from a network
/// to a range of positive integers and vice versa. The range of
/// integers can used to map fractions of the isotopomers to a
/// vector and with that formulate labeling systems.
class IsotopomerOrdering {
  public:
    using StateVariable = typename IsotopomerIterator::Isotopomer;

  private:
    Index numStateVariables_;
    std::vector<Index> offset_;
    std::vector<std::size_t> numAtoms_;

    /// Create sequential ordering of the networks isotopomers.
    /// \param network network information
    explicit IsotopomerOrdering(const MetaboliteNetwork &network);

  public:
    /// Create sequential ordering of the networks isotopomers.
    /// \param network network information
    static IsotopomerOrdering create(const MetaboliteNetwork &network);

    /// \return total number of isotopomers
    Index getNumStateVariables() const;

    /// \param stateVar isotopomer state variable
    /// \return calculated index of the isotopomer
    Index getSystemIndex(const StateVariable &stateVar) const;

    /// \param systemIndex index of the labeling system
    /// \return calculated isotopomer
    StateVariable getStateVariable(Index systemIndex) const;
};

} // namespace x3cflux

#endif // X3CFLUX_ISOTOPOMERORDERING_H
