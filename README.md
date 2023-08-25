# rpi-thermometer

## Installation

Install packages
```
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install libgpiod2 redis-server python3-venv python3-pip
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

## Monitoring temperature with DS18B20
```
python DS18B20.py --debug &
redis-cli GET DS18B20:temperature
```

## Monitoring CPU temperature
```
python cpu_temp.py --debug &
redis-cli GET cpu:temperature
```

## Local historian
```
python historian.py --debug
```

## Install
```
sudo mkdir -p /opt/termometer/bin
sudo mkdir -p /opt/termometer/etc
sudo mkdir -p /opt/termometer/logs
sudo pip install -r requirements.txt
sudo install -v -o root -g root -m 644 -t /opt/termometer/etc config.yaml
sudo install -v -o root -g root -m 644 -t /opt/termometer/bin dht22.py
sudo install -v -o root -g root -m 644 -t /opt/termometer/bin cpu_temperature.py
sudo install -v -o root -g root -m 644 -t /opt/termometer/bin DS18B20.py
sudo install -v -o root -g root -m 644 -t /opt/termometer/bin historian.py
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system dht22.service
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system cpu_temperature.service
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system DS18B20.service
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system historian.service
sudo systemctl daemon-reload
sudo systemctl enable dht22.service
sudo systemctl enable cpu_temperature.service
sudo systemctl enable DS18B20.service
sudo systemctl enable historian.service
sudo systemctl start dht22.service
sudo systemctl start cpu_temperature.service
sudo systemctl start DS18B20.service
sudo systemctl start historian.service
```
