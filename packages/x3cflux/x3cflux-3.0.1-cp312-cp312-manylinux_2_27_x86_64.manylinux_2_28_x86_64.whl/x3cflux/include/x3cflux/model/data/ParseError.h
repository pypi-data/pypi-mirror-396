#ifndef X3CFLUX_SRC_DATA_PARSEERROR_H
#define X3CFLUX_SRC_DATA_PARSEERROR_H

#include <stdexcept>
#include <string>

namespace x3cflux {

/// \brief Error for failed data parsing
class ParseError : public std::logic_error {
  public:
    /// \brief Creates parse error.
    /// \param message description of the error
    explicit ParseError(const std::string &message);
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_PARSEERROR_H