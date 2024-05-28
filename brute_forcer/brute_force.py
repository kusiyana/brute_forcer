import sys

from pymodbus.client import ModbusSerialClient
from config.config import settings, Config
from time import sleep
import logging


log = logging.getLogger("logger")
log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(message)s")

fh = logging.FileHandler(settings["log"], mode="w", encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
log.addHandler(ch)


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
        brute_force_settings = Config.make_list(settings["find_connection"])
        for slave in brute_force_settings["slaves"]:
            for baud in brute_force_settings["baudrate"]:
                for stopbit in brute_force_settings["stopbits"]:
                    for databit in brute_force_settings["databits"]:
                        for parity in brute_force_settings["parity"]:
                            try:
                                master = ModbusSerialClient(
                                    port=settings["port"],
                                    baudrate=int(baud),
                                    stopbits=int(stopbit),
                                    bytesize=int(databit),
                                    parity=str(parity),
                                )
                                if master.connect():
                                    log.info(
                                        f" - Trying: {baud}, {parity}, {stopbit}, {databit} slave: {slave}"
                                    )

                                    result = master.read_holding_registers(
                                        int(brute_force_settings["check_address"][0]),
                                        1,
                                        slave=int(slave),
                                    )
                                    try:
                                        assert result.registers
                                        log.info(" -- Hurrah, found it!")
                                        return {
                                            "port": settings["port"],
                                            "baudrate": int(baud),
                                            "parity": parity,
                                            "stopbits": int(stopbit),
                                            "databits": int(databit),
                                        }
                                    except AttributeError:
                                        log.info(" -- meh, failed")
                                        pass
                                    finally:
                                        master.close()
                            except KeyboardInterrupt:
                                log.info("Bye")
                                sys.exit()
                            except Exception as e:
                                log.error(e)
                                pass

    @classmethod
    def find_parameter_addresses(cls) -> int:
        """Locate which addressses contain settings data for slave_id
        baudrate, parity and stopbits"""
        output_parameters = {}
        # 2 fix parameter with slave_id, baud, parity, stopbits
        address_start = settings["find_parameters"]["address_start"]
        address_end = settings["find_parameters"]["address_end"]
        for address in range(address_start, address_end):
            log.info(f"Checking address {address}")
            original_value = cls.__get_original_value(address)
            if original_value is None:
                continue
            new_value = original_value + 1
            # break address N
            cls.__break_address_n(address, new_value)
            broken = cls.__test_breakage(address)

            if not broken:
                log.info(" -- Not broken")
                cls.__restore_original_value(address, original_value)
                continue
            # is broken
            slave_address = cls.__test_slave_address(address, original_value, new_value)
            if slave_address:
                output_parameters = output_parameters | slave_address
                log.info(f" -- Hurrah, found slave address at {slave_address}")
                continue

            for parameter in ["baudrate", "parity", "stopbits"]:
                parameter_found = cls.check_parameter(
                    parameter, address, original_value
                )
                if parameter_found:
                    output_parameters = output_parameters | parameter_found
                    break
        return output_parameters

    @classmethod
    def check_parameter(cls, parameter: str, address: int, original_value: int) -> dict:
        """Check if parameter (baudrate, parity, stopbits) is still working after a change
        has been made to a particular address"""
        connection_details_scratch = cls.return_connection().copy()
        for var in settings["find_parameters"][parameter].split(" "):
            sleep(float(settings["find_parameters"]["delay_time_seconds"]))
            log.info(f"-- Checking value for parameter {parameter} with {var}")
            try:
                var = int(var)
            except Exception as e:
                print(e)
                pass
            connection_details_scratch[parameter] = var
            master = ModbusSerialClient(**connection_details_scratch)
            result = master.read_holding_registers(
                address, 1, slave=settings["find_parameters"]["slave_id"]
            )
            master.close()
            if cls.__has_registers(result):
                cls.__restore_original_value(
                    address, original_value, connection_details_scratch
                )
                master.close()
                log.info(" -- -- Found it!")
                return {parameter: address}
        return {}

    @staticmethod
    def __has_registers(result):
        if hasattr(result, "registers"):
            return True
        return False

    @classmethod
    def __get_original_value(cls, address):
        """Get the original value contained at address X"""
        try:  # Get original value from address N
            sleep(float(settings["find_parameters"]["delay_time_seconds"]))
            master = cls.connect()
            result = master.read_holding_registers(
                address, 1, slave=settings["find_parameters"]["slave_id"]
            )
            original_value = result.registers[0]
            master.close()
            return original_value
        except Exception as e:
            log.info(" -- Could not read address {e}")
            master.close()
            return None

    @classmethod
    def __break_address_n(cls, address, new_value):
        """Change a value at address X to see if that stops the device from responding"""
        sleep(float(settings["find_parameters"]["delay_time_seconds"]))
        master = cls.connect()
        try:
            log.info(
                f" - Trying to break connection with {new_value} at address {address}"
            )
            master.write_register(
                int(address),
                int(new_value),
                slave=int(settings["find_parameters"]["slave_id"]),
            )
            master.close()
        except Exception as e:
            log.error(e)
            master.close()
            pass

    @classmethod
    def __test_breakage(cls, address):
        master = cls.connect()
        sleep(float(settings["find_parameters"]["delay_time_seconds"]))
        try:
            log.info("  -- Testing if it's broken")
            result = master.read_holding_registers(
                address, 1, slave=settings["find_parameters"]["slave_id"]
            )
            assert result.registers
            master.close()
            return False
        except AttributeError:
            log.info(f"  -- Eished, broken address {address}, trying to fix it...")
            master.close()
            return True

    @classmethod
    def __restore_original_value(
        cls, address, original_value, connection_details: dict = None
    ):
        """If the address hasn't broken after a new value is made, restore the original
        value"""
        if connection_details:
            master = ModbusSerialClient(**connection_details)
            master.close()
        else:
            master = cls.connect()
        sleep(float(settings["find_parameters"]["delay_time_seconds"]))
        try:
            master.write_register(
                address, original_value, slave=settings["find_parameters"]["slave_id"]
            )
        except Exception as e:
            log.error(f"oops {e}")
            pass
        finally:
            master.close()

        master.close()

    @classmethod
    def __test_slave_address(cls, address, original_value, new_value):
        sleep(float(settings["find_parameters"]["delay_time_seconds"]))
        master = cls.connect()
        master.write_register(address, original_value, slave=new_value)
        result = master.read_holding_registers(address, 1, slave=original_value)
        master.close()
        if cls.__has_registers(result):
            cls.__restore_original_value(address, original_value)
            log.info(f"  -- Reading address {address} slave {original_value}")
            sleep(float(settings["find_parameters"]["delay_time_seconds"]))
            result = master.read_holding_registers(address, 1, slave=original_value)
            master.close()
            try:
                assert result.registers
                return {"slave_id": address}
            except:
                pass
        master.close()
        return {}
