cmake_minimum_required(VERSION 3.16.0)
project(tds-control VERSION 0.0.1 LANGUAGES C CXX)
include(FetchContent)

set(TDS_CONTROL_HEADERS
        include/tdscontrol/tds.hpp
        include/tdscontrol/roots.hpp)

set(TDS_CONTROL_SRC 
            src/tds.cpp
            src/roots.cpp)

set(TDS_CONTROL_TEST
            tests/test_roots.cpp)

find_package(Eigen3 QUIET NO_MODULE)
if(NOT Eigen3_FOUND)
  message(STATUS "Eigen not found, fetching with FetchContent")

  FetchContent_Declare(
    eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG 3.4.0   
  )

  FetchContent_MakeAvailable(eigen)

endif()

add_library(tdscontrol STATIC ${TDS_CONTROL_HEADERS} ${TDS_CONTROL_SRC})
set_property(TARGET tdscontrol PROPERTY POSITION_INDEPENDENT_CODE ON)
target_include_directories(tdscontrol PUBLIC include)
target_link_libraries(tdscontrol PRIVATE Eigen3::Eigen)

add_executable(demo examples/demo.cpp)
target_link_libraries(demo tdscontrol)

if (PYTHON_BINDINGS)
    set(TDS_CONTROL_PY_BINDINGS
            src/py_bindings.cpp)

    # Add Python extension build using nanobind
    find_package(Python 3.9 REQUIRED COMPONENTS Interpreter Development.Module REQUIRED)
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
    find_package(nanobind CONFIG REQUIRED)

    nanobind_add_module(pytdscontrol MODULE ${TDS_CONTROL_PY_BINDINGS})
    target_link_libraries(pytdscontrol PUBLIC tdscontrol)

    # Install the compiled extension into the package dir inside the wheel
    install(TARGETS pytdscontrol
            LIBRARY DESTINATION "tdscontrol"    # Unix .so
            RUNTIME DESTINATION "tdscontrol")   # Windows .pyd/.dll
    install()
endif()

if (BUILD_TESTING)
    message(STATUS "Build tests")
    include(CTest)
    enable_testing()
    find_package(GTest REQUIRED)

    add_executable(test_tds ${TDS_CONTROL_TEST})
    target_link_libraries(test_tds PRIVATE GTest::gtest_main GTest::gmock tdscontrol)
    add_test(NAME test_tds COMMAND test_tds)
endif()