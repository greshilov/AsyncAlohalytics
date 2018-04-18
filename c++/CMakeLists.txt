cmake_minimum_required(VERSION 3.2)

project(pyalohareciever C CXX)

set(CMAKE_CXX_STANDART 11)
set(CMAKE_CXX_FLAGS "-std=c++11")

set(_Boost_PYTHON3_HEADERS "boost/python.hpp")
find_package(Boost 1.58 REQUIRED COMPONENTS python3)
find_package(PythonLibs ${PYTHON_VERSION} REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${PYTHON_INCLUDE_DIRS})

get_filename_component(ALOHA_ROOT . ABSOLUTE)

include_directories("${ALOHA_ROOT}")

set(
  SRC
  ${ALOHA_ROOT}/3party/Alohalytics/src/event_base.h
  reciever.cpp
)

add_library(${PROJECT_NAME} SHARED ${SRC})

target_link_libraries(${PROJECT_NAME} ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
set_target_properties(${PROJECT_NAME} PROPERTIES PREFIX "" SUFFIX ".so")
