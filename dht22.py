import argparse
import logging
import signal
import time

import adafruit_dht
import board
import redis
import yaml

logging.basicConfig(
    format="[%(module)s] [%(levelname)s] %(message)s",
    level=logging.INFO)
logger = logging.getLogger('DHT22')


class TerminatedException(Exception):
    pass


def signal_handler(signum, frame):
    logger.info('Catched signal [ %d ].' % (signum))
    raise TerminatedException


class DHT22:
    def __init__(self):
        self.dht22 = adafruit_dht.DHT22(board.D18)
        logger.info("Start measurement")

    def __del__(self):
        # self.dht22.exit()
        logger.info("Stop measurement")

    def read(self):
        try:
            temperature = self.dht22.temperature
            humidity = self.dht22.humidity
            return {"temperature": temperature, "humidity": humidity}
        except RuntimeError as e:
            logger.warning(e.args[0])
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
                humidity = readings.get("humidity")
                db.write("dht22:temperature", temperature)
                db.write("dht22:humidity", humidity)
                logger.debug("Temperature: %0.1f *C / Humidity: %0.1f %%" % (temperature, humidity))
            time.sleep(CONFIG.get('dht22').get('monitoring').get('intervals'))

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
        logger.info('Cleanup and stop DHT22 monitoring service.')


if __name__ == '__main__':
    logger.info("DHT22 monitoring service started.")
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

    sensor = DHT22()
    db = Redis()
    mainloop(sensor, db)
