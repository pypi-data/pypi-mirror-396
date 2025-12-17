#ifndef X3CFLUX_MSMSMEASUREMENTSIMULATION_H
#define X3CFLUX_MSMSMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false>
class MSMSMeasurementSimulation : public LabelingMeasurementSimulation<Method, Multi> {
  public:
    using Base = LabelingMeasurementSimulation<Method, Multi>;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    using StateVarOps = StateVariableOperations<Method, Multi>;
    using Converter = MeasurementConverter<Method>;

  private:
    MSMSSpecification specification_;
    std::vector<std::tuple<std::size_t, Index, Index>> conversionMapping_;

    template <typename Network>
    MSMSMeasurementSimulation(const MSMSMeasurement &measurement, const Network &network, std::size_t multiIndex = 0);

  public:
    template <typename Network>
    static std::unique_ptr<MSMSMeasurementSimulation> create(const MSMSMeasurement &measurement, const Network &network,
                                                             std::size_t multiIndex = 0);

    std::size_t getSize() const override;

    RealVector evaluate(const StationarySolution &solution) const override;

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override;

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override;

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override;

  private:
    RealVector evaluateIsotopomers(const RealVector &isotopomers) const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "MSMSMeasurementSimulation.tpp"
#endif

#endif // X3CFLUX_MSMSMEASUREMENTSIMULATION_H
