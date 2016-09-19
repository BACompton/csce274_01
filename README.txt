CSCE 274 Section 1 
Project 01
Group 3: Boyd Compton, Timothy Senn, & Jose Tadeo

-------------
- square.py -
-------------
    Dependences:
        - pySerial
        - robot_inf.py
        - serial_inf.py
        
        PySerial will need to be installed on the system while robot_inf.py and
        serial_inf.py just need to be placed in the same directory as square.py.
        
    Description:
        Square.py is the main program for project 1. This program was designed
        with the iRobot Create 2 in mind. The program will begin by initializing
        the robot's state to PASSIVE mode and then SAFE mode. After this point, 
        the robot will respond to the clean/power button being pressed.
        
        When the clean/power button is pressed and the robot is stopped, it will
        begin to move clockwise along a square with 250 mm sides by spawning
        a daemon to control the actuators. This daemon will track the robot's 
        progress by keeping track of the number of turns left to make. It will
        also calculate the time in between actuator commands by using dead
        reckoning. Alternatively, if the robot is moving when the button is 
        pressed, it will stop by stopping the daemon controlling the actuators 
        in a safe manner.
    
    Execution:
        While in the directory with square.py issue the command:
            
            python square.py
        
        This will start the main program. Once the text 'Listening for press' is
        printed to the console, you can start the robot by pressing the
        clean/power button. Alternatively, the LED around the clean/power button
        will turn off when it is ready for input. Stop the robot by pressing the
        clean/power button again. To stop the execution of square.py, first, 
        ensure the robot is stopped. Next, issue a keyboard interrupt(CTRL + C) 
        to the console.
    
    Additional Help:
        For additional help, import the square.py module and issue the python
        help function. Example:
            
            import square
            help(square)
            
----------------
- robot_inf.py -
----------------
    Dependences:
        - pySerial
        - serial_inf.py
        
        PySerial will need to be installed on the system while serial_inf.py 
        just needs to be placed in the same directory as robot_inf.py.
       
    Description:
        Robot_inf.py is an interface tailored specifically to the iRobot 
        Create 2. In doing so this module also contains specification for its OI
        such as:
            - Default Buad rate
            - Period for the sensor's update
            - States (Ex: START, PASSIVE, SAFE, RESET, STOP) 
            - Buttons (Ex: CLEAN, DOCK)
            - Special radii for the drive command (Ex: STRAIGHT, TURN_CW)
        
        On top of these constants, the interfaces contains methods that will:
            - Drive the robot using velocity and radius
            - Read individual button's or all buttons' values
            - Change the robot's state
        
    Implementation:
        To use any of the constants available in the robot_inf.py module,
        reference them like so:
            
            robot_inf.<constant>
        
        For example, the clean button would be referenced like so:
        
            robot_inf.Button.CLEAN
        
        
        To connect to a iRobot Create 2, instantiate an instance of the
        Robot class like so:
            
            create2 = robot_inf.Robot(serial_port)
        
        After creating the object, you have access to the following method:
            - Change State (Ex: create2.change_state(robot_inf.State.SAFE))
                NOTE: * Only the values found in 'robot_inf.State' should be 
                            used as arguments.
                            
            - Drive (Ex: create2.drive(velocity, radius)
                NOTE: * This method will only work in SAFE or FULL mode.    
                      * That velocity is in mm/s and radius is in mm.
                      * Velocity ranges from -500 mm/s to 500 mm/s while radius
                            ranges from -2000 mm to 2000 mm.
                      * The special codes found in 'robot_inf.Drive' are values
                            for the radius argument.
                            
            - Read button (Ex: create2.read_button(robot_inf.Buttons.CLEAN))
                NOTE: * Only the values found in 'robot_inf.Button' should be 
                            used as arguments.
                            
            - Read buttons (Ex: btns = create2.read_buttons())
                NOTE: * This will return a dictionary that can be addressed with
                            values from 'robot_inf.Button' 
                            (Ex: btns[robot_inf.Buttons.CLEAN]).
    
    Additional Help:
        For additional help, import the robot_inf.py module and issue the 
        python help function. Example:
            
            import robot_inf
            help(robot_inf)

-----------------
- serial_inf.py -
-----------------
    Dependences:
        - pySerial
        
        PySerial will need to be installed on the system.
    
    Description:
        Serial_inf.py is a generic interface for a serial connection. This
        interface will:
            - Establish a serial connection
            - Close a serial connection
            - Send space delimited command as encoded ASCII command
            - Read raw data
            - List available serial ports
        
        A serial connection can specify its serial port, buad rate, and read
        time out. However, the read time out will default to one second if it is
        not specified when establishing a connection. If you want to have no
        read time out, specify the time out as 'None'.
        
        When reading data with a read time out, the number of bytes returned 
        can be less than the request number of bytes!
        
    Implementation:
        To use serial_inf.py, begin by importing:
        
            import serial_inf
            
        If this import fails, ensure that serial_inf.py is within the current
        working directory. After this you can get the available list of serial
        ports by issuing the follow function:
        
            ports = serial_inf.list_serial_ports()
            
        This will return an array of strings that specify the available serial
        ports. To create a new serial connection, instantiate an instance of the
        SerialConn class like so:
            
            conn = serial_inf.SerialConn(ports[0], buadrate, timeout=timeout)
            
        Do note that the buadrate, and timeout are variables declared prior to
        this call. Buadrate is an integer while timeout is a float. After this
        point you can do the following:
            - Send commands (Ex: conn.send_command('142 18'))
            - Read data (Ex: conn.read_data(num_of_bytes))
            - Close the connection (Ex: conn.close())
                NOTE: * The connection will automatically close when the object 
                            gets destroyed.
        
    Additional Help:
        For additional help, import the serial_inf.py module and issue the 
        python help function. Example:
            
            import serial_inf
            help(serial_inf)