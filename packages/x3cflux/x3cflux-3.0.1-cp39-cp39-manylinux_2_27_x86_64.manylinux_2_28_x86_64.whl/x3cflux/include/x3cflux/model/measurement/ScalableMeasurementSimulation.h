#ifndef X3CFLUX_SCALABLEMEASUREMENTSIMULATION_H
#define X3CFLUX_SCALABLEMEASUREMENTSIMULATION_H

#include <model/system/LabelingSystem.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class ScalableMeasurementSimulation {
  public:
    using StationarySolution = typename LabelingSystem<Method, true, Multi>::Solution;
    using InstationarySolution = typename LabelingSystem<Method, false, Multi>::Solution;

  private:
    std::string name_;
    bool autoScalable_;
    std::vector<Real> timeStamps_;
    Index multiIndex_;

  public:
    ScalableMeasurementSimulation(std::string name, bool autoScalable, std::vector<Real> timeStamps, Index multiIndex);

    virtual ~ScalableMeasurementSimulation();

    const std::string &getName() const;

    bool isAutoScalable() const;

    const std::vector<Real> &getTimeStamps() const;

    std::size_t getNumTimeStamps() const;

    Index getMultiIndex() const;

    virtual void setTimeStamps(const std::vector<Real> &timeStamps);

    virtual std::size_t getSize() const = 0;

    virtual RealVector evaluate(const StationarySolution &solution) const = 0;

    virtual std::vector<RealVector> evaluate(const InstationarySolution &solution) const = 0;

    virtual RealVector evaluateDerivative(const StationarySolution &derivSolution) const = 0;

    virtual std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const = 0;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "ScalableMeasurementSimulation.tpp"
#endif

#endif // X3CFLUX_SCALABLEMEASUREMENTSIMULATION_H
