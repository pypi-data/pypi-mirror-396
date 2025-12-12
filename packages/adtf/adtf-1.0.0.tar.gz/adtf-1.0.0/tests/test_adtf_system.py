import asyncio
from contextlib import ExitStack

import adtf
import os
import pytest
import time
import threading
import queue


def test_invalid_session_sync():
    with pytest.raises(RuntimeError):
        with adtf.Session("na", "na"):
            pass


def test_invalid_session_async():
    async def run():
        with pytest.raises(RuntimeError):
            async with adtf.Session("na", "na"):
                pass

    asyncio.run(run())


adtf_runtime_dir = os.environ["adtf_runtime_DIR"]
adtf_environment = adtf_runtime_dir + "/adtf.adtfenvironment"


def create_test_session(session_name: str = "How to work with substreams"):
    return adtf.Session(adtf_environment,
                        adtf_runtime_dir + "/examples/demo_sessions/adtfsessions/" + session_name + ".adtfsession",
                        log_level=adtf.LogLevel.WARNING)


def test_session_creation():
    with create_test_session():
        with pytest.raises(RuntimeError):
            with create_test_session():
                pass

    with create_test_session() as session:
        for output_pin in session.output_pin_names:
            print(output_pin)

        with session.run():
            time.sleep(1)

        async def main():
            async with session.run():
                await asyncio.sleep(1)

        asyncio.run(main())


def test_session_after_context_exit():
    def check_session_closed(session: adtf.Session):
        with pytest.raises(RuntimeError):
            session.output_pin_names
        with pytest.raises(RuntimeError):
            session.open_stream("foo")
        with pytest.raises(RuntimeError):
            session.graph_object_names
        with pytest.raises(RuntimeError):
            session.run()

    session = create_test_session()
    check_session_closed(session)
    with session:
        pass
    check_session_closed(session)


test_session = os.path.dirname(
    os.path.abspath(__file__)) + "/adtf_test_sessions/adtfsessions/adtf_test_sessions.adtfsession"


def test_init_error_sync():
    with pytest.raises(RuntimeError):
        with adtf.Session(adtf_environment, test_session, "init_error") as session:
            pass


def test_init_error_async():
    with pytest.raises(RuntimeError):
        async def run():
            async with adtf.Session(adtf_environment, test_session, "init_error") as session:
                pass

        asyncio.run(run())


def test_start_error_sync():
    created = False
    with pytest.raises(RuntimeError):
        with adtf.Session(adtf_environment, test_session, "start_error") as session:
            created = True
            with session.run():
                pass
    assert created


def test_start_error_async():
    created = False

    with pytest.raises(RuntimeError):
        async def run():
            nonlocal created
            async with adtf.Session(adtf_environment, test_session, "start_error") as session:
                created = True
                async with session.run():
                    pass

        asyncio.run(run())

    assert created


def test_invalid_open_stream():
    with pytest.raises(RuntimeError):
        create_test_session().open_stream("substreams.Substream Merger.substreams")
    with create_test_session() as session:
        with pytest.raises(RuntimeError):
            session.open_stream("substreams.Substream Merger.not_existing_pin")
        with pytest.raises(RuntimeError):
            session.open_stream("substreams.not_existing_filter.not_existing_pin")
            with session.run():
                with pytest.raises(RuntimeError):
                    session.open_stream("substreams.Substream Merger.substreams")


class MyException(Exception):
    pass


def test_exception_in_run_sync():
    with pytest.raises(MyException):
        with create_test_session() as session:
            with session.open_stream("substreams.Substream Merger.substreams"):
                with session.run():
                    raise MyException


def test_exception_in_run_async():
    with pytest.raises(MyException):
        async def run():
            async with create_test_session() as session:
                with session.open_stream("substreams.Substream Merger.substreams"):
                    async with session.run():
                        raise MyException

        asyncio.run(run())


def test_multiple_streams_on_same_pin():
    with create_test_session() as session:
        with session.open_stream("substreams.Substream Merger.substreams",
                                 items=adtf.Items.STREAMTYPES) as stream1_processing_scope:
            with session.open_stream("substreams.Substream Merger.substreams",
                                     items=adtf.Items.SAMPLES) as stream2_processing_scope:
                with session.open_stream("substreams.Substream Merger.substreams",
                                         items=adtf.Items.TRIGGERS) as stream3_processing_scope:
                    with session.open_stream("substreams.Substream Merger.substreams",
                                             items=adtf.Items.SAMPLES | adtf.Items.TRIGGERS) as stream4_processing_scope:

                        stream_type_count = 0
                        sample_count = 0
                        trigger_count = 0

                        async def check_types(stream: adtf.StreamReader, expected_type: adtf.Items):
                            nonlocal stream_type_count
                            nonlocal sample_count
                            nonlocal trigger_count
                            try:
                                while True:
                                    async with stream as item:
                                        if expected_type is adtf.Items.STREAMTYPES:
                                            assert type(item) is adtf.StreamType
                                            stream_type_count += 1
                                        if expected_type is adtf.Items.SAMPLES:
                                            assert type(item) is adtf.Sample
                                            sample_count += 1
                                        if expected_type is adtf.Items.TRIGGERS:
                                            assert type(item) is adtf.Trigger
                                            trigger_count += 1
                            except EOFError:
                                pass

                        async def check_sample_or_triggers(stream: adtf.StreamReader):
                            try:
                                while True:
                                    async with stream as item:
                                        assert type(item) is adtf.Sample or type(item) is adtf.Trigger
                            except EOFError:
                                pass

                        async def check_all_items():
                            async with session.run():
                                checks = asyncio.gather(check_types(stream1_processing_scope, adtf.Items.STREAMTYPES),
                                                        check_types(stream2_processing_scope, adtf.Items.SAMPLES),
                                                        check_types(stream3_processing_scope, adtf.Items.TRIGGERS),
                                                        check_sample_or_triggers(stream4_processing_scope))
                                await asyncio.sleep(2)
                                checks.cancel()

                        asyncio.run(check_all_items())

                        assert stream_type_count > 0
                        assert sample_count > 0
                        assert trigger_count > 0


async def dump_all_items(session: adtf.Session, adtf_started_running: asyncio.Future = None):
    async with session:
        async def print_items(processing_scope: adtf.ProcessingScope):
            global item_count
            try:
                while True:
                    async with processing_scope as item:
                        if type(item) is adtf.StreamType:
                            print(item.meta_type)
                            print(item.properties)
                            print(item.substreams)
                        elif type(item) is adtf.Sample:
                            print(item.type)
                            print(item.timestamp)
                            print(item.substream)
                            print(item.content)
                            print(item.buffer)
                        elif type(item) is adtf.Trigger:
                            print(item.timestamp)
                        else:
                            assert False, f"unexpected item type: {type(item)}"
                        item_count += 1
            except EOFError:
                pass

        with ExitStack() as stack:
            processing_scopes: list[adtf.ProcessingScope] = []
            for pin_name in session.output_pin_names:
                stream = session.open_stream(pin_name, lambda substreams: substreams)
                processing_scopes.append(stack.enter_context(stream))

            async with session.run():
                # python 3.9 has no asyncio.TaskGroup yet.
                tasks: list[asyncio.Task] = []
                for processing_scope in processing_scopes:
                    tasks.append(asyncio.create_task(print_items(processing_scope)))
                if not adtf_started_running is None:
                    adtf_started_running.set_result(None)
                await asyncio.wait(tasks)


def test_live():
    global item_count
    item_count = 0

    async def main():
        adtf_started_running = asyncio.get_running_loop().create_future()
        run_task = asyncio.create_task(dump_all_items(create_test_session(), adtf_started_running))
        await adtf_started_running
        await asyncio.sleep(2)
        print("stopping")
        run_task.cancel()

    asyncio.run(main())
    assert item_count > 20


def test_playback():
    global item_count
    item_count = 0

    async def main():
        await dump_all_items(create_test_session("How to play back adtfdat files"))

    asyncio.run(main())
    assert item_count == 1471


def test_sync_playback():
    nested_struct_item_count = 0
    with create_test_session("How to play back adtfdat files") as session:
        with session.open_stream("single.Player.NESTED_STRUCT") as processing_scope:
            with session.run():
                try:
                    while True:
                        with processing_scope as item:
                            nested_struct_item_count += 1
                            print(item)
                except EOFError:
                    pass

    assert nested_struct_item_count == 596


def test_nesting_order():
    with create_test_session() as session:
        with session.open_stream("substreams.Substream Merger.substreams") as processing_scope:
            with session.run():
                with processing_scope as item:
                    print(item)

    with create_test_session() as session:
        reader = session.open_stream("substreams.Substream Merger.substreams")
        with session.run():
            with reader as processing_scope:
                with processing_scope as item:
                    print(item)


def test_string_decoder():
    with adtf.Session(adtf_runtime_dir + "/adtf.adtfenvironment", os.path.dirname(
            os.path.abspath(__file__)) + "/adtf_test_sessions/adtfsessions/adtf_test_sessions.adtfsession",
                      "strings") as session:
        with session.open_stream("strings.Demo String Sending.out_string", items=adtf.Items.SAMPLES) as stream_8bit:
            with session.open_stream("strings.Demo String Sending.out_16string",
                                     items=adtf.Items.SAMPLES) as stream_16bit:
                with session.run():
                    with stream_8bit as sample_8bit:
                        assert sample_8bit.content.startswith("Hello, current trigger time is")
                    with stream_16bit as sample_16bit:
                        assert sample_16bit.content.startswith("Hello, current trigger time is")


class AdtfHandler:
    def __init__(self):
        self.session = None
        self.stream = None
        self.processing_scope = None
        self.run_context = None

    def initialize(self):
        self.session = create_test_session()
        self.session.__enter__()
        try:
            self.stream = self.session.open_stream("substreams.Substream Merger.substreams",
                                                   requests=["dissected.sHeaderStruct.ui32HeaderVal",
                                                             "dissected.sSimpleStruct.f64Val"],
                                                   items=adtf.Items.SAMPLES)
            self.processing_scope = self.stream.__enter__()
            try:
                self.run_context = self.session.run()
                self.run_context.__enter__()
            except:
                self.stream.__exit__(None, None, None)
                raise

        except:
            self.session.__exit__(None, None, None)
            raise

    def deinitialize(self):
        self.run_context.__exit__(None, None, None)
        self.processing_scope = None
        self.stream.__exit__(None, None, None)
        self.session.__exit__(None, None, None)

    def get_data(self):
        # this will block until a sample becomes available
        with self.processing_scope as sample:
            return sample


def test_manual_context():
    handler = AdtfHandler()
    handler.initialize()
    print(handler.get_data())
    print(handler.get_data())
    handler.deinitialize()


class ThreadedAdtfHandler:
    def __init__(self):
        self.queue = queue.Queue(10)
        self.loop = None
        self.task = None
        self.thread = None

    async def _run_session(self):
        with create_test_session() as session:
            with session.open_stream("substreams.Substream Merger.substreams",
                                     requests=["dissected.sHeaderStruct.ui32HeaderVal",
                                               "dissected.sSimpleStruct.f64Val"],
                                     items=adtf.Items.SAMPLES) as processing_scope:
                async with session.run():
                    try:
                        while True:
                            async with processing_scope as sample:
                                self.queue.put(sample)
                    except EOFError:
                        pass

    def run_in_thread(self):
        try:
            self.loop.run_until_complete(self.task)
        except asyncio.exceptions.CancelledError:
            pass

    def initialize(self):
        self.loop = asyncio.new_event_loop()
        self.task = self.loop.create_task(self._run_session())
        self.thread = threading.Thread(target=self.run_in_thread)
        self.thread.start()

    def deinitialize(self):
        self.loop.call_soon_threadsafe(self.task.cancel)
        self.thread.join()
        self.loop.close()

    def get_data(self):
        return self.queue.get()


def test_session_in_thread():
    handler = ThreadedAdtfHandler()
    handler.initialize()
    print(handler.get_data())
    print(handler.get_data())
    handler.deinitialize()


class GeneratorAdtfHandler:
    def __init__(self):
        self.iterator = self.sample_generator().__iter__()

    def sample_generator(self):
        with create_test_session() as session:
            with session.open_stream("substreams.Substream Merger.substreams",
                                     requests=["dissected.sHeaderStruct.ui32HeaderVal",
                                               "dissected.sSimpleStruct.f64Val"],
                                     items=adtf.Items.SAMPLES) as processing_scope:
                with session.run():
                    # this allows us to run the initialization up until this point
                    yield None
                    try:
                        while True:
                            with processing_scope as sample:
                                yield sample
                    except EOFError:
                        pass

    def initialize(self):
        self.iterator.__next__()

    def get_data(self):
        return self.iterator.__next__()


# This one needs to be the last test because we do not know when the generator will be garbage collected
def test_polling_with_generator():
    handler = GeneratorAdtfHandler()
    handler.initialize()
    print(handler.get_data())
    print(handler.get_data())

# def test_concurrent_streams_mixed_mode():
#     """Verify concurrent processing with mixed sync/async"""
#
#     async def main():
#         async with create_test_session() as session:
#             stream1 = session.open_stream("substreams.Substream Merger.substreams")
#             stream2 = session.open_stream("substreams.Substream Merger.substreams")
#
#             with stream1, stream2:
#                 async with session.run():
#                     results = []
#
#                     async def async_processor():
#                         async with stream1.next_item():
#                             results.append("async")
#
#                     async def sync_processor():
#                         # Run sync in thread to avoid blocking
#                         def sync_work():
#                             with stream2.next_item():
#                                 results.append("sync")
#
#                         await asyncio.to_thread(sync_work)
#
#                     await asyncio.gather(async_processor(), sync_processor())
#
#                     assert "async" in results
#                     assert "sync" in results
#
#     asyncio.run(main())
