

# native imports
from enum import IntEnum
from typing import Any


def raise_NotImplementedError(*args: Any) -> Any:
  """
  Raise NotImplementedError
  """
  raise NotImplementedError


class CommunicationErrorCodes(IntEnum):
  """
  Error Codes for ER Replies
  """
  NO_ERROR = 0
  """
  Free of errors.
  """
  ERROR_009 = 9
  """
  Error 009:

  The written data is outside of the valid range.
  The sensor does not support writing to the specified ID or data number.
  """
  ERROR_012 = 12
  """
  Error 012:

  This is a state in which the operation command cannot be executed.
  The sensor does not support writing to the specified ID or data number.
  """
  ERROR_014 = 14
  """
  Error 014:

  This address is write-protected or is in a state
  in which it cannot be written to.
  The sensor does not support writing to the specified ID or data number.
  """
  ERROR_016 = 16
  """
  Error 016:

  This data number is read-protected or is in a state
  in which it cannot be read.
  """
  ERROR_020 = 20
  """
  Error 020:

  The data number is outside of the valid range.
  """
  ERROR_022 = 22
  """
  Error 022:

  The ID is outside of the valid range.
  """
  ERROR_031 = 31
  """
  Error 031:

  The sensor does not support reading from or writing
  to the specified ID or data number.
  Writing is not possible in the current mode.
  The device is currently initializing the communication.
  """
  ERROR_254 = 254
  """
  Error 254:

  This is the system error state.
  Wait for the length of time required to start the device.
  Wait for a response.
  Check for errors in the connectors such as the D-bus connector.
  Restart the DL-EN1.
  If the error still occurs, contact your nearest KEYENCE office.
  """
  ERROR_255 = 255
  """
  Error 255:

  The command format is not correct.
  """


class CommunicationException(Exception):
  """
  Base Exception for all custom Communication Exceptions
  """
  error_code: CommunicationErrorCodes


class WriteDataOutsideValidRangeError(CommunicationException):
  """
  Error 009:

  The written data is outside of the valid range.
  The sensor does not support writing to the specified ID or data number.
  """
  error_code = CommunicationErrorCodes.ERROR_009


class NonExecutableStateError(CommunicationException):
  """
  Error 012:

  This is a state in which the operation command cannot be executed.
  The sensor does not support writing to the specified ID or data number.
  """
  error_code = CommunicationErrorCodes.ERROR_012


class QueryWriteProtectedError(CommunicationException):
  """
  Error 014:

  This address is write-protected or is in a state
  in which it cannot be written to.
  The sensor does not support writing to the specified ID or data number.
  """
  error_code = CommunicationErrorCodes.ERROR_014


class QueryReadProtectedError(CommunicationException):
  """
  Error 016:

  This data number is read-protected or is in a state
  in which it cannot be read.
  """
  error_code = CommunicationErrorCodes.ERROR_016


class QueryOutsideValidRangeError(CommunicationException):
  """
  Error 020:

  The data number is outside of the valid range.
  """
  error_code = CommunicationErrorCodes.ERROR_020


class IDOutsideValidRangeError(CommunicationException):
  """
  Error 022:

  The ID is outside of the valid range.
  """
  error_code = CommunicationErrorCodes.ERROR_022


class InaccessibleIDOrQueryError(CommunicationException):
  """
  Error 031:

  The sensor does not support reading from or writing
  to the specified ID or data number.
  Writing is not possible in the current mode.
  The device is currently initializing the communication.
  """
  error_code = CommunicationErrorCodes.ERROR_031


class GeneralSystemError(CommunicationException):
  """
  Error 254:

  This is the system error state.
  Wait for the length of time required to start the device.
  Wait for a response.
  Check for errors in the connectors such as the D-bus connector.
  Restart the DL-EN1.
  If the error still occurs, contact your nearest KEYENCE office.
  """
  error_code = CommunicationErrorCodes.ERROR_254


class CommandFormatError(CommunicationException):
  """
  Error 255:

  The command format is not correct.
  """
  error_code = CommunicationErrorCodes.ERROR_255
