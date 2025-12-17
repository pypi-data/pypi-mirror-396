#ifndef X3CFLUX_SRC_UTILS_PERMUTATION_H
#define X3CFLUX_SRC_UTILS_PERMUTATION_H

#include <numeric>
#include <utility>
#include <valarray>
#include <vector>

#include "Logging.h"

namespace x3cflux {

/// \brief Permutation of a finite family.
class Permutation {
  private:
    std::valarray<std::size_t> indices_;

  public:
    /// \brief Creates identity permutation.
    /// \param numIndices number of indices of the family
    explicit Permutation(std::size_t numIndices);

    /// \brief Creates permutation.
    /// \param indices permutation of the families indices
    explicit Permutation(std::valarray<std::size_t> indices);

    /// \brief Applies the permutation.
    /// \param i index of the permuted family
    /// \return index of the not-permuted family
    std::size_t operator()(std::size_t i) const;

    /// \brief Compares two permutations for equality.
    /// \param permutation other permutation
    /// \return equal or not
    bool operator==(const Permutation &permutation) const;

    /// \brief Computes the inverse of this permutation.
    /// \return inverse permutation
    Permutation getInverse() const;

    /// \brief Applies permutation to a family.
    /// \tparam Family object with [] operator for 0,...,"length of this permutation"-1
    /// \param family indexed family to permute
    /// \return permuted indexed family
    template <typename Family> Family permute(const Family &family) const;

    /// \brief Applies inverse permutation to a family.
    /// \tparam Family object with [] operator for 0,...,"length of this permutation"-1
    /// \param family indexed family to permute inversely
    /// \return inverse-permuted indexed family
    template <typename Family> Family permuteInverse(const Family &family) const;

    /// \return number of indices of the family
    std::size_t getNumIndices() const;

    /// \return indices that encode the permutation
    const std::valarray<std::size_t> &getIndices() const;

  private:
    std::size_t apply(std::size_t i) const;

    bool checkIfAllIndicesExist() const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "Permutation.tpp"
#endif

#endif // X3CFLUX_SRC_UTILS_PERMUTATION_H
