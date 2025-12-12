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
cmake_minimum_required(VERSION 4.1 FATAL_ERROR)
project(adtf_python_bindings VERSION 0.1.0)
find_package(Python COMPONENTS Development)
find_package(pybind11 REQUIRED)
find_package(adtf_sdk 3.21 REQUIRED COMPONENTS systemsdk filtersdk)

add_subdirectory(src)