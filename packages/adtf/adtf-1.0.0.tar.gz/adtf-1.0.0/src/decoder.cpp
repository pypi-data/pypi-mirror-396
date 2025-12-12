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

#include "decoder.h"
#include <adtfstreaming3/sample.h>
#include <adtfstreaming3/sample_data.h>
#include <adtfstreaming3/streamtype.h>
#include <adtfmediadescription/adtf_mediadescription.h>

namespace py = pybind11;
using namespace std::literals;
using namespace adtf::ucom;
using namespace adtf::base;
using namespace adtf::streaming;

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    class DDLDecoder final : public Decoder
    {
    public:
        DDLDecoder() = delete;
        DDLDecoder(const iobject_ptr<const IStreamType>& stream_type)
        {
            const auto [name, ddl, rep] =
                adtf::mediadescription::get_media_description_from_stream_type(*stream_type.Get());
            _representation = rep;
            _factory = ddl::codec::CodecFactory(name, ddl);
        }

        DDLDecoder(const DDLDecoder&) = delete;
        DDLDecoder(DDLDecoder&&) = delete;

        DDLDecoder& operator=(const DDLDecoder&) = delete;
        DDLDecoder& operator=(DDLDecoder&&) = delete;

        py::object decode(const iobject_ptr<const ISample>& sample) override
        {
            sample_data<std::byte> sample_data(sample);
            const auto decoder =
                _factory.makeStaticDecoderFor(sample_data.GetDataPtr(), sample_data.GetDataSize(), _representation);
            return decode_elements(decoder.getElements());
        }

    private:
        py::object variant_to_py(const a_util::variant::Variant& value)
        {
            using namespace a_util::variant;
            switch (value.getType())
            {
                case VT_Bool: return py::cast(value.asBool()); break;
                case VT_Int8: return py::cast(value.asInt8()); break;
                case VT_UInt8: return py::cast(value.asUInt8()); break;
                case VT_Int16: return py::cast(value.asInt16()); break;
                case VT_UInt16: return py::cast(value.asUInt16()); break;
                case VT_Int32: return py::cast(value.asInt32()); break;
                case VT_UInt32: return py::cast(value.asUInt32()); break;
                case VT_Int64: return py::cast(value.asInt64()); break;
                case VT_UInt64: return py::cast(value.asUInt64()); break;
                case VT_Float32: return py::cast(value.asFloat()); break;
                case VT_Float64: return py::cast(value.asDouble()); break;
                default: throw std::runtime_error("unsupported type");
            }
        }

        py::object decode_element(const ddl::codec::StaticDecoder::Element& element)
        {
            switch (element.getType())
            {
                case ddl::codec::ElementType::cet_sub_codec:
                {
                    return decode_elements(element.getChildElements());
                }
                default:
                {
                    return variant_to_py(element.getVariantValue());
                }
            }
        }

        py::object decode_elements(const ddl::codec::StaticDecoder::Elements& elements)
        {
            py::object decoded_element = py::module_::import("types").attr("SimpleNamespace")();
            for (const auto& element : elements)
            {
                py::object attribute;
                if (element.getArraySize() > 1)
                {
                    py::list array;
                    for (size_t array_index = 0; array_index < element.getArraySize(); ++array_index)
                    {
                        array.append(decode_element(element.getArrayElement(array_index)));
                    }
                    attribute = array;
                }
                else
                {
                    attribute = decode_element(element);
                }

                decoded_element.attr(element.getBaseName().c_str()) = attribute;
            }

            return decoded_element;
        }

        ddl::codec::CodecFactory _factory;
        ddl::tDataRepresentation _representation;
    };

    class StringDecoder final : public Decoder
    {
    public:
        StringDecoder() = delete;
        StringDecoder(const iobject_ptr<const IStreamType>& stream_type)
        {
            const auto encoding = stream_meta_type_string::GetEncodingType(*stream_type.Get());
            if (encoding == stream_meta_type_string::EncodingType::w_char_16 ||
                encoding == stream_meta_type_string::EncodingType::utf16)
            {
                _words = true;
                const auto data_endianess =
                    get_property<uint8_t>(*stream_type.Get(), stream_meta_type_string::DataEndianess);
                if (PLATFORM_BYTEORDER != data_endianess)
                {
                    _swap = true;
                }
            }
        }

        StringDecoder(const StringDecoder&) = delete;
        StringDecoder(StringDecoder&&) = delete;

        StringDecoder& operator=(const StringDecoder&) = delete;
        StringDecoder& operator=(StringDecoder&&) = delete;

        py::object decode(const iobject_ptr<const ISample>& sample) override
        {
            if (_words)
            {
                sample_data<char16_t> buffer(sample);
                if (_swap)
                {
                    const auto word_count = buffer.GetDataSize() / sizeof(char16_t);
                    std::u16string result(word_count, 0);

                    for (auto character_index = 0ull; character_index < word_count; ++character_index)
                    {
                        const auto value = buffer.GetDataPtr()[character_index];
                        result[character_index] = (value >> 8) | (value << 8);
                    }

                    return py::cast(result);
                }
                else
                {
                    return py::cast(std::u16string(buffer.GetDataPtr(), buffer.GetDataSize() / sizeof(wchar_t)));
                }
            }
            else
            {
                sample_data<char> buffer(sample);
                return py::cast(std::string(buffer.GetDataPtr(), buffer.GetDataSize()));
            }
        }

    private:
        bool _words = false;
        bool _swap = false;
    };

    class PlainDecoder final : public Decoder
    {
    public:
        PlainDecoder() = delete;
        PlainDecoder(const iobject_ptr<const IStreamType>& stream_type)
        {
            const auto plaintype =
                get_property<std::string>(*stream_type.Get(), stream_meta_type_plain::PlainTypeProperty);
            _decoder = _type_decoders.at(plaintype).get();
        }

        PlainDecoder(const PlainDecoder&) = delete;
        PlainDecoder(PlainDecoder&&) = delete;

        PlainDecoder& operator=(const PlainDecoder&) = delete;
        PlainDecoder& operator=(PlainDecoder&&) = delete;

        py::object decode(const iobject_ptr<const ISample>& sample) override
        {
            return _decoder->decode(sample);
        }

    private:
        template<typename T>
        class plain_decoder : public Decoder
        {
            py::object decode(const iobject_ptr<const ISample>& sample) override
            {
                return py::cast(sample_data<T>(sample).GetData());
            }
        };

        template<typename T>
        class plain_array_decoder : public Decoder
        {
            py::object decode(const iobject_ptr<const ISample>& sample) override
            {
                return py::cast(sample_data<std::vector<T>>(sample).GetData());
            }
        };

        class bool_array_decoder : public Decoder
        {
            py::object decode(const iobject_ptr<const ISample>& sample) override
            {
                sample_data<bool> bools(sample);
                std::vector<bool> result(bools.GetDataPtr(), bools.GetDataPtr() + bools.GetDataSize());
                return py::cast(std::move(result));
            }
        };

        static inline std::unordered_map<std::string, std::shared_ptr<Decoder>> _type_decoders = {
            {"UINT8"s, std::make_shared<plain_decoder<uint8_t>>()},
            {"INT8"s, std::make_shared<plain_decoder<int8_t>>()},
            {"UINT16"s, std::make_shared<plain_decoder<uint16_t>>()},
            {"INT16"s, std::make_shared<plain_decoder<int16_t>>()},
            {"UINT32"s, std::make_shared<plain_decoder<uint32_t>>()},
            {"INT32"s, std::make_shared<plain_decoder<int32_t>>()},
            {"UINT64"s, std::make_shared<plain_decoder<uint64_t>>()},
            {"INT64"s, std::make_shared<plain_decoder<int64_t>>()},
            {"FLOAT32"s, std::make_shared<plain_decoder<float>>()},
            {"FLOAT64"s, std::make_shared<plain_decoder<double>>()},
            {"BOOL"s, std::make_shared<plain_decoder<bool>>()},
            {"UINT8_ARRAY"s, std::make_shared<plain_array_decoder<uint8_t>>()},
            {"INT8_ARRAY"s, std::make_shared<plain_array_decoder<int8_t>>()},
            {"UINT16_ARRAY"s, std::make_shared<plain_array_decoder<uint16_t>>()},
            {"INT16_ARRAY"s, std::make_shared<plain_array_decoder<int16_t>>()},
            {"UINT32_ARRAY"s, std::make_shared<plain_array_decoder<uint32_t>>()},
            {"INT32_ARRAY"s, std::make_shared<plain_array_decoder<int32_t>>()},
            {"UINT64_ARRAY"s, std::make_shared<plain_array_decoder<uint64_t>>()},
            {"INT64_ARRAY"s, std::make_shared<plain_array_decoder<int64_t>>()},
            {"FLOAT32_ARRAY"s, std::make_shared<plain_array_decoder<float>>()},
            {"FLOAT64_ARRAY"s, std::make_shared<plain_array_decoder<double>>()},
            {"BOOL_ARRAY"s, std::make_shared<bool_array_decoder>()},
        };

        Decoder* _decoder = nullptr;
    };

    std::unique_ptr<Decoder> create_decoder(const adtf::ucom::iobject_ptr<const adtf::streaming::IStreamType>& type)
    {
        std::string stream_meta_type;
        type->GetMetaTypeName(adtf_string_intf(stream_meta_type));
        if (stream_meta_type == stream_meta_type_string::MetaTypeName)
        {
            return std::make_unique<StringDecoder>(type);
        }
        else if (stream_meta_type == stream_meta_type_plain::MetaTypeName)
        {
            return std::make_unique<PlainDecoder>(type);
        }

        object_ptr<const IProperties> properties;
        if (IS_OK(type->GetConfig(properties)) &&
            properties->Exists(adtf::mediadescription::stream_meta_type_default::strMDDefinitionsProperty))
        {
            return std::make_unique<DDLDecoder>(type);
        }

        return {};
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION