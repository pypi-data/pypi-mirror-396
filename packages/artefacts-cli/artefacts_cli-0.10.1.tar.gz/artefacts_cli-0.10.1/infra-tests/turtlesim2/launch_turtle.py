import unittest
import sys
import os

import pytest
import launch_testing
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


@pytest.mark.launch_test
def generate_test_description():
    proc_env = os.environ.copy()
    proc_env["PYTHONUNBUFFERED"] = "1"
    # TODO switch to package
    sample_process = ExecuteProcess(
        cmd=[sys.executable, "turtlesim2/sample_node.py"],
        output="log",
        env=proc_env,
    )

    rosbag_cmd = ["ros2", "bag", "record", "-a"]
    bag_recorder = ExecuteProcess(cmd=rosbag_cmd, output="screen", env=proc_env)
    return LaunchDescription(
        [
            Node(
                package="turtlesim",
                executable="turtlesim_node",
            ),
            bag_recorder,
            sample_process,
            launch_testing.actions.ReadyToTest(),
        ]
    ), {"sample_process": sample_process}


class TestTurtle(unittest.TestCase):
    def test_tank_reach_target(self, proc_output, sample_process):
        # This will match stdout from test_process.
        proc_output.assertWaitFor("Turtle nearing right edge", timeout=5)
