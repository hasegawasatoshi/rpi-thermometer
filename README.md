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

## Monitoring CPU temperature
```
python cpu_temp.py --debug &
redis-cli GET cpu:temperature
```

## Install
```
sudo mkdir -p /opt/termometer/bin
sudo mkdir -p /opt/termometer/etc
sudo pip install -r requirements.txt
sudo install -v -o root -g root -m 644 -t /opt/termometer/etc config.yaml
sudo install -v -o root -g root -m 644 -t /opt/termometer/bin dht22.py
sudo install -v -o root -g root -m 644 -t /opt/termometer/bin cpu_temperature.py
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system dht22.service
sudo install -v -o root -g root -m 644 -t /usr/lib/systemd/system cpu_temperature.service
sudo systemctl enable dht22.service
sudo systemctl enable cpu_temperature.service
sudo systemctl daemon-reload
sudo systemctl start dht22.service
sudo systemctl start cpu_temperature.service
```
