from brute_forcer.brute_force import Bruteforce
from pprint import pprint

parameters = Bruteforce.find_parameter_addresses()
print("\n* * * * * Connection parameters found * * * * *\n")
pprint(parameters)
print("\n* * * * * * * * * *\n")
