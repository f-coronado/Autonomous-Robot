##
# @file imu02.py 
# @brief IMU testing
#
# @details
# This script initializes GPIO pins, accepts a sequence of movement commands
# from the user and executes them using the locomotion and localization classes.
# Encoder feedback is used to estimate robot position and heading.
#
# Supported commands:
# -f move forward
# -b move backward
# -r turn right
# -l turn left
#
# robot trajectory is plotted using matplotlib after execution
#
# @author
# Fabrizzio Coronado
# 
# @date
# 2026
##

import serial
import RPi.GPIO as GPIO
from libraries.localization import Localization
from libraries.locomotion import Locomotion
import matplotlib.pyplot as plt

##
# @brief Initializes Raspberry Pi GPIO pins.
#
# @details
# Configures GPIO pins 31, 33, 35, and 37 as output pins.
# These pins are used to control the motor driver inputs.
#
# @note Uses BOARD pin numbering scheme.
#
# @return None
##
def init():

        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT) # IN1
        gpio.setup(33, gpio.OUT) # IN2
        gpio.setup(35, gpio.OUT) # IN3
        gpio.setup(37, gpio.OUT) # IN4

##
# @brief Main execution function.
#
# @details
# Performs the following operations:
# 1. Instantiates Locomotion and Localization objects.
# 2. Prompts the user for a sequence of motion commands.
# 3. Executes each command using encoder feedback for motion control.
# 4. Updates estimated position and heading.
# 5. Plots the estimated trajectory.
#
# Encoder thresholds:
# - max_count: encoder ticks required for 0.5 meter movement
# - turn_count: encoder ticks required for ~45 degree turn
#
# @return None
##
def main():

	##
	# create control and localization objects
	##
	locomotion = Locomotion()
	localization = Localization()

	cnt = 0
	##
	# Prompt user for motion sequence
	##
	sequence = input("Enter a sequence of commands separated by spaces. \nAvailable commands are: f, b, r, l:\n").split()
	print("the sequence of commands entered was: \n", sequence)

	##
	# Motion parameters
	##
	max_count = 2343 		# ticks needed for half a meter
	turn_count = 2100 		# ticks needed for about 45 degrees
	duty = 20 				# PWM duty cycle for linear motion
	duty_turn = 100			# PWM duty cycle for turning
	
	enc_distances = []
	total_distance = 0

	##
	# Execute each command in the sequence
	##
	for command in sequence:
		print("\ncommand: ", command)
		cntrBR = 0
		cntrFL = 0
		localization.reset_tick_count()

		##
		# Turning commands (r / l)
		##
		if command == 'r' or command == 'l':
			while cntrBR <= turn_count and cntrFL <= turn_count:
				if command == 'l':
					locomotion.drive([0, 0, 0, duty_turn])
					#print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)

				elif command == 'r':
					locomotion.drive([duty_turn, 0, 0, 0])
					#print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)

				cntrBR, cntrFL = localization.get_tick_count()
				if cntrBR and cntrFL >= turn_count:
					theta = .78539 # 90 degrees in radians
					localization.update_enc_angle(theta, command)
					locomotion.gameover()
					print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)
					avg_tick = (cntrBR + cntrFL) / 2
					print("current angle: ", localization.angle)
					cntrBR, cntrFL = localization.reset_tick_count()
					break

		##
		# Linear motion commands (f / b)
		##
		if command == 'f' or command == 'b':
			while cntrBR <= max_count and cntrFL <= max_count:

				if command == 'f':
					locomotion.drive([duty, 0, 0, duty])
				elif command == 'b':
					locomotion.drive([0, duty, duty, 0])

				cntrBR, cntrFL = localization.get_tick_count()
				if cntrBR and cntrFL >= max_count:
					locomotion.gameover()
					avg_tick = (cntrBR + cntrFL) / 2
					print("avg_tick: ", avg_tick)

					if command == 'f' or command == 'b':
						if command == 'f':
							distance = localization.tick_2_distance(avg_tick)
						if command == 'b':
							distance = -localization.tick_2_distance(avg_tick)
						print("current distance travelled: ", distance)
						enc_distances.append(distance)
						localization.update_enc_angle(0, command)
						print("current angle is at: ", localization.angle)
						localization.update_enc_pos(distance)
						print("current position is at: ", localization.x, localization.y)
						counterBR, counterFL = localization.reset_tick_count()
						total_distance += distance
						print("total distance is at: ", total_distance)

					break
	##
	# plot final trajectory
	##
	print("\ncommand sequence: ", sequence)
	print("distances travelled: ", enc_distances)
	positions =list(zip(localization.x_pos, localization.y_pos))
	print("positions: ", positions)
	plt.plot(localization.x_pos, localization.y_pos)
	plt.title('plot of encoder positions')
	plt.xlabel('x [meters]')
	plt.ylabel('y [meters]')
	plt.grid(True)
	plt.show()

if __name__ == "__main__":
	main()
