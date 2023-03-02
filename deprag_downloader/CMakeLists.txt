cmake_minimum_required(VERSION 3.0.2)
project(deprag_downloader)

## Compile as C++11, supported in ROS Kinetic and newer
add_compile_options(-std=c++17)

find_package(catkin REQUIRED COMPONENTS
  rospy
  deprag_msgs
)

catkin_python_setup()

catkin_package(
  CATKIN_DEPENDS rospy deprag_msgs
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)
