#!/usr/bin/python

import struct

import serial_inf

# =============================================================================
#                   Constants for iRobot Create 2
# =============================================================================

SENSOR_UPDATE_WAIT = .015   # Time in between sensor updates

_BAUD_RATE = 115200     # iRobot Create 2 Default baud rate
_TIMEOUT = 1            # The default read timeout to avoid indefinite blocking
_SENSORS_OPCODE = "142" # Opcode for the sensors command
_BYTE = 0xFF            # Helps isolate a byte
_BYTE_SIZE = 8          # The number of bit in a byte of iRobot Create 2

class State:
    """ Represents the different states of the iRobot Create 2. The value at
        each state is the necessary command to enter that state.

        There is no command to transition back to the START state, so the
        transition from the START state is one way.
    """
    START = ""
    RESET = "7"
    STOP = "173"
    PASSIVE = "128"
    SAFE = "131"
    FULL = "132"

class Button:
    """ Represents the different buttons on the iRobot Create 2. The value of
        each button are the corresponding bit it refers to in the button packet.

        This also contains the packet id, and the number of data bytes to read.
    """
    # Buttons
    CLOCK = 0x80
    SCHEDULE = 0x40
    DAY = 0x20
    HOUR = 0x10
    MINUTE = 0x08
    DOCK = 0x04
    SPOT = 0x02
    CLEAN = 0x01

    # Packet Information
    PACKET_ID = "18"
    DATA_BYTES = 1

class Drive:
    """ Represents special cases for the radius of the iRobot Create 2's
        drive command, and the bounds for velocity and radius.
    """
    # Special Cases for the radius
    STRAIGHT = 0x8000
    STRAIGHT_ALT = 0x7FFF
    TURN_CW = 0xFFFF
    TURN_CCW = 0x0001

    # Bounds established by iRobot Create 2's OI specifications.
    MAX_VEL = 500
    MIN_VEL = -500
    MAX_RAD = 2000
    MIN_RAD = -2000

# =============================================================================
#                       iRobot Create 2's Interface
# =============================================================================

class Robot:
    """ Represents a interface for iRobot Create 2 over a serial connection.

        Attributes:
            state: A State value used to indicate the robot's current state.
    """
    state = None

    _serial_conn = None

    def __init__(self, port, buad=_BAUD_RATE, timeout=_TIMEOUT, start=True):
        """ Initializes a robot by first establishing the serial connection to
            the robot. and then sending the start command the robot. This
            command will set the robot's mode to PASSIVE, and grant the
            ability to send other command.

        :param port:
            The serial port to the robot
        :param buad:
            The buad rate of the robot
        :param timeout:
            The read timeout for the robot
        :param start:
            Flags the robot to enter the PASSIVE state. If this is false,
            the robot's state will need to be changed from START to
            PASSIVE before any other commands can be sent.
        :return:
        """
        self._serial_conn = serial_inf.SerialConn(port, buad, timeout)
        self.state = State.START

        if start:
            self.change_state(State.PASSIVE)

    def change_state(self, new_state):
        """ Changes the robot into the provided state provided it is a different
            state and the new state is not State.START.

        :type new_state State:
        :param new_state:
            The state that the robot should transition into.
        :return:
            True if the change was successful, otherwise false.
        """
        if new_state != self.state and new_state != State.START:
            self._serial_conn.send_command(new_state)
            self.state = new_state
            return True
        return False

    def drive(self, velocity, radius):
        """ Issues the drive command for the robot. This method specifically
            calls the drive command with opcode 137 which is only available
            to a robot is the SAFE or FULL state.

            Both arguments will be interrupt as 16 bit values in two's
            complement representation. This means this method supports
            explicit integer values(i.e. -1, 500, -150) and 16 bit
            integers(i.e 0xFFFF. 0x7FFF).

            All the special cases for this command can be found in the Drive
            class.
        :param velocity:
            The velocity of the robot in millimeters per second. This can
            range from -500 to 500 mm/s.
        :param radius:
            The radius the robot should turn in mm. This can range from
            -2000 to 2000 mm.
        """

        # Bounds the velocity and radius to the robot's specified range
        bound_vel = self._convert_bound(velocity, Drive.MIN_VEL, Drive.MAX_VEL)
        # Captures the special cases that fall outside the bounds for radius
        if radius == Drive.STRAIGHT or radius == Drive.STRAIGHT_ALT:
            bound_rad = radius
        else:
            bound_rad = self._convert_bound(radius, Drive.MIN_RAD, Drive.MAX_RAD)

        # Separates and prepares the data for encoding
        data = (bound_vel >> _BYTE_SIZE & _BYTE,
                bound_vel & _BYTE,
                bound_rad >> _BYTE_SIZE & _BYTE,
                bound_rad & _BYTE)

        # Sends drive command to robot
        self._serial_conn.send_command("137 %s %s %s %s" % data)

    def _convert_bound(self, value, lower_bound, upper_bound):
        """ This begins by converting the provided value into a 16 bit two's
            complement integer. Next, it bounds the converted integer between
             the provided upper and lower bounds.

        :param value:
            The value to bound.
        :param lower_bound:
            The minimum value this value can possesses.
        :param upper_bound:
            The maximum value this value can possesses.
        :return:
            The bounded version of the value which is based on the upper and
            lower bounds.
        """
        # Converts value to 16 bit two's complement integer via bitwise.
        most_sig_bit = 0x8000

        # Gets the two least significant bits
        convert_val = value & _BYTE << _BYTE_SIZE | value & _BYTE
        # Extends the most significant bit if it is a 1. This is done by
        # carrying out the most significant bit.
        if bool(convert_val & most_sig_bit):
            convert_val = convert_val | ~(_BYTE << _BYTE_SIZE | _BYTE)

        # Bounds the converted value
        if convert_val > upper_bound:
            return upper_bound
        elif convert_val < lower_bound:
            return lower_bound
        return convert_val

    def read_button(self, button):
        """ Reads the provided button's bit from the Buttons packet. This method
            is available to a robot in the PASSIVE, SAFE, or FULL state.

        :type button Button:
        :param button:
            The button to read
        :return:
            The boolean value of the corresponding button.
        """
        data = self._read_packet(Button.PACKET_ID, Button.DATA_BYTES)

        # Gets first byte
        byte = struct.unpack("B", data)[0]
        return bool(byte & button)

    def read_buttons(self):
        """ Reads all the buttons on the iRobot Create 2. This method
            is available to a robot in the PASSIVE, SAFE, or FULL state.

        :return:
            A dictionary of all the buttons' values. Each record is
            addressed by the value in Button. Thus, the individual button
            values can be acquired by like so:
                clean = someRobot.read_buttons()[Button.CLEAN]
        """
        data = self._read_packet(Button.PACKET_ID, Button.DATA_BYTES)

        # Gets first byte
        byte = struct.unpack("B", data)[0]
        return {
            Button.CLEAN: bool(byte & Button.CLEAN),
            Button.SPOT: bool(byte & Button.SPOT),
            Button.DOCK: bool(byte & Button.DOCK),
            Button.MINUTE: bool(byte & Button.MINUTE),
            Button.HOUR: bool(byte & Button.HOUR),
            Button.DAY: bool(byte & Button.DAY),
            Button.SCHEDULE: bool(byte & Button.SCHEDULE),
            Button.CLOCK: bool(byte & Button.CLOCK)
        }

    def _read_packet(self, packet_id, data_bytes):
        """ Sends the sensor command with the provided packet id to the robot
            and reads the robots response.

        :param packet_id:
            The packet id of the desired packet
        :param data_bytes:
            The number of bytes the robot will respond with
        :return:
            The raw data that the robot responded with.
        """
        self._serial_conn.send_command(_SENSORS_OPCODE+" "+packet_id)
        return self._serial_conn.read_data(data_bytes)