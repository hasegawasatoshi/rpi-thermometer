import argparse
import csv
import logging
import os
import signal
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import redis
import yaml

TZ = ZoneInfo("Asia/Tokyo")

logging.basicConfig(
    format="[%(module)s] [%(levelname)s] %(message)s",
    level=logging.INFO)
logger = logging.getLogger('historian')


class TerminatedException(Exception):
    pass


def signal_handler(signum, frame):
    logger.info('Catched signal [ %d ].' % (signum))
    raise TerminatedException


class CsvLogger:
    def __init__(self):
        self.output_dir = CONFIG.get('historian').get('output')
        logger.info("Start logging")

    def __del__(self):
        logger.info("Stop logging")

    def append(self, readings):
        try:
            path = os.path.join(
                CONFIG.get('historian').get('output'),
                readings['datetime'].split('T')[0] + '.csv')
            logger.debug(f'output file name = {path}')

            with open(path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(readings.values())
        except Exception as e:
            logger.error(e)
            raise e
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

    def read(self, key):
        try:
            return self._conn.get(key)
        except redis.exceptions.ConnectionError as e:
            logger.error(f'{e}')
            raise e


def mainloop(csvlogger, db):
    try:
        while True:
            keys = CONFIG.get('historian').get('monitoring').get('keys')
            now = datetime.now(tz=TZ)
            readings = {"datetime": now.isoformat()}
            readings['timestamp'] = now.timestamp()
            for k in keys:
                v = db.read(k)
                readings[k] = v
            logger.debug(readings)

            csvlogger.append(readings)
            time.sleep(CONFIG.get('historian').get('monitoring').get('intervals'))

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
        logger.info('Cleanup and stop Historian service.')


if __name__ == '__main__':
    logger.info("Historian service started.")
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

    csvlogger = CsvLogger()
    db = Redis()
    mainloop(csvlogger, db)
