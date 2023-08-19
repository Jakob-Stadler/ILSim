import socket
import sys


def main() -> None:
  """
  Entry point for clients.
  """
  HOST, PORT = "localhost", 9999
  arg = " ".join(sys.argv[1:])

  # Create a socket (SOCK_STREAM means a TCP socket)
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    data = bytes(arg + "\r\n", "utf-8")
    sock.sendall(data)

    # Receive data from the server and shut down
    received = sock.recv(1024)

  print(f"Sent:     {data!r}")
  print(f"Received: {received!r}")


if __name__ == "__main__":
  main()
