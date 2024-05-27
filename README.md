# brute_forcer
Brute force discovery of Modbus connection details and addresses that control slave_id, baudrate, parity and stopbits.

## Disclaimer
Use these scripts at your own risk! There is a chance that you will break a crucial address with the find_parameter_addresses.py script. As such, use this one at your own risk. The script has been tested on a selection of devices and performed well, but some devices may "get broken" by this script because it relies on altering address values that control connectivity to the device (such as baudrate, parity etc). There is a particular risk if holding registers set device IDs when only input registers are allowed by the device for reading data.

## Installation instructions
```
python -m venv venv
pip install -r requirements.txt
```
and then:

```python find_connection.py```
or:
```
find_parameter_addresses.py
```

## What to run and when
Run find_connection.py if you don't know what the connection details are to the device. This script will exhaustively try every combination of parameters until it unlocks the device.

Run find_parameter_addresses.py if you don't know which addresses need to be modified for slave_id, baudrate, parity and stopbits.
Usage:
Thi
