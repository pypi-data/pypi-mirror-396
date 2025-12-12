ADTF Python Package
===================

This package provides Python bindings for the [ADTF](https://adtf.dev) framework.

It allows you to:

- launch and manage ADTF sessions directly from Python,
- asynchronously or synchronously run those sessions,
- open streams for output pins,
- receive samples, stream type announcements and trigger events as Python objects, and
- access decoded payload data in a Python-friendly way.

The public package is typically imported as:

```python
import adtf
```

Installation
------------

The package is distributed as a *source distribution* only. You therefore need:

- a working C/C++ compiler toolchain,
- an installed **ADTF runtime package** and an installed **ADTF sdk package** (both at least version `3.21.0`).

### Linux

```bash
adtf_sdk_DIR="<path to your ADTF sdk package>" adtf_runtime_DIR="<path to your ADTF runtime package>" pip install -i https://test.pypi.org/simple --extra-index-url https://pypi.org/simple adtf
```

### Windows:

```cmd.exe
cmd /C (set adtf_sdk_DIR="<path to your ADTF sdk package>" && set adtf_runtime_DIR="<path to your ADTF runtime package>" && pip install -i https://test.pypi.org/simple --extra-index-url https://pypi.org/simple adtf)
```

Using [virtual environments](https://docs.python.org/3/tutorial/venv.html) is strongly recommended.


Getting Started
---------------

```python
import adtf

help(adtf)  # show API documentation
```

### Creating a session

To create and initialize a session, instantiate `adtf.Session` with an ADTF
environment file (`.adtfenvironment`) and a session file (`.adtfsession`):

```python
with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
```

Only one `Session` can be active per process at a time.

### Inspecting available output pins

```python
with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
    for pin_name in session.output_pin_names:
        print(pin_name)
```

Each entry in `output_pin_names` corresponds to an output pin of the active
filter graph and can be opened as a `SampleStream`.


Working with Streams
--------------------

### Opening a stream

To access the data of an output pin, use `Session.open_stream()`:

```python
with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
    with session.open_stream("example.my_filter.output") as processing_scope:
```

If you want to access multiple streams at once, enter all their contexts (for
example using an `ExitStack`) before starting the session run context.

### Running the session (async recommended)

The recommended way to run a session is with `asyncio`:

```python
import asyncio
from contextlib import ExitStack
import adtf


async def run_session():
    with adtf.Session("my.adtfenvironment",
                      "my.adtfsession") as session:
        # open a stream for each output pin 
        with ExitStack() as stack:
            processing_scopes: list[adtf.ProcessingScope] = []
            for pin_name in session.output_pin_names:
                stream = session.open_stream(pin_name, lambda substreams: substreams)
                processing_scopes.append(stack.enter_context(stream))

            async def print_items(processing_scope: adtf.ProcessingScope):
                try:
                    while True:
                        async with processing_scope as item:
                            print(item)
                except EOFError:
                    # stream finished
                    pass

            # run the graph
            async with session.run():
                async with asyncio.TaskGroup() as tg:
                    for processing_scope in processing_scopes:
                        tg.create_task(print_items(processing_scope))


asyncio.run(run_session())
```

You can also use the synchronous context:

```python
with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
    with session.open_stream("example.my filter.output") as processing_scope:
        with session.run():
            try:
                while True:
                    with processing_scope as item:
                        print(item)
            except EOFError:
                pass
```

Stream Items and Data Access
----------------------------

Items retrieved by entering `ProcessingScope` can be:

- `adtf.Sample`
- `adtf.StreamType`
- `adtf.Trigger`

You may either filter by type in your code or restrict what you receive by
using the `items` argument to `Session.open_stream()`.

### `Sample`

A `Sample` represents a single data sample from a stream.

Properties:

- `.type` – a `StreamType` describing the stream’s meta type and properties.
- `.substream` – name of the substream this sample belongs to (or `None`).
- `.timestamp` – timestamp of the sample (nanoseconds, `datetime.timedelta`-compatible).
- `.buffer` – a `SampleBuffer` exposing the raw bytes of the sample.
- `.content` – decoded, Python-friendly view of the payload if the format is supported.

Supported content formats currently include:

- POD / plain types,
- DDL-based structured data, and
- strings.

For structured DDL data you typically access elements as nested attributes:
```python
value = sample.content.my_parent.my_leaf_element
```

### `StreamType`

A `StreamType` describes the type of a stream:

- `.meta_type` – name of the ADTF meta type.
- `.properties` – mapping of string property names to strings.
- `.substreams` – list of substream names or `None` if not applicable.

You will usually see `StreamType` instances at the beginning of a stream or
via `sample.type`.

### `Trigger`

A `Trigger` represents a timing event on a stream when data should be processed:

- `.timestamp` – trigger timestamp in nanoseconds (duration).

Triggers are produced when the `Items.TRIGGERS` flag is enabled for a stream.


Examples
--------

The `examples` directory contains small scripts that demonstrate typical usage:

- `playback.py` – playing back recorded data.
- `stream_access.py` – accessing stream items.
- `substream_access.py` – working with substreams and requests.

Use these as a starting point for integrating ADTF data into your own Python
applications.

Support and Further Reading
---------------------------

- ADTF homepage and documentation: https://adtf.dev
- Python `asyncio` documentation: https://docs.python.org/3/library/asyncio.html

For detailed API information, use `help(adtf)` in Python or inspect the
docstrings of individual classes like `Session`, `SampleStream`, `Sample`,
`StreamType`, and `Trigger`.

License
-------

This package uses the [MPL-2.0](LICENSE.md) license.

Release Notes
-------------

The release notes can be found at [RELEASENOTES.md](RELEASENOTES.md).