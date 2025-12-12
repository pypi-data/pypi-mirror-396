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
#include "streaming_types.h"
#include "future.h"
#include <pybind11/pybind11.h>
#include <adtfstreaming3/sample_intf.h>
#include <adtfstreaming3/streamtype_intf.h>
#include <adtffiltersdk/filter.h>

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    using StreamItem = std::variant<std::shared_ptr<Sample>, std::shared_ptr<StreamType>, std::shared_ptr<Trigger>>;

    struct ItemState
    {
        std::mutex _mutex;
        std::optional<Future> _item_awaited;
        std::condition_variable _item_available;
        std::condition_variable _finished;
        bool _item_consumed = false;
        std::optional<StreamItem> _item;

        bool _running = false;
        bool _processing_scope_active = false;
        bool is_active() const
        {
            return _running && _processing_scope_active;
        }
    };

    class ProcessingScope final
    {
    public:
        ProcessingScope(std::shared_ptr<ItemState> item_state);
        ProcessingScope(const ProcessingScope&) = delete;
        ProcessingScope(ProcessingScope&&) = delete;
        ~ProcessingScope();

        ProcessingScope& operator=(const ProcessingScope&) = delete;
        ProcessingScope& operator=(ProcessingScope&&) = delete;

        pybind11::object enter();
        bool exit(const pybind11::handle&, const pybind11::handle&, const pybind11::handle&);

        pybind11::object aenter();
        pybind11::object
            aexit(const pybind11::handle& type, const pybind11::handle& value, const pybind11::handle& trace);

    private:
        std::shared_ptr<ItemState> _item_state;
    };

    enum Items
    {
        STREAMTYPES = 1,
        SAMPLES = 2,
        TRIGGERS = 4,
        ALL = STREAMTYPES | SAMPLES | TRIGGERS
    };

    class ProcessingBridge
    {
    public:
        ProcessingBridge();
        ProcessingBridge(const ProcessingBridge&) = delete;
        ProcessingBridge(ProcessingBridge&&) = delete;
        ~ProcessingBridge();

        ProcessingBridge& operator=(const ProcessingBridge&) = delete;
        ProcessingBridge& operator=(ProcessingBridge&&) = delete;

        void push(StreamItem item);

        std::unique_ptr<ProcessingScope> enter();
        bool exit(const pybind11::handle&, const pybind11::handle&, const pybind11::handle&);

        void set_running(bool running);

    private:
        void deactivate(bool running_flag);
        std::shared_ptr<ItemState> _item_state = std::make_shared<ItemState>();
    };

    class StreamReader final :
        public adtf::filter::cFilter,
        public ProcessingBridge,
        public std::enable_shared_from_this<StreamReader>
    {
    public:
        using RequestFilter = std::function<std::vector<std::string>(const std::vector<std::string>&)>;
        using RequestList = std::vector<std::string>;
        using Requests = std::variant<RequestList, RequestFilter>;
        StreamReader(Items items, std::optional<StreamReader::Requests> requests);
        StreamReader(const StreamReader&) = delete;
        StreamReader(StreamReader&&) = delete;
        ~StreamReader() override;

        StreamReader& operator=(const StreamReader&) = delete;
        StreamReader& operator=(StreamReader&&) = delete;

        tResult Init(tInitStage eStage) override;
        tResult Start() override;
        tResult Stop() override;

        tResult AcceptType(adtf::streaming::ISampleReader*,
                           const adtf::ucom::iobject_ptr<const adtf::streaming::IStreamType>& type) override;
        tResult ProcessInput(adtf::base::tNanoSeconds trigger, adtf::streaming::ISampleReader* reader) override;

    private:
        std::vector<std::string> requestable_substreams();
        void execute_requests(const std::vector<std::string>& substreams);
        void update_requests();

        Items _items;
        adtf::streaming::cDynamicSampleReader* _reader = nullptr;

        std::optional<Requests> _requests;
        std::optional<EventLoop> _requests_event_loop;

        adtf::ucom::object_ptr<const adtf::streaming::IStreamType> _last_request_type;
        std::vector<adtf::ucom::object_ptr<adtf::streaming::IStreamingRequest>> _substream_requests;

        std::shared_ptr<DecodingState> _decoding_state;
        bool _connection_established = false;
    };

    void add_sample_streams_bindings(pybind11::module& m);
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION