#ifndef X3CFLUX_SRC_DATA_MEASUREMENT_H
#define X3CFLUX_SRC_DATA_MEASUREMENT_H

#include <ExprTree.h>
#include <boost/dynamic_bitset.hpp>
#include <math/NumericTypes.h>
#include <memory>
#include <utility>
#include <vector>

namespace x3cflux {

/// \brief Base class for measurements
class Measurement {
  private:
    std::string name_;
    bool autoScalable_;

  public:
    /// \brief Creates a measurement.
    /// \param name name of the measurement
    /// \param autoScalable flag for weighting simulation residuals
    Measurement(std::string name, bool autoScalable);

    virtual ~Measurement();

    /// \return name of the measurement
    const std::string &getName() const;

    /// \return flag for weighting simulation residuals
    bool isAutoScalable() const;

    /// Copy function for measurements
    /// \return deep copy of measurement
    virtual std::unique_ptr<Measurement> copy() const = 0;
};

/// \brief Measured data with associated time points, standard deviation and error model
class MeasurementDataSet {
  private:
    std::vector<Real> timeStamps_;
    std::vector<RealVector> values_;
    std::vector<RealVector> standardDeviations_;
    std::vector<flux::symb::ExprTree> errorModels_;

  public:
    /// \brief Creates measurement data set.
    /// \param timeStamps measurement times (time since measurement start)
    /// \param value measured values
    /// \param standardDeviation standard deviations of the measurement
    /// \param errorModels statistical error models
    MeasurementDataSet(std::vector<Real> timeStamps, std::vector<RealVector> values,
                       std::vector<RealVector> standardDeviations, std::vector<flux::symb::ExprTree> errorModels);

    /// \return measurement times (time since measurement start)
    std::vector<Real> getTimeStamps() const;

    /// \return measured values
    const std::vector<RealVector> &getValues() const;

    /// \return standard deviations of the measurement
    const std::vector<RealVector> &getStandardDeviations() const;

    /// \return statistical error models
    const std::vector<flux::symb::ExprTree> &getErrorModels() const;

    /// \return number of measurements
    std::size_t getNumMeasurements() const;
};

/// \brief Information on mass spectrometry experiment
class MSSpecification {
  private:
    boost::dynamic_bitset<> mask_;
    std::vector<std::size_t> weights_;

  public:
    /// \brief Create mass spectrometry information.
    /// \param mask indicator for measured carbon positions
    /// \param weights measured molecule weights
    MSSpecification(boost::dynamic_bitset<> mask, std::vector<std::size_t> weights);

    /// \return indicator for measured carbon positions
    const boost::dynamic_bitset<> &getMask() const;

    /// \return measured molecule weights
    const std::vector<std::size_t> &getWeights() const;
};

/// \brief Information on multi-isotopic mass spectrometry measurement
class MIMSSpecification {
  private:
    boost::dynamic_bitset<> mask_;
    std::vector<std::vector<std::size_t>> weights_;

  public:
    /// \brief Creates multi-isotopic mass spectrometry information.
    /// \param mask indicator for measured atom positions
    /// \param weights measured molecule weights
    MIMSSpecification(boost::dynamic_bitset<> mask, std::vector<std::vector<std::size_t>> weights);

    /// \return indicator for measured atom positions
    const boost::dynamic_bitset<> &getMask() const;

    /// \return measured molecule weights
    const std::vector<std::vector<std::size_t>> &getWeights() const;
};

/// \brief Information on tandem mass spectrometry measurement
class MSMSSpecification {
  private:
    boost::dynamic_bitset<> firstMask_, secondMask_;
    std::vector<std::size_t> firstWeights_, secondWeights_;

  public:
    /// \brief Creates tandem mass spectrometry information.
    /// \param firstMask indicator for measured carbon positions before collision
    /// \param secondMask indicator for measured carbon positions after collision
    /// \param firstWeights measured molecule weights before collision
    /// \param secondWeights measured molecule weights after collision
    MSMSSpecification(boost::dynamic_bitset<> firstMask, boost::dynamic_bitset<> secondMask,
                      std::vector<std::size_t> firstWeights, std::vector<std::size_t> secondWeights);

    /// \return indicator for measured carbon positions before collision
    const boost::dynamic_bitset<> &getFirstMask() const;

    /// \return indicator for measured carbon positions after collision
    const boost::dynamic_bitset<> &getSecondMask() const;

    /// \return measured molecule weights before collision
    const std::vector<std::size_t> &getFirstWeights() const;

    /// \return measured molecule weights after collision
    const std::vector<std::size_t> &getSecondWeights() const;
};

/// \brief Information on hydrogen nuclear magnetic resonance measurement
class HNMRSpecification {
  private:
    std::vector<std::size_t> atomPositions_;

  public:
    /// \brief Creates hydrogen nuclear magnetic resonance information.
    /// \param atomPositions measured carbon positions
    explicit HNMRSpecification(std::vector<std::size_t> atomPositions);

    /// \return measured carbon positions
    const std::vector<std::size_t> &getAtomPositions() const;
};

/// \brief Information on 13C carbon nuclear magnetic resonance measurement
class CNMRSpecification {
  public:
    /// \brief Types of peak observations in 13C-NMR
    enum class CNMRType { SINGLET = 1, DOUBLET_LEFT = 2, DOUBLET_RIGHT = 3, DOUBLET_OF_DOUBLETS = 4, TRIPLETS = 5 };

  private:
    std::vector<std::size_t> atomPositions_;
    std::vector<CNMRType> types_;

  public:
    /// \brief Creates 13C carbon nuclear magnetic resonance information.
    /// \param atomPositions measured carbon positions
    /// \param types observed peak types
    CNMRSpecification(std::vector<std::size_t> atomPositions, std::vector<CNMRType> types);

    /// \return measured carbon positions
    const std::vector<std::size_t> &getAtomPositions() const;

    /// \return observed peak types
    const std::vector<CNMRType> &getTypes() const;
};

/// \brief Information on cumomer measurement
class CumomerSpecification {
  private:
    boost::dynamic_bitset<> labeledMask_;
    boost::dynamic_bitset<> wildcardMask_;

  public:
    /// \brief Creates cumomer measurement information.
    /// \param labeledMask indicator for labeled carbon positions
    /// \param wildcardMask indicator for labeled-or-unlabeled carbon positions
    CumomerSpecification(boost::dynamic_bitset<> labeledMask, boost::dynamic_bitset<> wildcardMask);

    /// \return indicator for labeled carbon positions
    const boost::dynamic_bitset<> &getLabeledMask() const;

    /// \return indicator for labeled-or-unlabeled carbon positions
    const boost::dynamic_bitset<> &getWildcardMask() const;
};

/// \brief Base class for labeling measurements of a metabolite
class LabelingMeasurement : public Measurement {
  private:
    std::string metaboliteName_;
    std::size_t numAtoms_;

    MeasurementDataSet data_;

  public:
    /// \brief Creates labeling measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param metaboliteName name of the measured metabolite
    /// \param numAtoms number of tracer atoms
    /// \param data measurement data
    LabelingMeasurement(const std::string &name, bool autoScaling, std::string metaboliteName, std::size_t numAtoms,
                        MeasurementDataSet data);

    /// \return name of the measured metabolic pool
    const std::string &getMetaboliteName() const;

    /// \return number of tracer atoms of the metabolic pool
    std::size_t getNumAtoms() const;

    /// \return measurement data
    const MeasurementDataSet &getData() const;
};

/// \brief Implementation of LabelingMeasurement
/// \tparam MethodSpecification_ Specification type for measurement method
template <typename MethodSpecification_> class LabelingMeasurementImpl : public LabelingMeasurement {
  public:
    using Specification = MethodSpecification_;

  private:
    Specification specification_;

  public:
    /// \brief Creates implementation of labeling measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param metaboliteName name of the measured metabolite
    /// \param numAtoms number of tracer atoms
    /// \param specification specification information of the used method
    /// \param data measurement data
    LabelingMeasurementImpl(const std::string &name, bool autoScaling, std::string metaboliteName, std::size_t numAtoms,
                            Specification specification, MeasurementDataSet data);

    /// \return specification information of the used method
    const Specification &getSpecification() const;

    std::unique_ptr<Measurement> copy() const override;
};

using MSMeasurement = LabelingMeasurementImpl<MSSpecification>;
using MIMSMeasurement = LabelingMeasurementImpl<MIMSSpecification>;
using MSMSMeasurement = LabelingMeasurementImpl<MSMSSpecification>;
using HNMRMeasurement = LabelingMeasurementImpl<HNMRSpecification>;
using CNMRMeasurement = LabelingMeasurementImpl<CNMRSpecification>;
using CumomerMeasurement = LabelingMeasurementImpl<CumomerSpecification>;

/// \brief Information on flux measurement
class FluxSpecification {
  private:
    std::vector<std::string> fluxNames_;
    bool isNet_;

  public:
    /// \brief Creates flux measurement information.
    /// \param fluxNames names of the fluxes that impacted the measurement
    /// \param isNet indicates if all fluxes are net or exchange
    FluxSpecification(std::vector<std::string> fluxNames, bool isNet);

    /// \return names of the fluxes that impacted the measurement
    const std::vector<std::string> &getFluxNames() const;

    /// \return indicates if all fluxes are net or exchange
    bool isNet() const;
};

/// \brief Information on pool size measurements
class PoolSizeSpecification {
  private:
    std::vector<std::string> poolNames_;

  public:
    /// \brief Creates pool sizes measurement information.
    /// \param poolNames names of the pools that impacted the measurement
    explicit PoolSizeSpecification(std::vector<std::string> poolNames);

    /// \return names of the pools that impacted the measurement
    const std::vector<std::string> &getPoolNames() const;
};

/// \brief Measurement of a combination of metabolic stationary parameters
///
/// Measurement data of parameter measurements is not stored in a list like in
/// labeling-based measurements. That is, because they must be time-independent
/// under isotopic steady-state assumptions.
class ParameterMeasurement : public Measurement {
  private:
    flux::symb::ExprTree measurementFormula_;
    Real value_;
    Real standardDeviation_;
    flux::symb::ExprTree errorModel_;

  public:
    /// \brief Creates parameter measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param measurementFormula formula to calculate the measurement data
    /// \param value measured value
    /// \param standardDeviation standard deviation of the measurement
    /// \param errorModel statistical error model
    ParameterMeasurement(const std::string &name, bool autoScaling, const flux::symb::ExprTree &measurementFormula,
                         Real value, Real standardDeviation, const flux::symb::ExprTree &errorModel);

    /// \return formula to calculate the measurement data
    const flux::symb::ExprTree &getMeasurementFormula() const;

    /// \return measured value
    Real getValue() const;

    /// \return standard deviation of the measurement
    Real getStandardDeviation() const;

    /// \return statistical error model
    const flux::symb::ExprTree &getErrorModel() const;
};

/// \brief Implementation of ParameterMeasurement
/// \tparam MethodSpecification_ Specification type for measurement method
///
/// Measurement data of parameter measurements is not stored in a list like in
/// labeling-based measurements. That is, because they must be time-independent
/// under isotopic steady-state assumptions.
template <typename MethodSpecification_> class ParameterMeasurementImpl : public ParameterMeasurement {
  public:
    using Specification = MethodSpecification_;

  private:
    Specification specification_;

  public:
    /// \brief Creates implementation of parameter measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param measurementFormula formula to calculate the measurement data
    /// \param specification specification information of the parameter type
    /// \param value measured value
    /// \param standardDeviation standard deviation of the measurement
    /// \param errorModel statistical error model
    ParameterMeasurementImpl(const std::string &name, bool autoScaling, const flux::symb::ExprTree &measurementFormula,
                             Specification specification, Real value, Real standardDeviation,
                             const flux::symb::ExprTree &errorModel);

    /// \return specification information of the parameter type
    const Specification &getSpecification() const;

    std::unique_ptr<Measurement> copy() const override;
};

using FluxMeasurement = ParameterMeasurementImpl<FluxSpecification>;
using PoolSizeMeasurement = ParameterMeasurementImpl<PoolSizeSpecification>;

/// \brief Measurements of combinations of labeling measurements
class GenericMeasurement : public Measurement {
  public:
    /// \brief Measurement of a combination of labeling measurements
    class SubMeasurement {
      private:
        flux::symb::ExprTree formula_;
        std::vector<std::string> variableNames_;
        std::vector<std::shared_ptr<LabelingMeasurement>> measurements_;

      public:
        /// \brief Creates generic sub measurement.
        /// \param formula formula to calculate the measurement value
        /// \param variableNames names that represent labeling measurements in the
        /// formula
        /// \param measurements labeling measurements that impacted the measurement
        SubMeasurement(const flux::symb::ExprTree &formula, std::vector<std::string> variableNames,
                       std::vector<std::shared_ptr<LabelingMeasurement>> measurements);

        /// Deep-copies generic sub measurement
        /// \param other other generic submeasurement
        SubMeasurement(const SubMeasurement &other);

        /// \return formula to calculate the measurement value
        const flux::symb::ExprTree &getFormula() const;

        /// \return names that represent labeling measurements in the formula
        const std::vector<std::string> &getVariableNames() const;

        /// \return labeling measurements that impacted the measurement
        const std::vector<std::shared_ptr<LabelingMeasurement>> &getMeasurements() const;
    };

  private:
    std::vector<SubMeasurement> subMeasurements_;

    MeasurementDataSet data_;

  public:
    /// \brief Creates generic measurement.
    /// \param name name of the measurement
    /// \param autoScaling flag for weighting simulation residuals
    /// \param subMeasurements component measurements
    /// \param data measurement data
    GenericMeasurement(const std::string &name, bool autoScaling, std::vector<SubMeasurement> subMeasurements,
                       MeasurementDataSet data);

    /// \return component measurements
    const std::vector<SubMeasurement> &getSubMeasurements() const;

    /// \return measurement data
    const MeasurementDataSet &getData() const;

    std::unique_ptr<Measurement> copy() const override;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "Measurement.tpp"
#endif

#endif // X3CFLUX_SRC_DATA_MEASUREMENT_H
