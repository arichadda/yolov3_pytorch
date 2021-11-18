import os
import rospy
import numpy as np
from geometry_msgs.msg import Vector3Stamped
from rospy.rostime import Time
FREQUENCY = 10

class AnglePublisher():
    def __init__(self):
        self.path = './object_angle.txt'
        self.angle_pub = rospy.Publisher('object_angle', Vector3Stamped, queue_size=1)

    def pub(self):
        rate = rospy.Rate(FREQUENCY)
        while not rospy.is_shutdown():
            if os.path.exists(self.path):
                with open(self.path, 'r') as f:
                    line = f.readline()
                    line = line.split(' ')
                    if len(line) > 0:
                        msg = Vector3Stamped()
                        msg.vector.x = np.float64(line[0])
                        msg.header.stamp = Time(int(line[1]), int(line[2]))

                        print(msg.header.stamp)
                        self.angle_pub.publish(msg)
                        print("publishing")

    def destroy(self):
        if os.path.exists(self.path):
            os.remove(self.path)


if __name__ == "__main__":
    rospy.init_node('angle_publisher')
    angle_publisher = AnglePublisher()
    rospy.sleep(2)
    # rospy.on_shutdown(angle_publisher.destroy)
    angle_publisher.pub()
