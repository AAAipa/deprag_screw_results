cmake_minimum_required(VERSION 3.0.2)
project(deprag_msgs)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

find_package(catkin REQUIRED COMPONENTS
  message_generation
  message_runtime
  std_msgs
)

add_message_files(
  FILES
    screwing.msg
)

add_service_files(
  FILES
    download_request.srv
)

generate_messages(
  DEPENDENCIES
    std_msgs
)

catkin_package()

include_directories(${catkin_INCLUDE_DIRS})
