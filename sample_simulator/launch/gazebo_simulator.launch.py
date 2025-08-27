import os.path as osp
from typing import Tuple

from launch import LaunchDescription, LaunchContext
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, OpaqueFunction
)
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

from sample_simulator.convert_urdf_to_sdf import convert_urdf_to_sdf
import shutil

def get_gz_model(context):
    vehicle_name = LaunchConfiguration("vehicle_name").perform(context)
    urdf_path = osp.join(get_package_share_directory("sample_vehicle"), "xacro", vehicle_name + ".urdf")
    sdf_path = osp.join(get_package_share_directory("sample_simulator"), "models", "ai_mobility_1", "model.sdf")
    convert_urdf_to_sdf(urdf_path, sdf_path)

    reference_path = osp.join(get_package_share_directory("sample_vehicle"),"xacro","meshes")
    create_path = osp.join(get_package_share_directory("sample_simulator"),"models", "ai_mobility_1", "meshes")
    if not osp.exists(create_path):
        shutil.copytree(reference_path, create_path)

    else:
        print("exist meshes file")


def generate_launch_description():
    VEHICLE_NAME = "ai_mobility_1"
    launch_args = (
        DeclareLaunchArgument(
            "world_name",
            default_value="shihou_course",
            description="World Name",
        ),
        DeclareLaunchArgument(
            "vehicle_name",
            default_value="ai_mobility_1",
            description="Vehicle Name",
        ),
        DeclareLaunchArgument(
            "world_path",
            default_value=[
                osp.join(get_package_share_directory("sample_simulator"), "worlds", ""),
                LaunchConfiguration("world_name"), ".model"
            ],
            description="Path to world file.",
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="If true, use simulation (Gazebo) clock",
        ),
    )

    tf_static_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            osp.join(get_package_share_directory("sample_vehicle"),
                     "launch/vehicle_tf_broadcaster.launch.py"),
        ),
        launch_arguments={
            "vehicle_name": VEHICLE_NAME,
            "use_sim_time": LaunchConfiguration("use_sim_time"),
        }.items(),
    )

    # ExecuteProcess(
    # cmd=["export", "GAZEBO_MODEL_PATH=$(ros2 pkg prefix vehicle)/share/vehicle/xacro"],
    # shell=True),
    gzserver = IncludeLaunchDescription(   
        PythonLaunchDescriptionSource(
            osp.join(get_package_share_directory("gazebo_ros"),
                     "launch/gzserver.launch.py"),
        ),
        launch_arguments={
            "world": LaunchConfiguration("world_path"),
            "world_name": LaunchConfiguration("world_name"),
        }.items(),
    )

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            osp.join(get_package_share_directory("gazebo_ros"),
                     "launch/gzclient.launch.py"),
        ),
    )
    set_use_sim_time = ExecuteProcess(
        cmd=['ros2', 'param', 'set', '/gazebo',
             'use_sim_time', LaunchConfiguration("use_sim_time")],
        output='screen'
    )
    generate_model = OpaqueFunction(function=get_gz_model)
    return LaunchDescription([
        *launch_args,
        tf_static_publisher,
        generate_model,
        gzserver,
        gzclient,
        set_use_sim_time,
    ])
