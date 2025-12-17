#ifndef X3CFLUX_WEIGHTEDLEASTSQUARESLOSSFUNCTION_H
#define X3CFLUX_WEIGHTEDLEASTSQUARESLOSSFUNCTION_H

#include "MeasurementSimulator.h"

namespace x3cflux {

template <typename Method, bool Stationary, bool Multi = false, bool Reduced = true>
class WeightedLeastSquaresLossFunction : public MeasurementSimulator<Method, Stationary, Multi, Reduced> {
  private:
    std::vector<RealVector> scaleMeasData_;
    std::vector<RealVector> scaleStdDeviations_;
    std::vector<Real> paramMeasData_;
    std::vector<Real> paramStdDeviations_;

  public:
    WeightedLeastSquaresLossFunction(const NetworkData &networkData,
                                     const std::vector<MeasurementConfiguration> &configurations);

    const std::vector<RealVector> &getScalableMeasurementData() const;

    const std::vector<RealVector> &getScalableMeasurementStandardDeviations() const;

    const std::vector<Real> &getParameterMeasurementData() const;

    const std::vector<Real> &getParameterMeasurementStandardDeviations() const;

    std::pair<std::vector<RealVector>, std::vector<Real>> getMeasurementData() const;

    std::pair<std::vector<RealVector>, std::vector<Real>> getMeasurementStandardDeviations() const;

    std::pair<std::vector<RealVector>, std::vector<Real>> computeScaledMeasurements(const RealVector &parameters);

    Real computeLoss(const RealVector &freeParameters) const;

    RealVector computeLoss(const RealMatrix &freeParameters) const;

    std::vector<Real> computeMultiLosses(const RealVector &freeParameters) const;

    RealVector computeLossGradient(const RealVector &freeParameters) const;

    RealMatrix computeLossGradient(const RealMatrix &freeParameters) const;

    std::vector<RealVector> computeMultiLossGradients(const RealVector &freeParameters) const;

    RealMatrix computeLinearizedHessian(const RealVector &freeParameters) const;

    std::vector<RealMatrix> computeMultiLinearizedHessians(const RealVector &freeParameters) const;

  private:
    Real computeNormalizedResidual(const RealVector &simMeasValue, std::size_t measIndex, bool isAutoScalable) const;

    Real computeNormalizedResidual(const std::vector<RealVector> &simMeasValues, std::size_t beginMeasIndex,
                                   bool isAutoScalable) const;

    Real computeNormalizedResidualDerivative(const RealVector &simMeasValue, const RealVector &simMeasValueDerivative,
                                             std::size_t measIndex, bool isAutoScalable) const;

    Real computeNormalizedResidualDerivative(const std::vector<RealVector> &simMeasValues,
                                             const std::vector<RealVector> &simMeasValueDerivatives,
                                             std::size_t beginMeasIndex, bool isAutoScalable) const;

    static Real computeScaleFactor(const RealVector &simMeasurements, const RealVector &realMeasurements,
                                   const RealVector &standardDeviations);

    static Real computeScaleFactorDerivative(const RealVector &simMeasurements,
                                             const RealVector &simMeasurementDerivatives,
                                             const RealVector &realMeasurements, const RealVector &standardDeviations);
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "WeightedLeastSquaresLossFunction.tpp"
#endif

#endif // X3CFLUX_WEIGHTEDLEASTSQUARESLOSSFUNCTION_H
