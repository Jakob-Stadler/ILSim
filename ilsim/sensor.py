

# native imports
import time
from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum
from enum import IntFlag
from enum import StrEnum
from enum import auto
from functools import partial
from random import uniform
from threading import Lock
from threading import Thread
from typing import Callable
from typing import Final
from typing import Literal
from typing import Self
from typing import TypeAlias

# internal imports
from .errors import IDOutsideValidRangeError
from .errors import InaccessibleIDOrQueryError
from .errors import NonExecutableStateError
from .errors import QueryOutsideValidRangeError
from .errors import QueryReadProtectedError
from .errors import QueryWriteProtectedError
from .errors import WriteDataOutsideValidRangeError


# Constants
THREAD_SLEEP_DURATION: Final = 0.01
# ------------------------------------------------------------------------------


# Types
BANK_INDEX: TypeAlias = Literal[0, 1, 2, 3]
# ------------------------------------------------------------------------------


class OutputState(IntEnum):
  """
  Output state for MS commands.
  """
  All_OFF = 0
  HIGH = 1
  LOW = 2
  Error = 3
  GO = 4
  HH = 8
  LL = 16
# ------------------------------------------------------------------------------


class ILError(IntFlag):
    """
    Internal error codes for sensor units.
    """

    NO_ERROR = 0b0000_0000_0000_0000  # No Bit
    Overcurrent = 0b0000_0000_0000_0001  # Bit 0
    EEPROM = 0b0000_0000_0000_0010  # Bit 1
    Sensor_Head = 0b0000_0000_0000_0100  # Bit 2
    ERROR_04 = 0b0000_0000_0000_1000  # Bit 3, reserved
    ERROR_05 = 0b0000_0000_0001_0000  # Bit 4, reserved
    ERROR_06 = 0b0000_0000_0010_0000  # Bit 5, reserved
    ERROR_07 = 0b0000_0000_0100_0000  # Bit 6, reserved
    Spot_Light_Laser = 0b0000_0000_1000_0000  # Bit 7
    Incompatible_Model = 0b0000_0001_0000_0000  # Bit 8
    ERROR_0A = 0b0000_0010_0000_0000  # Bit 9, reserved
    ERROR_0B = 0b0000_0100_0000_0000  # Bit 10, reserved
    Amplifier_Communication = 0b0000_1000_0000_0000  # Bit 11
    Number_Of_Units = 0b0001_0000_0000_0000  # Bit 12
    Calculation = 0b0010_0000_0000_0000  # Bit 13
    ERROR_0F = 0b0100_0000_0000_0000  # Bit 14, reserved
    ERROR_10 = 0b1000_0000_0000_0000  # Bit 15, reserved
# ------------------------------------------------------------------------------


class PowerSavingMode(IntEnum):
  """
  Valid values for Sensor's Power Saving Mode.
  """
  OFF = 0
  HALF = 1
  ALL = 2
# ------------------------------------------------------------------------------


class HeadDisplayMode(IntEnum):
  """
  Valid values for Sensor's Head Display Mode.
  """
  DEFAULT = 0
  OK_NG = 1
  OFF = 2
# ------------------------------------------------------------------------------


class OperationResult(IntEnum):
  """
  Three stage result of on operation.
  """
  OPERATING = 0
  NORMAL_TERMINATION = 1
  ABNORMAL_TERMINATION = 2
# ------------------------------------------------------------------------------


class TransistorMode(IntEnum):
  """
  NPN (0) or PNP (1) mode
  """
  NPN = 0
  PNP = 1
# ------------------------------------------------------------------------------


class AnalogOutputMode(IntEnum):
  """
  The type and range of the analog output
  """
  OFF = 0b000
  VOLTAGE_0_TO_5 = 0b001
  VOLTAGE_MINUS_5_TO_5 = 0b010
  VOLTAGE_1_TO_5 = 0b011
  CURRENT_4_TO_20 = 0b100
# ------------------------------------------------------------------------------


class SubdisplayScreenMode(IntEnum):
  """
  Contents of the sub display screen
  """
  RAW_VALUE = 0
  ANALOG_VALUE = 1
  HIGH_VALUE = 2
  LOW_VALUE = 3
  SHIFT_VALUE = 4
  CALC_VALUE = 5
# ------------------------------------------------------------------------------


class CalculationCalibrationMode(IntEnum):
  """
  The mode used for calculated value calibration
  """
  INITIAL = 0
  TWO_POINT = 1
  THREE_POINT = 2
# ------------------------------------------------------------------------------


class CalculationMode(IntEnum):
  """
  The type of function used for the CALC value.
  """
  OFF = 0
  ADDITION = 1
  SUBTRACTION = 2
# ------------------------------------------------------------------------------


class SamplingCycle(IntEnum):
  """
  The setting used for determining the sampling rate.
  """
  DEFAULT = 0
  ONE_THIRD_MS = 1
  ONE_MS = 2
  TWO_MS = 3
  FIVE_MS = 4
# ------------------------------------------------------------------------------


class FilterSetting(IntEnum):
  """
  The filter settings used after sampling.
  """
  TIMES_1 = 0
  TIMES_2 = 1
  TIMES_4 = 2
  TIMES_8 = 3
  TIMES_16 = 4
  TIMES_32 = 5
  TIMES_64 = 6
  TIMES_128 = 7
  TIMES_256 = 8
  TIMES_512 = 9
  TIMES_1024 = 10
  TIMES_2048 = 11
  TIMES_4096 = 12
  DIFF_COUNT = 13
  HIGH_PASS = 14
# ------------------------------------------------------------------------------


class HoldFunctionSetting(IntEnum):
  """
  The sampling hold function setting
  """
  SAMPLE_HOLD = 0
  PEAK_HOLD = 1
  BOTTOM_HOLD = 2
  PEAK_TO_PEAK_HOLD = 3
  AUTO_PEAK_HOLD = 4
  AUTO_BOTTOM_HOLD = 5
# ------------------------------------------------------------------------------


class DelayTimerSetting(IntEnum):
  """
  The delay timer setting.
  """
  OFF = 0
  ON_DELAY = 1
  OFF_DELAY = 2
  ONE_SHOT = 3
# ------------------------------------------------------------------------------


class AnalogOutputScalingMode(IntEnum):
  """
  Analog output mode on the main unit.
  """
  INITIAL = 0
  FREE_RANGE = 1
  BANK = 2
# ------------------------------------------------------------------------------


class ExternalInput1Setting(IntEnum):
  """
  Function assigned to external input 1.
  """
  ZERO_SHIFT = 0
  BANK_A = 1
  BANK_B = 2
  LASER_EMISSION_STOP = 3
  UNUSED = 4
# ------------------------------------------------------------------------------


class ExternalInput2Setting(IntEnum):
  """
  Function assigned to external input 2.
  """
  RESET = 0
  BANK_A = 1
  BANK_B = 2
  LASER_EMISSION_STOP = 3
  UNUSED = 4
# ------------------------------------------------------------------------------


class ExternalInput3Setting(IntEnum):
  """
  Function assigned to external input 3.
  """
  TIMING = 0
  BANK_A = 1
  BANK_B = 2
  LASER_EMISSION_STOP = 3
  UNUSED = 4
# ------------------------------------------------------------------------------


class ExternalInput4Setting(IntEnum):
  """
  Function assigned to external input 4.
  """
  UNUSED = 0
  BANK_A = 1
  BANK_B = 2
  LASER_EMISSION_STOP = 3
# ------------------------------------------------------------------------------


class DisplayDigit(IntEnum):
  """
  Amount of digits to display
  """
  DEFAULT = 0
  THREE_DIGITS = 1
  TWO_DIGITS = 2
  ONE_DIGIT = 3
  ZERO_DIGITS = 4
# ------------------------------------------------------------------------------


class DisplayColor(IntEnum):
  """
  Display color of amplifier unit.
  """
  GO_GREEN = 0
  GO_RED = 1
  ALWAYS_RED = 2
# ------------------------------------------------------------------------------


class HighPassCutoffFrequency(IntEnum):
  """
  Cutoff frequency of high pass filter.
  """
  HZ_POINT_1 = 0
  HZ_POINT_2 = 1
  HZ_POINT_5 = 2
  HZ_1 = 3
  HZ_2 = 4
  HZ_5 = 5
  HZ_10 = 6
  HZ_20 = 7
  HZ_50 = 8
  HZ_100 = 9
# ------------------------------------------------------------------------------


class AlarmSetting(IntEnum):
  """
  Alarm settings.
  """
  INITIAL = 0
  CLAMP = 1
  USER_SETTING = 2
# ------------------------------------------------------------------------------


class ProductCode(IntEnum):
  """
  Indicates the product code.
  """
  MAIN_UNIT = 4022
  EXPANSION_UNIT = 4023
# ------------------------------------------------------------------------------


class SensorHeadCode(IntEnum):
  """
  Indicates model of sensor head connected to the amplifier.
  """
  NOT_CONNECTED = 0
  IL_030 = 1
  IL_065 = 2
  IL_100 = 3
  IL_300 = 4
  IL_600 = 5
  IL_S025 = 106
  IL_S065 = 107
  IL_S100 = 208
  IL_2000 = 311
# ------------------------------------------------------------------------------


class ProductName(StrEnum):
  """
  Indicates the product name.
  """
  MAIN_UNIT = "IL-1000/1500"
  EXPANSION_UNIT = "IL-1050/1550"
# ------------------------------------------------------------------------------


class SeriesCode(IntEnum):
  """
  Indicates the series code.
  """
  MAIN_UNIT = 4022
  EXPANSION_UNIT = 4023
# ------------------------------------------------------------------------------


class LEDColor(IntEnum):
  """
  Color of Indicator LED
  """
  OFF = 0
  GREEN = auto()
  RED = auto()
  ORANGE = auto()
  BLINKING = auto()
# ------------------------------------------------------------------------------


def get_scale_values(
  x1: float,
  y1: float,
  x2: float,
  y2: float,
) -> tuple[float, float]:
  """
  Get tilt and offset values of straight line equation
  `f(x) = tilt * x + offset` as tuple `(tilt, offset)`.
  """
  tilt = (y2 - y1) / (x2 - x1)
  offset = (y1 - x1 * tilt)
  return tilt, offset
# ------------------------------------------------------------------------------


def scale_values(
  x: float,
  x1: float,
  y1: float,
  x2: float,
  y2: float,
) -> float:
  """
  Scale value `x` on straight line, defined by
  coordinates (x1, y1) and (x2, y2).
  """
  tilt, offset = get_scale_values(x1, y1, x2, y2)
  return tilt * x + offset
# ------------------------------------------------------------------------------


# Bank data
@dataclass
class Bank:
  """
  Stores banked values.
  """
  threshold_high: float = field(default=5)
  threshold_low: float = field(default=-5)
  shift_target: float = field(default=0)
  analog_upper_limit: float = field(default=10)
  analog_lower_limit: float = field(default=-10)
# ------------------------------------------------------------------------------


# Sensor data and functions
class SensorUnit:
  """
  Simulates sensor head + amplifier unit
  """
  # ----------------------------------------------------------------------------
  _error_during_sampling: bool
  _raw_value: float | None
  _r_v_value: float | None
  _calc_value: float | None
  _p_v_value: float | None
  _hold_value: float | None
  _hold_bottom: float | None
  _hold_peak: float | None
  _two_point_high_side_1st_point: float | None
  _two_point_low_side_1st_point: float | None
  _two_point_diff_count_1st_point: float | None
  _calc_2p_calibration_set_1_before_calc: float | None
  _calc_3p_calibration_set_1_before_calc: float | None
  _calc_3p_calibration_set_1_before_rv_main: float | None
  _calc_3p_calibration_set_1_before_rv_expansion: float | None
  _calc_3p_calibration_set_2_before_calc: float | None
  _calc_3p_calibration_set_2_before_rv_main: float | None
  _calc_3p_calibration_set_2_before_rv_expansion: float | None
  _calibration_set_1_before: float | None
  _eeprom_thread: Thread
  _eeprom_lock: Lock
  _input_thread: Thread
  _keep_threads_alive: bool
  _next_eeprom_write: float | None
  _timing_input: bool
  abnormal_settings: bool
  active_bank_setting: BANK_INDEX
  alarm_count: int
  alarm_setting: AlarmSetting
  analog_output_mode: AnalogOutputMode
  analog_output_scaling_mode: AnalogOutputScalingMode
  auto_trigger_level: float
  banks: tuple[Bank, Bank, Bank, Bank]
  calc_2p_calibration_set_1: float
  calc_2p_calibration_set_2: float
  calc_3p_calibration_set_1: float
  calc_3p_calibration_set_3: float
  calc_calibration_mode: CalculationCalibrationMode
  calculation_mode: CalculationMode
  calculation_tilt: float
  calculation_offset: float
  calibration_result: OperationResult
  calibration_tilt: float
  calibration_offset: float
  calibration_set_1: float
  calibration_set_2: float
  calibration_set_1_real: float
  calibration_set_2_real: float
  calibration_use_user_settings: bool
  connected_sensor_head: SensorHeadCode
  connected_amplifier: Self | None
  currently_sampling: bool
  decimal_position: int
  default_analog_lower_limit: float
  default_analog_upper_limit: float
  default_auto_trigger_level: float
  default_bank_analog_upper_limit: float
  default_bank_analog_lower_limit: float
  default_shift_target: float
  default_threshold_high: float
  default_threshold_low: float
  default_tolerance_setting_range: float
  delay_timer_setting: DelayTimerSetting
  device_type: int
  diff_count_filter_timer_duration: int
  display_color: DisplayColor
  default_display_digit: int
  display_digit_setting: DisplayDigit
  eeprom_write_result: OperationResult
  external_input_1: bool
  external_input_1_setting: ExternalInput1Setting
  external_input_2: bool
  external_input_2_setting: ExternalInput2Setting
  external_input_3: bool
  external_input_3_setting: ExternalInput3Setting
  external_input_4: bool
  external_input_4_setting: ExternalInput4Setting
  external_input_use_user_settings: bool
  filter_setting: FilterSetting
  free_analog_lower_limit: float
  free_analog_upper_limit: float
  future_analog_output_mode: AnalogOutputMode
  future_transistor_mode: TransistorMode
  head_display_mode: HeadDisplayMode
  high_pass_cutoff_frequency: HighPassCutoffFrequency
  hold_function_setting: HoldFunctionSetting
  hysteresis: float
  internal_error: ILError
  is_main_unit: bool
  key_locked: bool
  lower_bound: float
  measurement_range_max: float
  measurement_range_min: float
  mutual_interference_prevention_active: bool
  output_mode_normally_closed: bool
  power_saving_mode: PowerSavingMode
  randomized: bool
  randomized_upper_limit: float
  randomized_lower_limit: float
  reference_distance: float
  reference_distance_analog_tolerance: float
  reference_distance_tolerance: float
  reset_request_result: OperationResult
  reversed_measurement_direction: bool
  revision: int
  sampling_cycle: SamplingCycle
  default_sampling_cycle: float
  series_version: int
  stored_laser_emission_stop: bool
  stored_timing_input: bool
  subdisplay_screen_mode: SubdisplayScreenMode
  switch_banks_via_external_input: bool
  timer_duration: int
  timing_input_on_edge: bool
  tolerance_setting_range: float
  transistor_mode: TransistorMode
  tuning_result: OperationResult
  uncertainty: float
  upper_bound: float
  zero_shift_saved_in_memory: bool
  zero_shifting_result: OperationResult
  # ----------------------------------------------------------------------------
  read_mapping: dict[int, Callable[[], int | str]]
  write_mapping: dict[int, Callable[[int], None]]
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    initial_value: float | None = 0.000,
    measurement_range_max: float = 45.000,
    measurement_range_min: float = 20.000,
    reference_distance: float = 30.000,
    reference_distance_tolerance: float = 0.250,
    reference_distance_analog_tolerance: float = 5.000,
    decimal_position: int = 3,
    uncertainty: float = 0.010,   # 10x data sheet repeatability
    default_analog_upper_limit: float = 5.000,
    default_analog_lower_limit: float = -5.000,
    default_threshold_high: float = 5.000,
    default_threshold_low: float = -5.000,
    default_shift_target: float = 0.000,
    default_bank_analog_upper_limit: float = 10.000,
    default_bank_analog_lower_limit: float = -10.000,
    default_tolerance_setting_range: float = 0.200,
    default_auto_trigger_level: float = 1.00,
    default_sampling_cycle: float = 1.000,
    default_display_digit: int = 2,
    connected_sensor_head: SensorHeadCode = SensorHeadCode.IL_030,
  ) -> None:
    """
    Simulates sensor head + amplifier unit.

    Defaults to IL-030 settings.
    """
    self.init_mappings()

    self._keep_threads_alive = True
    self._next_eeprom_write = None
    self._eeprom_thread = Thread(
      target=self.perform_eeprom_writes,
      daemon=True
    )
    self._input_thread = Thread(
      target=self.perform_input_updates,
      daemon=True
    )
    self._eeprom_lock = Lock()

    self.calibration_tilt = 1.0
    self.calibration_offset = 0.0
    self.calculation_tilt = 1.0
    self.calculation_offset = 0.0
    self._hold_value = None
    self._hold_bottom = None
    self._hold_peak = None
    self.measurement_range_max = measurement_range_max
    self.measurement_range_min = measurement_range_min
    self.reference_distance = reference_distance
    self.reference_distance_tolerance = reference_distance_tolerance
    self.reference_distance_analog_tolerance = (
      reference_distance_analog_tolerance
    )
    self.decimal_position = decimal_position
    self.lower_bound = self.int_to_mm(-99999)
    self.upper_bound = self.int_to_mm(99999)
    self.uncertainty = uncertainty
    self.default_analog_upper_limit = default_analog_upper_limit
    self.default_analog_lower_limit = default_analog_lower_limit
    self.default_tolerance_setting_range = default_tolerance_setting_range
    self.default_threshold_high = default_threshold_high
    self.default_threshold_low = default_threshold_low
    self.default_shift_target = default_shift_target
    self.default_bank_analog_upper_limit = default_bank_analog_upper_limit
    self.default_bank_analog_lower_limit = default_bank_analog_lower_limit
    self.default_auto_trigger_level = default_auto_trigger_level
    self.default_sampling_cycle = default_sampling_cycle
    self.default_display_digit = default_display_digit
    self.connected_sensor_head = connected_sensor_head
    self.calibration_set_1 = self.int_to_mm(0)
    self.calibration_set_2 = self.int_to_mm(5000)
    self.calibration_set_1_real = self.calibration_set_1
    self.calibration_set_2_real = self.calibration_set_2
    self.calibration_use_user_settings = False

    self.randomized = False
    self.randomized_upper_limit = (
      self.reference_distance - self.measurement_range_min
    )
    self.randomized_lower_limit = (
      self.reference_distance - self.measurement_range_max
    )
    self.is_main_unit = True
    self.connected_amplifier = None
    self._timing_input = False
    self.abnormal_settings = False
    self.currently_sampling = True
    self.eeprom_write_result = OperationResult.NORMAL_TERMINATION
    self.tuning_result = OperationResult.NORMAL_TERMINATION
    self.zero_shifting_result = OperationResult.NORMAL_TERMINATION
    self.reset_request_result = OperationResult.NORMAL_TERMINATION
    self.calibration_result = OperationResult.NORMAL_TERMINATION
    self.internal_error = ILError.NO_ERROR
    self.device_type = 0
    self.revision = 0x0101
    self.series_version = 1

    self._error_during_sampling = False

    self.restore_default_settings()

    self.future_transistor_mode = TransistorMode.NPN
    self.future_analog_output_mode = AnalogOutputMode.OFF
    self.set_system_parameters()

    self.raw_value = initial_value
    self._eeprom_thread.start()
    self._input_thread.start()
  # ----------------------------------------------------------------------------

  def init_mappings(self) -> None:
    """
    Create the function mappings for SR and SW commands.
    """
    self.read_mapping = {
      33: self.read_033_sensor_amplifier_error,
      36: self.read_036_judgment_alarm_output,
      37: self.read_037_judgment_value,
      38: self.read_038_internal_measurement_value,
      39: self.read_039_peak_hold_value_during_hold_period,
      40: self.read_040_bottom_hold_value_during_hold_period,
      41: self.read_041_calculation_value,
      42: self.read_042_analog_output_value,
      43: self.read_043_bank_status,
      44: self.read_044_timing_status,
      50: self.read_050_laser_emission_stop_status,
      51: self.read_051_abnormal_setting,
      52: self.read_052_external_input_status,
      53: self.read_053_eeprom_write_result,
      54: self.read_054_zero_shift_zero_shift_reset_result,
      55: self.read_055_reset_request_result,
      56: self.read_056_current_system_parameters,
      60: self.read_060_tuning_result,
      61: self.read_061_calibraiton_result,
      97: self.read_097_key_lock_function,
      98: self.read_098_bank_function,
      99: self.read_099_timing_input,
      100: self.read_100_laser_emission_on_stop_input,
      104: self.read_104_sub_display_screen,
      105: self.read_105_system_parameter_settings,
      106: self.read_106_tolerance_tuning_setting_range,
      107: self.read_107_calibration_function,
      108: self.read_108_calibration_function_set_1,
      109: self.read_109_calibration_function_set_2,
      110: self.read_110_calculated_value_calibration_function,
      111: self.read_111_calculated_value_two_point_set_1,
      112: self.read_112_calculated_value_two_point_set_2,
      113: self.read_113_calculated_value_three_point_set_1,
      114: self.read_114_calculated_value_three_point_set_3,
      129: self.read_129_calculation_function,
      131: self.read_131_measurement_direction,
      132: self.read_132_sampling_cycle,
      133: self.read_133_averaging_diff_count_high_pass_filter,
      134: self.read_134_output_mode,
      136: self.read_136_hold_function_setting,
      137: self.read_137_auto_hold_trigger_level,
      138: self.read_138_timing_input_setting,
      139: self.read_139_delay_timer,
      140: self.read_140_timer_duration,
      141: self.read_141_hyseresis,
      142: self.read_142_analog_output_scaling,
      143: self.read_143_analog_output_upper_limit_value,
      144: self.read_144_analog_output_lower_limit_value,
      145: self.read_145_external_input,
      146: self.read_146_external_input_1,
      147: self.read_147_external_input_2,
      148: self.read_148_external_input_3,
      149: self.read_149_external_input_4,
      150: self.read_150_bank_switching_method,
      152: self.read_152_zero_shift_value_memory_function,
      153: self.read_153_mutual_interference_prevention_function,
      154: self.read_154_display_digit,
      155: self.read_155_power_saving_function,
      156: self.read_156_head_display_mode,
      157: self.read_157_display_color,
      158: self.read_158_timer_duration_diff_count_filter,
      159: self.read_159_cutoff_frequency_high_pass_filter,
      161: self.read_161_alarm_setting,
      162: self.read_162_alarm_count,
      193: self.read_193_product_code,
      194: self.read_194_revision,
      195: self.read_195_connected_sensor_head,
      200: self.read_200_product_name,
      215: self.read_215_series_code,
      216: self.read_216_series_version,
      217: self.read_217_device_type,
    }
    self.write_mapping = {
      1: self.write_001_zero_shift_execution_request,
      2: self.write_002_zero_shift_reset_request,
      3: self.write_003_reset_request,
      5: self.write_005_initial_reset_request,
      6: self.write_006_system_parameters_set_request,
      14: self.write_014_tolerance_tuning_request,
      15: self.write_015_2point_high_1st_point_request,
      16: self.write_016_2point_high_2nd_point_request,
      17: self.write_017_2point_low_1st_point_request,
      18: self.write_018_2point_low_2nd_point_request,
      19: self.write_019_calibration_set_1_request,
      20: self.write_020_calibration_set_2_request,
      21: self.write_021_calc_2point_calibration_set_1_request,
      22: self.write_022_calc_2point_calibration_set_2_request,
      23: self.write_023_calc_3point_calibration_set_1_request,
      24: self.write_024_calc_3point_calibration_set_2_request,
      25: self.write_025_calc_3point_calibration_set_3_request,
      26: self.write_026_diff_count_filter_1point_tuning_request,
      27: self.write_027_diff_count_filter_2point_1st_point_request,
      28: self.write_028_diff_count_filter_2point_2nd_point_request,
      97: self.write_097_key_lock_function,
      98: self.write_098_bank_function,
      99: self.write_099_timing_input,
      100: self.write_100_laser_emission_on_stop_input,
      104: self.write_104_sub_display_screen,
      105: self.write_105_system_parameter_settings,
      106: self.write_106_tolerance_tuning_setting_range,
      107: self.write_107_calibration_function,
      108: self.write_108_calibration_function_set_1,
      109: self.write_109_calibration_function_set_2,
      110: self.write_110_calculated_value_calibration_function,
      111: self.write_111_calculated_value_two_point_set_1,
      112: self.write_112_calculated_value_two_point_set_2,
      113: self.write_113_calculated_value_three_point_set_1,
      114: self.write_114_calculated_value_three_point_set_3,
      129: self.write_129_calculation_function,
      131: self.write_131_measurement_direction,
      132: self.write_132_sampling_cycle,
      133: self.write_133_averaging_diff_count_high_pass_filter,
      134: self.write_134_output_mode,
      136: self.write_136_hold_function_setting,
      137: self.write_137_auto_hold_trigger_level,
      138: self.write_138_timing_input_setting,
      139: self.write_139_delay_timer,
      140: self.write_140_timer_duration,
      141: self.write_141_hyseresis,
      142: self.write_142_analog_output_scaling,
      143: self.write_143_analog_output_upper_limit_value,
      144: self.write_144_analog_output_lower_limit_value,
      145: self.write_145_external_input,
      146: self.write_146_external_input_1,
      147: self.write_147_external_input_2,
      148: self.write_148_external_input_3,
      149: self.write_149_external_input_4,
      150: self.write_150_bank_switching_method,
      152: self.write_152_zero_shift_value_memory_function,
      153: self.write_153_mutual_interference_prevention_function,
      154: self.write_154_display_digit,
      155: self.write_155_power_saving_function,
      156: self.write_156_head_display_mode,
      157: self.write_157_display_color,
      158: self.write_158_timer_duration_diff_count_filter,
      159: self.write_159_cutoff_frequency_high_pass_filter,
      161: self.write_161_alarm_setting,
      162: self.write_162_alarm_count,
    }
    for i in (0, 1, 2, 3):
      self.read_mapping[65 + 5 * i + 0] = partial(
        self.read_06X_high_setting_value_bank_Y, i
      )
      self.read_mapping[65 + 5 * i + 1] = partial(
        self.read_06X_low_setting_value_bank_Y, i
      )
      self.read_mapping[65 + 5 * i + 2] = partial(
        self.read_06X_shift_target_value_bank_Y, i
      )
      self.read_mapping[65 + 5 * i + 3] = partial(
        self.read_06X_analog_output_upper_limit_bank_Y, i
      )
      self.read_mapping[65 + 5 * i + 4] = partial(
        self.read_06X_analog_output_lower_limit_bank_Y, i
      )

      self.write_mapping[65 + 5 * i + 0] = partial(
        self.write_06X_high_setting_value_bank_Y, i
      )
      self.write_mapping[65 + 5 * i + 1] = partial(
        self.write_06X_low_setting_value_bank_Y, i
      )
      self.write_mapping[65 + 5 * i + 2] = partial(
        self.write_06X_shift_target_value_bank_Y, i
      )
      self.write_mapping[65 + 5 * i + 3] = partial(
        self.write_06X_analog_output_upper_limit_bank_Y, i
      )
      self.write_mapping[65 + 5 * i + 4] = partial(
        self.write_06X_analog_output_lower_limit_bank_Y, i
      )
  # ----------------------------------------------------------------------------

  def restore_default_settings(self) -> None:
    """
    Sets all values to their initial defaults.
    """
    self._hold_value = None
    self._hold_bottom = None
    self._hold_peak = None

    def create_bank() -> Bank:
      return Bank(
        threshold_high=self.default_threshold_high,
        threshold_low=self.default_threshold_low,
        shift_target=self.default_shift_target,
        analog_upper_limit=self.default_bank_analog_upper_limit,
        analog_lower_limit=self.default_bank_analog_lower_limit,
      )

    self.banks = (
      create_bank(),
      create_bank(),
      create_bank(),
      create_bank(),
    )  # Create 4 banks with default values

    self.active_bank_setting = 0

    self.free_analog_upper_limit = self.default_bank_analog_upper_limit
    self.free_analog_lower_limit = self.default_bank_analog_lower_limit

    self.tolerance_setting_range = self.default_tolerance_setting_range
    self.auto_trigger_level = self.default_auto_trigger_level

    self._two_point_high_side_1st_point = None
    self._two_point_low_side_1st_point = None
    self._two_point_diff_count_1st_point = None
    self._calibration_set_1_before = None
    self._calc_2p_calibration_set_1_before_calc = None
    self._calc_3p_calibration_set_1_before_calc = None
    self._calc_3p_calibration_set_1_before_rv_main = None
    self._calc_3p_calibration_set_1_before_rv_expansion = None
    self._calc_3p_calibration_set_2_before_calc = None
    self._calc_3p_calibration_set_2_before_rv_main = None
    self._calc_3p_calibration_set_2_before_rv_expansion = None

    self.alarm_count = 7
    self.alarm_setting = AlarmSetting.INITIAL
    self.analog_output_scaling_mode = AnalogOutputScalingMode.INITIAL
    self.calc_2p_calibration_set_1 = self.int_to_mm(5000)
    self.calc_2p_calibration_set_2 = self.int_to_mm(10000)
    self.calc_3p_calibration_set_1 = self.int_to_mm(5000)
    self.calc_3p_calibration_set_3 = self.int_to_mm(10000)
    self.calc_calibration_mode = CalculationCalibrationMode.INITIAL
    self.calculation_mode = CalculationMode.OFF
    self.delay_timer_setting = DelayTimerSetting.OFF
    self.diff_count_filter_timer_duration = 10
    self.display_color = DisplayColor.GO_GREEN
    self.display_digit_setting = DisplayDigit.DEFAULT
    self.external_input_1 = False
    self.external_input_1_setting = ExternalInput1Setting.ZERO_SHIFT
    self.external_input_2 = False
    self.external_input_2_setting = ExternalInput2Setting.RESET
    self.external_input_3 = False
    self.external_input_3_setting = ExternalInput3Setting.TIMING
    self.external_input_4 = False
    self.external_input_4_setting = ExternalInput4Setting.UNUSED
    self.external_input_use_user_settings = False
    self.filter_setting = FilterSetting.TIMES_16
    self.head_display_mode = HeadDisplayMode.DEFAULT
    self.high_pass_cutoff_frequency = HighPassCutoffFrequency.HZ_1
    self.hold_function_setting = HoldFunctionSetting.SAMPLE_HOLD
    self.hysteresis = 0.000
    self.key_locked = False
    self.stored_laser_emission_stop = False
    self.mutual_interference_prevention_active = False
    self.output_mode_normally_closed = False
    self.power_saving_mode = PowerSavingMode.OFF
    self.reversed_measurement_direction = False
    self.sampling_cycle = SamplingCycle.DEFAULT
    self.stored_timing_input = False
    self.subdisplay_screen_mode = SubdisplayScreenMode.RAW_VALUE
    self.subdisplay_screen_mode = SubdisplayScreenMode.RAW_VALUE
    self.switch_banks_via_external_input = False
    self.timer_duration = 60  # ms
    self.timing_input_on_edge = False
    self.zero_shift_saved_in_memory = False
    self.update_timing_input_status()
    self.start_eeprom_write(write_duration=3.0)
  # ----------------------------------------------------------------------------

  def set_system_parameters(self) -> None:
    """
    Changes the system parameters (the polarity of the
    judgment and alarm outputs and the analog output
    setting) to the values written in "System parameter
    settings" of data number 105.
    [`future_analog_output_mode` and `future_transistor_mode`]

    To set the system parameters, confirm that the change is
    proper according to the connected devices and wiring.
    A wrong change may damage the sensor amplifier or the
    connected equipment.
    """
    self.analog_output_mode = self.future_analog_output_mode
    self.transistor_mode = self.future_transistor_mode
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def reset(self) -> None:
    """
    Resets the sensor
    """
    if not self.zero_shift_saved_in_memory:
      self.change_shift_target(0)
      for bank in self.banks:
        bank.shift_target = 0
    # TODO: Implement real reset
  # ----------------------------------------------------------------------------

  def perform_input_updates(self) -> None:
    """
    Thread entry point for _input_thread.

    Simulates changing internal variables on external input changes.
    """
    while self._keep_threads_alive:
      self.update_timing_input_status()
      time.sleep(THREAD_SLEEP_DURATION)
  # ----------------------------------------------------------------------------

  def perform_eeprom_writes(self) -> None:
    """
    Thread entry point for _eeprom_thread.

    Simulates the write operation after 2 seconds of inactivity.
    """
    while self._keep_threads_alive:
      with self._eeprom_lock:
        if self._next_eeprom_write and self._next_eeprom_write <= time.time():
          if self.internal_error == ILError.EEPROM:
            self.eeprom_write_result = OperationResult.ABNORMAL_TERMINATION
          else:
            self.eeprom_write_result = OperationResult.NORMAL_TERMINATION
          self._next_eeprom_write = None
      time.sleep(THREAD_SLEEP_DURATION)
  # ----------------------------------------------------------------------------

  def start_eeprom_write(self, write_duration: float = 2.0) -> None:
    """
    Starts the EEPROM write process.

    The actual writing will be performed 2* seconds after the last call to this
    function. Every call will reset the timer back to 2* seconds.

    *) 2 seconds by default, can be changed via parameter `write_duration`
    """
    self.eeprom_write_result = OperationResult.OPERATING
    next_write: float = time.time() + write_duration
    with self._eeprom_lock:
      if (
        self._next_eeprom_write is None
        or self._next_eeprom_write < next_write
      ):
        self._next_eeprom_write = next_write
  # ----------------------------------------------------------------------------

  def stop_threads(self) -> None:
    """
    Stops all sub-threads.
    """
    self._keep_threads_alive = False
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_S025(cls) -> Self:
    """
    Create SensorUnit with IL-S025 parameters.
    """
    return cls(
      initial_value=0.000,
      measurement_range_max=30.000,
      measurement_range_min=20.000,
      reference_distance=25.000,
      reference_distance_tolerance=0.250,
      reference_distance_analog_tolerance=5.000,
      decimal_position=3,
      uncertainty=0.010,
      default_analog_upper_limit=5.000,
      default_analog_lower_limit=-5.000,
      default_tolerance_setting_range=0.200,
      default_threshold_high=5.000,
      default_threshold_low=-5.000,
      default_auto_trigger_level=1.00,
      default_bank_analog_upper_limit=10.000,
      default_bank_analog_lower_limit=-10.000,
      default_sampling_cycle=1.000,
      default_display_digit=2,
      connected_sensor_head=SensorHeadCode.IL_S025,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_030(cls) -> Self:
    """
    Create SensorUnit with IL-030 parameters.
    """
    return cls(
      initial_value=0.000,
      measurement_range_max=45.000,
      measurement_range_min=20.000,
      reference_distance=30.000,
      reference_distance_tolerance=0.250,
      reference_distance_analog_tolerance=5.000,
      decimal_position=3,
      uncertainty=0.010,
      default_analog_upper_limit=5.000,
      default_analog_lower_limit=-5.000,
      default_tolerance_setting_range=0.200,
      default_threshold_high=5.000,
      default_threshold_low=-5.000,
      default_auto_trigger_level=1.00,
      default_bank_analog_upper_limit=10.000,
      default_bank_analog_lower_limit=-10.000,
      default_sampling_cycle=1.000,
      default_display_digit=2,
      connected_sensor_head=SensorHeadCode.IL_030,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_065(cls) -> Self:
    """
    Create SensorUnit with IL-065 parameters.
    """
    return cls(
      initial_value=0.000,
      measurement_range_max=105.000,
      measurement_range_min=55.000,
      reference_distance=65.000,
      reference_distance_tolerance=0.500,
      reference_distance_analog_tolerance=10.000,
      decimal_position=3,
      uncertainty=0.020,
      default_analog_upper_limit=10.000,
      default_analog_lower_limit=-10.000,
      default_tolerance_setting_range=0.200,
      default_threshold_high=5.000,
      default_threshold_low=-5.000,
      default_auto_trigger_level=1.00,
      default_bank_analog_upper_limit=10.000,
      default_bank_analog_lower_limit=-10.000,
      default_sampling_cycle=1.000,
      default_display_digit=2,
      connected_sensor_head=SensorHeadCode.IL_065,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_S065(cls) -> Self:
    """
    Create SensorUnit with IL-S065 parameters.
    """
    return cls(
      initial_value=0.000,
      measurement_range_max=75.000,
      measurement_range_min=55.000,
      reference_distance=65.000,
      reference_distance_tolerance=0.500,
      reference_distance_analog_tolerance=10.000,
      decimal_position=3,
      uncertainty=0.020,
      default_analog_upper_limit=10.000,
      default_analog_lower_limit=-10.000,
      default_tolerance_setting_range=0.200,
      default_threshold_high=5.000,
      default_threshold_low=-5.000,
      default_auto_trigger_level=1.00,
      default_bank_analog_upper_limit=10.000,
      default_bank_analog_lower_limit=-10.000,
      default_sampling_cycle=1.000,
      default_display_digit=2,
      connected_sensor_head=SensorHeadCode.IL_S065,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_100(cls) -> Self:
    """
    Create SensorUnit with IL-100 parameters.
    """
    return cls(
      initial_value=0.000,
      measurement_range_max=130.000,
      measurement_range_min=75.000,
      reference_distance=100.000,
      reference_distance_tolerance=1.000,
      reference_distance_analog_tolerance=20.000,
      decimal_position=3,
      uncertainty=0.040,
      default_analog_upper_limit=20.000,
      default_analog_lower_limit=-20.000,
      default_tolerance_setting_range=0.200,
      default_threshold_high=5.000,
      default_threshold_low=-5.000,
      default_auto_trigger_level=1.00,
      default_bank_analog_upper_limit=10.000,
      default_bank_analog_lower_limit=-10.000,
      default_sampling_cycle=1.000,
      default_display_digit=2,
      connected_sensor_head=SensorHeadCode.IL_100,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_300(cls) -> Self:
    """
    Create SensorUnit with IL-300 parameters.
    """
    return cls(
      initial_value=0.00,
      measurement_range_max=450.00,
      measurement_range_min=160.00,
      reference_distance=300.00,
      reference_distance_tolerance=7.00,
      reference_distance_analog_tolerance=140.00,
      decimal_position=2,
      uncertainty=0.30,
      default_analog_upper_limit=140.00,
      default_analog_lower_limit=-140.00,
      default_tolerance_setting_range=2.00,
      default_threshold_high=50.00,
      default_threshold_low=-50.00,
      default_auto_trigger_level=10.00,
      default_bank_analog_upper_limit=100.00,
      default_bank_analog_lower_limit=-100.00,
      default_sampling_cycle=2.000,
      default_display_digit=1,
      connected_sensor_head=SensorHeadCode.IL_300,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_600(cls) -> Self:
    """
    Create SensorUnit with IL-600 parameters.
    """
    return cls(
      initial_value=0.00,
      measurement_range_max=1000.00,
      measurement_range_min=200.00,
      reference_distance=600.00,
      reference_distance_tolerance=20.00,
      reference_distance_analog_tolerance=400.00,
      decimal_position=2,
      uncertainty=0.50,
      default_analog_upper_limit=400.00,
      default_analog_lower_limit=-400.00,
      default_tolerance_setting_range=2.00,
      default_threshold_high=50.00,
      default_threshold_low=-50.00,
      default_auto_trigger_level=10.00,
      default_bank_analog_upper_limit=100.00,
      default_bank_analog_lower_limit=-100.00,
      default_sampling_cycle=2.000,
      default_display_digit=1,
      connected_sensor_head=SensorHeadCode.IL_600,
    )
  # ----------------------------------------------------------------------------

  @classmethod
  def create_IL_2000(cls) -> Self:
    """
    Create SensorUnit with IL-2000 parameters.
    """
    return cls(
      initial_value=0.0,
      measurement_range_max=3500.0,
      measurement_range_min=1000.0,
      reference_distance=2000.0,
      reference_distance_tolerance=50.0,
      reference_distance_analog_tolerance=1000.0,
      decimal_position=1,
      uncertainty=1.0,
      default_analog_upper_limit=1000.0,
      default_analog_lower_limit=-1000.0,
      default_tolerance_setting_range=20.0,
      default_threshold_high=500.0,
      default_threshold_low=-500.0,
      default_auto_trigger_level=100.0,
      default_bank_analog_upper_limit=1000.0,
      default_bank_analog_lower_limit=-1000.0,
      default_sampling_cycle=5.000,
      default_display_digit=0,
      connected_sensor_head=SensorHeadCode.IL_2000,
    )
  # ----------------------------------------------------------------------------

  def calibrate_sensor(
    self,
    p1_before: float,
    p1_after: float,
    p2_before: float,
    p2_after: float
  ) -> None:
    """
    Calibrate sensor with two points p1 and p2.
    """
    # Back-transform to raw values without calibration
    old_tilt: float = self.calibration_tilt
    old_offset: float = self.calibration_offset
    p1_raw: float = (p1_before - old_offset) / old_tilt
    p2_raw: float = (p2_before - old_offset) / old_tilt
    # Calculate and set new calibration coefficents
    new_tilt, new_offset = get_scale_values(p1_raw, p1_after, p2_raw, p2_after)
    self.calibration_tilt = new_tilt
    self.calibration_offset = new_offset
    # How do calibration and zero shifting interact?
    # Does calibration change the interal shifiting values so the shifted
    # pointed stays the same, or does is the shifitng also affected by
    # calibration tilt?
    # if self.calibration_use_user_settings:
    #   for bank in self.banks:
    #     bank.shift_target = new_tilt * bank.shift_target / old_tilt
  # ----------------------------------------------------------------------------

  def calibrate_calc(
    self,
    p1_before: float,
    p1_after: float,
    p2_before: float,
    p2_after: float
  ) -> None:
    """
    Calibrate sensor with two points p1 and p2.
    """
    # Back-transform to raw values without calibration
    old_tilt: float = self.calculation_tilt
    old_offset: float = self.calculation_offset
    p1_raw: float = (p1_before - old_offset) / old_tilt
    p2_raw: float = (p2_before - old_offset) / old_tilt
    # Calculate and set new calibration coefficents
    new_tilt, new_offset = get_scale_values(p1_raw, p1_after, p2_raw, p2_after)
    self.calculation_tilt = new_tilt
    self.calculation_offset = new_offset
  # ----------------------------------------------------------------------------

  def mm_to_int(self, value: float | None) -> int:
    """
    Convert millimeter values to Protocol integers.
    """
    if value is None:
      return -99998
    if value > self.upper_bound:
      return 99999
    if value < self.lower_bound:
      return -99999
    return int(value * 10**self.decimal_position)
  # ----------------------------------------------------------------------------

  def int_to_mm(self, value: int) -> float:
    """
    Convert Protocol integers to millimeter values.
    """
    return float(value / 10**self.decimal_position)
  # ----------------------------------------------------------------------------

  def change_low_threshold(
    self,
    value: float,
    index: BANK_INDEX | None = None
  ) -> None:
    """
    Change the LOW signal threshold.
    """
    if index is None:
      index = self.active_bank_index
    self.banks[index].threshold_low = value
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_low_threshold(
    self,
    index: BANK_INDEX | None = None
  ) -> float:
    """
    Read the LOW signal threshold.
    """
    if index is None:
      index = self.active_bank_index
    return self.banks[index].threshold_low
  # ----------------------------------------------------------------------------

  def change_high_threshold(
    self,
    value: float,
    index: BANK_INDEX | None = None
  ) -> None:
    """
    Change the HIGH signal threshold.
    """
    if index is None:
      index = self.active_bank_index
    self.banks[index].threshold_high = value
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_high_threshold(
    self,
    index: BANK_INDEX | None = None
  ) -> float:
    """
    Read the HIGH signal threshold.
    """
    if index is None:
      index = self.active_bank_index
    return self.banks[index].threshold_high
  # ----------------------------------------------------------------------------

  def change_shift_target(
    self,
    value: float,
    index: BANK_INDEX | None = None
  ) -> None:
    """
    Change the Zero Shift target value.
    """
    if index is None:
      index = self.active_bank_index
    self.banks[index].shift_target = value
    if self.zero_shift_saved_in_memory:
      self.start_eeprom_write(write_duration=0)
  # ----------------------------------------------------------------------------

  def read_shift_target(
    self,
    index: BANK_INDEX | None = None
  ) -> float:
    """
    Read the Zero Shift target value.
    """
    if index is None:
      index = self.active_bank_index
    return self.banks[index].shift_target
  # ----------------------------------------------------------------------------

  def change_analog_upper_limit(
    self,
    value: float,
    index: BANK_INDEX | None = None
  ) -> None:
    """
    Change the analog output upper limit value.
    """
    if index is None:
      index = self.active_bank_index
    self.banks[index].analog_upper_limit = value
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_analog_upper_limit(
    self,
    index: BANK_INDEX | None = None
  ) -> float:
    """
    Read the analog output upper limit value.
    """
    if index is None:
      index = self.active_bank_index
    return self.banks[index].analog_upper_limit
  # ----------------------------------------------------------------------------

  def change_analog_lower_limit(
    self,
    value: float,
    index: BANK_INDEX | None = None
  ) -> None:
    """
    Change the analog output upper limit value.
    """
    if index is None:
      index = self.active_bank_index
    self.banks[index].analog_lower_limit = value
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_analog_lower_limit(
    self,
    index: BANK_INDEX | None = None
  ) -> float:
    """
    Read the analog output upper limit value.
    """
    if index is None:
      index = self.active_bank_index
    return self.banks[index].analog_lower_limit
  # ----------------------------------------------------------------------------

  def change_bank(self, index: BANK_INDEX) -> None:
    """
    Change the currently active bank
    (influences HIGH, LOW threshold, Zero Shift target)
    """
    self.active_bank_setting = index
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def set_error(self, error_code: int) -> None:
    """
    Influence the internal error state.
    """
    self.internal_error = ILError(error_code)
  # ----------------------------------------------------------------------------

  def clear_error(self) -> None:
    """
    Remove all internal errors.
    """
    self.internal_error = ILError.NO_ERROR
  # ----------------------------------------------------------------------------

  def has_error(self) -> bool:
    """
    Does the Sensor have an interal error state?
    """
    return self.internal_error != ILError.NO_ERROR
  # ----------------------------------------------------------------------------

  def is_out_of_range(self) -> bool:
    """
    Is there a valid measurement available?
    """
    return (
      not self.laser_active
      or not isinstance(self.judgment_value, (int, float))
      or self.judgment_value > self.upper_bound
      or self.judgment_value < self.lower_bound
    )
  # ----------------------------------------------------------------------------

  def randomize_value(self) -> None:
    """
    Do a randomized "measurement".
    """
    self.raw_value = uniform(
      self.randomized_upper_limit,
      self.randomized_lower_limit
    )
  # ----------------------------------------------------------------------------

  def apply_uncertainty(self) -> None:
    """
    Simulate measurement uncertainty.
    """
    if isinstance(self.raw_value, (int, float)):
      if self.randomized:
        self.randomize_value()
      self.raw_value = (
        self.raw_value + uniform(-1 * self.uncertainty, self.uncertainty)
      )
  # ----------------------------------------------------------------------------

  def judgment_value_for_communication_unit(self) -> int:
    """
    Return adjusted value converted to integer,
    invalid values will be represented by the constants:

    If an error occurs on a sensor, the value "+100000000" is output.
    When a sensor over range has occurred (the sensor amplifier displays
    FFFF), "+099999999" is output.
    When a sensor under range has occurred (the sensor amplifier displays
    -FFFF), "-099999999" is output.
    When a sensor's value is invalid (the sensor amplifier displays ----),
    "-099999998" is output.
    """
    CONSTANT_ERROR: Final = +100000000
    CONSTANT_INVALID: Final = -99999998
    CONSTANT_OVERRANGE: Final = +99999999
    CONSTANT_UNDERRANGE: Final = +99999999
    value: int
    if self.internal_error != ILError.NO_ERROR:
      value = CONSTANT_ERROR
    elif self.value_invalid:
      value = CONSTANT_INVALID
    elif self.value_over_range:
      value = CONSTANT_OVERRANGE
    elif self.value_under_range:
      value = CONSTANT_UNDERRANGE
    else:
      assert isinstance(self.judgment_value, (int, float))
      value = self.mm_to_int(self.judgment_value)
    return value
  # ----------------------------------------------------------------------------

  def get_calculated_value(self) -> float | None:
    """
    Calculate Value based on connected amplifier
    """
    calc_mode = self.calculation_mode
    sub_unit = self.connected_amplifier
    if calc_mode == CalculationMode.OFF or sub_unit is None:
      return self.measurement_value
    if self.measurement_value is None or sub_unit.measurement_value is None:
      return None

    tilt: float = 1.0
    offset: float = 0.0
    if self.calibration_use_user_settings:
      tilt = self.calculation_tilt
      offset = self.calculation_offset

    if calc_mode == CalculationMode.ADDITION:
      return (
        tilt * (self.measurement_value + sub_unit.measurement_value) + offset
      )
    if calc_mode == CalculationMode.SUBTRACTION:
      return (
        tilt * (self.measurement_value - sub_unit.measurement_value) + offset
      )
    # Should never be here
    raise ValueError(f"Invalid calculation mode {calc_mode}")
  # ----------------------------------------------------------------------------

  @property
  def active_bank_index(self) -> BANK_INDEX:
    """
    Returns the current active bank index, switching method included.
    """
    if self.switch_banks_via_external_input:
      ext_1_setting = self.external_input_1_setting
      ext_2_setting = self.external_input_2_setting
      ext_3_setting = self.external_input_3_setting
      ext_4_setting = self.external_input_4_setting
      EXT_1_BANK_A = ExternalInput1Setting.BANK_A
      EXT_2_BANK_A = ExternalInput2Setting.BANK_A
      EXT_3_BANK_A = ExternalInput3Setting.BANK_A
      EXT_4_BANK_A = ExternalInput4Setting.BANK_A
      EXT_1_BANK_B = ExternalInput1Setting.BANK_B
      EXT_2_BANK_B = ExternalInput2Setting.BANK_B
      EXT_3_BANK_B = ExternalInput3Setting.BANK_B
      EXT_4_BANK_B = ExternalInput4Setting.BANK_B

      bank_a: bool = (
        self.external_input_use_user_settings and (
          (ext_1_setting == EXT_1_BANK_A and self.external_input_1)
          or (ext_2_setting == EXT_2_BANK_A and self.external_input_2)
          or (ext_3_setting == EXT_3_BANK_A and self.external_input_3)
          or (ext_4_setting == EXT_4_BANK_A and self.external_input_4)
        )
      )
      bank_b: bool = (
        self.external_input_use_user_settings and (
          (ext_1_setting == EXT_1_BANK_B and self.external_input_1)
          or (ext_2_setting == EXT_2_BANK_B and self.external_input_2)
          or (ext_3_setting == EXT_3_BANK_B and self.external_input_3)
          or (ext_4_setting == EXT_4_BANK_B and self.external_input_4)
        )
      )
      bank_index: int = (2 * bank_b) + (1 * bank_a)
      # For the dumb type hinters, we need to manually narrow the type
      assert bank_index in (0, 1, 2, 3)
    return self.active_bank_setting
  # ----------------------------------------------------------------------------

  @property
  def active_bank(self) -> Bank:
    """
    Get the currently active bank, switching method included.
    """
    return self.banks[self.active_bank_index]
  # ----------------------------------------------------------------------------

  @property
  def threshold_high(self) -> float:
    """
    Get the active bank's HIGH threshold.
    """
    return self.active_bank.threshold_high
  # ----------------------------------------------------------------------------

  @property
  def threshold_low(self) -> float:
    """
    Get the active bank's LOW threshold.
    """
    return self.active_bank.threshold_low
  # ----------------------------------------------------------------------------

  @property
  def analog_upper_limit(self) -> float:
    """
    Get the active bank's analog upper limit.
    """
    if self.analog_output_scaling_mode == AnalogOutputScalingMode.BANK:
      return self.active_bank.analog_upper_limit
    elif self.analog_output_scaling_mode == AnalogOutputScalingMode.FREE_RANGE:
      return self.free_analog_upper_limit
    return self.default_analog_upper_limit
  # ----------------------------------------------------------------------------

  @property
  def analog_lower_limit(self) -> float:
    """
    Get the active bank's analog lower limit.
    """
    if self.analog_output_scaling_mode == AnalogOutputScalingMode.BANK:
      return self.active_bank.analog_lower_limit
    elif self.analog_output_scaling_mode == AnalogOutputScalingMode.FREE_RANGE:
      return self.free_analog_lower_limit
    return self.default_analog_lower_limit
  # ----------------------------------------------------------------------------

  @property
  def shift_target(self) -> float:
    """
    Get the active bank's zero shift target.
    """
    return self.active_bank.shift_target
  # ----------------------------------------------------------------------------

  @property
  def raw_value(self) -> float | None:
    """
    Get the raw value used by simulator.
    """
    return self._raw_value
  # ----------------------------------------------------------------------------

  @raw_value.setter
  def raw_value(self, value: float | None) -> None:
    """
    Set the raw value used by simulator.
    """
    self._raw_value = value
    # Updated raw value --> trigger upate of measurement value
    self.update_R_V_value()
  # ----------------------------------------------------------------------------

  def update_R_V_value(self) -> None:
    """
    Updated raw value --> trigger upate of measurement value
    """
    if self._raw_value is None:
      self.measurement_value = None
    else:
      direction: float = -1 if self.reversed_measurement_direction else 1
      tilt: float = 1.0
      offset: float = 0.0
      if self.calibration_use_user_settings:
        tilt = self.calibration_tilt
        offset = self.calibration_offset
      # The way shift target and calibration interact is not 100% clear.
      self.measurement_value = (
        tilt * (direction * self._raw_value - self.shift_target) + offset
      )
  # ----------------------------------------------------------------------------

  @property
  def measurement_value(self) -> float | None:
    """
    Get the R.V. internal measurment value (raw + zero shift).
    """
    return self._r_v_value
  # ----------------------------------------------------------------------------

  @measurement_value.setter
  def measurement_value(self, value: float | None) -> None:
    """
    Set the R.V. internal measurment value (raw + zero shift).
    """
    self._r_v_value = value
    # Updated measurement value --> trigger upate of calculation value
    self.update_CALC_value()
  # ----------------------------------------------------------------------------

  def update_CALC_value(self, *, _from_sub_unit: bool = False) -> None:
    """
    Updated measurement value --> trigger upate of calculation value
    """
    if self._r_v_value is None:
      self.calculation_value = None
    else:
      if self.is_main_unit:
        self.calculation_value = self.get_calculated_value()
      else:
        self.calculation_value = self._r_v_value
        if self.connected_amplifier is not None and not _from_sub_unit:
          self.connected_amplifier.update_CALC_value(_from_sub_unit=True)
  # ----------------------------------------------------------------------------

  @property
  def calculation_value(self) -> float | None:
    """
    Get the CALC value: calc(rv1, rv2).
    """
    return self._calc_value
  # ----------------------------------------------------------------------------

  @calculation_value.setter
  def calculation_value(self, value: float | None) -> None:
    """
    Set the CALC value: calc(rv1, rv2).
    """
    self._calc_value = value
    # Updated calculation value --> trigger upate of judgment value
    self.update_P_V_value()
  # ----------------------------------------------------------------------------

  def _sample_hold(self) -> None:
    """
    Sample Hold implementation for update_P_V_value()
    """
    if not (self.timing_input_on_edge or self.timing_input):
      self.judgment_value = self.calculation_value
  # ----------------------------------------------------------------------------

  def _peak_hold(self) -> None:
    """
    Peak Hold implementation for update_P_V_value()
    """
    if self.currently_sampling and not self._error_during_sampling:
      if self.calculation_value is None:
        # If the R.V. value (or CALC value) causes an alarm even once during
        # the sampling period, the hold results will be "-----".
        self._hold_value = None
        self._hold_peak = None
        self._hold_bottom = None
        # Stop further sampling during this sampling period
        self._error_during_sampling = True
      else:
        self._hold_peak = (
          self.calculation_value if self._hold_peak is None
          else max(self._hold_peak, self.calculation_value)
        )
        self._hold_bottom = (
          self.calculation_value if self._hold_bottom is None
          else min(self._hold_bottom, self.calculation_value)
        )
        self._hold_value = self._hold_peak
  # ----------------------------------------------------------------------------

  def _bottom_hold(self) -> None:
    """
    Bottom Hold implementation for update_P_V_value()
    """
    if self.currently_sampling and not self._error_during_sampling:
      if self.calculation_value is None:
        # If the R.V. value (or CALC value) causes an alarm even once during
        # the sampling period, the hold results will be "-----".
        self._hold_value = None
        self._hold_peak = None
        self._hold_bottom = None
        # Stop further sampling during this sampling period
        self._error_during_sampling = True
      else:
        self._hold_peak = (
          self.calculation_value if self._hold_peak is None
          else max(self._hold_peak, self.calculation_value)
        )
        self._hold_bottom = (
          self.calculation_value if self._hold_bottom is None
          else min(self._hold_bottom, self.calculation_value)
        )
        self._hold_value = self._hold_bottom
  # ----------------------------------------------------------------------------

  def _peak_to_peak_hold(self) -> None:
    """
    Peak to Peak Hold implementation for update_P_V_value()
    """
    if self.currently_sampling and not self._error_during_sampling:
      if self.calculation_value is None:
        # If the R.V. value (or CALC value) causes an alarm even once during
        # the sampling period, the hold results will be "-----".
        self._hold_value = None
        self._hold_peak = None
        self._hold_bottom = None
        # Stop further sampling during this sampling period
        self._error_during_sampling = True
      else:
        self._hold_peak = (
          self.calculation_value if self._hold_peak is None
          else max(self._hold_peak, self.calculation_value)
        )
        self._hold_bottom = (
          self.calculation_value if self._hold_bottom is None
          else min(self._hold_bottom, self.calculation_value)
        )
        self._hold_value = self._hold_peak - self._hold_bottom
  # ----------------------------------------------------------------------------

  def _auto_peak_hold(self) -> None:
    """
    Auto Peak Hold implementation for update_P_V_value()
    """
    start_level: float = self.auto_trigger_level
    end_level: float = self.auto_trigger_level - self.hysteresis
    if self.calculation_value is None or self.calculation_value < end_level:
      # ## Stop sampling  ##
      # After the sampling starts, if the internal measurement value (R.V.)
      # becomes "-----" before the sampling falls below the specified trigger
      # level, the sampling is automatically finished and the maximized value
      # during the sampling period is held as a judgment value (P.V.).
      self.currently_sampling = False
      self.judgment_value = self._hold_value
    elif (
      self.calculation_value > start_level
      and (self.currently_sampling or not self.timing_input)
    ):
      if not self.currently_sampling:
        # Start sampling
        self._hold_value = None
        self._hold_peak = None
        self._hold_bottom = None
        self.currently_sampling = True
      self._hold_peak = (
        self.calculation_value if self._hold_peak is None
        else max(self._hold_peak, self.calculation_value)
      )
      self._hold_bottom = (
        self.calculation_value if self._hold_bottom is None
        else min(self._hold_bottom, self.calculation_value)
      )
      self._hold_value = self._hold_peak
  # ----------------------------------------------------------------------------

  def _auto_bottom_hold(self) -> None:
    """
    Auto Bottom Hold implementation for update_P_V_value()
    """
    start_level: float = self.auto_trigger_level
    end_level: float = self.auto_trigger_level + self.hysteresis
    if self.calculation_value is None or self.calculation_value > end_level:
      # ## Stop sampling  ##
      # After the sampling starts, if the internal measurement value (R.V.)
      # becomes "-----" before the sampling goes beyond the specified trigger
      # level, the sampling is automatically finished and the minimized value
      # during the sampling period is held as a judgment value (P.V.).
      self.currently_sampling = False
      self.judgment_value = self._hold_value
    elif (
      self.calculation_value < start_level
      and (self.currently_sampling or not self.timing_input)
    ):
      if not self.currently_sampling:
        # Start sampling
        self._hold_value = None
        self._hold_peak = None
        self._hold_bottom = None
        self.currently_sampling = True
      self._hold_peak = (
        self.calculation_value if self._hold_peak is None
        else max(self._hold_peak, self.calculation_value)
      )
      self._hold_bottom = (
        self.calculation_value if self._hold_bottom is None
        else min(self._hold_bottom, self.calculation_value)
      )
      self._hold_value = self._hold_bottom
  # ----------------------------------------------------------------------------

  def update_P_V_value(self) -> None:
    """
    Updated calculation value --> trigger upate of judgment value
    """
    hold_mapping = {
      HoldFunctionSetting.SAMPLE_HOLD: self._sample_hold,
      HoldFunctionSetting.PEAK_HOLD: self._peak_hold,
      HoldFunctionSetting.BOTTOM_HOLD: self._bottom_hold,
      HoldFunctionSetting.PEAK_TO_PEAK_HOLD: self._peak_to_peak_hold,
      HoldFunctionSetting.AUTO_PEAK_HOLD: self._auto_peak_hold,
      HoldFunctionSetting.AUTO_BOTTOM_HOLD: self._auto_bottom_hold,
    }
    holding_method = hold_mapping.get(self.hold_function_setting)
    if holding_method is None:
      raise ValueError(f"Invalid Holding Mode: {self.hold_function_setting}")
    holding_method()
  # ----------------------------------------------------------------------------

  @property
  def judgment_value(self) -> float | None:
    """
    Get the P.V. judgment value (CALC + holding).
    """
    return self._p_v_value
  # ----------------------------------------------------------------------------

  @judgment_value.setter
  def judgment_value(self, value: float | None) -> None:
    """
    Set the P.V. judgment value (CALC + holding).
    """
    self._p_v_value = value
  # ----------------------------------------------------------------------------

  @property
  def timing_input(self) -> bool:
    """
    Get the actual state of timing input (internal variable OR input signal)
    """
    return self._timing_input
  # ----------------------------------------------------------------------------

  @timing_input.setter
  def timing_input(self, value: bool) -> None:
    """
    Set the actual state of timing input (internal variable OR input signal)
    """
    edge: bool = (value != self._timing_input)
    positive_edge: bool = edge and value
    negative_edge: bool = edge and not value
    self._timing_input = value

    hold_mode = self.hold_function_setting

    if hold_mode == HoldFunctionSetting.SAMPLE_HOLD:
      if self.timing_input_on_edge and positive_edge:
        self.judgment_value = self.calculation_value
    elif hold_mode in (
      HoldFunctionSetting.PEAK_HOLD,
      HoldFunctionSetting.BOTTOM_HOLD,
      HoldFunctionSetting.PEAK_TO_PEAK_HOLD,
    ):
      if positive_edge:
        # stop sampling
        self.currently_sampling = False
        self._error_during_sampling = False
        self.judgment_value = self._hold_value
      if edge and (self.timing_input_on_edge or negative_edge):
        # Restart sampling
        self._hold_value = None
        self._hold_peak = None
        self._hold_bottom = None
        self.currently_sampling = True
  # ----------------------------------------------------------------------------

  def update_timing_input_status(self) -> None:
    """
    Update the state of timing input.

    Call periodically to update `timing_input`
    """
    self.timing_input = (
      (
        self.external_input_3_setting == ExternalInput3Setting.TIMING
        or not self.external_input_use_user_settings
      )
      and self.external_input_3
      or self.stored_timing_input
    )
  # ----------------------------------------------------------------------------

  @property
  def error_code(self) -> int:
    """
    Return first error code.
    """
    bitmask: int = int(self.internal_error)
    return int(-bitmask & bitmask).bit_length()
  # ----------------------------------------------------------------------------

  @property
  def laser_active(self) -> bool:
    """
    Is the Laser currently emiting radiation?
    """
    ext_1_setting = self.external_input_1_setting
    ext_2_setting = self.external_input_2_setting
    ext_3_setting = self.external_input_3_setting
    ext_4_setting = self.external_input_4_setting
    EXT_1_STOP = ExternalInput1Setting.LASER_EMISSION_STOP
    EXT_2_STOP = ExternalInput2Setting.LASER_EMISSION_STOP
    EXT_3_STOP = ExternalInput3Setting.LASER_EMISSION_STOP
    EXT_4_STOP = ExternalInput4Setting.LASER_EMISSION_STOP
    if (
      self.external_input_use_user_settings and (
        (ext_1_setting == EXT_1_STOP and self.external_input_1)
        or (ext_2_setting == EXT_2_STOP and self.external_input_2)
        or (ext_3_setting == EXT_3_STOP and self.external_input_3)
        or (ext_4_setting == EXT_4_STOP and self.external_input_4)
      )
      or self.stored_laser_emission_stop
      or self.internal_error == ILError.Sensor_Head
    ):
      return False
    return True
  # ----------------------------------------------------------------------------

  @property
  def reference_distance_led(self) -> LEDColor:
    """
    Output of the reference distance LED.
    """
    if self.head_display_mode == HeadDisplayMode.DEFAULT:
      if (
        isinstance(self.raw_value, (int, float))
        and self.raw_value > (
          self.reference_distance - self.reference_distance_tolerance
        )
        and self.raw_value < (
          self.reference_distance + self.reference_distance_tolerance
        )
      ):
        return LEDColor.GREEN

    elif self.head_display_mode == HeadDisplayMode.OK_NG:
      go_color: LEDColor = (
        LEDColor.GREEN
        if self.display_color == DisplayColor.GO_GREEN
        else LEDColor.RED
      )
      nogo_color: LEDColor = (
        LEDColor.GREEN
        if self.display_color == DisplayColor.GO_RED
        else LEDColor.RED
      )

      if self.go_output:
        return go_color
      if (
        self.high_output
        or self.low_output
        or not isinstance(self.raw_value, (int, float))
      ):
        return nogo_color

    return LEDColor.OFF
  # ----------------------------------------------------------------------------

  @property
  def analog_range_led(self) -> LEDColor:
    """
    Lights when in the range of the analog output.
    """
    if self.head_display_mode == HeadDisplayMode.DEFAULT:
      if (
        isinstance(self.raw_value, (int, float))
        and self.raw_value > (
          self.reference_distance - self.reference_distance_analog_tolerance
        )
        and self.raw_value < (
          self.reference_distance + self.reference_distance_analog_tolerance
        )
      ):
        return LEDColor.ORANGE
    return LEDColor.OFF
  # ----------------------------------------------------------------------------

  @property
  def laser_radiation_emission_led(self) -> LEDColor:
    """
    Lights when in the range of the analog output.
    """
    if self.laser_active:
      return LEDColor.GREEN
    return LEDColor.BLINKING
  # ----------------------------------------------------------------------------

  @property
  def alarm_led(self) -> bool:
    """
    Lights up in the alarm state or error state.
    """
    return self.internal_error != ILError.NO_ERROR
  # ----------------------------------------------------------------------------

  @property
  def sampling_rate(self) -> float:
    """
    Returns sampling rate in milliseconds.
    """
    value_mapping = {
      SamplingCycle.DEFAULT: self.default_sampling_cycle,
      SamplingCycle.ONE_THIRD_MS: 0.33,
      SamplingCycle.ONE_MS: 1.0,
      SamplingCycle.TWO_MS: 2.0,
      SamplingCycle.FIVE_MS: 5.0,
    }
    value = value_mapping.get(self.sampling_cycle)
    if value is None:
      raise ValueError(f"No valid sampling cycle: {self.sampling_cycle}")
    return value
  # ----------------------------------------------------------------------------

  @property
  def display_digts(self) -> int:
    """
    Returns the amount of digits after the decimal points display on screen.
    """
    value_mapping = {
      DisplayDigit.DEFAULT: self.default_display_digit,
      DisplayDigit.THREE_DIGITS: 3,
      DisplayDigit.TWO_DIGITS: 2,
      DisplayDigit.ONE_DIGIT: 1,
      DisplayDigit.ZERO_DIGITS: 0,
    }
    value = value_mapping.get(self.display_digit_setting)
    if value is None:
      raise ValueError(
        f"Invalid display digits setting: {self.display_digit_setting}"
      )
    return value
  # ----------------------------------------------------------------------------

  @property
  def OUTPUT_FALSE(self) -> bool:
    """
    Returns True when output is set to normally closed,
    False when output is set to normally open.

    Default is Normally Open --> False
    """
    return self.output_mode_normally_closed
  # ----------------------------------------------------------------------------

  @property
  def OUTPUT_TRUE(self) -> bool:
    """
    Returns False when output is set to normally closed,
    True when output is set to normally open.

    Default is Normally Open --> True
    """
    return not self.output_mode_normally_closed
  # ----------------------------------------------------------------------------

  @property
  def alarm_state(self) -> bool:
    """
    Get theoretical state of ALARM output.
    No Alarm: True
    Alarm: False
    """
    if (
      self.internal_error != ILError.NO_ERROR
      or not isinstance(self.raw_value, (int, float))
    ):
      return True
    return False
  # ----------------------------------------------------------------------------

  @property
  def high_state(self) -> bool:
    """
    Get theoretical state of HIGH output.
    """
    if ILError.Overcurrent & self.internal_error:
      return False
    if (
      self.internal_error != ILError.NO_ERROR
      and self.internal_error != ILError.EEPROM
    ):
      return True
    if (
      not self.laser_active
      or not isinstance(self.raw_value, (int, float))
      or not isinstance(self.judgment_value, (int, float))
    ):
      return False
    if (
      self.raw_value > self.upper_bound  # FFFF
      or self.judgment_value > self.threshold_high
    ):
      return True
    return False
  # ----------------------------------------------------------------------------

  @property
  def low_state(self) -> bool:
    """
    Get theoretical state of LOW output.
    """
    if ILError.Overcurrent & self.internal_error:
      return False
    if (
      self.internal_error != ILError.NO_ERROR
      and self.internal_error != ILError.EEPROM
    ):
      return True
    if (
      not self.laser_active
      or not isinstance(self.raw_value, (int, float))
      or not isinstance(self.judgment_value, (int, float))
    ):
      return False
    if (
      self.raw_value < self.lower_bound  # -FFFF
      or self.judgment_value < self.threshold_low
    ):
      return True
    return False
  # ----------------------------------------------------------------------------

  @property
  def go_state(self) -> bool:
    """
    Get theoretical state of GO output.
    """
    if ILError.Overcurrent & self.internal_error:
      return False
    if (
      self.internal_error != ILError.NO_ERROR
      and self.internal_error != ILError.EEPROM
    ):
      return False
    if (
      not self.laser_active
      or not isinstance(self.raw_value, (int, float))
      or not isinstance(self.judgment_value, (int, float))
    ):
      return False
    if (
      self.raw_value > self.upper_bound  # FFFF
      or self.judgment_value > self.threshold_high
      or self.raw_value < self.lower_bound  # -FFFF
      or self.judgment_value < self.threshold_low
    ):
      return False
    return True
  # ----------------------------------------------------------------------------

  @property
  def alarm_output(self) -> bool:
    """
    Get physical state of ALARM output (Normally Closed).
    No Alarm: True
    Alarm: False
    """
    return not self.alarm_state
  # ----------------------------------------------------------------------------

  @property
  def high_output(self) -> bool:
    """
    Get physical state of HIGH output.
    """
    return self.OUTPUT_TRUE if self.high_state else self.OUTPUT_FALSE
  # ----------------------------------------------------------------------------

  @property
  def low_output(self) -> bool:
    """
    Get physical state of LOW output.
    """
    return self.OUTPUT_TRUE if self.low_state else self.OUTPUT_FALSE
  # ----------------------------------------------------------------------------

  @property
  def go_output(self) -> bool:
    """
    Get physical state of GO output.
    """
    return self.OUTPUT_TRUE if self.go_state else self.OUTPUT_FALSE
  # ----------------------------------------------------------------------------

  @property
  def value_invalid(self) -> bool:
    """
    Does the adjusted value display '----'?
    """
    return (
      not self.laser_active
      or not isinstance(self.judgment_value, (int, float))
    )
  # ----------------------------------------------------------------------------

  @property
  def value_under_range(self) -> bool:
    """
    Does the adjusted value display '-FFFF'?
    """
    if not isinstance(self.judgment_value, (int, float)):
      return False
    return (
      self.judgment_value < self.lower_bound
    )
  # ----------------------------------------------------------------------------

  @property
  def value_over_range(self) -> bool:
    """
    Does the adjusted value display '+FFFF'?
    """
    if not isinstance(self.judgment_value, (int, float)):
      return False
    return (
      self.judgment_value > self.upper_bound
    )
  # ----------------------------------------------------------------------------

  @property
  def output_state(self) -> OutputState:
    """
    Get state for MS command.
    """
    if self.internal_error != ILError.NO_ERROR:
      return OutputState.Error
    if self.high_state:
      return OutputState.HIGH
    if self.low_state:
      return OutputState.LOW
    if self.go_state:
      return OutputState.GO
    return OutputState.All_OFF
  # ----------------------------------------------------------------------------

  @property
  def stringified_state(self) -> str:
    """
    Get formatted state for MS command.
    """
    return f"{self.output_state.value:0>2}"
  # ----------------------------------------------------------------------------

  @property
  def stringified_value(self) -> str:
    """
    Get formatted measurement value for M0/MS command.
    """
    value: int = self.judgment_value_for_communication_unit()
    return f"{value:+010d}"
  # ----------------------------------------------------------------------------

  @property
  def max_analog_value(self) -> float:
    """
    Returns the maximum analog value (in Volts/Amps)
    """
    value_mapping = {
      AnalogOutputMode.OFF: 0,
      AnalogOutputMode.CURRENT_4_TO_20: 20,
      AnalogOutputMode.VOLTAGE_0_TO_5: 5,
      AnalogOutputMode.VOLTAGE_1_TO_5: 5,
      AnalogOutputMode.VOLTAGE_MINUS_5_TO_5: 5,
    }
    value = value_mapping.get(self.analog_output_mode)
    if value is None:
      raise ValueError(
        f"Invalid analog_output_mode: {self.analog_output_mode}"
      )
    return value
  # ----------------------------------------------------------------------------

  @property
  def min_analog_value(self) -> float:
    """
    Returns the minimum analog value (in Volts/Amps)
    """
    value_mapping = {
      AnalogOutputMode.OFF: 0,
      AnalogOutputMode.CURRENT_4_TO_20: 4,
      AnalogOutputMode.VOLTAGE_0_TO_5: 0,
      AnalogOutputMode.VOLTAGE_1_TO_5: 1,
      AnalogOutputMode.VOLTAGE_MINUS_5_TO_5: -5,
    }
    value = value_mapping.get(self.analog_output_mode)
    if value is None:
      raise ValueError(
        f"Invalid analog_output_mode: {self.analog_output_mode}"
      )
    return value
  # ----------------------------------------------------------------------------

  @property
  def analog_value(self) -> float:
    """
    Transform the measurement value (Distance)
    into the value at the analog output (Voltage/Current)
    """
    if self.analog_output_mode == AnalogOutputMode.OFF:
      return 0
    if (
      self.internal_error != ILError.NO_ERROR
      or self.value_invalid
    ):
      if self.analog_output_mode == AnalogOutputMode.CURRENT_4_TO_20:
        # Current
        return 3.0
      else:
        # Voltage
        return 5.5

    assert isinstance(self.judgment_value, (int, float))
    if self.judgment_value > self.analog_upper_limit:
      return self.max_analog_value
    if self.judgment_value <= self.analog_lower_limit:
      return self.min_analog_value

    return scale_values(
      self.judgment_value,
      self.analog_lower_limit,
      self.min_analog_value,
      self.analog_upper_limit,
      self.max_analog_value
    )
  # ----------------------------------------------------------------------------

  def handle_read(self, query_data: int) -> int | str:
    """
    Dispatch read calls for SR commands.
    """
    if query_data > 223:
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
    if query_data > 223:
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

  def write_001_zero_shift_execution_request(self, setting_data: int) -> None:
    """
    Executes zero shift. Turning off the power to the sensor
    amplifier after executing zero shift restores the state that
    existed before the zero shift function was used. To retain
    the shifted state after turning off the power, turn on the
    zero shift value memory function.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.zero_shifting_result = OperationResult.OPERATING
    value = self.raw_value
    if value is None:
      self.zero_shifting_result = OperationResult.ABNORMAL_TERMINATION
    else:
      self.change_shift_target(value)
      self.zero_shifting_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_002_zero_shift_reset_request(self, setting_data: int) -> None:
    """
    Resets the zero shift value.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.zero_shifting_result = OperationResult.OPERATING
    self.change_shift_target(0)
    self.zero_shifting_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_003_reset_request(self, setting_data: int) -> None:
    """
    Executes resetting.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.reset_request_result = OperationResult.OPERATING
    self.reset()
    self.reset_request_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_005_initial_reset_request(self, setting_data: int) -> None:
    """
    Initializes all settings, except for sensor amplifier
    calibration and system parameters. Once an initial reset
    request is executed, all parameters are stored into the
    nonvolatile memory (EEPROM) in approximately three
    seconds. When completed, the setting/status command
    parameter "EEPROM write result" flips to "successfully
    completed (1)". After the completion, "EEPROM write
    result" of data number 053 changes to Normal termination
    (1).
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.restore_default_settings()
  # ----------------------------------------------------------------------------

  def write_006_system_parameters_set_request(self, setting_data: int) -> None:
    """
    Changes the system parameters (the polarity of the
    judgment and alarm outputs and the analog output
    setting) to the values written in "System parameter
    settings" of data number 105.

    To set the system parameters, confirm that the change is
    proper according to the connected devices and wiring.
    A wrong change may damage the sensor amplifier or the
    connected equipment.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.set_system_parameters()
  # ----------------------------------------------------------------------------

  def write_014_tolerance_tuning_request(self, setting_data: int) -> None:
    """
    Executes tolerance tuning.

    Use "Tolerance tuning - tolerance setting range" of data
    number 106 to set the tolerance setting range.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING

    if not isinstance(self.judgment_value, (int, float)):
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    new_upper_limit = self.judgment_value + self.tolerance_setting_range
    new_lower_limit = self.judgment_value - self.tolerance_setting_range
    self.change_high_threshold(new_upper_limit)
    self.change_low_threshold(new_lower_limit)
    self.tuning_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_015_2point_high_1st_point_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes two-point tuning. For the operating procedure,
    refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING

    if not isinstance(self.measurement_value, (int, float)):
      self._two_point_high_side_1st_point = None
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    self._two_point_high_side_1st_point = self.measurement_value
  # ----------------------------------------------------------------------------

  def write_016_2point_high_2nd_point_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes two-point tuning. For the operating procedure,
    refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING

    if (
      not isinstance(self.measurement_value, (int, float))
      or not isinstance(self._two_point_high_side_1st_point, (int, float))
    ):
      self._two_point_high_side_1st_point = None
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    two_point_high_side_2nd_point = self.measurement_value
    new_high = (
      self._two_point_high_side_1st_point + two_point_high_side_2nd_point
    ) / 2
    self.change_high_threshold(new_high)
    self.tuning_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_017_2point_low_1st_point_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes two-point tuning. For the operating procedure,
    refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING

    if not isinstance(self.measurement_value, (int, float)):
      self._two_point_low_side_1st_point = None
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    self._two_point_low_side_1st_point = self.measurement_value
  # ----------------------------------------------------------------------------

  def write_018_2point_low_2nd_point_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes two-point tuning. For the operating procedure,
    refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING

    if (
      not isinstance(self.measurement_value, (int, float))
      or not isinstance(self._two_point_low_side_1st_point, (int, float))
    ):
      self._two_point_low_side_1st_point = None
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    two_point_low_side_2nd_point = self.measurement_value
    new_low = (
      self._two_point_low_side_1st_point + two_point_low_side_2nd_point
    ) / 2
    self.change_low_threshold(new_low)
    self.tuning_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_019_calibration_set_1_request(self, setting_data: int) -> None:
    """
    Executes calibration.

    Set the R.V. value to be displayed using "Calibration
    function SET1" and "Calibration function SET2" of data
    number 108 and 109.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not isinstance(self.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    self._calibration_set_1_before = self.measurement_value
  # ----------------------------------------------------------------------------

  def write_020_calibration_set_2_request(self, setting_data: int) -> None:
    """
    Executes calibration.

    Set the R.V. value to be displayed using "Calibration
    function SET1" and "Calibration function SET2" of data
    number 108 and 109.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not isinstance(self.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calibration_set_1_before = None
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(self._calibration_set_1_before, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calibration_set_1_before = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    _calibration_set_1_before: float = self._calibration_set_1_before
    _calibration_set_2_before: float = self.measurement_value

    calibration_factor: float = (
      (self.calibration_set_2 - self.calibration_set_1)
      / (_calibration_set_2_before - _calibration_set_1_before)
    )

    if not (0.5 <= calibration_factor <= 2.0):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calibration_set_1_before = None
      raise NonExecutableStateError  # TODO: Not verified

    self.calibrate_sensor(
      _calibration_set_1_before,
      self.calibration_set_1,
      _calibration_set_2_before,
      self.calibration_set_2
    )
    self._calibration_set_1_before = None
    self.start_eeprom_write()
    self.calibration_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_021_calc_2point_calibration_set_1_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes calculated value two-point calibration (main unit only).

    Set the R.V. value to be displayed using "Calculated value
    two-point calibration function SET1" and "Calculated value
    two-point calibration function SET2" of data number 111
    and 112.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not isinstance(self.calculation_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calc_calibration_mode == CalculationCalibrationMode.TWO_POINT:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    self._calc_2p_calibration_set_1_before_calc = self.calculation_value
  # ----------------------------------------------------------------------------

  def write_022_calc_2point_calibration_set_2_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes calculated value two-point calibration (main unit only).

    Set the R.V. value to be displayed using "Calculated value
    two-point calibration function SET1" and "Calculated value
    two-point calibration function SET2" of data number 111
    and 112.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not isinstance(self.calculation_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_2p_calibration_set_1_before_calc = None
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(
      self._calc_2p_calibration_set_1_before_calc,
      (int, float)
    ):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_2p_calibration_set_1_before_calc = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_2p_calibration_set_1_before_calc = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calc_calibration_mode == CalculationCalibrationMode.TWO_POINT:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_2p_calibration_set_1_before_calc = None
      raise NonExecutableStateError  # TODO: Not verified

    set_1_before_calc: float = (
      self._calc_2p_calibration_set_1_before_calc
    )
    set_2_before_calc: float = self.calculation_value

    calibration_factor: float = (
      (self.calc_2p_calibration_set_2 - self.calc_2p_calibration_set_1)
      / (set_2_before_calc - set_1_before_calc)
    )

    if not (0.5 <= calibration_factor <= 2.0):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_2p_calibration_set_1_before_calc = None
      raise NonExecutableStateError  # TODO: Not verified

    self.calibrate_calc(
      set_1_before_calc,
      self.calc_2p_calibration_set_1,
      set_2_before_calc,
      self.calc_2p_calibration_set_2
    )
    self._calc_2p_calibration_set_1_before_calc = None
    self.start_eeprom_write()
    self.calibration_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_023_calc_3point_calibration_set_1_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes calculated value three-point calibration (main unit only).

    Set the R.V. value to be displayed using "Calculated value
    three-point calibration function SET1" and "Calculated
    value three-point calibration function SET3" of data
    number 113 and 114.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not self.is_main_unit or self.connected_amplifier is None:
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    expansion_unit = self.connected_amplifier
    if not isinstance(self.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(expansion_unit.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(self.calculation_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calc_calibration_mode == CalculationCalibrationMode.THREE_POINT:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError  # TODO: Not verified

    self._calc_3p_calibration_set_1_before_calc = self.calculation_value
    self._calc_3p_calibration_set_1_before_rv_main = self.measurement_value
    self._calc_3p_calibration_set_1_before_rv_expansion = (
      expansion_unit.measurement_value
    )
  # ----------------------------------------------------------------------------

  def write_024_calc_3point_calibration_set_2_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes calculated value three-point calibration (main unit only).

    Set the R.V. value to be displayed using "Calculated value
    three-point calibration function SET1" and "Calculated
    value three-point calibration function SET3" of data
    number 113 and 114.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not self.is_main_unit or self.connected_amplifier is None:
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    expansion_unit = self.connected_amplifier

    if not isinstance(self.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(expansion_unit.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(self.calculation_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calc_calibration_mode == CalculationCalibrationMode.THREE_POINT:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not (
      isinstance(
        self._calc_3p_calibration_set_1_before_calc,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_1_before_rv_main,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_1_before_rv_expansion,
        (int, float)
      )
    ):
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    self._calc_3p_calibration_set_2_before_calc = self.calculation_value
    self._calc_3p_calibration_set_2_before_rv_main = self.measurement_value
    self._calc_3p_calibration_set_2_before_rv_expansion = (
      expansion_unit.measurement_value
    )
  # ----------------------------------------------------------------------------

  def write_025_calc_3point_calibration_set_3_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes calculated value three-point calibration (main unit only).

    Set the R.V. value to be displayed using "Calculated value
    three-point calibration function SET1" and "Calculated
    value three-point calibration function SET3" of data
    number 113 and 114.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.calibration_result = OperationResult.OPERATING

    if not self.is_main_unit or self.connected_amplifier is None:
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    expansion_unit = self.connected_amplifier

    if not isinstance(self.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(expansion_unit.measurement_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not isinstance(self.calculation_value, (int, float)):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calibration_use_user_settings:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not self.calc_calibration_mode == CalculationCalibrationMode.THREE_POINT:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if self.calculation_mode == CalculationMode.OFF:
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    if not (
      isinstance(
        self._calc_3p_calibration_set_1_before_calc,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_1_before_rv_main,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_1_before_rv_expansion,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_2_before_calc,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_2_before_rv_main,
        (int, float)
      )
      and isinstance(
        self._calc_3p_calibration_set_2_before_rv_expansion,
        (int, float)
      )
    ):
      # TODO: Does this fail silently or loudly?
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    set_1_before_calc: float = self._calc_3p_calibration_set_1_before_calc
    set_1_before_rv_main: float = self._calc_3p_calibration_set_1_before_rv_main
    set_1_before_rv_expansion: float = (
      self._calc_3p_calibration_set_1_before_rv_expansion
    )
    # set_2_before_calc: float = self._calc_3p_calibration_set_2_before_calc
    set_2_before_rv_main: float = self._calc_3p_calibration_set_2_before_rv_main
    set_2_before_rv_expansion: float = (
      self._calc_3p_calibration_set_2_before_rv_expansion
    )
    set_3_before_calc: float = self.calculation_value
    # set_3_before_rv_main: float = self.measurement_value
    # set_3_before_rv_expansion: float = expansion_unit.measurement_value

    calibration_factor_1: float = (
      (self.calc_3p_calibration_set_3 - self.calc_3p_calibration_set_1)
      / (set_3_before_calc - set_1_before_calc)
    )
    coeff: float = -1 if self.calculation_mode.ADDITION else 1
    calibration_factor_2: float = (
      coeff * (set_2_before_rv_expansion - set_1_before_rv_expansion)
      / (set_2_before_rv_main - set_1_before_rv_main)
    )

    if not (
      (0.5 <= calibration_factor_1 <= 2.0)
      and (0.5 <= calibration_factor_2 <= 2.0)
    ):
      self.calibration_result = OperationResult.ABNORMAL_TERMINATION
      self._calc_3p_calibration_set_1_before_calc = None
      self._calc_3p_calibration_set_1_before_rv_main = None
      self._calc_3p_calibration_set_1_before_rv_expansion = None
      self._calc_3p_calibration_set_2_before_calc = None
      self._calc_3p_calibration_set_2_before_rv_main = None
      self._calc_3p_calibration_set_2_before_rv_expansion = None
      raise NonExecutableStateError  # TODO: Not verified

    # TODO: Implement calibration
    self.start_eeprom_write()
    self.calibration_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_026_diff_count_filter_1point_tuning_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes one-point tuning for diff. count filter.

    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING
    if not isinstance(self.judgment_value, (int, float)):
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    new_high: float = abs(self.judgment_value * 2)
    new_low: float = abs(self.judgment_value / 2)
    self.change_high_threshold(new_high)
    self.change_low_threshold(new_low)
    self.tuning_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def write_027_diff_count_filter_2point_1st_point_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes two-point tuning for diff. count filter.
    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING
    if not isinstance(self.measurement_value, (int, float)):
      self._two_point_diff_count_1st_point = None
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    self._two_point_diff_count_1st_point = self.measurement_value
  # ----------------------------------------------------------------------------

  def write_028_diff_count_filter_2point_2nd_point_request(
    self,
    setting_data: int
  ) -> None:
    """
    Executes two-point tuning for diff. count filter.
    For the operating procedure, refer to the “IL Series User's Manual”.
    """
    if setting_data != 1:
      raise WriteDataOutsideValidRangeError
    self.tuning_result = OperationResult.OPERATING
    if (
      not isinstance(self.measurement_value, (int, float))
      or not isinstance(self._two_point_diff_count_1st_point, (int, float))
    ):
      self._two_point_diff_count_1st_point = None
      self.tuning_result = OperationResult.ABNORMAL_TERMINATION
      raise NonExecutableStateError

    _two_point_diff_count_2nd_point = self.measurement_value
    expected_step_size = (
      self._two_point_diff_count_1st_point - _two_point_diff_count_2nd_point
    )
    new_high = abs(expected_step_size * 2)
    new_low = abs(expected_step_size / 2)
    self.change_high_threshold(new_high)
    self.change_low_threshold(new_low)
    self.tuning_result = OperationResult.NORMAL_TERMINATION
  # ----------------------------------------------------------------------------

  def read_033_sensor_amplifier_error(self) -> int:
    """
    Indicates the error status of the sensor amplifier.
    When an error occurs, the corresponding bit turns on.

    bit0: Overcurrent error
    bit1: EEPROM error
    bit2: Head error
    bit7: Spot light laser error
    bit8: Incompatible model error
    bit11: Amplifier communication error
    bit12: Number-of-units error
    bit13: Calculation error
    Other than above: Fixed to 0
    """
    return int(self.internal_error)
  # ----------------------------------------------------------------------------

  def read_036_judgment_alarm_output(self) -> int:
    """
    Indicates the output status of the sensor.

    When an output is on, the corresponding bit turns on.

    Bit0:HIGH judgment output
    Bit1:LOW judgment output
    Bit2:GO judgment output
    Bit3:Alarm output
    """
    return (
      2**0 * self.high_output
      + 2**1 * self.low_output
      + 2**2 * self.go_output
      + 2**3 * self.alarm_output
    )
  # ----------------------------------------------------------------------------

  def read_037_judgment_value(self) -> int:
    """
    Indicates the judgment value (P.V. value).

    Parameter range: -99.999 to +99.999
    """
    if (
      not self.laser_active
      or not isinstance(self.judgment_value, (int, float))
    ):
      return -99998
    if self.judgment_value > self.upper_bound:
      return 99999
    if self.judgment_value < self.lower_bound:
      return -99999
    return self.mm_to_int(self.judgment_value)
  # ----------------------------------------------------------------------------

  def read_038_internal_measurement_value(self) -> int:
    """
    Indicates the internal measurement value (R.V. value).

    Parameter range:-99.999 to +99.999
    """
    if (
      not self.laser_active
      or not isinstance(self.measurement_value, (int, float))
    ):
      return -99998
    if self.measurement_value > self.upper_bound:
      return 99999
    if self.measurement_value < self.lower_bound:
      return -99999
    return self.mm_to_int(self.measurement_value)
  # ----------------------------------------------------------------------------

  def read_039_peak_hold_value_during_hold_period(self) -> int:
    """
    • In the mode other than the sample hold mode
    Indicates the peak-hold value during the sampling
    period.
    Parameter range: -99.999 to +99.999

    • In the sample hold mode
    Parameter range: -99.998
    """
    if self.hold_function_setting == HoldFunctionSetting.SAMPLE_HOLD:
      return -99998
    # Documentation is unclear on whether the value is the peak value of the
    # currently active sampling period, or the sampling period preceeding the
    # current hold period!
    # This implementation choses the current active sampling period only.
    return self.mm_to_int(self._hold_peak)
  # ----------------------------------------------------------------------------

  def read_040_bottom_hold_value_during_hold_period(self) -> int:
    """
    • In the mode other than the sample hold mode
    Indicates the bottom-hold value during the sampling
    period.
    Parameter range: -99.999 to +99.999

    • In the sample hold mode
    Parameter range: -99.998
    """
    if self.hold_function_setting == HoldFunctionSetting.SAMPLE_HOLD:
      return -99998
    # Documentation is unclear on whether the value is the bottom value of the
    # currently active sampling period, or the sampling period preceeding the
    # current hold period!
    return self.mm_to_int(self._hold_bottom)
  # ----------------------------------------------------------------------------

  def read_041_calculation_value(self) -> int:
    """
    Indicates calculation value (CALC value).

    Parameter range: -99.999 to +99.999
    """
    if (
      not self.laser_active
      or not isinstance(self.calculation_value, (int, float))
      or not self.is_main_unit
    ):
      return -99998
    if self.calculation_value > self.upper_bound:
      return 99999
    if self.calculation_value < self.lower_bound:
      return -99999
    return self.mm_to_int(self.calculation_value)
  # ----------------------------------------------------------------------------

  def read_042_analog_output_value(self) -> int:
    """
    Indicates the current analog output value. (main unit only)

    Parameter range:
    Voltage: -5.000 to +5.000 (+5.500 for error)
    4 to 20 mA: +4.00 to +20.00 (+3.00 for error)
    OFF: Fixed to 0
    """
    if not self.is_main_unit or self.analog_output_mode == AnalogOutputMode.OFF:
      return 0
    # The documentation is not super clear on this, but it looks like
    # Current only has 2 digit precision, while Voltage has 3 digit precision
    if self.analog_output_mode == AnalogOutputMode.CURRENT_4_TO_20:
      return int(self.analog_value * 100)
    else:
      return int(self.analog_value * 1000)
  # ----------------------------------------------------------------------------

  def read_043_bank_status(self) -> int:
    """
    Indicates the currently active bank No.

    Use this value to check the number of the bank where the
    sensor amplifier is actually operating.

    Parameter range: 0 to 3
    0: Bank 0
    1: Bank 1
    2: Bank 2
    3: Bank 3
    """
    return self.active_bank_index
  # ----------------------------------------------------------------------------

  def read_044_timing_status(self) -> int:
    """
    Indicates the currently active timing status.

    Use this value to check the timing status where the sensor
    amplifier is actually operating.

    Parameter range: 0 to 1
    0: During Sampling
    1: Not during sampling
    """
    return 1 * self.timing_input
  # ----------------------------------------------------------------------------

  def read_050_laser_emission_stop_status(self) -> int:
    """
    Indicates the currently active laser emission stop status.

    Use this value to check the laser emission stop status
    where the sensor amplifier is actually operating.

    Parameter range: 0 to 1
    0:Laser emitting
    1:Laser stopped (Emission stop input ON/Laser error/
    Sensor head error)
    """
    return 1 * (not self.laser_active)
  # ----------------------------------------------------------------------------

  def read_051_abnormal_setting(self) -> int:
    """
    Indicates an abnormal setting status.
    Parameter range: 0 to 1
    0:Normal setting
    1:Abnormal setting
    """
    # TODO: Implement real detection of abnormal settings
    return 1 * self.abnormal_settings
  # ----------------------------------------------------------------------------

  def read_052_external_input_status(self) -> int:
    """
    Indicates the external input status. When the external
    input line of the sensor amplifier is ON, the corresponding
    bit is set to ON.

    This operation is enabled even when "Not used" is
    selected for the function setting of external inputs 1
    through 4.

    Bit0:External input 1
    Bit1:External input 2
    Bit2:External input 3
    Bit3:External input 4
    """
    output: int = 0
    output += 2**0 * (self.external_input_1)
    output += 2**1 * (self.external_input_2)
    output += 2**2 * (self.external_input_3)
    output += 2**3 * (self.external_input_4)
    return output
  # ----------------------------------------------------------------------------

  def read_053_eeprom_write_result(self) -> int:
    """
    Indicates the result of writing to EEPROM.

    Parameter range: 0 to 2
    0:Writing
    1:Normal termination
    2:Abnormal termination
    """
    return int(self.eeprom_write_result)
  # ----------------------------------------------------------------------------

  def read_054_zero_shift_zero_shift_reset_result(self) -> int:
    """
    Indicates the result of zero shift or zero shift reset.

    Parameter range: 0 to 2
    0:Executing
    1:Normal termination
    2:Abnormal termination
    """
    return int(self.zero_shifting_result)
  # ----------------------------------------------------------------------------

  def read_055_reset_request_result(self) -> int:
    """
    Indicates the result of reset.

    Parameter range: 0 to 2
    0:Executing
    1:Normal termination
    2:Abnormal termination
    """
    return int(self.reset_request_result)
  # ----------------------------------------------------------------------------

  def read_056_current_system_parameters(self) -> int:
    """
    Indicates the current status of the system parameters. Use
    this value to check the system parameters where the
    sensor amplifier is actually operating.
    The corresponding bit turns on according to the current
    status.

    bit 0:
    0:NPN
    1:PNP

    bits 1, 2 and 3 (For main unit only. Fixed to 000 for
    expansion unit):
    000: Analog output OFF
    001: 0 to 5 V
    010: -5 to +5 V
    011: 1 to 5 V
    100: 4 to 20 mA
    """
    output: int = 0
    output += 1 * int(self.transistor_mode)
    if self.is_main_unit:
      output += 2 * int(self.analog_output_mode)
    return output
  # ----------------------------------------------------------------------------

  def read_060_tuning_result(self) -> int:
    """
    Indicates the result of tuning.

    Parameter range: 0 to 2
    0:Executing
    1:Normal termination
    2:Abnormal termination
    """
    return int(self.tuning_result)
  # ----------------------------------------------------------------------------

  def read_061_calibraiton_result(self) -> int:
    """
    Indicates the result of calibration.

    Parameter range: 0 to 2
    0:Executing
    1:Normal termination
    2:Abnormal termination
    """
    return int(self.calibration_result)
  # ----------------------------------------------------------------------------

  def read_06X_high_setting_value_bank_Y(self, bank_index: BANK_INDEX) -> int:
    """
    Set up setting value of HIGH side (BANK Y).

    Parameter range: -99.999 to +99.999
    (initial value: +5.000)
    """
    return self.mm_to_int(self.read_high_threshold(bank_index))
  # ----------------------------------------------------------------------------

  def write_06X_high_setting_value_bank_Y(
    self,
    bank_index: BANK_INDEX,
    setting_data: int
  ) -> None:
    """
    Set up setting value of HIGH side (BANK Y).

    Parameter range: -99.999 to +99.999
    (initial value: +5.000)
    """
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.change_high_threshold(self.int_to_mm(setting_data), bank_index)
  # ----------------------------------------------------------------------------

  def read_06X_low_setting_value_bank_Y(self, bank_index: BANK_INDEX) -> int:
    """
    Set up setting value of LOW side (BANK Y).

    Parameter range: -99.999 to +99.999
    (initial value: -5.000)
    """
    return self.mm_to_int(self.read_low_threshold(bank_index))
  # ----------------------------------------------------------------------------

  def write_06X_low_setting_value_bank_Y(
    self,
    bank_index: BANK_INDEX,
    setting_data: int
  ) -> None:
    """
    Set up setting value of LOW side (BANK Y).

    Parameter range: -99.999 to +99.999
    (initial value: -5.000)
    """
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.change_low_threshold(self.int_to_mm(setting_data), bank_index)
  # ----------------------------------------------------------------------------

  def read_06X_shift_target_value_bank_Y(self, bank_index: BANK_INDEX) -> int:
    """
    Set up target value of shift (BANK Y).

    Parameter range: -99.999 to +99.999
    (initial value: 0)
    """
    return self.mm_to_int(self.read_shift_target(bank_index))
  # ----------------------------------------------------------------------------

  def write_06X_shift_target_value_bank_Y(
    self,
    bank_index: BANK_INDEX,
    setting_data: int
  ) -> None:
    """
    Set up target value of shift (BANK Y).

    Parameter range: -99.999 to +99.999
    (initial value: 0)
    """
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.change_shift_target(self.int_to_mm(setting_data), bank_index)
  # ----------------------------------------------------------------------------

  def read_06X_analog_output_upper_limit_bank_Y(
    self,
    bank_index: BANK_INDEX
  ) -> int:
    """
    Set up upper limit of analog output (BANK Y). (Main unit only)

    Parameter range: (Main unit only)
    -99.999 to +99.999
    (initial value: +10.000)
    """
    # if not self.is_main_unit:
    #   raise NonExecutableStateError
    return self.mm_to_int(self.read_analog_upper_limit(bank_index))
  # ----------------------------------------------------------------------------

  def write_06X_analog_output_upper_limit_bank_Y(
    self,
    bank_index: BANK_INDEX,
    setting_data: int
  ) -> None:
    """
    Set up upper limit of analog output (BANK Y). (Main unit only)

    Parameter range: (Main unit only)
    -99.999 to +99.999
    (initial value: +10.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.change_analog_upper_limit(self.int_to_mm(setting_data), bank_index)
  # ----------------------------------------------------------------------------

  def read_06X_analog_output_lower_limit_bank_Y(
    self,
    bank_index: BANK_INDEX
  ) -> int:
    """
    Set up lower limit of analog output (BANK 0). (Main unit only)

    Parameter range: -99.999 to +99.999
    (initial value: 1.0000)
    """
    # if not self.is_main_unit:
    #   raise NonExecutableStateError
    return self.mm_to_int(self.read_analog_lower_limit(bank_index))
  # ----------------------------------------------------------------------------

  def write_06X_analog_output_lower_limit_bank_Y(
    self,
    bank_index: BANK_INDEX,
    setting_data: int
  ) -> None:
    """
    Set up lower limit of analog output (BANK 0). (Main unit only)

    Parameter range: -99.999 to +99.999
    (initial value: 1.0000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.change_analog_lower_limit(self.int_to_mm(setting_data), bank_index)
  # ----------------------------------------------------------------------------

  def read_097_key_lock_function(self) -> int:
    """
    Sets key lock.

    Parameter range: 0 to 1 (initial value: 0)
    0: Unlock
    1: Key lock
    """
    return 1 * self.key_locked
  # ----------------------------------------------------------------------------

  def write_097_key_lock_function(self, setting_data: int) -> None:
    """
    Sets key lock.

    Parameter range: 0 to 1 (initial value: 0)
    0: Unlock
    1: Key lock
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.key_locked = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_098_bank_function(self) -> int:
    """
    For read:

    Reads the current value. Use the "Bank status" of data
    number 043 to check the bank No. for which the sensor
    amplifier is operating.

    Parameter range: 0 to 3 (initial value: 0)
    """
    return self.active_bank_setting
  # ----------------------------------------------------------------------------

  def write_098_bank_function(self, setting_data: int) -> None:
    """
    For write:

    To use this value to change the bank No., set the "Bank
    switching method" of data number 150 to "Button".
    The change is disabled when "External input" is set.

    Parameter range: 0 to 3
    0: Switches to bank 0.
    1: Switches to bank 1.
    2: Switches to bank 2.
    3: Switches to bank 3.
    """
    if setting_data not in (0, 1, 2, 3):
      raise WriteDataOutsideValidRangeError
    if not self.switch_banks_via_external_input:
      self.change_bank(setting_data)  # type: ignore[arg-type]  # Mypy is dumb
  # ----------------------------------------------------------------------------

  def read_099_timing_input(self) -> int:
    """
    Set up status of timing input.

    Use the "Timing status" of data number 044 to check the
    timing input status under which the sensor amplifier is
    operating.

    The sensor amplifier operates according to the OR of this
    input and the external input cable.

    Parameter range: 0 to 1 (initial value: 0)
    0:Timing input OFF
    1:Timing input ON
    """
    return 1 * self.stored_timing_input
  # ----------------------------------------------------------------------------

  def write_099_timing_input(self, setting_data: int) -> None:
    """
    Set up status of timing input.

    Use the "Timing status" of data number 044 to check the
    timing input status under which the sensor amplifier is
    operating.

    The sensor amplifier operates according to the OR of this
    input and the external input cable.

    Parameter range: 0 to 1 (initial value: 0)
    0:Timing input OFF
    1:Timing input ON
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.stored_timing_input = bool(setting_data)
    self.start_eeprom_write()
    # Update the internal state and process edge triggers
    self.update_timing_input_status()
  # ----------------------------------------------------------------------------

  def read_100_laser_emission_on_stop_input(self) -> int:
    """
    Set up status of laser emission stop input.

    Use the "Laser emission stop status" of data number 050
    to check the laser emission stop status under which the
    sensor amplifier is operating.

    The sensor amplifier operates according to the OR of this
    input and the external input cable.

    Parameter range: 0 to 1 (initial value: 0)
    0:Emission stop input OFF
    1:Emission stop input ON
    """
    return 1 * self.stored_laser_emission_stop
  # ----------------------------------------------------------------------------

  def write_100_laser_emission_on_stop_input(self, setting_data: int) -> None:
    """
    Set up status of laser emission stop input.

    Use the "Laser emission stop status" of data number 050
    to check the laser emission stop status under which the
    sensor amplifier is operating.

    The sensor amplifier operates according to the OR of this
    input and the external input cable.

    Parameter range: 0 to 1 (initial value: 0)
    0:Emission stop input OFF
    1:Emission stop input ON
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.stored_laser_emission_stop = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_104_sub_display_screen(self) -> int:
    """
    Set up sub display's screen.

    Parameter range: 0 to 5 (initial value: 0)
    0: R.V. value screen
    1: Analog value screen
    2: HI setting value screen
    3: LO setting value screen
    4: Zero shift value screen
    5: CALC value screen
    """
    return int(self.subdisplay_screen_mode)
  # ----------------------------------------------------------------------------

  def write_104_sub_display_screen(self, setting_data: int) -> None:
    """
    Set up sub display's screen.

    Parameter range: 0 to 5 (initial value: 0)
    0: R.V. value screen
    1: Analog value screen
    2: HI setting value screen
    3: LO setting value screen
    4: Zero shift value screen
    5: CALC value screen
    """
    if setting_data not in (0, 1, 2, 3, 4, 5):
      raise WriteDataOutsideValidRangeError
    self.subdisplay_screen_mode = SubdisplayScreenMode(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_105_system_parameter_settings(self) -> int:
    """
    Set up system parameter.

    To reflect the setting, you need to execute the "System
    parameter set request" of data number 006 after writing
    the setting.

    Use the "Current system parameters" of data number 056
    to check the system parameter with which the sensor
    amplifier is operating.

    bit 0:
    0: NPN
    1: PNP

    bits 1, 2 and 3 (For main unit only. Fixed to 000 for
    expansion unit)
    000: Analog output OFF
    001: 0 to 5V
    010: -5 to 5V
    011: 1 to 5V
    100: 4 to 20mA
    """
    output: int = 0
    output += 1 * int(self.future_transistor_mode)
    if self.is_main_unit:
      output += 2 * int(self.future_analog_output_mode)
    return output
  # ----------------------------------------------------------------------------

  def write_105_system_parameter_settings(self, setting_data: int) -> None:
    """
    Set up system parameter.

    To reflect the setting, you need to execute the "System
    parameter set request" of data number 006 after writing
    the setting.

    Use the "Current system parameters" of data number 056
    to check the system parameter with which the sensor
    amplifier is operating.

    bit 0:
    0: NPN
    1: PNP

    bits 1, 2 and 3 (For main unit only. Fixed to 000 for
    expansion unit)
    000: Analog output OFF
    001: 0 to 5V
    010: -5 to 5V
    011: 1 to 5V
    100: 4 to 20mA
    """
    bit_0: int = setting_data & 0b0001
    bit_123: int = (setting_data & 0b1110) >> 1
    rest_bits: int = setting_data >> 4
    if (
      rest_bits != 0
      or bit_123 not in (0b000, 0b001, 0b010, 0b011, 0b100)
    ):
      raise WriteDataOutsideValidRangeError
    self.future_transistor_mode = TransistorMode(bit_0)
    self.future_analog_output_mode = AnalogOutputMode(bit_123)
  # ----------------------------------------------------------------------------

  def read_106_tolerance_tuning_setting_range(self) -> int:
    """
    Set up setting range for tolerance tuning.

    Parameter range: 0.000 to 99.999
    """
    return self.mm_to_int(self.tolerance_setting_range)
  # ----------------------------------------------------------------------------

  def write_106_tolerance_tuning_setting_range(self, setting_data: int) -> None:
    """
    Set up setting range for tolerance tuning.

    Parameter range: 0.000 to 99.999
    """
    if setting_data not in range(0, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.tolerance_setting_range = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_107_calibration_function(self) -> int:
    """
    Set up calibration function.

    Parameter range: 0 to 1 (initial value: 0)
    0:Initial state
    1:User setting
    """
    return 1 * self.calibration_use_user_settings
  # ----------------------------------------------------------------------------

  def write_107_calibration_function(self, setting_data: int) -> None:
    """
    Set up calibration function.

    Parameter range: 0 to 1 (initial value: 0)
    0:Initial state
    1:User setting
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.calibration_use_user_settings = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_108_calibration_function_set_1(self) -> int:
    """
    Set up target value of 1st point for calibration.

    Parameter range: -99.999 to 99.999 (initial value: 0.000)
    """
    return self.mm_to_int(self.calibration_set_1)
  # ----------------------------------------------------------------------------

  def write_108_calibration_function_set_1(self, setting_data: int) -> None:
    """
    Set up target value of 1st point for calibration.

    Parameter range: -99.999 to 99.999 (initial value: 0.000)
    """
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.calibration_set_1 = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_109_calibration_function_set_2(self) -> int:
    """
    Set up target value of 2nd point for calibration.

    Parameter range: -99.999 to 99.999 (initial value: +5.000)
    """
    return self.mm_to_int(self.calibration_set_2)
  # ----------------------------------------------------------------------------

  def write_109_calibration_function_set_2(self, setting_data: int) -> None:
    """
    Set up target value of 2nd point for calibration.

    Parameter range: -99.999 to 99.999 (initial value: +5.000)
    """
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.calibration_set_2 = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_110_calculated_value_calibration_function(self) -> int:
    """
    Set up calculated value calibration function. (Main unit only)

    Parameter range: 0 to 2 (initial value: 0)
    0:Initial state
    1:Calculated 2-p calibration
    2:Calculated 3-p calibration
    """
    return int(self.calc_calibration_mode)
  # ----------------------------------------------------------------------------

  def write_110_calculated_value_calibration_function(
    self,
    setting_data: int
  ) -> None:
    """
    Set up calculated value calibration function. (Main unit only)

    Parameter range: 0 to 2 (initial value: 0)
    0:Initial state
    1:Calculated 2-p calibration
    2:Calculated 3-p calibration
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.calc_calibration_mode = CalculationCalibrationMode(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_111_calculated_value_two_point_set_1(self) -> int:
    """
    Set up target value of 1st point for calculated value twopoint
    calibration. (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +5.000)
    """
    return self.mm_to_int(self.calc_2p_calibration_set_1)
  # ----------------------------------------------------------------------------

  def write_111_calculated_value_two_point_set_1(
    self,
    setting_data: int
  ) -> None:
    """
    Set up target value of 1st point for calculated value twopoint
    calibration. (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +5.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.calc_2p_calibration_set_1 = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_112_calculated_value_two_point_set_2(self) -> int:
    """
    Calculated value two-point calibration function SET2 (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +10.000)
    """
    return self.mm_to_int(self.calc_2p_calibration_set_2)
  # ----------------------------------------------------------------------------

  def write_112_calculated_value_two_point_set_2(
    self,
    setting_data: int
  ) -> None:
    """
    Calculated value two-point calibration function SET2 (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +10.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.calc_2p_calibration_set_2 = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_113_calculated_value_three_point_set_1(self) -> int:
    """
    Set up target value of 1st point for calculated value threepoint
    calibration. (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +5.000)
    """
    return self.mm_to_int(self.calc_3p_calibration_set_1)
  # ----------------------------------------------------------------------------

  def write_113_calculated_value_three_point_set_1(
    self,
    setting_data: int
  ) -> None:
    """
    Set up target value of 1st point for calculated value threepoint
    calibration. (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +5.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.calc_3p_calibration_set_1 = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_114_calculated_value_three_point_set_3(self) -> int:
    """
    Set up target value of 3rd point for calculated value threepoint
    calibration. (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +10.000)
    """
    return self.mm_to_int(self.calc_3p_calibration_set_3)
  # ----------------------------------------------------------------------------

  def write_114_calculated_value_three_point_set_3(
    self,
    setting_data: int
  ) -> None:
    """
    Set up target value of 3rd point for calculated value threepoint
    calibration. (Main unit only)

    Parameter range: -99.999 to 99.999
    (initial value: +10.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.calc_3p_calibration_set_3 = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_129_calculation_function(self) -> int:
    """
    Set up calculation function.

    Parameter range: 0 to 2 (initial value: 0)
    0: OFF
    1: Addition mode
    2: Subtraction mode
    """
    return int(self.calculation_mode)
  # ----------------------------------------------------------------------------

  def write_129_calculation_function(self, setting_data: int) -> None:
    """
    Set up calculation function.

    Parameter range: 0 to 2 (initial value: 0)
    0: OFF
    1: Addition mode
    2: Subtraction mode
    """
    if not self.is_main_unit or self.connected_amplifier is None:
      raise QueryWriteProtectedError
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.calculation_mode = CalculationMode(setting_data)
    if self.calculation_mode != CalculationMode.OFF:
      self.connected_amplifier.filter_setting = self.filter_setting
      self.connected_amplifier.sampling_cycle = self.sampling_cycle
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_131_measurement_direction(self) -> int:
    """
    Set up measurement direction.

    Parameter range: 0 to 1 (initial value: 0)
    0:n or
    1: rEv
    """
    return 1 * self.reversed_measurement_direction
  # ----------------------------------------------------------------------------

  def write_131_measurement_direction(self, setting_data: int) -> None:
    """
    Set up measurement direction.

    Parameter range: 0 to 1 (initial value: 0)
    0:n or
    1: rEv
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.reversed_measurement_direction = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_132_sampling_cycle(self) -> int:
    """
    Set up sampling cycle.

    Parameter range: 0 to 4 (initial value: 0)
    0:dEFLt
    1: 0.33 ms
    2: 1 ms
    3: 2 ms
    4: 5 ms
    """
    return int(self.sampling_cycle)
  # ----------------------------------------------------------------------------

  def write_132_sampling_cycle(self, setting_data: int) -> None:
    """
    Set up sampling cycle.

    Parameter range: 0 to 4 (initial value: 0)
    0:dEFLt
    1: 0.33 ms
    2: 1 ms
    3: 2 ms
    4: 5 ms
    """
    if setting_data not in (0, 1, 2, 3, 4):
      raise WriteDataOutsideValidRangeError
    self.sampling_cycle = SamplingCycle(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_133_averaging_diff_count_high_pass_filter(self) -> int:
    """
    Set up averaging/diff. count filter/high-pass filter.

    Parameter range: 0 to 14 (initial value: 4)
    0: 1 time
    1: 2 times
    2: 4 times
    3: 8 times
    4: 16 times
    5: 32 times
    6: 64 times
    7: 128 times
    8: 256 times
    9: 512 times
    10: 1024 times
    11: 2048 times
    12: 4096 times
    13: Diff. count filter
    14: High-pass filter
    """
    return int(self.filter_setting)
  # ----------------------------------------------------------------------------

  def write_133_averaging_diff_count_high_pass_filter(
    self,
    setting_data: int
  ) -> None:
    """
    Set up averaging/diff. count filter/high-pass filter.

    Parameter range: 0 to 14 (initial value: 4)
    0: 1 time
    1: 2 times
    2: 4 times
    3: 8 times
    4: 16 times
    5: 32 times
    6: 64 times
    7: 128 times
    8: 256 times
    9: 512 times
    10: 1024 times
    11: 2048 times
    12: 4096 times
    13: Diff. count filter
    14: High-pass filter
    """
    if setting_data not in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
      raise WriteDataOutsideValidRangeError
    self.filter_setting = FilterSetting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_134_output_mode(self) -> int:
    """
    Set up output mode.

    Parameter range: 0 to 1 (initial value: 0)
    0: N.O.
    1: N.C.
    """
    return 1 * self.output_mode_normally_closed
  # ----------------------------------------------------------------------------

  def write_134_output_mode(self, setting_data: int) -> None:
    """
    Set up output mode.

    Parameter range: 0 to 1 (initial value: 0)
    0: N.O.
    1: N.C.
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.output_mode_normally_closed = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_136_hold_function_setting(self) -> int:
    """
    Set up hold function.

    Parameter range: 0 to 5 (initial value: 0)
    0:Sample hold
    1:Peak hold
    2:Bottom hold
    3:Peak-to-peak hold
    4:Auto peak hold
    5:Auto bottom hold
    """
    return int(self.hold_function_setting)
  # ----------------------------------------------------------------------------

  def write_136_hold_function_setting(self, setting_data: int) -> None:
    """
    Set up hold function.

    Parameter range: 0 to 5 (initial value: 0)
    0:Sample hold
    1:Peak hold
    2:Bottom hold
    3:Peak-to-peak hold
    4:Auto peak hold
    5:Auto bottom hold
    """
    if setting_data not in (0, 1, 2, 3, 4, 5):
      raise WriteDataOutsideValidRangeError
    self.hold_function_setting = HoldFunctionSetting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_137_auto_hold_trigger_level(self) -> int:
    """
    Set up Auto-peak hold or Auto bottom hold trigger level.

    Parameter range: -99.999 to +99.999
    (initial value: +1.000)
    """
    return self.mm_to_int(self.auto_trigger_level)
  # ----------------------------------------------------------------------------

  def write_137_auto_hold_trigger_level(self, setting_data: int) -> None:
    """
    Set up Auto-peak hold or Auto bottom hold trigger level.

    Parameter range: -99.999 to +99.999
    (initial value: +1.000)
    """
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.auto_trigger_level = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_138_timing_input_setting(self) -> int:
    """
    Set up timing input.

    Parameter range: 0 to 1 (initial value: 0)
    0:Level
    1:Edge
    """
    return 1 * self.timing_input_on_edge
  # ----------------------------------------------------------------------------

  def write_138_timing_input_setting(self, setting_data: int) -> None:
    """
    Set up timing input.

    Parameter range: 0 to 1 (initial value: 0)
    0:Level
    1:Edge
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.timing_input_on_edge = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_139_delay_timer(self) -> int:
    """
    Set up delay timer.

    Parameter range: 0 to 3 (initial value: 0)
    0:OFF
    1:On delay
    2:Off delay
    3:One-shot
    """
    return int(self.delay_timer_setting)
  # ----------------------------------------------------------------------------

  def write_139_delay_timer(self, setting_data: int) -> None:
    """
    Set up delay timer.

    Parameter range: 0 to 3 (initial value: 0)
    0:OFF
    1:On delay
    2:Off delay
    3:One-shot
    """
    if setting_data not in (0, 1, 2, 3):
      raise WriteDataOutsideValidRangeError
    self.delay_timer_setting = DelayTimerSetting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_140_timer_duration(self) -> int:
    """
    Set up timer duration (unit: ms).

    Parameter range: 5 to 9999 (Initial value: 60)
    """
    return self.timer_duration
  # ----------------------------------------------------------------------------

  def write_140_timer_duration(self, setting_data: int) -> None:
    """
    Set up timer duration (unit: ms).

    Parameter range: 5 to 9999 (Initial value: 60)
    """
    if setting_data not in range(5, 9999 + 1):
      raise WriteDataOutsideValidRangeError
    self.timer_duration = setting_data
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_141_hyseresis(self) -> int:
    """
    Set up hysteresis.

    Parameter range: 0.000 to 99.999
    """
    return self.mm_to_int(self.hysteresis)
  # ----------------------------------------------------------------------------

  def write_141_hyseresis(self, setting_data: int) -> None:
    """
    Set up hysteresis.

    Parameter range: 0.000 to 99.999
    """
    if setting_data not in range(0, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    self.hysteresis = self.int_to_mm(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_142_analog_output_scaling(self) -> int:
    """
    Set up analog output scaling. (Main unit only)

    Parameter range: 0 to 1 (initial value: 0)
    0:Initial state
    1:Free range
    2:Bank
    """
    return int(self.analog_output_scaling_mode)
  # ----------------------------------------------------------------------------

  def write_142_analog_output_scaling(self, setting_data: int) -> None:
    """
    Set up analog output scaling. (Main unit only)

    Parameter range: 0 to 1 (initial value: 0)
    0:Initial state
    1:Free range
    2:Bank
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.analog_output_scaling_mode = AnalogOutputScalingMode(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_143_analog_output_upper_limit_value(self) -> int:
    """
    Set up upper limit of analog output.

    Parameter range: -99.999 to 99.999
    (Initial value: +10.000)
    """
    return self.mm_to_int(self.free_analog_upper_limit)
  # ----------------------------------------------------------------------------

  def write_143_analog_output_upper_limit_value(
    self,
    setting_data: int
  ) -> None:
    """
    Set up upper limit of analog output.

    Parameter range: -99.999 to 99.999
    (Initial value: +10.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    value: float = self.int_to_mm(setting_data)
    if self.analog_output_scaling_mode == AnalogOutputScalingMode.BANK:
      # TODO: not verified, may fail siltently or change the free range value
      raise NonExecutableStateError
    elif self.analog_output_scaling_mode == AnalogOutputScalingMode.FREE_RANGE:
      self.free_analog_upper_limit = value
      self.start_eeprom_write()
    else:
      raise QueryWriteProtectedError  # could also be NonExecutableStateError
  # ----------------------------------------------------------------------------

  def read_144_analog_output_lower_limit_value(self) -> int:
    """
    Set up lower limit of analog output.

    Parameter range: -99.999 to 99.999
    (initial value: -10.000)
    """
    return self.mm_to_int(self.free_analog_lower_limit)
  # ----------------------------------------------------------------------------

  def write_144_analog_output_lower_limit_value(
    self,
    setting_data: int
  ) -> None:
    """
    Set up lower limit of analog output.

    Parameter range: -99.999 to 99.999
    (initial value: -10.000)
    """
    if not self.is_main_unit:
      raise QueryWriteProtectedError
    if setting_data not in range(-99999, 99999 + 1):
      raise WriteDataOutsideValidRangeError
    value: float = self.int_to_mm(setting_data)
    if self.analog_output_scaling_mode == AnalogOutputScalingMode.BANK:
      # TODO: not verified, may fail siltently or change the free range value
      raise NonExecutableStateError
    elif self.analog_output_scaling_mode == AnalogOutputScalingMode.FREE_RANGE:
      self.free_analog_lower_limit = value
      self.start_eeprom_write()
    else:
      raise QueryWriteProtectedError  # could also be NonExecutableStateError
  # ----------------------------------------------------------------------------

  def read_145_external_input(self) -> int:
    """
    Set up whether to change the function assigned to
    external input 1/2/3/4 from the initial state.

    Parameter range: 0 to 1 (initial value: 0)
    0:Initial state
    1:User setting
    """
    return 1 * self.external_input_use_user_settings
  # ----------------------------------------------------------------------------

  def write_145_external_input(self, setting_data: int) -> None:
    """
    Set up whether to change the function assigned to
    external input 1/2/3/4 from the initial state.

    Parameter range: 0 to 1 (initial value: 0)
    0:Initial state
    1:User setting
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.external_input_use_user_settings = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_146_external_input_1(self) -> int:
    """
    Set up function to be assigned to external input 1.

    Parameter range: 0 to 4 (initial value: 0)
    0:Zero shift input
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    4:Not used
    """
    return int(self.external_input_1_setting)
  # ----------------------------------------------------------------------------

  def write_146_external_input_1(self, setting_data: int) -> None:
    """
    Set up function to be assigned to external input 1.

    Parameter range: 0 to 4 (initial value: 0)
    0:Zero shift input
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    4:Not used
    """
    if setting_data not in (0, 1, 2, 3, 4):
      raise WriteDataOutsideValidRangeError
    self.external_input_1_setting = ExternalInput1Setting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_147_external_input_2(self) -> int:
    """
    Set up function to be assigned to external input 2.

    Parameter range: 0 to 4 (initial value: 0)
    0:Reset input
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    4:Not used
    """
    return int(self.external_input_2_setting)
  # ----------------------------------------------------------------------------

  def write_147_external_input_2(self, setting_data: int) -> None:
    """
    Set up function to be assigned to external input 2.

    Parameter range: 0 to 4 (initial value: 0)
    0:Reset input
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    4:Not used
    """
    if setting_data not in (0, 1, 2, 3, 4):
      raise WriteDataOutsideValidRangeError
    self.external_input_2_setting = ExternalInput2Setting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_148_external_input_3(self) -> int:
    """
    Set up function to be assigned to external input 3.

    Parameter range: 0 to 4 (initial value: 0)
    0:Timing input
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    4:Not used
    """
    return int(self.external_input_3_setting)
  # ----------------------------------------------------------------------------

  def write_148_external_input_3(self, setting_data: int) -> None:
    """
    Set up function to be assigned to external input 3.

    Parameter range: 0 to 4 (initial value: 0)
    0:Timing input
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    4:Not used
    """
    if setting_data not in (0, 1, 2, 3, 4):
      raise WriteDataOutsideValidRangeError
    self.external_input_3_setting = ExternalInput3Setting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_149_external_input_4(self) -> int:
    """
    Set up function to be assigned to external input 4.

    Parameter range: 0 to 3 (initial value: 0)
    0:Not used
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    """
    return int(self.external_input_4_setting)
  # ----------------------------------------------------------------------------

  def write_149_external_input_4(self, setting_data: int) -> None:
    """
    Set up function to be assigned to external input 4.

    Parameter range: 0 to 3 (initial value: 0)
    0:Not used
    1:Bank A input
    2:Bank B input
    3:Laser emission stop input
    """
    if setting_data not in (0, 1, 2, 3):
      raise WriteDataOutsideValidRangeError
    self.external_input_4_setting = ExternalInput4Setting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_150_bank_switching_method(self) -> int:
    """
    Set up method for switching the Bank.

    Parameter range: 0 to 1 (initial value: 0)
    0:Button
    1:External input
    """
    return 1 * self.switch_banks_via_external_input
  # ----------------------------------------------------------------------------

  def write_150_bank_switching_method(self, setting_data: int) -> None:
    """
    Set up method for switching the Bank.

    Parameter range: 0 to 1 (initial value: 0)
    0:Button
    1:External input
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.switch_banks_via_external_input = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_152_zero_shift_value_memory_function(self) -> int:
    """
    Set up whether to save the zero-shift state.

    Parameter range: 0 to 1 (initial value: 0)
    0: OFF
    1: ON
    """
    return 1 * self.zero_shift_saved_in_memory
  # ----------------------------------------------------------------------------

  def write_152_zero_shift_value_memory_function(
    self,
    setting_data: int
  ) -> None:
    """
    Set up whether to save the zero-shift state.

    Parameter range: 0 to 1 (initial value: 0)
    0: OFF
    1: ON
    """
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.zero_shift_saved_in_memory = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_153_mutual_interference_prevention_function(self) -> int:
    """
    Set up mutual interference prevention function.

    Parameter range: 0 to 1 (initial value: 0)
    0:Interference prevention OFF
    1:Interference prevention ON
    """
    return 1 * self.mutual_interference_prevention_active
  # ----------------------------------------------------------------------------

  def write_153_mutual_interference_prevention_function(
    self,
    setting_data: int
  ) -> None:
    """
    Set up mutual interference prevention function.

    Parameter range: 0 to 1 (initial value: 0)
    0:Interference prevention OFF
    1:Interference prevention ON
    """
    if not self.is_main_unit:
      raise IDOutsideValidRangeError
    if setting_data not in (0, 1):
      raise WriteDataOutsideValidRangeError
    self.mutual_interference_prevention_active = bool(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_154_display_digit(self) -> int:
    """
    Set up display digit. (initial value: 0)

    0:Initial state
    2:0.001
    3:0.01
    4:0.1
    5:1
    """
    return int(self.display_digit_setting)
  # ----------------------------------------------------------------------------

  def write_154_display_digit(self, setting_data: int) -> None:
    """
    Set up display digit. (initial value: 0)

    0:Initial state
    2:0.001
    3:0.01
    4:0.1
    5:1
    """
    if setting_data not in (0, 1, 2, 3, 4, 5):
      raise WriteDataOutsideValidRangeError
    self.display_digit_setting = DisplayDigit(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_155_power_saving_function(self) -> int:
    """
    Set up power saving mode.

    Parameter range: 0 to 2 (initial value: 0)
    0:OFF
    1:Half
    2:All
    """
    return int(self.power_saving_mode)
  # ----------------------------------------------------------------------------

  def write_155_power_saving_function(self, setting_data: int) -> None:
    """
    Set up power saving mode.

    Parameter range: 0 to 2 (initial value: 0)
    0:OFF
    1:Half
    2:All
    """
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.power_saving_mode = PowerSavingMode(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_156_head_display_mode(self) -> int:
    """
    Set up head display mode.

    Parameter range: 0 to 2 (initial value: 0)
    0:Initial state
    1:OK/NG display
    2:OFF
    """
    return int(self.head_display_mode)
  # ----------------------------------------------------------------------------

  def write_156_head_display_mode(self, setting_data: int) -> None:
    """
    Set up head display mode.

    Parameter range: 0 to 2 (initial value: 0)
    0:Initial state
    1:OK/NG display
    2:OFF
    """
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.head_display_mode = HeadDisplayMode(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_157_display_color(self) -> int:
    """
    Set up display color of the amplifier.

    Parameter range: 0 to 2 (initial value: 0)
    0:GO Green
    1:GO Red
    2:Always Red
    """
    return int(self.display_color)
  # ----------------------------------------------------------------------------

  def write_157_display_color(self, setting_data: int) -> None:
    """
    Set up display color of the amplifier.

    Parameter range: 0 to 2 (initial value: 0)
    0:GO Green
    1:GO Red
    2:Always Red
    """
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.display_color = DisplayColor(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_158_timer_duration_diff_count_filter(self) -> int:
    """
    Set up timer duration of diff. count filter (unit: ms).

    Parameter range: 2 to 9999 (initial value: 10)
    """
    return self.diff_count_filter_timer_duration
  # ----------------------------------------------------------------------------

  def write_158_timer_duration_diff_count_filter(
    self,
    setting_data: int
  ) -> None:
    """
    Set up timer duration of diff. count filter (unit: ms).

    Parameter range: 2 to 9999 (initial value: 10)
    """
    if setting_data not in range(2, 9999 + 1):
      raise WriteDataOutsideValidRangeError
    self.diff_count_filter_timer_duration = setting_data
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_159_cutoff_frequency_high_pass_filter(self) -> int:
    """
    Set up cutoff frequency of high-pass filter.

    Parameter range: 0 to 9 (initial value: 10)
    0: 0.1Hz
    1: 0.2Hz
    2: 0.5Hz
    3: 1Hz
    4: 2Hz
    5: 5Hz
    6: 10Hz
    7: 20Hz
    8: 50Hz
    9: 100Hz
    """
    return int(self.high_pass_cutoff_frequency)
  # ----------------------------------------------------------------------------

  def write_159_cutoff_frequency_high_pass_filter(
    self,
    setting_data: int
  ) -> None:
    """
    Set up cutoff frequency of high-pass filter.

    Parameter range: 0 to 9 (initial value: 10)
    0: 0.1Hz
    1: 0.2Hz
    2: 0.5Hz
    3: 1Hz
    4: 2Hz
    5: 5Hz
    6: 10Hz
    7: 20Hz
    8: 50Hz
    9: 100Hz
    """
    if setting_data not in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
      raise WriteDataOutsideValidRangeError
    self.high_pass_cutoff_frequency = HighPassCutoffFrequency(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_161_alarm_setting(self) -> int:
    """
    Set up alarm setting.

    Parameter range: 0 to 2 (initial value: 0)
    0:Initial state
    1:Clamp
    2:User setting
    """
    return int(self.alarm_setting)
  # ----------------------------------------------------------------------------

  def write_161_alarm_setting(self, setting_data: int) -> None:
    """
    Set up alarm setting.

    Parameter range: 0 to 2 (initial value: 0)
    0:Initial state
    1:Clamp
    2:User setting
    """
    # This is function is listed as Read-Only in DL-EN1 user manual,
    # while the DL-RS1A user manual has it as R/W.
    # I asssume this is a printing error in the DL-EN1 manual.
    if setting_data not in (0, 1, 2):
      raise WriteDataOutsideValidRangeError
    self.alarm_setting = AlarmSetting(setting_data)
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_162_alarm_count(self) -> int:
    """
    Set up alarm count.

    Parameter range: 2 to 1000 (initial value: 7)
    """
    return self.alarm_count
  # ----------------------------------------------------------------------------

  def write_162_alarm_count(self, setting_data: int) -> None:
    """
    Set up alarm count.

    Parameter range: 2 to 1000 (initial value: 7)
    """
    # This is function is listed as Read-Only in DL-EN1 user manual,
    # while the DL-RS1A user manual has it as R/W.
    # I asssume this is a printing error in the DL-EN1 manual.
    if setting_data not in range(0, 1000 + 1):
      raise WriteDataOutsideValidRangeError
    self.alarm_count = setting_data
    self.start_eeprom_write()
  # ----------------------------------------------------------------------------

  def read_193_product_code(self) -> int:
    """
    Indicates the product code.

    Main unit : 4022
    Expansion unit : 4023
    """
    return 4022 if self.is_main_unit else 4023
  # ----------------------------------------------------------------------------

  def read_194_revision(self) -> int:
    """
    Indicates the revision.

    The higher-order bytes in the lower-order word indicate
    the major revision and the lower-order bytes indicate the
    minor revision.

    Parameter range: 0101H
    """
    return 0x0101
  # ----------------------------------------------------------------------------

  def read_195_connected_sensor_head(self) -> int:
    """
    Indicates model of sensor head connected to the
    amplifier.

    0:Not connected
    1:IL-030
    2:IL-065
    3:IL-100
    4:IL-300
    5:IL-600
    106:IL-S025
    107:IL-S065
    208:IL-S100
    311:IL-2000
    """
    return int(self.connected_sensor_head)
  # ----------------------------------------------------------------------------

  def read_200_product_name(self) -> str:
    """
    Indicates the product name.

    Main unit : "IL-1000/1500"
    Expansion unit : "IL-1050/1550"
    """
    return "IL-1000/1500" if self.is_main_unit else "IL-1050/1550"
  # ----------------------------------------------------------------------------

  def read_215_series_code(self) -> int:
    """
    Indicates the series code.

    Main unit : 4022
    Expansion unit : 4023
    """
    return 4022 if self.is_main_unit else 4023
  # ----------------------------------------------------------------------------

  def read_216_series_version(self) -> int:
    """
    Indicates the series version.

    Parameter range: 1
    """
    return 1
  # ----------------------------------------------------------------------------

  def read_217_device_type(self) -> int:
    """
    Indicates the device type.

    Parameter range: 0
    """
    return 0
  # ----------------------------------------------------------------------------


FACTORY_MAPPING: dict[str, Callable[[], SensorUnit]] = {
  "IL-S025": SensorUnit.create_IL_S025,
  "IL-030": SensorUnit.create_IL_030,
  "IL-065": SensorUnit.create_IL_065,
  "IL-S065": SensorUnit.create_IL_S065,
  "IL-100": SensorUnit.create_IL_100,
  "IL-300": SensorUnit.create_IL_300,
  "IL-600": SensorUnit.create_IL_600,
  "IL-2000": SensorUnit.create_IL_2000,
}
