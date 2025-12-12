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

#include "streaming_types.h"

#include "sample_streams.h"

#include <adtfstreaming3/sample.h>

#include <pybind11/chrono.h>

namespace py = pybind11;
using namespace std::literals;
using namespace adtf::ucom;
using namespace adtf::base;
using namespace adtf::streaming;

namespace adtf::python::MODULE_RELEASE_ABI_VERSION::detail
{
    void copy_properties(const IProperties& properties,
                         std::map<std::string, std::string>& map,
                         const std::string& prefix = {})
    {
        const auto fnVisitor = [&](const IProperty& property)
        {
            std::string name;
            property.GetName(adtf_string_intf(name));
            map.try_emplace(prefix + name, adtf::base::get_property_value<std::string>(
                                               *property.GetValue())); ///@todo do we need native types?
            object_ptr<const IProperties> children;
            if (property.HasProperties() && IS_OK(property.GetProperties(children)))
            {
                copy_properties(*children, map, name + "."s);
            }
        };

        visit_properties(properties, fnVisitor);
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION::detail

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    Trigger::Trigger(adtf::base::tNanoSeconds timestamp): timestamp(timestamp)
    {
    }

    Trigger::~Trigger() = default;

    StreamType::StreamType(object_ptr<const IStreamType> type): _type(type)
    {
    }

    StreamType::~StreamType() = default;

    std::string StreamType::meta_type() const
    {
        std::string name;
        _type->GetMetaTypeName(adtf_string_intf(name));
        return name;
    }

    std::map<std::string, std::string> StreamType::properties() const
    {
        // cache them?
        std::map<std::string, std::string> result;

        object_ptr<const IProperties> type_properties;
        if (IS_OK(_type->GetConfig(type_properties)))
        {
            detail::copy_properties(*type_properties, result);
        }

        return result;
    }

    py::object StreamType::substreams() const
    {
        if (!stream_meta_type_substreams::HasSubStreams(*_type))
        {
            return py::none();
        }

        std::vector<std::string> substreams;

        stream_meta_type_substreams::ListSubStreams(*_type.Get(), [&](std::string name)
                                                    { substreams.emplace_back(std::move(name)); });

        return py::cast(std::move(substreams));
    }

    SampleBuffer::SampleBuffer(const iobject_ptr<const ISample>& sample)
    {
        THROW_IF_FAILED(sample->Lock(_buffer));
    }

    SampleBuffer::~SampleBuffer() = default;

    DecodingState::DecodingState(object_ptr<const IStreamType> type): _type(std::move(type))
    {
    }

    DecodingState::~DecodingState()
    {
        if (std::holds_alternative<Substreams>(_streams))
        {
            py::gil_scoped_acquire gil_lock;
            std::get<Substreams>(_streams).names.clear();
        }
    }

    void DecodingState::initialize()
    {
        if (std::holds_alternative<std::monostate>(_streams))
        {
            if (stream_meta_type_substreams::HasSubStreams(*_type.Get()))
            {
                _streams.emplace<Substreams>();
                stream_meta_type_substreams::ListSubStreams(*_type.Get(), [&](std::string name, uint32_t id)
                    { std::get<Substreams>(_streams).names.emplace(id, py::cast(name)); });
            }
            else
            {
                _streams.emplace<Stream>();
            }
        }
    }

    pybind11::object DecodingState::get_name(uint32_t substream_id)
    {
        {
            std::scoped_lock lock(_mutex);
            initialize();
        }

        if (std::holds_alternative<Stream>(_streams))
        {
            return py::none();
        }

        return get_substream_name(substream_id);
    }

    object_ptr<const IStreamType> DecodingState::get_type(uint32_t substream_id)
    {
        {
            std::scoped_lock lock(_mutex);
            initialize();
        }

        if (std::holds_alternative<Stream>(_streams))
        {
            return _type;
        }

        return get_substream_type(substream_id);
    }

    Decoder* DecodingState::get_decoder(uint32_t substream_id)
    {
        std::scoped_lock lock(_mutex);

        initialize();

        if (std::holds_alternative<Stream>(_streams))
        {
            auto& stream_decoder = std::get<Stream>(_streams);
            if (!stream_decoder)
            {
                stream_decoder.emplace(create_decoder(_type));
            }
            return stream_decoder->get();
        }
        else
        {
            auto& substreams = std::get<Substreams>(_streams);
            auto decoder = substreams.decoders.find(substream_id);
            if (decoder == substreams.decoders.end())
            {
                decoder =
                    substreams.decoders.try_emplace(substream_id, create_decoder(get_substream_type(substream_id)))
                        .first;
            }

            return decoder->second.get();
        }
    }

    pybind11::object DecodingState::get_substream_name(uint32_t substream_id)
    {
        assert(std::holds_alternative<Substreams>(_streams));
        const auto& substreams = std::get<Substreams>(_streams);

        if (const auto name = substreams.names.find(substream_id); name != substreams.names.end())
        {
            return name->second;
        }

        THROW_ERROR_DESC(ERR_NOT_FOUND, "No substream with id %" PRIu32, substream_id);
    }

    object_ptr<const IStreamType> DecodingState::get_substream_type(uint32_t substream_id)
    {
        assert(std::holds_alternative<Substreams>(_streams));
        return stream_meta_type_substreams::GetSubStreamType(
            *_type, get_substream_name(substream_id).cast<std::string>().c_str());
    }

    Sample::Sample(object_ptr<const ISample> sample, std::shared_ptr<DecodingState> decoding_state):
        _sample(std::move(sample)),
        _decoding_state(std::move(decoding_state)),
        _substream_id(get_sample_substream_id(_sample))
    {
    }

    Sample::~Sample() = default;

    std::shared_ptr<StreamType> Sample::type() const
    {
        return std::make_shared<StreamType>(_decoding_state->get_type(_substream_id));
    }

    pybind11::object Sample::substream() const
    {
        return _decoding_state->get_name(_substream_id);
    }

    std::chrono::nanoseconds Sample::timestamp() const
    {
        return get_sample_time(_sample);
    }

    std::unique_ptr<SampleBuffer> Sample::buffer() const
    {
        return std::make_unique<SampleBuffer>(_sample);
    }

    py::object Sample::content() const
    {
        if (const auto decoder = _decoding_state->get_decoder(_substream_id))
        {
            return decoder->decode(_sample);
        }

        return py::none();
    }

    void add_streaming_types_bindings(pybind11::module& m)
    {
        py::class_<Trigger, py::smart_holder>(m, "Trigger")
            .def_readonly("timestamp", &Trigger::timestamp)
            .def("__repr__", [](const Trigger& trigger)
                 { return "<adtf.Trigger timestamp=" + std::to_string(trigger.timestamp.count()) + ">"; })
            .doc() = R"doc(Represents a trigger event on an ADTF stream.

Trigger items are emitted by :class:`SampleStream` when the ``Items.TRIGGERS``
flag is enabled in :meth:`Session.open_stream`. They carry timing information
but no payload data.)doc";

        py::class_<StreamType, py::smart_holder>(m, "StreamType")
            .def_property_readonly("meta_type", &StreamType::meta_type,
                                   "Name of the ADTF meta type (e.g. plain, ddl, string).")
            .def_property_readonly("properties", &StreamType::properties,
                                   "Flat dict of all stream type properties as ``str -> str``.")
            .def_property_readonly(
                "substreams", &StreamType::substreams,
                "List of available substream names, or ``None`` if the stream does not define substreams.")
            .def("__repr__",
                 [](const StreamType& type)
                 {
                     return "<adtf.StreamType meta_type=" + type.meta_type() +
                            " properties=" + py::str(py::cast(type.properties())).cast<std::string>() +
                            " substreams=" + py::str(type.substreams()).cast<std::string>() + ">";
                 })
            .doc() = R"doc(Describes the ADTF stream type of samples on a pin.

A `StreamType` instance contains metadata about a stream.
`StreamType` objects are typically obtained from:
- ``sample.type`` on a :class:`adtf.Sample` instance, or
- items yielded by a :class:`adtf.SampleStream` when ``Items.STREAMTYPES``
  are requested.)doc";

        py::class_<SampleBuffer, py::smart_holder>(m, "SampleBuffer", py::buffer_protocol())
            .def_buffer(
                [](const SampleBuffer& buffer)
                {
                    return py::buffer_info(const_cast<void*>(buffer._buffer->GetPtr()), sizeof(unsigned char),
                                           py::format_descriptor<unsigned char>::format(), buffer._buffer->GetSize(),
                                           true);
                })
            .doc() = R"doc(Exposes the raw bytes of an ADTF sample as a Python buffer.

`SampleBuffer` instances are usually obtained from :attr:`adtf.Sample.buffer`.
They implement the Python buffer protocol and can be used wherever a bytes-like
object is accepted, e.g.:

- ``memoryview(sample.buffer)``
- ``bytes(sample.buffer)``
- ``numpy.frombuffer(sample.buffer, dtype=...)``

The underlying content is the unmodified payload of the corresponding ADTF
sample.)doc";

        py::class_<Sample, py::smart_holder>(m, "Sample")
            .def_property_readonly("type", &Sample::type, "The `StreamType` of the sample.")
            .def_property_readonly("substream", &Sample::substream,
                                   "Name of the substream this sample belongs to, or `None` if not applicable.")
            .def_property_readonly(
                "timestamp", &Sample::timestamp,
                "ADTF timestamp of the sample as a `datetime.timedelta`-compatible duration (nanoseconds).")
            .def_property_readonly("buffer", &Sample::buffer, "A `SampleBuffer` exposing the raw bytes of the sample.")
            .def_property_readonly(
                "content", &Sample::content,
                "A decoded, Python-friendly representation of the sample payload if the format is supported (POD / "
                "plain types, DDL and string types). For structured data this is typically a nested object that can be "
                "accessed via attributes, e.g. `sample.content.my_parent.my_leaf_element`.")
            .def("__repr__",
                 [](const Sample& sample)
                 {
                     return "<adtf.Sample substream=" + py::str(sample.substream()).cast<std::string>() +
                            " timestamp=" + std::to_string(sample.timestamp().count()) +
                            " content=" + py::str(sample.content()).cast<std::string>() + ">";
                 })
            .doc() = R"doc(Represents a single data sample from an ADTF stream.

A Sample instance is typically obtained from `SampleStream.next_item()`.
If the payload format is not supported, `content` is `None` while `buffer` still exposes the raw data.)doc";
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION