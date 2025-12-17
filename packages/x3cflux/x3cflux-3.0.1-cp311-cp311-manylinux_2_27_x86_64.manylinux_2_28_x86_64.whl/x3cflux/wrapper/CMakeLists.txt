pybind11_add_module(core)

target_sources(core
    PRIVATE
        AddExceptions.cpp
        AddFluxMLParser.cpp
        AddLabelingNetwork.cpp
        AddMeasurementConfiguration.cpp
        AddMeasurements.cpp
        AddNetworkData.cpp
        AddParameterConstaints.cpp
        AddParameterSpace.cpp
        AddSimulator.cpp
        AddSubstrate.cpp
        AddSystemBuilder.cpp
        TypeCasts.h
        TypeCasts.cpp
        wrapper.cpp
)

target_link_libraries(core PRIVATE x3cflux-measurement)
target_include_directories(core PRIVATE .)
target_link_libraries(core PRIVATE Boost::test_exec_monitor)
target_compile_definitions(core PRIVATE VERSION_INFO=${CMAKE_PROJECT_VERSION})

# pybind11_add_module adds some options that makes it possible that the build will succeed, but the library still can
# not be imported
# By adding this as an explicit build step, we ensure that there are not hidden problems in the library.
add_custom_command(
        TARGET core
        POST_BUILD
        COMMAND ${PYTHON_EXECUTABLE} -c "import core"
        COMMENT "Try to import the build python module to ensure it is build correct."
)

install(TARGETS core DESTINATION lib)
