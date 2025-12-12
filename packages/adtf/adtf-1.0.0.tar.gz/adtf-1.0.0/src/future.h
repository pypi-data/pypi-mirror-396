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

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    class Future;

    class EventLoop
    {
    public:
        EventLoop();
        EventLoop(pybind11::object loop);
        EventLoop(const EventLoop&);
        EventLoop(EventLoop&&);
        ~EventLoop();

        EventLoop& operator=(const EventLoop&);
        EventLoop& operator=(EventLoop&&);

        pybind11::function schedule();
        Future create_future();

        bool operator!=(const EventLoop&) const noexcept;

    private:
        pybind11::object _event_loop;
    };

    class Future
    {
    public:
        Future(pybind11::object future);
        Future(const Future&);
        Future(Future&&);
        ~Future();

        Future& operator=(const Future&);
        Future& operator=(Future&&);

        pybind11::object get();

        void set_result(pybind11::object result);
        void set_exception(pybind11::object exception);
        void set_exception(std::exception_ptr error);
        void add_done_callback(std::function<void(const Future&)> callback);
        bool cancelled() const;
        pybind11::object exception() const;

        EventLoop loop();

    private:
        pybind11::object _future;
    };
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION