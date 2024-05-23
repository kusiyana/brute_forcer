import sys

from pymodbus.client import ModbusSerialClient
from serial import Serial
from config.config import settings


class Bruteforce:

    @staticmethod
    def return_connection():
        return {
            "port": settings["port"],
            "baudrate": int(settings["connection"]["baudrate"]),
            "parity": settings["connection"]["parity"],
            "stopbits": int(settings["connection"]["stopbits"]),
            "databits": int(settings["connection"]["databits"]),
            "databits": int(settings["connection"]["databits"]),
            "bytesize": int(settings["connection"]["databits"]),
        }

    @staticmethod
    def connect():
        return ModbusSerialClient(port=settings["port"], **settings["connection"])

    @staticmethod
    def close(connection):
        connection.close()

    @staticmethod
    def find_connection_params() -> dict:
        """Brute force the basic connection parameters"""
        slaves = str(settings["brute_force"]["slave_id"]).split(" ")
        check_address = str(settings["brute_force"]["check_address"])
        baudrates = str(settings["brute_force"]["baudrates"]).split(" ")
        stopbits = str(settings["brute_force"]["stopbits"]).split(" ")
        databits = str(settings["brute_force"]["databits"]).split(" ")
        parities = str(settings["brute_force"]["parities"]).split(" ")
        print(baudrates)
        print(stopbits)
        print(databits)
        print(databits)
        for slave in slaves:
            for baud in baudrates:
                for stopbit in stopbits:
                    for databit in databits:
                        for parity in parities:
                            try:
                                master = ModbusSerialClient(
                                    port=settings["port"],
                                    baudrate=int(baud),
                                    stopbits=int(stopbit),
                                    bytesize=int(databit),
                                    parity=str(parity),
                                )
                                if master.connect():
                                    print("asdfasdf")
                                    print(
                                        f"trying: {baud}, {parity}, {stopbit}, {databit} slave: {slave}"
                                    )
                                    try:
                                        print(check_address, slave)
                                        result = master.read_holding_registers(
                                            int(check_address), 1, slave=int(slave)
                                        )
                                        print(result)
                                        result.registers
                                        return {
                                            "port": settings["port"],
                                            "baudrate": int(baud),
                                            "parity": parity,
                                            "stopbits": int(stopbit),
                                            "databits": int(databit),
                                        }
                                    except:
                                        try:
                                            result = master.read_input_registers(
                                                check_address, 1, slave=slave
                                            )
                                            print(result)
                                            result.registers
                                            return {
                                                "port": settings["port"],
                                                "baudrate": int(baud),
                                                "parity": str(parity),
                                                "stopbits": int(stopbit),
                                                "databits": int(databit),
                                            }
                                        except:
                                            pass
                                    finally:
                                        master.close()
                            except KeyboardInterrupt:
                                print("Bye")
                                sys.exit()
                            except Exception as exception:
                                # print(exception)
                                pass

    @classmethod
    def find_parameter_addresses(cls, connection_details: dict) -> int:
        master = ModbusSerialClient(**connection_details)
        connection_parameters = {}
        # 2 fix parameter with slave_id, baud, parity, stopbits
        address_start = settings["brute_force"]["address_start"]
        address_end = settings["brute_force"]["address_end"]
        for address in range(address_start, address_end):
            print(f"Checking address {address}")
            try:  # Get original value from address N
                result = master.read_holding_registers(
                    address, 1, slave=settings["brute_force"]["slave_id"]
                )
                print(result)
                original_value = result.registers[0]
                new_value = int(original_value) + 1
            except Exception as e:
                print(e)
                print("Could not read address, skipping...")
                continue

            # break address N

            try:
                print(f"trying to break address {address}")
                print(
                    master.write_register(
                        int(address),
                        int(new_value),
                        slave=int(settings["brute_force"]["slave_id"]),
                    )
                )
            except:
                pass
            # Does it break?
            try:
                print("testing if it is broken")
                master.close()
                master = cls.connect()
                result = master.read_holding_registers(
                    address, 1, slave=settings["brute_force"]["slave_id"]
                )
                print(result.registers)
                print(" Not broken")
                # No it doesn't break, restore value
                master.write_register(
                    address, original_value, slave=settings["brute_force"]["slave_id"]
                )
                continue
            except Exception:
                print(f"-- Eished, broken address {address}, trying to fix it...")

                # It is broken

                # Check slave ID
                master.write_register(address, original_value, slave=new_value)
                result = master.read_holding_registers(address, 1, slave=original_value)
                if hasattr(result, "registers"):
                    print(f"Located slave ID address {address}")
                    connection_parameters["slave_address"] = address

                    print(f"reading address {address} slave {original_value}")
                    result = master.read_holding_registers(
                        address, 1, slave=original_value
                    )
                    continue

                # check baudrates

            baudrate_result = False
            for baudrate in str(settings["brute_force"]["baudrates"]).split(" "):
                print(f"checking baudrate {baudrate}")
                master.close()
                master = ModbusSerialClient(
                    port=settings["port"],
                    baudrate=int(baudrate),
                    stopbits=connection_details["stopbits"],
                    databits=connection_details["databits"],
                    parity=connection_details["parity"],
                )
                result = master.read_holding_registers(
                    address, 1, slave=settings["brute_force"]["slave_id"]
                )
                if hasattr(result, "registers"):
                    baudrate_result = True
                    print(
                        f'restoring original baudrate value {original_value} ==> {connection_details["baudrate"]}'
                    )
                    connection_parameters["baudrate"] = address
                    master.write_register(
                        address,
                        original_value,
                        slave=settings["brute_force"]["slave_id"],
                    )
                    master.close()
                    master = cls.connect()
                    break
            if baudrate_result:
                continue

            # check parities
            parities = ["N", "E", "O"]
            parity_result = False
            for parity in parities:
                print(f"checking parity {parity}")
                master.close()
                master = ModbusSerialClient(
                    port=settings["port"],
                    baudrate=connection_details["baudrate"],
                    stopbits=connection_details["stopbits"],
                    databits=connection_details["databits"],
                    parity=parity,
                )
                result = master.read_holding_registers(
                    address, 1, slave=settings["brute_force"]["slave_id"]
                )
                if hasattr(result, "registers"):
                    parity_result = True
                    connection_parameters["parity"] = address
                    master.write_register(
                        address,
                        original_value,
                        slave=settings["brute_force"]["slave_id"],
                    )
                    master.close()
                    master = cls.connect()
                    break
            if parity_result:
                continue

            # check stopbits
            stopbits = [1, 2]
            for stopbit in stopbits:
                print(f"checking stopbits {stopbit}")
                master = ModbusSerialClient(
                    port=settings["port"],
                    baudrate=connection_details["baudrate"],
                    stopbits=stopbit,
                    databits=connection_details["databits"],
                    parity=connection_details["parity"],
                )
                result = master.read_holding_registers(
                    address, 1, slave=settings["brute_force"]["slave_id"]
                )
                if hasattr(result, "registers"):
                    connection_parameters["stopbits"] = address
                    master.write_register(
                        address,
                        original_value,
                        slave=settings["brute_force"]["slave_id"],
                    )
                    master.close()
                    master = cls.connect()
                    break
        print(connection_parameters)
        return connection_parameters
