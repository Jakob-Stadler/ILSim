

# native imports
import json
import sys
from dataclasses import dataclass
from socketserver import StreamRequestHandler
from socketserver import TCPServer
from time import sleep
from typing import Any, ClassVar

# internal imports
from .communication import CommunicationUnit
from .sensor import FACTORY_MAPPING
from .sensor import SensorUnit


@dataclass
class Config:
  """
  Container class for parsed config data.
  """
  communication_unit: CommunicationUnit
  host: str
  port: int


def load_config(filename: str = "config.json") -> Config:
  """
  Read and parse JSON file and create instane of config data container.
  """
  with open(filename, 'r', encoding='utf-8') as file:
    raw_config = json.load(file)
  host: str = raw_config['host']
  port: int = raw_config['port']
  communication_unit: CommunicationUnit = CommunicationUnit()
  for sensor_config in raw_config['sensors']:
    sensor_type: str = sensor_config['type']
    overrides: dict[str, Any] = sensor_config['overrides']
    factory = FACTORY_MAPPING[sensor_type]
    sensor: SensorUnit = factory()
    for attribute, value in overrides.items():
      setattr(sensor, attribute, value)
    communication_unit.add_unit(sensor)
  return Config(
    communication_unit=communication_unit,
    host=host,
    port=port
  )


class DLEN1TCPHandler(StreamRequestHandler):
  """
  Custom TCPHander subclass to handle raw socket communication and delegate
  to/from communication_unit.
  """
  communication_unit: ClassVar[CommunicationUnit | None] = None

  def handle(self) -> None:
    assert isinstance(self.communication_unit, CommunicationUnit)
    print(f"{self.client_address} established connection")
    # self.rfile is a file-like object created by the handler;
    # we can now use e.g. readline() instead of raw recv() calls
    while True:
      self.data = self.rfile.readline()
      if self.data == b'':
        print(f"{self.client_address} closed connection")
        break
      if self.data == b'RELOAD_CONFIG\r\n':
        cfg: Config = load_config()
        self.__class__.communication_unit = cfg.communication_unit
        print("Config reloaded")
        self.wfile.write(b"Config reloaded")
        continue
      print(f"Received: {self.data!r}")
      # Likewise, self.wfile is a file-like object used to write back
      # to the client
      sleep(0.020)  # Artifical delay
      response = self.communication_unit.handle_query(self.data)
      print(f"Response: {response!r}")
      self.wfile.write(response)


def main() -> None:
  """
  Entry point for servers.
  """
  try:
    config_file: str = sys.argv[1]
  except IndexError:
    config_file = 'config.json'
  config: Config = load_config(config_file)
  DLEN1TCPHandler.communication_unit = config.communication_unit

  with TCPServer((config.host, config.port), DLEN1TCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
      server.serve_forever()
    except KeyboardInterrupt:
      config.communication_unit.stop_threads()


if __name__ == "__main__":
  main()
