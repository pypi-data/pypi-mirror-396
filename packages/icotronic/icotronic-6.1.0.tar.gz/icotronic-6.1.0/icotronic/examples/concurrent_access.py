"""Show concurrent capabilities of ICOtronic system"""

# -- Imports ------------------------------------------------------------------

from asyncio import Event, run, TaskGroup
from contextlib import asynccontextmanager
from typing import AsyncIterator

from netaddr import EUI

from icotronic.can import Connection, SensorNode, StreamingConfiguration
from icotronic.can.adc import ADCConfiguration

# -- Functions ----------------------------------------------------------------


@asynccontextmanager
async def sensor_node_connection(
    identifier: int | str | EUI,
) -> AsyncIterator[SensorNode]:
    """Create a connection to a sensor node

    Args:

        The identifier of the sensor node

    Returns:

        A asynchronous context manager for accessing the sensor node

    """

    async with Connection() as stu:
        async with stu.connect_sensor_node(identifier) as sensor_node:
            yield sensor_node


async def stream_and_read_adc():
    """Read ADC configuration, while streaming is active"""

    async with sensor_node_connection("Test-STH") as sensor_node:

        async def stream_data(started_streaming: Event) -> None:
            """Enable streaming and read streaming data until cancelled"""

            async with sensor_node.open_data_stream(
                StreamingConfiguration(first=True)
            ) as stream:
                async for _ in stream:
                    if not started_streaming.is_set():
                        started_streaming.set()

        async def read_adc() -> ADCConfiguration:
            """Read ADC configuration"""

            return await sensor_node.get_adc_configuration()

        started_streaming = Event()

        async with TaskGroup() as task_group:
            stream_data_task = task_group.create_task(
                stream_data(started_streaming)
            )
            await started_streaming.wait()  # Wait until streaming is active
            read_adc_task = task_group.create_task(read_adc())
            adc_configuration = await read_adc_task
            print(adc_configuration)
            stream_data_task.cancel()


# -- Main ---------------------------------------------------------------------


if __name__ == "__main__":
    run(stream_and_read_adc())
