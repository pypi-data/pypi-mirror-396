#ifndef X3CFLUX_LABELINGMEASUREMENTSIMULATION_H
#define X3CFLUX_LABELINGMEASUREMENTSIMULATION_H

#include "ScalableMeasurementSimulation.h"

namespace x3cflux {

template <typename Method, bool Multi = false>
class LabelingMeasurementSimulation : public ScalableMeasurementSimulation<Method, Multi> {
  public:
    using StationarySolution = typename ScalableMeasurementSimulation<Method, Multi>::StationarySolution;
    using InstationarySolution = typename ScalableMeasurementSimulation<Method, Multi>::InstationarySolution;

  private:
    std::string poolName_;

  public:
    LabelingMeasurementSimulation(std::string name, bool autoScalable, std::vector<Real> timeStamps,
                                  std::size_t multiIndex, std::string poolName);

    const std::string &getPoolName() const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "LabelingMeasurementSimulation.tpp"
#endif

#endif // X3CFLUX_LABELINGMEASUREMENTSIMULATION_H
