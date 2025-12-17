#ifndef X3CFLUX_PARAMETERMEASUREMENTSIMULATION_H
#define X3CFLUX_PARAMETERMEASUREMENTSIMULATION_H

#include <math/NumericTypes.h>
#include <model/data/Measurement.h>

#include <model/parameter/ParameterClassification.h>
#include <utility>

namespace x3cflux {

class ParameterMeasurementSimulation {
  private:
    std::string name_;
    Index offset_;
    std::vector<std::string> parameterNames_;
    std::vector<std::string> freeParameterNames_;
    flux::symb::ExprTree measurementFormula_;
    Index multiIndex_;

    ParameterMeasurementSimulation(std::string name, Index offset, const ParameterClassification &paramClass,
                                   const flux::symb::ExprTree &measurementFormula, Index multiIndex);

  public:
    static std::unique_ptr<ParameterMeasurementSimulation>
    createFluxMeasurement(const FluxMeasurement &measurement, Index numFreePrevTypeFluxes,
                          const ParameterClassification &paramClass, Index multiIndex);

    static std::unique_ptr<ParameterMeasurementSimulation>
    createPoolSizeMeasurement(const PoolSizeMeasurement &measurement, std::size_t numFreeParams,
                              const ParameterClassification &paramClass, Index multiIndex);

    const std::string &getName() const;

    const std::vector<std::string> &getParameterNames() const;

    const flux::symb::ExprTree &getMeasurementFormula() const;

    Index getMultiIndex() const;

    Real evaluate(const RealVector &freeParameters) const;

    Real evaluateDerivative(Index derivParamIndex, const RealVector &freeParameters) const;
};

} // namespace x3cflux

#endif // X3CFLUX_PARAMETERMEASUREMENTSIMULATION_H
