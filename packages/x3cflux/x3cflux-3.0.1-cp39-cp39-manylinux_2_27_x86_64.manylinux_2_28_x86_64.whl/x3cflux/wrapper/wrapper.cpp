#include <pybind11/detail/common.h>
#include <pybind11/eigen.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <util/Logging.h>
#if defined(_OPENMP)
#include <omp.h>
#endif

namespace py = pybind11;

class LogDummy {
  public:
    static int level;
};
int LogDummy::level = 3;

#if defined(_OPENMP)
class OMPDummy {
  public:
    static int numThreads;
};
int OMPDummy::numThreads = 1;
#endif

void addNetworkData(py::module &m);
void addParameterConstraints(py::module &m);
void addSubstrate(py::module &m);
void addMeasurements(py::module &m);
void addMeasurementConfiguration(py::module &m);
void addFluxMLParser(py::module &m);
void addParameterSpace(py::module &m);
void addLabelingNetwork(py::module &m);
void addSystemBuilder(py::module &m);
void addSimulator(py::module &m);
void addExceptions(py::module &m);

PYBIND11_MODULE(core, m) {
    X3CFLUX_LOG_INIT();
    py::class_<LogDummy>(m, "logging")
        .def_property_static(
            "level", [](py::object) { return LogDummy::level; },
            [](py::object, int level) {
                if (level > 4) {
                    X3CFLUX_INFO() << "Given log level (" + std::to_string(level) +
                                          ") exceeds the allowed range (0-4). "
                                          "It was set to 4 (full logging).";
                    LogDummy::level = 4;
                } else if (level < 0) {
                    X3CFLUX_INFO() << "Given log level (" + std::to_string(level) +
                                          ") exceeds the allowed range (0-4). "
                                          "It was set to 0 (no logging).";
                    LogDummy::level = 0;
                } else {
                    LogDummy::level = level;
                }
                auto boostLevel = static_cast<boost::log::trivial::severity_level>(4 - LogDummy::level);
                boost::log::core::get()->set_filter(boost::log::trivial::severity >= boostLevel);
            });
#if defined(_OPENMP)
    OMPDummy::numThreads = omp_get_max_threads();
    py::class_<OMPDummy>(m, "omp").def_property_static(
        "num_threads", [](py::object) { return OMPDummy::numThreads; },
        [](py::object, int numMaxThreads) {
            OMPDummy::numThreads = numMaxThreads;
            omp_set_num_threads(numMaxThreads);
        });
#endif

    addNetworkData(m);
    addParameterConstraints(m);
    addSubstrate(m);
    addMeasurements(m);
    addMeasurementConfiguration(m);
    addFluxMLParser(m);
    addParameterSpace(m);
    addLabelingNetwork(m);
    addSystemBuilder(m);
    addSimulator(m);
    addExceptions(m);
}
