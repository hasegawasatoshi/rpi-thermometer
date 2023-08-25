# rpi-thermometer

## Installation

Install packages
```
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install libgpiod2 redis-server python3-venv
```

Create virtual environment
```
python3 -m venv .venv
. .venv/bin/activate
```

Install python packages
```
pip install adafruit-circuitpython-dht
pip install redis
pip install PyYAML
```

Install python packages for development
```
pip install pycodestyle
pip install flake8
pip install autopep8
pip install isort
```

## Monitoring temperature and humidity with DHT22
```
python dht22.py --debug &
redis-cli GET dht22:temperature
redis-cli GET dht22:humidity
```

## Monitoring CPU temperature
```
python cpu_temp.py --debug &
redis-cli GET cpu:temperature
```
