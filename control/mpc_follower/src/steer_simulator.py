#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import math
from autoware_vehicle_msgs.msg import VehicleCommand
from autoware_vehicle_msgs.msg import Steering


def wait_for_param(key):
    while not rospy.has_param(key):
        rospy.loginfo("waiting for parameter: {}".format(key))
        rospy.sleep(1.0)


class SimulateSteer():

    def __init__(self):
        self.current_steer = None
        self.current_time = None
        self.command_array = []

        input_delay_param_name = rospy.get_param("~mpc_input_delay_param")
        steer_tau_param_name = rospy.get_param("~mpc_steer_tau_param")

        wait_for_param(input_delay_param_name)
        wait_for_param(steer_tau_param_name)
        self.delay_compensation_time = rospy.get_param(input_delay_param_name)
        self.steer_tau = rospy.get_param(steer_tau_param_name)

        # steering command from Autoware
        self.subcmd = rospy.Subscriber(
            "input/vehicle_cmd", VehicleCommand, self.CallBackVehicleCmd, queue_size=1, tcp_nodelay=True)

        # current steering from vehicle
        self.substatus = rospy.Subscriber(
            "input/steering", Steering, self.CallBackSteering, queue_size=1, tcp_nodelay=True)

        # simulated steering
        self.pubstatus = rospy.Publisher(
            "output/predicted_steering", Steering, queue_size=1)

    def CallBackVehicleCmd(self, cmdmsg):
        steercmd = cmdmsg.control.steering_angle
        self.StackCurrentSteer(steercmd, rospy.Time.now().to_sec())
        self.CalcCurrentSteer()

    def CallBackSteering(self, statusmsg):
        steer = statusmsg.data
        if self.current_time is None:
            self.current_steer = steer
            self.current_time = rospy.Time.now().to_sec()

    def StackCurrentSteer(self, steercmd, current_time):
        self.command_array.append(
            [steercmd, current_time+self.delay_compensation_time])

        while(True):  # remove unused command
            if len(self.command_array) < 2 or self.current_time is None:
                break
            # oldest_cmd = self.command_array[0]
            next_oldest_cmd = self.command_array[1]
            cmd_time = next_oldest_cmd[1]
            if self.current_time > cmd_time:
                self.command_array.pop(0)  # pop oldest_cmd
            else:
                break

    def CalcCurrentSteer(self):
        if self.current_time is None:
            # no ready
            return False

        target_time = rospy.Time.now().to_sec()
        if target_time < self.current_time:
            # error case
            return False

        # calculation
        mpc_calc_time = self.current_time

        array_oldest_time = self.command_array[0][1]
        if mpc_calc_time < array_oldest_time:
            #not ready
            self.current_time = None

        steer = self.current_steer
        for i in range(0, len(self.command_array)-1):
            command_steer = self.command_array[i][0]
            next_command_time = self.command_array[i][1]
            if next_command_time < mpc_calc_time:
                pass
            else:
                if next_command_time > target_time:
                    steer = self.OneStepForwardSteer(
                        steer, command_steer, mpc_calc_time, target_time)
                    mpc_calc_time = target_time
                    break  # finish calculation
                else:
                    steer = self.OneStepForwardSteer(
                        steer, command_steer, mpc_calc_time, next_command_time)
                    mpc_calc_time = next_command_time

        self.UpdateState(steer, target_time)
        self.PublishSteer()

    def OneStepForwardSteer(self, steer, cmd_steer, current_time, target_time):
        diff_time = target_time - current_time
        if diff_time < 0:
            print("Error")
            return steer
        else:
            # next_steer = steer + (cmd_steer - steer) * (diff_time / self.steer_tau) #1d approximation
            next_steer = steer + \
                (cmd_steer - steer) * \
                (1 - math.exp(-diff_time/self.steer_tau))  # exponential
            return next_steer

    def UpdateState(self, steer, steer_time):
        self.current_steer = steer
        self.current_time = steer_time

    def PublishSteer(self):
        steermsg = Steering()
        steermsg.header.stamp = rospy.Time.now()  # self.current_time?
        steermsg.data = self.current_steer
        self.pubstatus.publish(steermsg)


def main():
    rospy.init_node("mpc_steer_simulator")
    SimulateSteer()
    rospy.spin()


if __name__ == "__main__":
    main()
