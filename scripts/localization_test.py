##
# @file localization_test.py
# @brief Autonomous navigation script for distance-based locomotion.
# @details This script integrates the Locomotion and Localization libraries to 
# execute a simple "Drive-to-Distance" mission using encoder feedback. Once 
# the robot travelled 1 meter using encoder for measuring, it was compared with
# the actual distance traveled.
# @author Fabrizzio
# @date 2026-02-16

from libraries.localization import Localization
from libraries.locomotion import Locomotion
import time

def main():
	## initialize locomotion object
	loco = Locomotion()
	print("intialized locomotion")
	# allow 5s to pass so hardware properly initializes
	time.sleep(5)
	## initialize localization object
	local = Localization()
	print("initialized localization")


	loco.drive([loco.duty, 0, 0, loco.duty])
	print("started driving")
	time.sleep(5)

	while True:


		print("counterFL: ", local.counterFL, "counterBR: ", local.counterBR)

		## convert raw encoder ticks to meters using library-defined wheel geometry 
		distance = round(local.tick_2_distance(local.counterFL), 2)
		print("distance: ", distance)

		## If the distnace reaches 1 meter, stop the motors
		if distance >= 1:
			print("traveled 1 meter")
			loco.drive([0, 0, 0, 0])
			break



if __name__ == "__main__":
	main()
