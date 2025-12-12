import asyncio
import adtf
import sys

# In this examples we are using the default ADTF environment and one of the delivered example sessions
adtf_runtime_directory = sys.argv[1]

with adtf.Session(adtf_runtime_directory + "/adtf.adtfenvironment",
                  adtf_runtime_directory + "/examples/demo_sessions/adtfsessions/How to trigger data streaming.adtfsession") as session:
    print(session.output_pin_names)

    with session.open_stream("every_second.processing.Demo Time Trigger.nested_struct",
                             items=adtf.Items.SAMPLES) as processing_scope:
        async def run_session():
            async with session.run():
                try:
                    while True:
                        async with processing_scope as item:
                            print(item)
                except EOFError:
                    pass


        async def run_and_stop():
            task = asyncio.create_task(run_session())
            await asyncio.sleep(3)
            task.cancel()


        asyncio.run(run_and_stop())
