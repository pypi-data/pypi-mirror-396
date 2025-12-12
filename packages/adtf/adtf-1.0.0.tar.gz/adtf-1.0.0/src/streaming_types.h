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

#include "decoder.h"

#include <pybind11/pybind11.h>
#include <adtfstreaming3/sample_intf.h>
#include <adtfstreaming3/streamtype_intf.h>

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    struct Trigger final
    {
        Trigger() = delete;
        Trigger(const Trigger&) = delete;
        Trigger(Trigger&&) = delete;
        Trigger& operator=(const Trigger&) = delete;
        Trigger& operator=(Trigger&&) = delete;
        Trigger(adtf::base::tNanoSeconds timestamp);
        ~Trigger();

        std::chrono::nanoseconds timestamp;
    };

    class StreamType final
    {
    public:
        StreamType() = delete;
        StreamType(adtf::ucom::object_ptr<const adtf::streaming::IStreamType> type);
        StreamType(const StreamType&) = delete;
        StreamType(StreamType&&) = delete;
        ~StreamType();

        StreamType& operator=(const StreamType&) = delete;
        StreamType& operator=(StreamType&&) = delete;

        std::string meta_type() const;
        std::map<std::string, std::string> properties() const;
        pybind11::object substreams() const;

    private:
        adtf::ucom::object_ptr<const adtf::streaming::IStreamType> _type;
    };

    struct SampleBuffer final
    {
        SampleBuffer() = delete;
        SampleBuffer(const adtf::ucom::iobject_ptr<const adtf::streaming::ISample>& sample);
        SampleBuffer(const SampleBuffer&) = delete;
        SampleBuffer(SampleBuffer&&) = delete;
        ~SampleBuffer();

        SampleBuffer& operator=(const SampleBuffer&) = delete;
        SampleBuffer& operator=(SampleBuffer&&) = delete;

        adtf::ucom::object_ptr_shared_locked<const adtf::streaming::ISampleBuffer> _buffer;
    };

    class DecodingState final
    {
    public:
        DecodingState() = delete;
        DecodingState(adtf::ucom::object_ptr<const adtf::streaming::IStreamType> type);
        DecodingState(const DecodingState&) = delete;
        DecodingState(DecodingState&&) = delete;
        ~DecodingState();

        DecodingState& operator=(const DecodingState&) = delete;
        DecodingState& operator=(DecodingState&&) = delete;

        Decoder* get_decoder(uint32_t substream_id);
        adtf::ucom::object_ptr<const adtf::streaming::IStreamType> get_type(uint32_t substream_id);
        pybind11::object get_name(uint32_t substream_id);

    private:
        void initialize();
        pybind11::object get_substream_name(uint32_t substream_id);
        adtf::ucom::object_ptr<const adtf::streaming::IStreamType> get_substream_type(uint32_t substream_id);

        adtf::ucom::object_ptr<const adtf::streaming::IStreamType> _type;

        std::mutex _mutex;
        struct Substreams
        {
            std::unordered_map<uint32_t, pybind11::object> names;
            std::unordered_map<uint32_t, std::shared_ptr<Decoder>> decoders;
        };
        using Stream = std::optional<std::shared_ptr<Decoder>>;
        std::variant<std::monostate, Stream, Substreams> _streams;
    };

    class Sample final
    {
    public:
        Sample() = delete;
        Sample(adtf::ucom::object_ptr<const adtf::streaming::ISample> sample,
               std::shared_ptr<DecodingState> decoding_state);
        Sample(const Sample&) = delete;
        Sample(Sample&&) = delete;
        ~Sample();

        Sample& operator=(const Sample&) = delete;
        Sample& operator=(Sample&&) = delete;

        std::shared_ptr<StreamType> type() const;
        pybind11::object substream() const;
        std::chrono::nanoseconds timestamp() const;
        std::unique_ptr<SampleBuffer> buffer() const;

        pybind11::object content() const;

    private:
        adtf::ucom::object_ptr<const adtf::streaming::ISample> _sample;
        std::shared_ptr<DecodingState> _decoding_state;
        uint32_t _substream_id;
    };

    void add_streaming_types_bindings(pybind11::module& m);
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION
