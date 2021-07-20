#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # Set to False to start only Rviz2 when the ZED node is started by other launch files 
    # For example when you run this script on a remote console to monitor the robot status.
    start_zed_node = True

    # Camera model
    # use:
    #  - 'zed' for "ZED" camera
    #  - 'zedm' for "ZED mini" camera
    #  - 'zed2' for "ZED2" camera
    #  - 'zed2i' for "ZED2i" camera
    camera_model = 'zed'

    # Camera name. Can be different from camera model, used to distinguish camera in multi-camera systems
    camera_name = 'zed'

    # Rviz2 Configurations to be loaded by ZED Node
    config_rviz2 = os.path.join(
        get_package_share_directory('zed_display_rviz2'),
        'rviz2',
        camera_model + '.rviz'
    )

    # Set LOG format
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '{time} [{name}] [{severity}] {message}'

    # Rviz2 node
    rviz2_node = Node(
        package='rviz2',
        namespace=camera_name,
        executable='rviz2',
        name=camera_name+'_rviz2',
        output='screen',
        arguments=[["-d"], [config_rviz2]],
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()

    if start_zed_node:
        # Launch configuration variables (can be changed by CLI command)
        svo_path = LaunchConfiguration('svo_path')

        # Configuration variables
        node_name = 'zed_node'  # Zed Node name
        publish_urdf = 'true'  # Publish static frames from camera URDF
        # Robot base frame. Note: overrides the parameter `pos_tracking.base_frame` in `common.yaml`.
        base_frame = 'base_link'
        # Position X of the camera with respect to the base frame [m].
        cam_pos_x = '0.0'
        # Position Y of the camera with respect to the base frame [m].
        cam_pos_y = '0.0'
        # Position Z of the camera with respect to the base frame [m].
        cam_pos_z = '0.0'
        # Roll orientation of the camera with respect to the base frame [rad].
        cam_roll = '0.0'
        # Pitch orientation of the camera with respect to the base frame [rad].
        cam_pitch = '0.0'
        # Yaw orientation of the camera with respect to the base frame [rad].
        cam_yaw = '0.0'

        # ZED Configurations to be loaded by ZED Node
        config_common_path = os.path.join(
            get_package_share_directory('zed_wrapper'),
            'config',
            'common.yaml'
        )

        if(camera_model != 'zed'):
            config_camera_path = os.path.join(
                get_package_share_directory('zed_wrapper'),
                'config',
                camera_model + '.yaml'
            )
        else:
            config_camera_path = ''

        # URDF/xacro file to be loaded by the Robot State Publisher node
        xacro_path = os.path.join(
            get_package_share_directory('zed_wrapper'),
            'urdf', 'zed_descr.urdf.xacro'
        )

        # ZED Wrapper node
        zed_wrapper_launch = IncludeLaunchDescription(
            launch_description_source=PythonLaunchDescriptionSource([
                get_package_share_directory('zed_wrapper'),
                '/launch/include/zed_camera.launch.py'
            ]),
            launch_arguments={
                'camera_model': camera_model,
                'camera_name': camera_name,
                'node_name': node_name,
                'config_common_path': config_common_path,
                'config_camera_path': config_camera_path,
                'publish_urdf': publish_urdf,
                'xacro_path': xacro_path,
                'svo_path': svo_path,
                'base_frame': base_frame,
                'cam_pos_x': cam_pos_x,
                'cam_pos_y': cam_pos_y,
                'cam_pos_z': cam_pos_z,
                'cam_roll': cam_roll,
                'cam_pitch': cam_pitch,
                'cam_yaw': cam_yaw
            }.items()
        )

        declare_svo_path_cmd = DeclareLaunchArgument(
            'svo_path',
            default_value='',
            description='Path to an input SVO file. Note: overrides the parameter `general.svo_file` in `common.yaml`.')

        # Launch parameters
        ld.add_action(declare_svo_path_cmd)

        # Add nodes to LaunchDescription
        ld.add_action(zed_wrapper_launch)

    ld.add_action(rviz2_node)

    return ld
