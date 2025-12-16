#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose as TurtlePose


class TestListener(Node):
    def __init__(self):
        super().__init__("artefacts_listener")
        self.turtle_pose_sub = self.create_subscription(
            TurtlePose, "/turtle1/pose", self.gt_callback, 10
        )
        self.velocity_publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.gt_pose = None
        self.twist = Twist()

    def gt_callback(self, msg):
        vel_msg = Twist()
        vel_msg.linear.x = 1.0
        self.velocity_publisher.publish(vel_msg)
        self.gt_pose = msg
        if self.gt_pose.x > 3:
            self.get_logger().info("Turtle nearing right edge")


def main():
    rclpy.init()
    node = TestListener()
    try:
        while True:
            rclpy.spin_once(node, timeout_sec=1)
        rclpy.shutdown()
    except KeyboardInterrupt:
        rclpy.shutdown()


if __name__ == "__main__":
    main()
