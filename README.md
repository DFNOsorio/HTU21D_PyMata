# HTU21D_PyMata
I2C Library for HTU21D using pymata. (Based on sparkFun's HTU21D library)

## Description

Port of the HTU21D temperature and humidity sensor library by sparkFun to python (pyMata).

## Usage

sensor = HTU21D(board) -> Initializes a new instance of the sensor.

sensor.start() -> configures the sensor.

sensor.read_temperature() -> returns the temperature
sensor.read_humidity()    -> returns the humidity
