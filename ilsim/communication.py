

# native imports
import re
from enum import IntEnum
from functools import partial
from typing import Callable
from typing import Iterable

# internal imports
from .errors import CommandFormatError
from .errors import CommunicationException
from .errors import GeneralSystemError
from .errors import IDOutsideValidRangeError
from .errors import InaccessibleIDOrQueryError
from .errors import QueryOutsideValidRangeError
from .errors import QueryReadProtectedError
from .errors import QueryWriteProtectedError
from .errors import WriteDataOutsideValidRangeError
from .sensor import SensorUnit


class DLEN1Error(IntEnum):
  """
  Internal error codes for communication unit.
  """
  NO_ERROR = 0
  """No error"""
  ERROR_051 = 51
  """
  Unassigned ID error

  The main unit assigned no ID within 10 seconds after the DL-EN1 had been
  started.
  """
  ERROR_052 = 52
  """
  Start-time communication error

  Communication between sensor amplifiers ended abnormally before ID
  assignment completion.
  """
  ERROR_053 = 53
  """
  Unsupported sensor amplifier connection error

  A sensor amplifier not supported by the DL-EN1 is connected.
  """
  ERROR_054 = 54
  """
  Mixed model error

  Sensor amplifiers outside the specifications have a mixed connection.
  """
  ERROR_055 = 55
  """
  Start-time communication error

  ID number assignment is successful but communication failed during the
  subsequent initial communication.
  """
  ERROR_056 = 56
  """
  Current limitation error

  The number of connected sensor amplifiers exceeds the allowable range.
  """
  ERROR_057 = 57
  """
  Communication error between sensor amplifiers

  An error occurred during communication between sensor amplifiers.
  """
  ERROR_070 = 70
  """
  IP address duplicate error

  The IP address is the same as another device.
  """
  ERROR_100 = 100
  """
  System error

  The IP address is incorrect.
  """
  ERROR_101 = 101
  """
  System error

  A default gateway setting error occurred.
  """
  ERROR_102 = 102
  """
  System error

  An attempt to read data in EEPROM such as the MAC address has failed.
  """
  ERROR_103 = 103
  """
  System error

  An attempt to start the protocol stack has failed.
  """
  ERROR_104 = 104
  """
  System error

  An attempt to access FlashROM has failed.
  """
  ERROR_150 = 150
  """
  System error

  The number of held IDs is incorrect.
  """
  ERROR_151 = 151
  """
  System error

  The number of sensors is incorrect.
  """
  ERROR_152 = 152
  """
  System error

  An initial read error occurred.
  """


class CommunicationUnit:
  """
  Simulates communication unit
  """
  # ----------------------------------------------------------------------------
  connected_sensors: list[SensorUnit]
  internal_error: DLEN1Error
  valid_query_regex: re.Pattern[str]
  mask_sensor_status: bool
  read_mapping: dict[int, Callable[[], int]]
  write_mapping: dict[int, Callable[[int], None]]
  # ----------------------------------------------------------------------------

  def __init__(self) -> None:
    self.connected_sensors = []
    self.internal_error = DLEN1Error.NO_ERROR
    self.valid_query_regex = re.compile(
      r"(?:M0|MS|SR,(\d{2}),(\d{3})|SW,(\d{2}),(\d{3}),([+-]\d{9})"
      r"|FR,(\d{2}),(\d{3}))\r\n"
    )
    self.mask_sensor_status = False
    self.init_mappings()
  # ----------------------------------------------------------------------------

  def init_mappings(self) -> None:
    """
    Create the function mappings for SR and SW commands.
    """
    self.read_mapping = {
      0: self.read_000_status,
      1: self.read_001_sensor_error_status,
      2: self.read_002_warning_status,
      4: self.read_004_current_value_0_property,
      8: self.read_008_error_id_number,
      9: self.read_009_error_code,
      10: self.read_010_warning_id_number,
      11: self.read_011_warning_code,
      16: self.read_016_output_1_high,
      17: self.read_017_output_2_low,
      18: self.read_018_output_3_go,
      19: self.read_019_output_4_alarm,
      20: self.read_020_output_5,
      38: self.read_038_current_value_0_invalid,
      39: self.read_039_current_value_0_under_range,
      40: self.read_040_current_value_0_over_range,
      76: self.read_076_sensor_status_mask_setting,
      77: self.read_077_sensor_connected_number,
      668: self.read_668_error_code_id_00,
    }
    self.write_mapping = {
      76: self.write_076_sensor_status_mask_setting
    }
    # Add 044-058 and 669-683 to the mapping
    for i in range(15):
      self.read_mapping[44 + i] = partial(
        self.read_044_to_058_current_value_id_Y, i
      )
      self.read_mapping[669 + i] = partial(
        self.read_669_to_683_error_code_id_Y, i
      )
  # ----------------------------------------------------------------------------

  def assign_main_unit(self) -> None:
    """
    Assign main unit status to first connected sensor and remove it from
    all other sensors.
    """
    try:
      main_unit = self.connected_sensors[0]
      main_unit.is_main_unit = True
      sub_unit = self.connected_sensors[1]
      main_unit.connected_amplifier = sub_unit
      sub_unit.connected_amplifier = main_unit
      for su in self.connected_sensors[1:]:
        su.is_main_unit = False
    except IndexError:
      pass
  # ----------------------------------------------------------------------------

  def add_unit(self, unit: SensorUnit) -> None:
    """
    Add a single sensor unit to the communication unit.
    """
    self.connected_sensors.append(unit)
    self.assign_main_unit()
  # ----------------------------------------------------------------------------

  def add_multiple_units(self, units: Iterable[SensorUnit]) -> None:
    """
    Add an iteralbe of one or more sensor units to the communication unit.
    """
    self.connected_sensors.extend(units)
    self.assign_main_unit()
  # ----------------------------------------------------------------------------

  def stop_threads(self) -> None:
    """
    Stop all sub-threads of connected sensors.
    """
    for sensor in self.connected_sensors:
      sensor.stop_threads()
  # ----------------------------------------------------------------------------

  def randomize_sensors(self) -> None:
    """
    Randomize measurements for all sensors.
    """
    for sensor in self.connected_sensors:
      sensor.randomize_value()
  # ----------------------------------------------------------------------------

  def apply_sensor_uncertainty(self) -> None:
    """
    Simulate measurment uncertainty of all sensors.
    """
    for sensor in self.connected_sensors:
      sensor.apply_uncertainty()
  # ----------------------------------------------------------------------------

  def handle_query(self, raw_query: bytes) -> bytes:
    """
    Handle incoming command from client communicating with sensors.
    """
    reply: str
    translated_query: str = raw_query.decode('utf-8')
    query: str = translated_query[0:2]
    mo: re.Match[str] | None = (
      self.valid_query_regex.fullmatch(translated_query)
    )
    if mo is None:
      print(f"Invalid query! {translated_query}")
      reply = f'ER,{query},{CommandFormatError.error_code.value:0>3}\r\n'
      return reply.encode('utf-8')

    if self.internal_error != DLEN1Error.NO_ERROR:
      reply = f'ER,{query},{GeneralSystemError.error_code.value:0>3}\r\n'
      return reply.encode('utf-8')

    id: str | None = None
    query_data: str | None = None
    setting_data: str | None = None
    if query == 'SR':
      id = mo.group(1)
      query_data = mo.group(2)
    elif query == 'SW':
      id = mo.group(3)
      query_data = mo.group(4)
      setting_data = mo.group(5)
    elif query == 'FR':
      id = mo.group(6)
      query_data = mo.group(7)

    try:
      reply = self.response(query, id, query_data, setting_data)
    except CommunicationException as e:
      reply = f'ER,{query},{e.error_code.value:0>3}\r\n'
    except Exception:
      reply = f'ER,{query},{GeneralSystemError.error_code.value:0>3}\r\n'
      raise
    return reply.encode('utf-8')
  # ----------------------------------------------------------------------------

  def response(
    self,
    query: str,
    id: str | None = None,
    query_data: str | None = None,
    setting_data: str | None = None,
  ) -> str:
    """
    Preapre resposne for known commands.
    """
    if query == 'M0':
      self.apply_sensor_uncertainty()
      return self.response_M0()
    if query == 'MS':
      self.apply_sensor_uncertainty()
      return self.response_MS()
    if query == 'SR':
      assert id is not None
      assert query_data is not None
      return self.response_SR(id, query_data)
    if query == 'SW':
      assert id is not None
      assert query_data is not None
      assert setting_data is not None
      return self.response_SW(id, query_data, setting_data)
    if query == 'FR':
      assert id is not None
      assert query_data is not None
      return self.response_FR(id, query_data)

    return "MISSING_RESPONSE!\r\n"
  # ----------------------------------------------------------------------------

  def response_M0(self) -> str:
    """
    M0 command

    The measured values of all the connected sensor amplifiers are read.
    """
    values = ','.join(u.stringified_value for u in self.connected_sensors)
    return f"M0,{values}\r\n"
  # ----------------------------------------------------------------------------

  def response_MS(self) -> str:
    """
    MS command

    The measured values and output statuses of all the
    connected sensor amplifiers are read.
    """
    values = ','.join(
      f"{u.stringified_state},{u.stringified_value}"
      for u in self.connected_sensors
    )
    return f"MS,{values}\r\n"
  # ----------------------------------------------------------------------------

  def response_SR(self, id: int | str, query_data: int | str) -> str:
    """
    SR command

    The data of the specified connected sensor amplifier is read.
    """
    try:
      id = int(id)
    except ValueError:
      raise CommandFormatError
    try:
      query_data = int(query_data)
    except ValueError:
      raise CommandFormatError
    output: int | str
    if id == 0:
      # handle on communication unit
      try:
        output = self.handle_read(query_data)
      except NotImplementedError:
        return "NOT_IMPLEMENTED!"
    else:
      # handle on sensor
      try:
        relevant_sensor = self.connected_sensors[id - 1]
      except IndexError:
        raise IDOutsideValidRangeError
      try:
        output = relevant_sensor.handle_read(query_data)
      except NotImplementedError:
        return "NOT_IMPLEMENTED!"

    if isinstance(output, str):
      return f"SR,{id:0>2},{query_data:0>3},{output}\r\n"
    return f"SR,{id:0>2},{query_data:0>3},{output:+010d}\r\n"
  # ----------------------------------------------------------------------------

  def response_SW(
    self,
    id: int | str,
    query_data: int | str,
    setting_data: int | str
  ) -> str:
    """
    SW command

    Data is written to the specified connected sensor amplifier.
    """
    try:
      id = int(id)
    except ValueError:
      raise CommandFormatError
    try:
      query_data = int(query_data)
    except ValueError:
      raise CommandFormatError
    try:
      setting_data = int(setting_data)
    except ValueError:
      raise CommandFormatError
    if id == 0:
      # handle on communication unit
      try:
        self.handle_write(query_data, setting_data)
      except NotImplementedError:
        return "NOT_IMPLEMENTED!"
      return f"SW,{id:0>2},{query_data:0>3}\r\n"
    else:
      # handle on sensor
      try:
        relevant_sensor = self.connected_sensors[id - 1]
      except IndexError:
        raise IDOutsideValidRangeError
      try:
        relevant_sensor.handle_write(query_data, setting_data)
      except NotImplementedError:
        return "NOT_IMPLEMENTED!"
      return f"SW,{id:0>2},{query_data:0>3}\r\n"
  # ----------------------------------------------------------------------------

  def response_FR(self, id: int | str, query_data: int | str) -> str:
    """
    FR command

    The decimal position of the specified connected sensor
    amplifier is read.
    """
    try:
      id = int(id)
    except ValueError:
      raise CommandFormatError
    try:
      query_data = int(query_data)
    except ValueError:
      raise CommandFormatError
    if id == 0:
      raise IDOutsideValidRangeError
    else:
      # handle on sensor
      try:
        relevant_sensor = self.connected_sensors[id - 1]
      except IndexError:
        raise IDOutsideValidRangeError
      try:
        # TODO: Investigate if the real sensor gives different decimal position
        # for different query_data arguments
        # e.g. analog output, integer values, boolean 0/1
        output: int = relevant_sensor.decimal_position
      except NotImplementedError:
        return "NOT_IMPLEMENTED!"
      return f"FR,{id:0>2},{query_data:0>3},{output:+010d}\r\n"
  # ----------------------------------------------------------------------------

  def handle_read(self, query_data: int) -> int:
    """
    Dispatch read calls for SR commands.
    """
    if query_data > 1179:
      raise QueryOutsideValidRangeError
    handler_function = self.read_mapping.get(query_data)
    if handler_function is None:
      if query_data in self.write_mapping:
        # Write-Only function
        raise QueryReadProtectedError
      # System-reserved:
      raise InaccessibleIDOrQueryError
    return handler_function()
  # ----------------------------------------------------------------------------

  def handle_write(self, query_data: int, setting_data: int) -> None:
    """
    Dispatch write calls for SW commands.
    """
    if query_data > 1179:
      raise QueryOutsideValidRangeError
    handler_function = self.write_mapping.get(query_data)
    if handler_function is None:
      if query_data in self.read_mapping:
        # Read-Only function
        raise QueryWriteProtectedError
      # System-reserved:
      raise InaccessibleIDOrQueryError
    handler_function(setting_data)
  # ----------------------------------------------------------------------------

  def read_000_status(self) -> int:
    """
    Indicates the status of this unit and connected sensor
    amplifier.
    Bit 0: DL-EN1 Error Status
    Bit 1 to bit 13: Reserved for system
    Bit14: Warning Status
    Bit15: Error Status
    """
    output: int = 0
    output += 2**0 * (self.internal_error != DLEN1Error.NO_ERROR)
    output += 2**15 * any(s.has_error() for s in self.connected_sensors)
    return output
  # ----------------------------------------------------------------------------

  def read_001_sensor_error_status(self) -> int:
    """
    Indicates the error status of the connected sensor
    amplifiers. If an error occurs, the bit of the corresponding
    ID number of amplifier is turned to ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.has_error()
    return output
  # ----------------------------------------------------------------------------

  def read_002_warning_status(self) -> int:
    """
    (This is only valid when the IB Series is connected. The
    value is always 0 when using other sensor amplifiers.)
    """
    return 0
  # ----------------------------------------------------------------------------

  def read_004_current_value_0_property(self) -> int:
    """
    Indicates the status of current value 0 of each amplifier. If
    the current value 0 is “Over Range (FFFF)", “Under
    Range (-FFFF)", or "Invalid (----)", the bit corresponding to
    the ID number is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.is_out_of_range()
    return output
  # ----------------------------------------------------------------------------

  def read_008_error_id_number(self) -> int:
    """
    Indicates the ID number of the unit having error.
    Parameter range: 0 to 15 (initial value: 0)
    """
    if self.internal_error != DLEN1Error.NO_ERROR:
      return 0  # error in communication unit
    for i, sensor in enumerate(self.connected_sensors):
      if sensor.has_error():
        return (i + 1)
    return 0  # No Error
  # ----------------------------------------------------------------------------

  def read_009_error_code(self) -> int:
    """
    Indicates the error code that is happening.
    Parameter range: 0 to 65535 (initial value: 0)
    """
    if self.internal_error != DLEN1Error.NO_ERROR:
      return self.internal_error
    for sensor in self.connected_sensors:
      if sensor.has_error():
        return sensor.error_code
    return 0
  # ----------------------------------------------------------------------------

  def read_010_warning_id_number(self) -> int:
    """
    Indicates the ID number of the unit on which a warning
    has occurred.
    Parameter range: 0 to 15 (initial value: 0)
    """
    return 0
  # ----------------------------------------------------------------------------

  def read_011_warning_code(self) -> int:
    """
    Indicates the code of the warning that is happening.
    Parameter range: 0 to 65535 (initial value: 0)
    """
    return 0
  # ----------------------------------------------------------------------------

  def read_016_output_1_high(self) -> int:
    """
    Indicates the HIGH output (output 1) status of each
    amplifier. When HIGH is output, the bit corresponding to
    the ID number of the sensor amplifier is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.high_output
    return output
  # ----------------------------------------------------------------------------

  def read_017_output_2_low(self) -> int:
    """
    Indicates the LOW output (output 2) status of each
    amplifier. When LOW is output, the bit corresponding to
    the ID number of the sensor amplifier is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.low_output
    return output
  # ----------------------------------------------------------------------------

  def read_018_output_3_go(self) -> int:
    """
    Indicates the GO output (output 3) status of each
    amplifier. When GO is output, the bit corresponding to the
    ID number of the sensor amplifier is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.go_output
    return output
  # ----------------------------------------------------------------------------

  def read_019_output_4_alarm(self) -> int:
    """
    Indicates the status of HH** output (output 4) *1 of each
    amplifier. When HH** is output, the bit corresponding to the
    ID number of the sensor amplifier is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system

    ** Alarm output for IL sensors
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.alarm_output
    return output
  # ----------------------------------------------------------------------------

  def read_020_output_5(self) -> int:
    """
    Indicates the status of LL** output (output 5) *1 of each
    amplifier. When LL** is output, the bit corresponding to the
    ID number of the sensor amplifier is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system

    ** Not used for IL sensors
    """
    return 0
  # ----------------------------------------------------------------------------

  def read_038_current_value_0_invalid(self) -> int:
    """
    When the current value 0 of each amplifier is invalid, the
    bit of corresponding ID number is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.value_invalid
    return output
  # ----------------------------------------------------------------------------

  def read_039_current_value_0_under_range(self) -> int:
    """
    When the current value 0 of each amplifier is less than the
    lower limit of the detection range, the bit of the
    corresponding ID number is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.value_under_range
    return output
  # ----------------------------------------------------------------------------

  def read_040_current_value_0_over_range(self) -> int:
    """
    When the current value 0 of each amplifier is higher than the
    upper limit of the detection range, the bit of corresponding
    ID number is turned ON.
    Bit 0 to bit 14: ID number 1 to ID number 15
    Bit15: Reserved for system
    """
    output: int = 0
    for i, sensor in enumerate(self.connected_sensors):
      output += 2**i * sensor.value_over_range
    return output
  # ----------------------------------------------------------------------------

  def read_044_to_058_current_value_id_Y(self, id: int) -> int:
    """
    Indicates the current value 0 of the sensor of ID number Y <id+1>.
    Parameter range:
    -999999999 to +999999999 (initial value: 0)
    """
    try:
      return self.connected_sensors[id].judgment_value_for_communication_unit()
    except IndexError:
      raise IDOutsideValidRangeError
  # ----------------------------------------------------------------------------

  def read_076_sensor_status_mask_setting(self) -> int:
    """
    Set up the condition to determine if the sensor error or
    warning is a recoverable DL-EN1 error (MS LED blinks in
    red). If mask is selected, MS LED does not blink in red
    when a sensor error or warning occurs.
    Parameter range: 0 to 1 (initial value: 0)
    0: Not mask
    1: Mask
    """
    return 1 * self.mask_sensor_status
  # ----------------------------------------------------------------------------

  def write_076_sensor_status_mask_setting(self, setting_data: int) -> None:
    """
    Set up the condition to determine if the sensor error or
    warning is a recoverable DL-EN1 error (MS LED blinks in
    red). If mask is selected, MS LED does not blink in red
    when a sensor error or warning occurs.
    Parameter range: 0 to 1 (initial value: 0)
    0: Not mask
    1: Mask
    """
    if setting_data != 0 and setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.mask_sensor_status = bool(setting_data)
  # ----------------------------------------------------------------------------

  def read_077_sensor_connected_number(self) -> int:
    """
    Indicates the number of connected sensor amplifiers.
    Parameter range: 0 to 15 (initial value: 0)
    """
    return len(self.connected_sensors)
  # ----------------------------------------------------------------------------

  def read_668_error_code_id_00(self) -> int:
    """
    Indicates the error code of ID number 0.
    Parameter range: 0 to 65535 (initial value: 0)
    """
    return self.internal_error
  # ----------------------------------------------------------------------------

  def read_669_to_683_error_code_id_Y(self, id: int) -> int:
    """
    Indicates the error code of ID number Y <id+1>.
    Parameter range: 0 to 65535 (initial value: 0)
    """
    try:
      return self.connected_sensors[id].internal_error
    except IndexError:
      raise IDOutsideValidRangeError
  # ----------------------------------------------------------------------------
