#!/usr/bin/python

import threading
import time

import serial_inf
import robot_inf

# =============================================================================
#                       Main program for project 1
# =============================================================================


class DriveControl(threading.Thread):
    """
        This performs the action sequence. In this case, it will move in a
        square with 250 mm.

        In more detail, this is where the low-level actuator controls are
        held. The robot will only respond to the actuator commands if it is
        in SAFE or FULL mode.
    """
    _robot = None
    _stop = None

    def __init__(self, robot):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._stop = False
        self._robot = robot

    def run(self):
        turns = 3               # The number of turns left to make.
        side_len = 250          # The length of the square in mm.
        vel = 50                # Robot's velocity in mm/s.
        turn_time = 3.20        # The time it take to turn 90 degrees in seconds

        while not self._stop and turns >= 0:
            # Drive forward
            self._robot.drive(vel, robot_inf.Drive.STRAIGHT)
            # Time to run the command
            if self._wait(abs(side_len/vel), robot_inf.SENSOR_UPDATE_WAIT):
                break

            # Turn 90 degrees
            self._robot.drive(vel, robot_inf.Drive.TURN_CW)
            # Time it takes to turn
            if self._wait(turn_time, robot_inf.SENSOR_UPDATE_WAIT):
                break
            turns -= 1

        # Stops robot
        self._robot.drive(0, 0)

    def stop(self):
        """
            Sets the flag to stop the thread to True. The thread will
            not immediately stop. Instead, the thread will exit safely.
        """
        self._stop = True

    def _wait(self, wait_time, interval):
        """ Internal method that divides the time in between actuator
            commands into small intervals. This enables the ability
            to check for the stopping condition while running an action.

        :param wait_time:
            The total amount of time to wait
        :param interval:
            The amount of time for a single interval.
        :return:
            True if the stopping condition was detected, otherwise false.
        """
        time_left = wait_time

        while time_left > 0:
            # Tell the caller it needs to stop
            if self._stop:
                return True

            # Wait another time interval
            interval_time = interval
            if interval_time > time_left:
                interval_time = time_left
            time_left -= interval_time
            time.sleep(interval_time)
        return False


def robot_controller():
    """
        This listens for the button press. If the clean button is pressed,
        this will decide if the robot should stop or start its action sequence.

        In this case the action sequence is to make a square with 250 mm sides.
        The robot will start if the action sequence is not running. The robot
        will stop if the action sequence is running.
    """

    port_list = serial_inf.list_serial_ports()

    if len(port_list) > 1:
        print "Requires a serial connection."
        return -1

    # The State space for the robot is the constants defined in
    # robot_inf.State (change to is thread running)

    robot = robot_inf.Robot(port_list[0])     # Serial connection to robot
    robot.change_state(robot_inf.State.SAFE)
    print "Connected to robot"

    act_control = None                  # Low-level actuator control
    release = True

    print "Listening for press"
    while True:
        # High-Level State Action
        if robot.read_button(robot_inf.Button.CLEAN):
            # Only allows the initial press perform an action.
            if not release:
                continue

            # Start Square
            release = False
            if act_control is None or not act_control.isAlive():
                act_control = DriveControl(robot)
                act_control.start()

            # Stop Driving
            else:
                act_control.stop()
                act_control = None
        else:
            release = True

        # Clocks while loop to the update rate of the iRobot Create 2.
        time.sleep(robot_inf.SENSOR_UPDATE_WAIT)
    print "Stopping Listening"

if __name__ == '__main__':
    robot_controller()