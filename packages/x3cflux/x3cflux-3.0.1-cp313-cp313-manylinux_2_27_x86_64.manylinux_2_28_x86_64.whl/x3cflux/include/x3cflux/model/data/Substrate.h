#ifndef X3CFLUX_SRC_DATA_INPUTSUBSTRATE_H
#define X3CFLUX_SRC_DATA_INPUTSUBSTRATE_H

#include <ExprTree.h>
#include <boost/dynamic_bitset.hpp>
#include <list>
#include <map>
#include <utility>

namespace x3cflux {

/// \brief Base class for substrate of a labeling measurement setup
class Substrate {
  protected:
    std::string name_;
    std::string metaboliteName_;
    double costs_;

  public:
    /// \brief Creates substrate.
    /// \param name name of the substrate
    /// \param poolName name of the metabolic pool
    /// \param costs costs of the substrate
    Substrate(std::string name, std::string metaboliteName, double costs);

    virtual ~Substrate();

    /// \return name of the substrate
    const std::string &getName() const;

    /// \return name of the metabolic pool
    const std::string &getMetaboliteName() const;

    /// \return costs of the substrate
    double getCosts() const;

    /// Copy function for substrates
    /// \return deep copy of substrate
    virtual std::unique_ptr<Substrate> copy() const = 0;
};

/// \brief Implementation of Substrate
/// \tparam Profile_ Profile type (Real, VariateProfile)
template <typename Profile_> class SubstrateImpl : public Substrate {
  public:
    using Profile = Profile_;

  private:
    std::map<boost::dynamic_bitset<>, Profile> profiles_;

  public:
    /// \brief Creates implementation of substrate.
    /// \param name name of the substrate
    /// \param poolName name of the metabolic pool
    /// \param costs costs of the substrate
    /// \param profiles substrate profiles by isotopomer
    SubstrateImpl(const std::string &name, const std::string &poolName, double costs,
                  const std::map<boost::dynamic_bitset<>, Profile> &profiles);

    /// \return substrate profiles by isotopomer
    auto getProfiles() const -> const std::map<boost::dynamic_bitset<>, Profile> &;

    std::unique_ptr<Substrate> copy() const override;
};

/// \brief Substrate profile that varies over time
///
/// Variate profiles can be expressed as a set of sub profiles with
/// conditions. The sub profiles are closed formulas that model how much a
/// substrate is available at a certain point of time. Conditions determine when
/// to change from one sub profile to the next one.
using VariateProfile = std::vector<std::tuple<double, double, flux::symb::ExprTree>>;
using ConstantSubstrate = SubstrateImpl<double>;
using VariateSubstrate = SubstrateImpl<VariateProfile>;

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "Substrate.tpp"
#endif

#endif // X3CFLUX_SRC_DATA_INPUTSUBSTRATE_H
