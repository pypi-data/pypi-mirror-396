import asyncio
import adtf
import sys

# In this examples we are using the default ADTF environment and one of the delivered example sessions
adtf_runtime_directory = sys.argv[1]

with adtf.Session(adtf_runtime_directory + "/adtf.adtfenvironment",
                  adtf_runtime_directory + "/examples/demo_sessions/adtfsessions/How to play back adtfdat files.adtfsession") as session:
    print(session.output_pin_names)

    with session.open_stream("single.Player.NESTED_STRUCT") as processing_scope:
        async def run():
            async with session.run():
                try:
                    while True:
                        async with processing_scope as item:
                            print(item)
                except EOFError:
                    pass


        asyncio.run(run())
