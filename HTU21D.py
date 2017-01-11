# Constants.I2C_READ | Constants.I2C_END_TX_MASK
import time
from PyMata.pymata import PyMata

class HTU21D(object):
	"""Port of the HTU21D Humidity sensor """

	HTU21DR_register = {
		"TRIGGER_TEMP_MEASURE_HOLD":    0xE3,
		"TRIGGER_HUMD_MEASURE_HOLD":    0xE5,
		"TRIGGER_TEMP_MEASURE_NOHOLD":  0xF3,
		"TRIGGER_HUMD_MEASURE_NOHOLD":  0xF5,
		"WRITE_USER_REG":  				0xE6,
		"READ_USER_REG":  				0xE7,
		"SOFT_RESET":  					0xFE,

		"USER_REGISTER_RESOLUTION_MASK": 		0x81,
		"USER_REGISTER_RESOLUTION_RH12_TEMP14": 0x00,
		"USER_REGISTER_RESOLUTION_RH8_TEMP12": 	0x01,
		"USER_REGISTER_RESOLUTION_RH10_TEMP13": 0x80,
		"USER_REGISTER_RESOLUTION_RH11_TEMP11": 0x81,

		"USER_REGISTER_END_OF_BATTERY": 		0x40,
		"USER_REGISTER_HEATER_ENABLED": 		0x04,
		"USER_REGISTER_DISABLE_OTP_RELOAD": 	0x02,
	}

	def __init__(self, board, address = 0x40):

		self.board 	 = board
		self.address = address

		self.callback = []

		self.config = False

	def start(self, SDA = 20, SCL = 21, delay_time = 100):
		#datasheet say arround 50ms per channel
		self.board.i2c_config(delay_time, self.board.DIGITAL, SCL, SDA)
		time.sleep(0.015)
		self.config = True

	def data_val(self, data):
		print data
		self.callback = data

	def read_user_registry(self):
		if self.config:
			self.board.i2c_read(self.address, self.HTU21DR_register["READ_USER_REG"], 1, self.board.I2C_READ, self.data_val)
		# time.sleep(0.1)
		else:
			print "Not configured"

	def change_resolution(self, resolution = self.HTU21DR_register["USER_REGISTER_RESOLUTION_RH12_TEMP14"]):
		if self.config:
			self.read_user_registry()
			user_registry = self.callback[0]
			user_registry = user_registry & 126 # Turn off the resolution bits
			resolution   = resolution & 129 # Turn off the other bits but resolution (7 and 1)

			user_registry = user_registy|resolution

			print "NEW USER REGISTRY" , user_registry

			# board.i2c_write(self.address, user_registry)
			board.i2c_write(self.address, [self.HTU21DR_register["WRITE_USER_REG"], user_registry])

			self.read_user_registry()
		else:
			print "Not configured"

	def read_temperature(self, hold = True):
		if self.config:
			self.callback = []
			if hold:
				register = self.HTU21DR_register["TRIGGER_TEMP_MEASURE_HOLD"]
			else
				register = self.HTU21DR_register["TRIGGER_TEMP_MEASURE_NOHOLD"]

			self.board.i2c_read(self.address, register, 3, self.board.I2C_READ, self.data_val)

			print "Waiting for data"
			while len(self.callback)<=2:
				True
			print "Data available"

			if not self.CRC():
				return 999

			raw_temp = (self.callback[0] << 8) + self.callback[1]

			raw_temp = raw_temp & 0xFFFC #Clear status bits
			actual_temp = -46.85 + (175.72 * raw_temp / 65536.0)

			return actual_temp
		else:
			print "Not configured"
			return 998

	def read_humidity(self, hold = True):
		if self.config:
			self.callback = []
		
			if hold:
				register = self.HTU21DR_register["TRIGGER_HUMD_MEASURE_HOLD"]
			else
				register = self.HTU21DR_register["TRIGGER_HUMD_MEASURE_NOHOLD"]

			self.board.i2c_read(self.address, register, 3, self.board.I2C_READ, self.data_val)

			print "Waiting for data"
			while len(self.callback)<=2:
				True
			print "Data available"
			
			if not self.CRC():
				return 999

			raw_hum = (self.callback[0] << 8) + self.callback[1]

			raw_hum = raw_hum & 0xFFFC #Clear status bits
			actual_hum = -6 + (125.0 * raw_hum / 65536.0)

			return actual_hum
		else:
			print "Not configured"
			return 998

	def CRC(self):
		remainder = ((self.callback[0] << 8) + self.callback[1]) << 8

		remainder = remainder | self.callback[2]

		divsor = 0x988000

		for i in range(0, 16):
			if( remainder & 1 << (23 - i) ):
				remainder ^= divsor

			divsor = divsor >> 1
		
		if remainder == 0:
			return True
		else:
			return False



		