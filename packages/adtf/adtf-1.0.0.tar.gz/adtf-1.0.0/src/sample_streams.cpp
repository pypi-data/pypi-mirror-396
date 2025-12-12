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

#include "sample_streams.h"
#include <pybind11/native_enum.h>

namespace py = pybind11;
using namespace std::literals;
using namespace adtf::ucom;
using namespace adtf::base;
using namespace adtf::streaming;

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    ProcessingScope::ProcessingScope(std::shared_ptr<ItemState> item_state): _item_state(std::move(item_state))
    {
    }

    ProcessingScope::~ProcessingScope()
    {
    }
    pybind11::object ProcessingScope::enter()
    {
        decltype(_item_state->_item) available_item;
        {
            py::gil_scoped_release gil_release;

            std::unique_lock lock(_item_state->_mutex);
            _item_state->_item_available.wait(lock, [&]() { return _item_state->_item || !_item_state->is_active(); });

            if (!_item_state->is_active())
            {
                py::gil_scoped_acquire gil_lock;
                pybind11::set_error(PyExc_EOFError, "");
                throw pybind11::error_already_set();
            }

            std::swap(_item_state->_item, available_item);
        }

        return std::visit([&](auto&& item) { return py::cast(std::move(item)); }, std::move(*available_item));
    }

    bool ProcessingScope::exit(const pybind11::handle&, const pybind11::handle&, const pybind11::handle&)
    {
        std::unique_lock lock(_item_state->_mutex);
        _item_state->_item_consumed = true;
        _item_state->_finished.notify_one();
        return false;
    }

    pybind11::object ProcessingScope::aenter()
    {
        auto future = EventLoop().create_future();
        const auto python_future = future.get();

        std::scoped_lock lock(_item_state->_mutex);
        assert(!_item_state->_item_awaited);
        if (_item_state->_item)
        {
            std::visit([&](auto&& item) { future.set_result(py::cast(std::move(item))); },
                       std::move(*_item_state->_item));
            _item_state->_item.reset();
        }
        else
        {
            _item_state->_item_awaited.emplace(std::move(future));
        }

        return python_future;
    }

    pybind11::object ProcessingScope::aexit(const py::handle& type, const py::handle& value, const py::handle& trace)
    {
        {
            std::scoped_lock lock(_item_state->_mutex);
            _item_state->_item_awaited.reset();
            _item_state->_item_consumed = true;
            _item_state->_finished.notify_one();
        }

        auto future = EventLoop().create_future();
        future.set_result(py::cast(false));

        return future.get();
    }

    ProcessingBridge::ProcessingBridge() = default;
    ProcessingBridge::~ProcessingBridge() = default;

    void ProcessingBridge::push(StreamItem item)
    {
        std::unique_lock lock(_item_state->_mutex);
        if (!_item_state->is_active())
        {
            return;
        }

        _item_state->_item_consumed = false;

        if (_item_state->_item_awaited)
        {
            // We cannot call schedule() below with the mutex held, because schedule() will release and re-acquire the
            // GIL internally, this will then lead to a deadlock because the lock order (GIL then mutex) is violated.
            Future future(std::move(*_item_state->_item_awaited));
            _item_state->_item_awaited.reset();
            lock.unlock();

            {
                py::gil_scoped_acquire gil_lock;
                auto loop = future.loop();
                loop.schedule()(std::function(
                    [item = std::move(item), future = std::move(future)]() mutable
                    {
                        if (!future.cancelled())
                        {
                            std::visit([&](auto&& item) { future.set_result(py::cast(std::move(item))); }, item);
                        }
                    }));
            }

            lock.lock();
        }
        else
        {
            _item_state->_item.emplace(std::move(item));
            _item_state->_item_available.notify_one();
        }

        _item_state->_finished.wait(lock, [&]() { return _item_state->_item_consumed || !_item_state->is_active(); });
    }

    std::unique_ptr<ProcessingScope> ProcessingBridge::enter()
    {
        {
            std::scoped_lock lock(_item_state->_mutex);
            if (_item_state->_processing_scope_active)
            {
                THROW_ERROR_DESC(ERR_RESOURCE_IN_USE, "A stream can only be entered once at a time.");
            }

            _item_state->_processing_scope_active = true;
        }
        return std::make_unique<ProcessingScope>(_item_state);
    }

    bool ProcessingBridge::exit(const pybind11::handle&, const pybind11::handle&, const pybind11::handle&)
    {
        deactivate(false);
        return false;
    }

    void ProcessingBridge::set_running(bool running)
    {
        if (running)
        {
            std::scoped_lock lock(_item_state->_mutex);
            _item_state->_running = true;
        }
        else
        {
            deactivate(true);
        }
    }

    void ProcessingBridge::deactivate(bool running_flag)
    {
        std::unique_lock lock(_item_state->_mutex);
        bool was_active = _item_state->is_active();

        if (running_flag)
        {
            _item_state->_running = false;
        }
        else
        {
            _item_state->_processing_scope_active = false;
        }

        if (was_active)
        {
            _item_state->_finished.notify_one();
            _item_state->_item_available.notify_one();
            if (_item_state->_item_awaited)
            {
                Future future(std::move(*_item_state->_item_awaited));
                _item_state->_item_awaited.reset();
                lock.unlock();

                py::gil_scoped_acquire gil_lock;
                auto loop = future.loop();
                loop.schedule()(std::function(
                    [future = std::move(future)]() mutable
                    {
                        if (!future.cancelled())
                        {
                            future.set_exception(py::module_::import("builtins").attr("EOFError")());
                        }
                    }));
            }
        }
    }

    StreamReader::StreamReader(Items items, std::optional<StreamReader::Requests> requests):
        _items(items), _requests(std::move(requests))
    {
        // we might outlive the adtf system
        _clock.Reset();

        _reader = CreateInputPin("input");
        _reader->SetSynchronousTypeUpdateCallback(
            [this](const adtf::ucom::iobject_ptr<const IStreamType>& type) -> tResult
            {
                _last_request_type = type;
                RETURN_IF_THROWS(update_requests());
                RETURN_NOERROR;
            });

        if (_requests && std::holds_alternative<RequestFilter>(*_requests))
        {
            _requests_event_loop.emplace();
        }
    }

    StreamReader::~StreamReader()
    {
        if (_requests)
        {
            py::gil_scoped_acquire gil_lock;
            _requests.reset();
            _requests_event_loop.reset();
        }
    }

    tResult StreamReader::Init(tInitStage eStage)
    {
        RETURN_IF_FAILED(cFilter::Init(eStage));
        if (eStage == StageGraphReady)
        {
            _connection_established = true;
        }
        RETURN_NOERROR;
    }

    tResult StreamReader::Start()
    {
        RETURN_IF_FAILED(cFilter::Start());
        set_running(true);
        RETURN_NOERROR;
    }

    tResult StreamReader::Stop()
    {
        set_running(false);
        return cFilter::Stop();
    }

    std::vector<std::string> StreamReader::requestable_substreams()
    {
        std::vector<std::string> substreams;
        if (_last_request_type && stream_meta_type_substreams::HasSubStreams(*_last_request_type))
        {
            stream_meta_type_substreams::ListSubStreams(*_last_request_type, [&](const char* substream)
                                                        { substreams.emplace_back(substream); });
        }
        return substreams;
    }

    void StreamReader::execute_requests(const std::vector<std::string>& substreams)
    {
        for (const auto& requested_substream : substreams)
        {
            try
            {
                object_ptr<IStreamingRequest> request;
                THROW_IF_FAILED(_reader->RequestSamples(
                    request,
                    stream_meta_type_substreams::GetSubStreamId(*_last_request_type, requested_substream.c_str())));
                _substream_requests.push_back(request);
            }
            catch (...)
            {
                const auto result = ADTF_UTIL_ANNOTATE_RESULT(
                    CURRENT_EXCEPTION(), "Unable to request substream, it might be available later on.");
                LOG_INFO("%s", adtf::util::detail::to_string(result).c_str());
            }
        }
    }

    void StreamReader::update_requests()
    {
        _substream_requests.clear();

        if (_requests)
        {
            if (const auto filter = std::get_if<RequestFilter>(&(*_requests)))
            {
                if (!_connection_established)
                {
                    // we are being called synchronously from python when the connection is established
                    execute_requests((*filter)(this->requestable_substreams()));
                }
                else
                {
                    std::promise<std::vector<std::string>> requested_substreams;

                    {
                        py::gil_scoped_acquire gil_lock;
                        _requests_event_loop->schedule()(std::function(
                            [&]() { requested_substreams.set_value((*filter)(this->requestable_substreams())); }));
                    }

                    execute_requests(requested_substreams.get_future().get());
                }
            }
            else
            {
                execute_requests(std::get<RequestList>(*_requests));
            }
        }
        else
        {
            if (_last_request_type && stream_meta_type_substreams::HasSubStreams(*_last_request_type))
            {
                stream_meta_type_substreams::ListSubStreams(*_last_request_type,
                                                            [&](const char* substream, uint32_t id)
                                                            {
                                                                object_ptr<IStreamingRequest> request;
                                                                THROW_IF_FAILED(_reader->RequestSamples(request, id));
                                                                _substream_requests.push_back(request);
                                                            });
            }
        }
    }

    tResult StreamReader::AcceptType(ISampleReader*, const adtf::ucom::iobject_ptr<const IStreamType>& type)
    {
        _decoding_state = std::make_shared<DecodingState>(type);

        if (_items & Items::STREAMTYPES)
        {
            push(std::make_shared<StreamType>(type));
        }
        RETURN_NOERROR;
    }

    tResult StreamReader::ProcessInput(tNanoSeconds trigger, ISampleReader* reader)
    {
        object_ptr<const ISample> sample;
        while (IS_OK(reader->GetNextSample(sample)))
        {
            if (_items & Items::SAMPLES)
            {
                push(std::make_shared<Sample>(sample, _decoding_state));
            }
        }

        if (_items & Items::TRIGGERS)
        {
            push(std::make_shared<Trigger>(trigger));
        }
        RETURN_NOERROR;
    }

    void add_sample_streams_bindings(pybind11::module& m)
    {
        py::class_<ProcessingScope, py::smart_holder>(m, "ProcessingScope")
            .def("__enter__", &ProcessingScope::enter,
                 "Enter scope, await start of processing interval and return the item to process.")
            .def("__exit__", &ProcessingScope::exit, "Exit scope and signal ADTF that processing is complete.")
            .def("__aenter__", &ProcessingScope::aenter,
                 "Enter scope, await start of processing interval and return the item to process.")
            .def("__aexit__", &ProcessingScope::aexit, "Exit scope and signal ADTF that processing is complete.")
            .doc() =
            R"doc(Reusable context manager that defines ADTF processing boundaries and yields the next item from the stream on each entry.

The ProcessingScope ensures ADTF's trigger-based scheduler waits until processing
is complete before resuming the schedule for this stream. Exiting the scope (either normally
or via exception) signals ADTF that processing has finished.

If the stream has reached the end of data entering the context raises
:class:`EOFError` instead of returning an item.

The item remains valid past the ProcessingScope, but any further processing will
be arbitrarily out of sync with ADTF's scheduler.

Example:
    try:
        while True:
            # We wait for ADTF to provide an item to process.
            with processing_scope as item:
                # ADTF waits while we're in this processing scope.
                ...
            # item is still valid, but processing would now be out-of-sync with ADTF.
    except EOFError:
        pass
)doc";

        py::native_enum<Items>(m, "Items", "enum.Flag")
            .value("STREAMTYPES", Items::STREAMTYPES)
            .value("SAMPLES", Items::SAMPLES)
            .value("TRIGGERS", Items::TRIGGERS)
            .value("ALL", Items::ALL)
            .finalize();

        py::class_<StreamReader, py::smart_holder>(m, "StreamReader")
            .def("__enter__", &StreamReader::enter, "Enter scope and delegate processing for this stream to Python.")
            .def("__exit__", &StreamReader::exit, "Exit scope and signal ADTF to run free again.")
            .doc() =
            R"doc("Context manager that holds an ADTF filter connected to the output of an arbitrary output pin."

Entering its context delegates processing of items (Sample, StreamType, Trigger) to Python.

A :class:`StreamReader` is created via :meth:`Session.open_stream` for a given
output pin of the active ADTF session. It acts as a context manager that
attaches a temporary internal filter to the graph and exposes incoming data
items one-by-one through the :class:`ProcessingScope`.

Typical synchronous usage:

    # We become responsible for processing items on this stream.
    with session.open_stream("my.filter.my_output") as processing_scope:
        # Start data streaming only after registering as a processor.
        # The other way around, data loss could occur at the start of the stream.
        with session.run() as run_guard:
            try:
                while True:
                    # We wait for ADTF to provide an item to process.
                    with processing_scope as item:
                        # ADTF waits while we're in this processing scope.
                        ...
                    # item is still valid, but processing would now be out-of-sync with ADTF.
            except EOFError:
                pass

Typical asynchronous usage:

    # We become responsible for processing items on this stream.
    with session.open_stream("my.filter.my_output") as processing_scope:
        # Start data streaming only after registering as a processor.
        # The other way around, data loss could occur at the start of the stream.
        async with session.run() as run_guard:
            try:
                while True:
                    # We wait for ADTF to provide an item to process.
                    async with processing_scope as item:
                        # ADTF waits while we're in this processing scope.
                        ...
                    # item is still valid, but processing would now be out-of-sync with ADTF.
            except EOFError:
                pass

Items
-----
The kind of items produced is controlled by the ``items`` flag passed to
:meth:`Session.open_stream` (see :class:`Items`):

- ``Items.SAMPLES``   – yield :class:`Sample` instances.
- ``Items.STREAMTYPES`` – yield :class:`StreamType` announcements.
- ``Items.TRIGGERS``  – yield :class:`Trigger` instances.
- ``Items.ALL``       – yield all of the above.

Requests
--------
The optional ``requests`` argument to :meth:`Session.open_stream` can be used
to select or modify which substreams are requested from ADTF. It can be:

- A list of substream names, or
- A callable ``fn(substreams: list[str]) -> list[str]`` that receives all
  available substreams and returns the subset to request.

Context nesting
---------------
Instances of StreamReader can only be obtained (via adtf.Session.open_stream()) outside of the context of :class:RunGuard.

Depending on the nesting order of the :class:RunGuard and the :class:ProcessingScope, the following can happen:

- When :class:RunGuard is entered before :class:ProcessingScope, items at the start of the stream may be lost.
- When :class:ProcessingScope is entered before :class:RunGuard, no items will be lost.
)doc";
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION