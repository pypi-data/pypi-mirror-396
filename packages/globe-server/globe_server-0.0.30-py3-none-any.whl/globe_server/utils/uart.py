# app/utils/uart.py

import serial
from globe_server import config

def send_uart_command(command: str):
    """Sends a command to the FPGA via UART."""
    try:
        ser = serial.Serial(config.UART_DEVICE, config.UART_BAUD_RATE, timeout=1)  # Open serial port
        ser.write(command.encode())  # Send command
        ser.close()  # Close serial port
        return True
    except Exception as e:
        print(f"Error sending UART command: {e}")
        return False


def convert_brightness_to_hex(brightness: int) -> str:
    """Converts a brightness value (0-255) to a two-character hexadecimal string."""
    if not (0 <= brightness <= 255):
        raise ValueError("Brightness value must be between 0 and 255.")
    return "{:02X}".format(brightness)  # Format as two-digit hexadecimal string

def create_uart_message(colour, hex_value):
    start_char = 'B'
    end_char = 'E'

    if colour == "red":
      register_char = "R"
    elif colour == "green":
      register_char = "G"
    elif colour == "blue":
      register_char = "B"
    else:
      raise ValueError("Colour value must be red, green or blue");

    message = f"{start_char}{register_char}{hex_value}{end_char}"

    return message