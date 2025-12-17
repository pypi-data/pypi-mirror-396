#ifndef X3CFLUX_SYMBOLICLINEARELEMENT_H
#define X3CFLUX_SYMBOLICLINEARELEMENT_H

#include "ParameterAccessor.h"
#include <math/NumericTypes.h>

namespace x3cflux {

/// \brief Symbolic element of a linear system
/// \tparam Stationary IST or INST MFA
template <bool Stationary> class SymbolicLinearElement {
  private:
    Index rowIndex_;
    Index columnIndex_;
    Index poolSizeIndex_;
    bool diagonal_;
    std::vector<std::pair<Index, bool>> fluxCoefficients_;

  public:
    /// Create symbolic linear element
    /// \param rowIndex row index of element
    /// \param columnIndex column index of element
    /// \param poolSizeIndex index of metabolic pool size corresponding to the row
    SymbolicLinearElement(Index rowIndex, Index columnIndex, Index poolSizeIndex);

    /// Add symbolic flux value to the element
    /// \param reactionIndex index of metabolic reaction associated with flux
    /// \param forward forward or backward flux
    void addFlux(std::size_t reactionIndex, bool forward);

    /// \return row index of element
    Index getRowIndex() const;

    /// \return column index of element
    Index getColumnIndex() const;

    /// \return index of metabolic pool size corresponding to the row
    Index getPoolSizeIndex() const;

    /// \return row index equal to column index
    bool isDiagonal() const;

    /// \return list of index and type representation of metabolic fluxes
    const std::vector<std::pair<Index, bool>> &getFluxCoefficients() const;

    /// Evaluate the symbolic summation of fluxes
    /// \param accessor accessor of metabolic fluxes
    /// \return triplet holding the element value
    RealTriplet evaluate(const ParameterAccessor &accessor) const;

    /// Evaluate the partial derivative of the symbolic summation of fluxes
    /// \param accessor accessor of metabolic fluxes and partial derivatives
    /// \return triplet holding the element derivative value
    RealTriplet evaluateDerivative(const DerivativeParameterAccessor &accessor) const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "SymbolicLinearElement.tpp"
#endif

#endif // X3CFLUX_SYMBOLICLINEARELEMENT_H
