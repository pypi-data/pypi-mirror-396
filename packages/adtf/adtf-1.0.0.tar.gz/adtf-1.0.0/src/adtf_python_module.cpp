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

#include "session.h"

PYBIND11_MODULE(_adtf, m)
{
    m.doc() =  R"(ADTF Python bindings.

This module provides the core building blocks to control ADTF runtime
sessions and to access data flowing through ADTF filter graphs.

The primary concepts exposed are:

- Session
    Owns a single ADTF runtime instance for a given environment and session
    file. It is a sync and async context manager that initializes and shuts
    down the ADTF system, and enforces that only one session is active per
    process.

- RunContext
    Context manager returned by ``Session.run()``. Entering it (sync or async)
    raises the ADTF runlevel to ``RL_Running`` and starts processing; leaving
    it brings the runlevel back to ``RL_FilterGraph`` while keeping the
    session initialized.

- SampleStream
    Represents a stream of items from a single ADTF output pin. It is a
    context manager created via ``Session.open_stream()`` and yields
    ``Sample``, ``StreamType`` and ``Trigger`` instances via
    ``SampleStream.next_item()``.

- Sample / StreamType / Trigger / SampleBuffer
    Data model types used to represent individual items from a stream:
      * ``Sample`` exposes a single data sample, including ``type``,
        ``substream``, ``timestamp``, ``buffer`` and decoded ``content``.
      * ``StreamType`` describes the meta type, properties and substreams of
        a stream.
      * ``Trigger`` represents timing events on a stream.
      * ``SampleBuffer`` exposes the raw bytes of a sample via the Python
        buffer protocol.

- Items
    Bitmask flags controlling which kinds of items (samples, stream types,
    triggers) a ``SampleStream`` should produce.

Typical usage is through the high-level ``adtf`` package:

    import asyncio
    from contextlib import ExitStack
    import adtf

    async def print_all_data():
        async with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
            async def print_items(stream):
                try:
                    while True:
                        async with stream.next_item() as item:
                            print(item)
                except EOFError:
                    pass

            from contextlib import ExitStack
            with ExitStack() as stack:
                streams = []
                for pin_name in session.output_pin_names:
                    stream = session.open_stream(pin_name)
                    streams.append(stream)
                    stack.enter_context(stream)

                async with session.run():
                    async with asyncio.TaskGroup() as task_group:
                        for stream in streams:
                            task_group.create_task(print_items(stream))

    asyncio.run(print_all_data())
)";
    adtf::python::MODULE_RELEASE_ABI_VERSION::add_session_bindings(m);
}
