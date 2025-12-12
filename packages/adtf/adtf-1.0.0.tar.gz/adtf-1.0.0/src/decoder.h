/**
 *
 * @file
 * Copyright 2025 Digitalwerk GmbH.
 *
 *     This Source Code Form is subject to the terms of the Mozilla
 *     Public License, v. 2.0. If a copy of the MPL was not distributed
 *     with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * If it is not possible or desirable to put the notice in a particular file, then
 * You may include the notice in a location (such as a LICENSE file in a
 * relevant directory) where a recipient would be likely to look for such a notice.
 *
 * You may add additional accurate notices of copyright ownership.
 */
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include <pybind11/functional.h>

#include <adtfstreaming3/sample_intf.h>
#include <adtfstreaming3/streamtype_intf.h>

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    class Decoder
    {
    public:
        virtual ~Decoder() = default;
        virtual pybind11::object decode(const adtf::ucom::iobject_ptr<const adtf::streaming::ISample>& sample) = 0;
    };

    std::unique_ptr<Decoder> create_decoder(const adtf::ucom::iobject_ptr<const adtf::streaming::IStreamType>& type);
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION