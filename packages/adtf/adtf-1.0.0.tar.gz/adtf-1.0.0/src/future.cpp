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
#include "future.h"
#include <pybind11/functional.h>
#include <adtf_utils.h>

namespace py = pybind11;

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    EventLoop::EventLoop(): EventLoop(py::module_::import("asyncio.events").attr("get_running_loop")())
    {
    }

    EventLoop::EventLoop(pybind11::object loop): _event_loop(std::move(loop))
    {
    }

    EventLoop::EventLoop(const EventLoop&) = default;
    EventLoop::EventLoop(EventLoop&&) = default;
    EventLoop::~EventLoop() = default;
    EventLoop& EventLoop::operator=(const EventLoop&) = default;
    EventLoop& EventLoop::operator=(EventLoop&&) = default;

    pybind11::function EventLoop::schedule()
    {
        return _event_loop.attr("call_soon_threadsafe");
    }

    Future EventLoop::create_future()
    {
        return Future(_event_loop.attr("create_future")());
    }

    bool EventLoop::operator!=(const EventLoop& other) const noexcept
    {
        return !_event_loop.is(other._event_loop);
    }

    Future::Future(py::object future): _future(std::move(future))
    {
    }

    Future::Future(const Future&) = default;
    Future::Future(Future&&) = default;
    Future::~Future() = default;
    Future& Future::operator=(const Future&) = default;
    Future& Future::operator=(Future&&) = default;

    pybind11::object Future::get()
    {
        return _future;
    }

    void Future::set_exception(py::object exception)
    {
        _future.attr("set_exception")(exception);
    }

    void Future::set_exception(std::exception_ptr error)
    {
        try
        {
            std::rethrow_exception(error);
        }
        catch (...)
        {
            auto exception = py::module_::import("builtins")
                                 .attr("RuntimeError")(py::cast(adtf::util::detail::current_exception_to_string()));
            set_exception(exception);
        }
    }

    void Future::set_result(py::object result)
    {
        _future.attr("set_result")(std::move(result));
    }

    void Future::add_done_callback(std::function<void(const Future&)> callback)
    {
        _future.attr("add_done_callback")(std::function<void(py::object)>(
            [callback = std::move(callback)](py::object future) { callback(Future(std::move(future))); }));
    }

    bool Future::cancelled() const
    {
        return _future.attr("cancelled")().cast<bool>();
    }

    pybind11::object Future::exception() const
    {
        return _future.attr("exception")();
    }

    EventLoop Future::loop()
    {
        return _future.attr("get_loop")();
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION