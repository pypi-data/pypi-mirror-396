#ifndef X3CFLUX_COMBINATION_H
#define X3CFLUX_COMBINATION_H

#include "Logging.h"

namespace x3cflux {

/// \brief Combination of finite set
/// \tparam Binary Binary number representation (e.g. unsigned integer types)
///
/// Combinations sets that contain fixed-size subset of finite sets. Given a
/// set of size \f$n\f$, the \f$k\f$-combination is the set that contain all
/// \f$k\f$-sized subsets of the base set. The size of the \f$k\f$-combination
/// set is \f${n \choose k}\f$.
template <typename Binary> class Combination {
  public:
    class SubsetIterator {
      public:
        using difference_type = std::ptrdiff_t;
        using value_type = Binary;
        using reference = Binary &;
        using pointer = Binary *;
        using iterator_category = std::input_iterator_tag;

      private:
        Binary state_;
        Binary maxState_;

      public:
        explicit SubsetIterator(const Binary &initialState, const Binary &maxState);

        bool operator==(const SubsetIterator &other) const;

        bool operator!=(const SubsetIterator &other) const;

        SubsetIterator &operator++();

        reference operator*();

        pointer operator->();
    };

  private:
    std::size_t length_;
    std::size_t order_;
    Binary beginState_;
    Binary maxState_;

  public:
    /// Create combination by base set size and subset size.
    /// \param length size of the base set
    /// \param order size of the subsets
    Combination(std::size_t length, std::size_t order);

    /// Generates iterator for all subsets of this combination.
    /// The subsets are represented as binary numbers that whether
    /// the i-th element is included (1) or not (0).
    /// \return iterator for first subset (0, ..., 0, 1, ..., 1)
    SubsetIterator begin() const;

    /// Generates iterator for all subsets of this combination.
    /// The subsets are represented as binary numbers that whether
    /// the i-th element is included (1) or not (0).
    /// \return iterator for last subset (1, ..., 1, 0, ..., 0)
    SubsetIterator end() const;

    /// \return size of the base set
    std::size_t getLength() const;

    /// \return size of the subsets
    std::size_t getOrder() const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "Combination.tpp"
#endif

#endif // X3CFLUX_COMBINATION_H
