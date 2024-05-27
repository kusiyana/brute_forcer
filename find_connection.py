from brute_forcer.brute_force import Bruteforce
from pprint import pprint

# master = Bruteforce.connect()
# print(master.read_holding_registers(96,1,slave=1))
parameters = Bruteforce.find_connection_params()
print("\n* * * * * Connection parameters found * * * * *\n")
pprint(parameters)
print("\n* * * * * * * * * *\n")
