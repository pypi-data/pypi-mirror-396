#ifndef X3CFLUX_MEASUREMENTCONVERTER_H
#define X3CFLUX_MEASUREMENTCONVERTER_H

#include "CumomerMethod.h"
#include "EMUMethod.h"
#include <model/data/Measurement.h>

template <class CastType, typename StoreType> static bool isInstanceOf(const std::shared_ptr<StoreType> &pointer) {
    return std::dynamic_pointer_cast<CastType>(pointer) != nullptr;
}

namespace x3cflux {

/// \brief Default measurement converter (cannot be used)
/// \tparam T modeling method
///
/// For certain state variables labeling networks can be reduced based
/// on their state type. To do so the state variables identified by measurement
/// need to be extracted using the underlying modeling method.
template <typename T> struct MeasurementConverter;

/// \brief Measurement converter check (default false)
/// \tparam T modeling method
///
/// Check should be implemented for types that have a
/// sensible measurement converter implementation.
template <typename T> struct HasMeasurementConverter : public std::false_type {};

/// \brief Measurement converter implementation for the Cumomer method
template <> struct MeasurementConverter<CumomerMethod> {
    using State = typename CumomerMethod::StateType;

    /// \param mask measured atom positions
    /// \return Cumomer state variables
    static auto getMSStates(const State &mask) -> std::vector<State>;

    /// \param mask measured atom positions
    /// \return Cumomer state variables
    static auto getMIMSStates(const State &mask) -> std::vector<State>;

    /// \param firstMask measured atom positions of parent
    /// \param secondMask measured atom positions of child
    /// \return Cumomer state variables
    static auto getMSMSStates(const State &firstMask, const State &secondMask) -> std::vector<State>;

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \return Cumomer state variables
    static auto getHNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions)
        -> std::vector<State>;

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \param types labeling neighborhood information
    /// \return Cumomer state variables
    static auto getCNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions,
                              const std::vector<CNMRSpecification::CNMRType> &types) -> std::vector<State>;

    /// \param labeledMask surely labeled atom positions
    /// \param wildcardMask not surely labeled atom positions
    /// \return Cumomer state variables
    static auto getCumomerStates(const State &labeledMask, const State &wildcardMask) -> std::vector<State>;

    /// Calculate Cumomer state variables from measurement setup information.
    /// \param measurement metabolite labeling measurement
    /// \return Cumomer state variables
    static auto calculateStates(const std::shared_ptr<LabelingMeasurement> &measurement) -> std::vector<State>;
};

/// \brief Measurement converter check for Cumomer method
template <> struct HasMeasurementConverter<CumomerMethod> : public std::true_type {};

/// \brief Measurement converter implementation for EMU method
template <> struct MeasurementConverter<EMUMethod> {
    using State = typename EMUMethod::StateType;

    /// \param mask measured atom positions
    /// \return EMU state variables
    static auto getMSStates(const State &mask) -> std::vector<State>;

    /// \param mask measured atom positions
    /// \return EMU state variables
    static auto getMIMSStates(const State &mask) -> std::vector<State>;

    /// \param firstMask measured atom positions of parent
    /// \param secondMask measured atom positions of child
    /// \return EMU state variables
    static auto getMSMSStates(const State &firstMask, const State &secondMask) -> std::vector<State>;

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \return EMU state variables
    static auto getHNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions)
        -> std::vector<State>;

    /// \param numAtoms metabolites number of traceable atom
    /// \param atomPositions measured atom positions
    /// \param types labeling neighborhood information
    /// \return EMU state variables
    static auto getCNMRStates(std::size_t numAtoms, const std::vector<std::size_t> &atomPositions,
                              const std::vector<CNMRSpecification::CNMRType> &types) -> std::vector<State>;

    /// \param labeledMask surely labeled atom positions
    /// \param wildcardMask not surely labeled atom positions
    /// \return EMU state variables
    static auto getCumomerStates(const State &labeledMask, const State &wildcardMask) -> std::vector<State>;

    /// Calculate EMU state variables from measurement setup information.
    /// \param measurement metabolite labeling measurement
    /// \return EMU state variables
    static auto calculateStates(const std::shared_ptr<LabelingMeasurement> &measurement) -> std::vector<State>;
};

/// \brief Measurement converter check for EMU method
template <> struct HasMeasurementConverter<EMUMethod> : public std::true_type {};

} // namespace x3cflux

#endif // X3CFLUX_MEASUREMENTCONVERTER_H
