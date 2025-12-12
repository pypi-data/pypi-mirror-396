import asyncio
import adtf
import sys
from collections.abc import Callable

# In this examples we are using the default ADTF environment and one of the delivered example sessions
adtf_runtime_directory = sys.argv[1]

with adtf.Session(adtf_runtime_directory + "/adtf.adtfenvironment",
                  adtf_runtime_directory + "/examples/demo_sessions/adtfsessions/How to work with substreams.adtfsession") as session:
    handlers: dict[str, Callable[[adtf.Sample], None]] = {
        "dissected.sHeaderStruct.ui32HeaderVal": lambda sample: print(sample),
        "dissected.sSimpleStruct.f64Val": lambda sample: print(sample)}

    with session.open_stream("substreams.Substream Merger.substreams", requests=handlers.keys(),
                             items=adtf.Items.SAMPLES) as processing_scope:
        async def run_session():
            async with session.run():
                try:
                    while True:
                        async with processing_scope as sample:
                            if sample.substream in handlers:
                                handlers[sample.substream](sample)
                except EOFError:
                    pass


        async def run_and_stop():
            run_task = asyncio.create_task(run_session())
            await asyncio.sleep(1)
            run_task.cancel()


        asyncio.run(run_and_stop())
