#ifndef X3CFLUX_MEASUREMENTSIMULATOR_H
#define X3CFLUX_MEASUREMENTSIMULATOR_H

#include <omp.h>

#include <model/data/FluxMLParser.h>
#include <model/measurement/CNMRMeasurementSimulation.h>
#include <model/measurement/GenericMeasurementSimulation.h>
#include <model/measurement/HNMRMeasurementSimulation.h>
#include <model/measurement/MIMSMeasurementSimulation.h>
#include <model/measurement/MSMSMeasurementSimulation.h>
#include <model/measurement/MSMeasurementSimulation.h>
#include <model/measurement/ParameterMeasurementSimulation.h>
#include <model/network/CumomerMethod.h>
#include <model/network/EMUMethod.h>
#include <model/network/LabelingNetwork.h>
#include <model/parameter/ParameterSpaceAdapter.h>
#include <model/parameter/ParameterSpaceFactory.h>
#include <model/system/CascadeSystemBuilder.h>

namespace x3cflux {

class SimulatorBase {
  public:
    virtual ~SimulatorBase();
};

void append(std::vector<RealVector> &measurements, const std::vector<RealVector> &measurement);

RealVector flatten(const std::vector<RealVector> &measurements);

/// Finds the position of a parameter entry.
/// \param paramEntries names, types and values of the set parameters
/// \param name parameter name
/// \param type parameter type
/// \return iterator at the position
std::vector<ParameterEntry>::const_iterator findParameterEntry(const std::vector<ParameterEntry> &paramEntries,
                                                               const std::string &name, ParameterType type);

/// Gets binary representation of selected parameters.
/// \tparam ParamObject either Reaction or Metabolite class
/// \param paramEntries names, types and values of the set parameters
/// \param paramObjects Reaction or Metabolite object
/// \param type parameter type
/// \return parameter selection
template <typename ParamObject>
boost::dynamic_bitset<> getParameterSelection(const std::vector<ParameterEntry> &paramEntries,
                                              const std::vector<ParamObject> &paramObjects, ParameterType type);

/// Gets parameter values from list of parameter entries, e.g. taken from measurement configuration. A warning
/// is issued, if a free parameter is not present.
/// \tparam Stationary IST or INST MFA
/// \tparam ParameterSpace parameter space class, per default chosen based on Stationary
/// \param parameterSpace parameter space instance
/// \param paramEntries names, types and values of the set parameters
/// \return free parameter vector
template <bool Stationary, typename ParameterSpace =
                               std::conditional_t<Stationary, StationaryParameterSpace, NonStationaryParameterSpace>>
RealVector getParameters(const ParameterSpace &parameterSpace, const std::vector<ParameterEntry> &paramEntries);

/// \brief Implementation of the labeling measurement simulator.
///
/// This is the core class of 13CFLUX3. All heavy computation is based on
/// this object. It combines all important pieces like the network of
/// labeling states, the parameter space and the builder of numerical
/// systems used for simulation.
///
/// \tparam Method labeling state simulation method
/// \tparam Stationary IST or INST MFA
/// \tparam Multi multiple or single experiment
/// \tparam Reduced reduced or full simulation of labeling states
template <typename Method, bool Stationary, bool Multi = false, bool Reduced = true>
class MeasurementSimulator : public SimulatorBase {
  public:
    using ParameterSpace = std::conditional_t<Stationary, StationaryParameterSpace, NonStationaryParameterSpace>;
    using Network = std::conditional_t<Reduced, ReducedLabelingNetwork<Method>, LabelingNetwork<Method>>;
    using Builder = CascadeSystemBuilder<Method, Stationary, Multi>; // todo: enable other system types in the future
    using System = typename Builder::ProductSystem;
    using Solution = typename System::Solution;
    using ScaleMeasSimulation = ScalableMeasurementSimulation<Method, Multi>;
    using ParamMeasSimulation = ParameterMeasurementSimulation;

  private:
    NetworkData networkData_;
    std::vector<MeasurementConfiguration> configurations_;
    std::unique_ptr<ParameterSpace> parameterSpace_;
    std::unique_ptr<Network> network_;
    std::unique_ptr<Builder> builder_;
    mutable std::vector<std::unique_ptr<ScaleMeasSimulation>> scaleMeasSimulations_;
    std::vector<std::unique_ptr<ParamMeasSimulation>> paramMeasSimulations_;
    std::size_t numMulti_;

  public:
    /// Create labeling simulator from network and measurement data.
    /// \param networkData data object containing metabolites and reactions
    /// \param configurations measurement configurations
    explicit MeasurementSimulator(const NetworkData &networkData,
                                  const std::vector<MeasurementConfiguration> &configurations);

    ~MeasurementSimulator() override;

    /// \return the simulator's metabolites and reactions
    const NetworkData &getNetworkData() const;

    /// \return the simulator's measurement configurations
    const std::vector<MeasurementConfiguration> &getConfigurations() const;

    /// \return description of parameters and constraints
    auto getParameterSpace() const -> const ParameterSpace &;

    /// \return description of parameters and constraints
    auto getParameterSpace() -> ParameterSpace &;

    /// \return network of labeling states to simulate
    auto getLabelingNetwork() const -> const Network &;

    /// \return network of labeling states to simulate
    auto getLabelingNetwork() -> Network &;

    /// \return builder for the underlying numerical systems
    auto getSystemBuilder() const -> const Builder &;

    /// \return builder for the underlying numerical systems
    auto getSystemBuilder() -> Builder &;

    /// \return measurements with scaling factor (labeling and generic
    /// measurements)
    auto getScalableMeasurementSimulations() const -> const std::vector<std::unique_ptr<ScaleMeasSimulation>> &;

    /// \return measurements of simulation parameters
    auto getParameterMeasurementSimulations() const -> const std::vector<std::unique_ptr<ParamMeasSimulation>> &;

    /// \return number of multiple labeling experiments
    std::size_t getNumMulti() const;

    /// Simulates measurements for a given set of free parameters.
    /// \param freeParameters parameter vector
    /// \param timeStamps optional grid of time stamps (no effect on
    /// stationary simulations) \return simulated measurements (first
    /// labeling measurements, then parameter measurements)
    std::pair<std::vector<RealVector>, std::vector<Real>>
    computeMeasurements(const RealVector &freeParameters, const std::vector<Real> &timeStamps = {}) const;

    /// \return names of the measurements (first labeling measurements, then parameter measurements)
    std::pair<std::vector<std::string>, std::vector<std::string>> getMeasurementNames() const;

    std::pair<std::vector<Index>, std::vector<Index>> getMeasurementMultiIndices() const;

    /// \return time stamps of labeling measurements
    std::vector<std::vector<Real>> getMeasurementTimeStamps() const;

    /// Compute the Jacobian of the measurements simulation for a given set of free parameters.
    /// \param freeParameters parameter vector
    /// \return simulation Jacobian
    RealMatrix computeJacobian(const RealVector &freeParameters) const;

    /// Compute the Jacobian of each of the multiple measurements simulation
    /// for a given set of free parameters. \param freeParameters parameter
    /// vector \return all simulation Jacobians
    std::vector<RealMatrix> computeMultiJacobians(const RealVector &freeParameters) const;

  private:
    NetworkData filterNetworkData(const std::unordered_set<std::string> &substrateNames) const;
};

} // namespace x3cflux

#ifndef COMPILE_TEMPLATES
#include "MeasurementSimulator.tpp"
#endif

#endif // X3CFLUX_MEASUREMENTSIMULATOR_H
