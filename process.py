import asyncio
import os
from dotenv import load_dotenv
from viam.logging import getLogger
from viam.robot.client import RobotClient
from viam.components.sensor import Sensor
from viam.components.generic import Generic

load_dotenv()
LOGGER = getLogger(__name__)

robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''

# Define the sensor and plug names from the Viam app CONFIGURE tab
sensor_name = os.getenv("SENSOR_NAME", "")
plug_name = os.getenv("PLUG_NAME", "")

async def connect():
    opts = RobotClient.Options.with_api_key( 
        api_key=robot_api_key,
        api_key_id=robot_api_key_id
    )
    return await RobotClient.at_address(robot_address, opts)

async def main():
    machine = await connect()

    pms_7003 = Sensor.from_robot(machine, sensor_name)
    kasa_plug = Generic.from_robot(machine, plug_name)

    # Define unhealthy thresholds
    unhealthy_thresholds = {
        'pm2_5_atm': 35.4,
        'pm10_atm': 150
    }

    while True:
        readings = await pms_7003.get_readings()
        # Check if any of the PM values exceed the unhealthy thresholds
        if any(readings.get(pm_type, 0) > threshold for pm_type, threshold in unhealthy_thresholds.items()): 
            LOGGER.info('UNHEALTHY.')
            await kasa_plug.do_command({"turn_on": []})
        else:
            LOGGER.info('HEALTHY!')
            await kasa_plug.do_command({"turn_off": []})

        # wait before checking again
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())