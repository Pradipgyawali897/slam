import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='esp32_cam_slam',
            executable='fetcher',
            name='fetcher_node',
            output='screen',
            parameters=[{'url': 'https://192.168.1.5:8080/video'}]
        ),
        Node(
            package='esp32_cam_slam',
            executable='processor',
            name='processor_node',
            output='screen'
        ),
        Node(
            package='esp32_cam_slam',
            executable='mapper',
            name='mapper_node',
            output='screen'
        )
    ])
