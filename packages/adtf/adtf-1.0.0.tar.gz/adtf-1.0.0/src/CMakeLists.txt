# Copyright 2025 Digitalwerk GmbH.
#
#     This Source Code Form is subject to the terms of the Mozilla
#     Public License, v. 2.0. If a copy of the MPL was not distributed
#     with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# If it is not possible or desirable to put the notice in a particular file, then
# You may include the notice in a location (such as a LICENSE file in a
# relevant directory) where a recipient would be likely to look for such a notice.
#
# You may add additional accurate notices of copyright ownership.

configure_file(version.py.in "${CMAKE_CURRENT_BINARY_DIR}/version.py")

string(MAKE_C_IDENTIFIER "v${SKBUILD_PROJECT_VERSION_FULL}" MODULE_RELEASE_ABI_VERSION)

add_library(adtf_system_python_bindings STATIC
        session.h
        session.cpp
        decoder.h
        decoder.cpp
        streaming_types.h
        streaming_types.cpp
        sample_streams.h
        sample_streams.cpp
        future.h
        future.cpp
        graph_utils_compat.h
)

target_link_libraries(adtf_system_python_bindings PUBLIC pybind11::module PRIVATE adtf::systemsdk adtf::filtersdk)
set_target_properties(adtf_system_python_bindings PROPERTIES POSITION_INDEPENDENT_CODE True)
target_include_directories(adtf_system_python_bindings PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)
target_compile_features(adtf_system_python_bindings PUBLIC cxx_std_17)
target_compile_definitions(adtf_system_python_bindings PUBLIC MODULE_RELEASE_ABI_VERSION=${MODULE_RELEASE_ABI_VERSION})

pybind11_add_module(_adtf MODULE adtf_python_module.cpp)
target_link_libraries(_adtf PRIVATE adtf_system_python_bindings Python::Python)

if(WIN32)
    set(original_pythonpath ";$ENV{PYTHONPATH}")
else()
    set(original_pythonpath ":$ENV{PYTHONPATH}")
endif ()
add_custom_command(TARGET _adtf POST_BUILD COMMAND ${CMAKE_COMMAND} -E env "PYTHONPATH=$<TARGET_FILE_DIR:_adtf>${original_pythonpath}" pybind11-stubgen -o "${CMAKE_CURRENT_BINARY_DIR}" --enum-class-locations LogLevel:_adtf.LogLevel --enum-class-locations Items:_adtf.Items _adtf)
install(TARGETS _adtf DESTINATION adtf COMPONENT adtf_python)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/_adtf.pyi" DESTINATION adtf COMPONENT adtf_python)
install(FILES py.typed __init__.py "${CMAKE_CURRENT_BINARY_DIR}/version.py" DESTINATION adtf COMPONENT adtf_python)

if(MSVC)
    install(FILES "$<TARGET_PDB_FILE:_adtf>" DESTINATION adtf
            CONFIGURATIONS "Debug" "RelWithDebInfo"
            COMPONENT adtf_python
    )
endif()
