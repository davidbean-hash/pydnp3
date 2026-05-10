cmake_minimum_required(VERSION 3.15)

project(pydnp3 LANGUAGES CXX)
set(PYDNP3_MAJOR_VERSION 0)
set(PYDNP3_MINOR_VERSION 2)
set(PYDNP3_MICRO_VERSION 0)
set(PYDNP3_VERSION ${PYDNP3_MAJOR_VERSION}.${PYDNP3_MINOR_VERSION}.${PYDNP3_MICRO_VERSION})

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING
      "Choose the type of build, options are: Debug Release
RelWithDebInfo MinSizeRel."
      FORCE)
endif()

message(STATUS "CMake build is: ${CMAKE_BUILD_TYPE}")

# other options off-by-default that you can enable
option(WERROR "Set all warnings to errors" OFF)
option(STATICLIBS "Builds static versions of all installed libraries" OFF)
option(COVERAGE "Builds the libraries with coverage info for gcov (gcc only)" OFF)
option(PROFILE "Builds the libraries with profiling support (gcc only)" OFF)

set(CMAKE_REQUIRED_FLAGS ${CMAKE_CXX_FLAGS})

set(STATICLIBS ON)

if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden")
endif()

# Use pybind11 from pip (installed as build dependency) or fall back to submodule
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    message(STATUS "pybind11 not found via find_package, using submodule")
    add_subdirectory(deps/pybind11)
else()
    message(STATUS "Using installed pybind11 ${pybind11_VERSION}")
endif()

# Apply patch to dnp3 submodule if needed (adds missing #include <string>)
set(IMASTER_OPS_H "${CMAKE_CURRENT_SOURCE_DIR}/deps/dnp3/cpp/libs/include/asiodnp3/IMasterOperations.h")
file(READ "${IMASTER_OPS_H}" IMASTER_OPS_CONTENT)
string(FIND "${IMASTER_OPS_CONTENT}" "<string>" HAS_STRING_INCLUDE)
if(HAS_STRING_INCLUDE EQUAL -1)
    message(STATUS "Applying imasteroperations.patch to dnp3 submodule")
    execute_process(
        COMMAND git apply "${CMAKE_CURRENT_SOURCE_DIR}/imasteroperations.patch"
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/deps/dnp3"
        RESULT_VARIABLE PATCH_RESULT
    )
    if(NOT PATCH_RESULT EQUAL 0)
        message(WARNING "Failed to apply patch, build may fail")
    endif()
endif()

# Build the opendnp3 C++ library from submodule
add_subdirectory(deps/dnp3)

# include paths for all the local libraries
include_directories(deps/dnp3/cpp/libs/include)
include_directories(deps/dnp3/cpp/libs/src)

# asio
include_directories(deps/dnp3/deps/asio/asio/include)
add_definitions(-DASIO_STANDALONE)

pybind11_add_module(pydnp3 MODULE src/pydnp3.cpp src/pydnp3asiodnp3.cpp src/pydnp3asiopal.cpp src/pydnp3opendnp3.cpp src/pydnp3openpal.cpp)
target_link_libraries(pydnp3 PRIVATE asiopal asiodnp3 openpal opendnp3)

install(TARGETS pydnp3 LIBRARY DESTINATION .)
