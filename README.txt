CSCE 274
Project 1
Boyd Compton
Timothy Senn
Jose Tadeo

robot_inf.py:
	Robot_inf.py is tailored specifically to the iRobot Create 2, and contains the constants for the robot to use, as well as the interface to be used. This file is called by "robot_inf._robot" to set to passive and request data. Within the constants, State, Button, and Drive are all set up. "State" is made for the different states of the robot and each state command is necessary to enter the state. These were set up as integer values such as "7" for reset and "128" for passive. "Button" was made for the different buttons on the iRobot Create 2, and each button was set to the corresponding bit in the packet. "Drive" represents the cases for the radius of the robot's drive command and contains bounds for both velocity and radius.
	The interface section of this file contains the initialization and some commands for the robot. Change_state changes the robot to whichever state the user chooses as long as it is a different state and not state.START. Drive calls the drive command for the robot and is only available in the SAFE or FULL states. Also, this command supports integer or hex values. Read_button and read_buttons read the buttons on the iRobot Create 2. For this to happen, a command such as "robot_inf.Button.CLEAN" must be called in the main method. Finally, read_packet simply sends the sensor command with the packet id to the robot and gets the robot's response.

serial_inf.py:
	Serial_inf.py is the actual interface for the iRobot Create 2. The exit, connect, close, send_command, and read_data functions are all contained in this file. "Exit" simply ensures that the connection is closed. "Connect" creates a serial connection with the timeout and buad rate that the user specifies. "Close" simply closes an open connection. "Send_command" pushes commands to the serial connection. "Read_data" is what retrieves the data on the serial connection, as long as there is a set timeout. This is called with the number of bytes to be read.
	Finally, this file also contains a helper function for the serial connection, list_serial_ports. This function creates a list of all serial ports that are connected on the system. These are specified ports such as "/dev/ttyUSB0" or "COM" on Windows systems, typically "COM3" or "COM4".

square.py:
	Square.py is the main program for project 1, and it contains the main controls for the iRobot Create 2. This file contains commands for initialization, run, stop, wait, and the robot controller. When first initialized, the robot is set up and stop is set to false. "Run" simply sets up the number of turns to make, the length of said turns, velocity, and time taken. For ease of conversion, values that contain length are stored as mm and mm/s, respectively. "Stop" simply sets the flag to stop the thread to True. This will cause the thread to exit safely. "Wait" divides the time in between commands into smaller intervals so that the robot can check for the "stop" condition while already running an action. The robot controller listens for the button press and allow for the starting and stopping of actions.
	The main file can only be run by having both robot_inf.py and serial_inf.py in the same directory. Pyserial is also needed. Simply run square.py.







