#ifndef X3CFLUX_MSMEASUREMENTSIMULATION_H
#define X3CFLUX_MSMEASUREMENTSIMULATION_H

#include "LabelingMeasurementSimulation.h"
#include <model/data/Measurement.h>
#include <model/measurement/IsotopomerTransformation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/MeasurementConverter.h>
#include <model/system/StateVariableOperations.h>

namespace x3cflux {

template <typename Method, bool Multi = false> class MSMeasurementSimulation;

template <bool Multi>
class MSMeasurementSimulation<EMUMethod, Multi> : public LabelingMeasurementSimulation<EMUMethod, Multi> {
  public:
    using Base = LabelingMeasurementSimulation<EMUMethod, Multi>;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    using StateVarOps = StateVariableOperations<EMUMethod, Multi>;

  private:
    MSSpecification specification_;
    std::size_t levelIndex_;
    Index systemIndex_;

    template <typename Network>
    MSMeasurementSimulation(const MSMeasurement &measurement, const Network &network, std::size_t multiIndex = 0);

  public:
    template <typename Network>
    static std::unique_ptr<MSMeasurementSimulation> create(const MSMeasurement &measurement, const Network &network,
                                                           std::size_t multiIndex = 0);

    std::size_t getSize() const override;

    RealVector evaluate(const StationarySolution &solution) const override;

    std::vector<RealVector> evaluate(const InstationarySolution &solution) const override;

    RealVector evaluateDerivative(const StationarySolution &derivSolution) const override;

    std::vector<RealVector> evaluateDerivative(const InstationarySolution &derivSolution) const override;
};

template <bool Multi>
class MSMeasurementSimulation<CumomerMethod, Multi> : public LabelingMeasurementSimulation<CumomerMethod, Multi> {
  public:
    using Base = LabelingMeasurementSimulation<CumomerMethod, Multi>;
    using typename Base::InstationarySolution;
    using typename Base::StationarySolution;
    using StateVarOps = StateVariableOperations<CumomerMethod, Multi>;
    using Converter = MeasurementConverter<CumomerMethod>;
    using IsotopomerTrafo = IsotopomerTransformation<CumomerMethod>;

  private:
    MSSpecification specification_;
    std::vector<std::tuple<std::size_t, Index, Index>> conversionMapping_;

    template <typename Network>
    MSMeasurementSimulation(const MSMeasurement &measurement, const Network &network, std::size_t multiIndex = 0);

  public:
    template <typename Network>
    static std::unique_ptr<MSMeasurementSimulation> create(const MSMeasurement &measurement, const Network &network,
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
#include "MSMeasurementSimulation.tpp"
#endif

#endif // X3CFLUX_MSMEASUREMENTSIMULATION_H
