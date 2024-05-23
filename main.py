from brute_forcer.brute_force2 import Bruteforce
from config.config import settings, Config
from pymodbus.client import ModbusSerialClient

# connection = Bruteforce.find_connection_params()
# print(Config.make_list(settings['brute_force']))

# master = Bruteforce.connect()
# result = master.read_holding_registers(95, 2, 1)
# print(result.registers)
# master.close()

# # print(master.write_register(95,2, slave=1))
# Bruteforce.find_parameter_addresses(Bruteforce.return_connection())
