import argparse
import logging
import re
import shlex
import signal
import subprocess
import time

import redis
import yaml

logging.basicConfig(
    format="[%(module)s] [%(levelname)s] %(message)s",
    level=logging.INFO)
logger = logging.getLogger('CPU Temp')


class TerminatedException(Exception):
    pass


def signal_handler(signum, frame):
    logger.info('Catched signal [ %d ].' % (signum))
    raise TerminatedException


class Sensor:
    def __init__(self):
        self.re_temperature = re.compile(r'temp=(?P<temperature>\d+.\d+)\'C')
        logger.info("Start measurement")

    def __del__(self):
        logger.info("Stop measurement")

    def read(self):
        try:
            args = shlex.split("vcgencmd measure_temp")
            ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = ret.stdout.decode("utf-8")
            m = self.re_temperature.search(result)
            if m and m.group('temperature'):
                temperature = float(m.group('temperature'))
                return {'temperature': temperature}
        except subprocess.CalledProcessError as e:
            logger.warning(e)
        return None


class Redis:
    def __init__(self):
        self._conn = redis.StrictRedis(
            host=CONFIG.get('redis').get('host'),
            port=CONFIG.get('redis').get('port'),
            db=CONFIG.get('redis').get('db'),
            decode_responses=True)

    def write(self, key, value, ex=10):
        try:
            self._conn.set(key, value, ex)
        except redis.exceptions.ConnectionError as e:
            logger.error(f'{e}')
            raise e


def mainloop(sensor, db):
    try:
        while True:
            readings = sensor.read()
            if readings is not None:
                temperature = readings.get("temperature")
                db.write("cpu:temperature", temperature)
                logger.debug("Temperature: %0.1f *C" % temperature)
            time.sleep(CONFIG.get('cpu').get('monitoring').get('intervals'))

    except KeyboardInterrupt:
        logger.error('Stopped by keyboard imput (ctrl-c)')

    except TerminatedException:
        logger.error('Stopded by systemd.')

    except OSError as e:
        import traceback
        traceback.print_exc()
        raise e

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

    finally:
        logger.info('Cleanup and stop CPU temperature monitoring service.')


if __name__ == '__main__':
    logger.info("CPU temperature monitoring service started.")
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="enable debug log",
                        action="store_true")
    parser.add_argument('-c', '--config', default='config.yaml')
    args = parser.parse_args()

    if args.debug:
        logger.info("Enable debug log.")
        logging.getLogger().setLevel(logging.DEBUG)

    with open(args.config) as file:
        global CONFIG
        CONFIG = yaml.safe_load(file.read())
        logger.info("Configuration: {0}".format(CONFIG))

    sensor = Sensor()
    db = Redis()
    mainloop(sensor, db)
