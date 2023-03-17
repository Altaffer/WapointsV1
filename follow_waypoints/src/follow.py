#!/usr/bin/env python
import math
import rospy
import csv
import utm
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import Twist

"""""""""
CONSTANTS
"""""""""
# gain constants
yaw_rho = 0
x_rho = 0
# position constants
yaw_offset = 1
x_offset = 1
short_dist = 5 	# 5 meters
enough = 0.0025	# 1 inch
# speed constants
max_v = 3		# 3mph

# waypoints from scv
wp=[]
wp_trigger = 0		# trigger flag for next waypoint
pub = None

def yaw_rate(msg):
	# calculating yaw change 
	yaw = math.atan2((wp[wp_trigger][0]-msg[0])/(wp[wp_trigger][1]-msg[1])) * (yaw_rho+yaw_offset)
	return yaw

def x_rate(msg):
	# calculating the distance to travel
	x = math.sqrt((wp[wp_trigger][0]-msg[0])^2 + (wp[wp_trigger][1]-msg[1])^2) *(x_rho+x_offset)
	if(x >= short_dist):
		return max_v
	if ((x < short_dist) and (x > enough)):
		return x
	if (x <= enough):
		wp_trigger += 1
		return 0

def callback(msg):
	t = Twist()
	t.angular.x = yaw_rate(msg)
	t.linear.x = x_rate(msg)

	rospy.publish("controller", t)

def main(msg):
	rospy.init_node("")
	pub = rospy.Publisher("controller", Twist)

	# waypoints are converted to utm from csv and placed in list
	with open('wapoint_list.csv', newline='') as f:
		reader = csv.reader(f)
		data = reader.split(',')
		u = utm.from_latlon(float(data[0], float(data[1])))
		wp.append(u[:2])

	rospy.Subscriber("/current_pose", PoseWithCovarianceStamped, callback)

	rospy.spin()
