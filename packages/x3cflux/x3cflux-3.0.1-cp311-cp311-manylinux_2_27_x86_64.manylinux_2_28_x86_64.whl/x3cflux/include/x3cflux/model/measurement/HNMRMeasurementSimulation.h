#ifndef X3CFLUX_HNMRMEASUREMENTSIMULATION_H
#define X3CFLUX_HNMRMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class HNMRMeasurementSimulation;

template <bool Multi>
class HNMRMeasurementSimulation<EMUMethod, Multi> : public LabelingMeasurementSimulation<EMUMethod, Multi> {
  public:
    using Base = LabelingMeasurementSimulation<EMUMethod, Multi>;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    using StateVarOps = StateVariableOperations<EMUMethod, Multi>;
    using Converter = MeasurementConverter<EMUMethod>;

  private:
    HNMRSpecification specification_;
    Index numAtoms_;
    std::vector<Index> systemIndices_;

    template <typename Network>
    HNMRMeasurementSimulation(const HNMRMeasurement &measurement, const Network &network, std::size_t multiIndex = 0);

  public:
    template <typename Network>
    static std::unique_ptr<HNMRMeasurementSimulation> create(const HNMRMeasurement &measurement, const Network &network,
                                                             std::size_t multiIndex = 0);

    std::size_t getSize() const override;

    RealVector evaluate(const StationarySolution &solution) const override;

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override;

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override;

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override;
};

template <bool Multi>
class HNMRMeasurementSimulation<CumomerMethod, Multi> : public LabelingMeasurementSimulation<CumomerMethod, Multi> {
  public:
    using Base = LabelingMeasurementSimulation<CumomerMethod, Multi>;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    using StateVarOps = StateVariableOperations<CumomerMethod, Multi>;
    using Converter = MeasurementConverter<CumomerMethod>;

  private:
    HNMRSpecification specification_;
    Index numAtoms_;
    std::vector<Index> systemIndices_;

    template <typename Network>
    HNMRMeasurementSimulation(const HNMRMeasurement &measurement, const Network &network, std::size_t multiIndex = 0);

  public:
    template <typename Network>
    static std::unique_ptr<HNMRMeasurementSimulation> create(const HNMRMeasurement &measurement, const Network &network,
                                                             std::size_t multiIndex = 0);

    std::size_t getSize() const override;

    RealVector evaluate(const StationarySolution &solution) const override;

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override;

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override;

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "HNMRMeasurementSimulation.tpp"
#endif

#endif // X3CFLUX_HNMRMEASUREMENTSIMULATION_H
