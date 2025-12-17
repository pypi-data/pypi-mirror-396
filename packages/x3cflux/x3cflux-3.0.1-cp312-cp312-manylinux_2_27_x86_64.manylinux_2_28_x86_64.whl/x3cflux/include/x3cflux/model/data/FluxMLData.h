#ifndef X3CFLUX_SRC_DATA_FLUXMLMODEL_H
#define X3CFLUX_SRC_DATA_FLUXMLMODEL_H

#include "MeasurementConfiguration.h"
#include "NetworkData.h"
#include <boost/date_time/posix_time/posix_time.hpp>

namespace x3cflux {

/// \brief Data from a FluxML file
class FluxMLData {
  private:
    std::string name_;
    std::string modelerName_;
    std::string version_;
    std::string comment_;
    boost::posix_time::ptime date_;

    NetworkData networkData_;
    std::vector<MeasurementConfiguration> configurations_;

  public:
    /// \brief Creates FluxML data.
    /// \param name name of the data
    /// \param modelerName name of the modeler
    /// \param version data version
    /// \param comment comment from the modeler
    /// \param date calendar date and time of last data change
    /// \param networkData metabolic network information (pools and reactions)
    /// \param configurations measurement setups based on the network data
    FluxMLData(std::string name, std::string modelerName, std::string version, std::string comment,
               const boost::posix_time::ptime &date, NetworkData networkData,
               std::vector<MeasurementConfiguration> configurations);

    /// \return name of the data
    const std::string &getName() const;

    /// \return name of the modeler
    const std::string &getModelerName() const;

    /// \return data version
    const std::string &getVersion() const;

    /// \return comment from the modeler
    const std::string &getComment() const;

    /// \return date and time of the last data change
    const boost::posix_time::ptime &getDate() const;

    /// \return metabolic network information (pools and reactions)
    const NetworkData &getNetworkData() const;

    /// \return measurement setups based on the network data
    const std::vector<MeasurementConfiguration> &getConfigurations() const;
};

} // namespace x3cflux

#endif // X3CFLUX_SRC_DATA_FLUXMLMODEL_H