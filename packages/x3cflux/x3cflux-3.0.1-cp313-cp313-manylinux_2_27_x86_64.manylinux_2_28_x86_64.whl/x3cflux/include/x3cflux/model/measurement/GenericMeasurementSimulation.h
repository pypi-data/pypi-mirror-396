#ifndef X3CFLUX_GENERICMEASUREMENTSIMULATION_H
#define X3CFLUX_GENERICMEASUREMENTSIMULATION_H

#include <model/data/Measurement.h>
#include <model/measurement/CNMRMeasurementSimulation.h>
#include <model/measurement/CumomerMeasurementSimulation.h>
#include <model/measurement/HNMRMeasurementSimulation.h>
#include <model/measurement/MSMSMeasurementSimulation.h>
#include <model/measurement/MSMeasurementSimulation.h>
#include <model/measurement/ScalableMeasurementSimulation.h>

namespace x3cflux {

template <typename Method, bool Multi = false>
class GenericMeasurementSimulation : public ScalableMeasurementSimulation<Method, Multi> {
  public:
    using StationarySolution = typename ScalableMeasurementSimulation<Method, Multi>::StationarySolution;
    using InstationarySolution = typename ScalableMeasurementSimulation<Method, Multi>::InstationarySolution;
    using LabelMeasSim = LabelingMeasurementSimulation<Method, Multi>;

  private:
    std::vector<flux::symb::ExprTree> formulas_;
    std::vector<std::vector<std::string>> variableNames_;
    std::vector<std::vector<std::shared_ptr<LabelMeasSim>>> measurements_;

    template <typename Network>
    GenericMeasurementSimulation(const GenericMeasurement &measurement, const Network &network, Index multiIndex = 0);

  public:
    template <typename Network>
    static std::unique_ptr<GenericMeasurementSimulation> create(const GenericMeasurement &measurement,
                                                                const Network &network, Index multiIndex = 0);

    void setTimeStamps(const std::vector<Real> &timeStamps) override;

    std::size_t getSize() const override;

    RealVector evaluate(const StationarySolution &solution) const override;

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override;

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override;

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "GenericMeasurementSimulation.tpp"
#endif

#endif // X3CFLUX_GENERICMEASUREMENTSIMULATION_H
