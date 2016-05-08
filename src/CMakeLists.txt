cmake_minimum_required(VERSION 3.3)
project(VIC_Hime)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES
        main.cpp
        statics.cpp
        vic_hime.h vic_core.cpp)

add_executable(VIC_Hime ${SOURCE_FILES})

TARGET_LINK_LIBRARIES(VIC_Hime vic pthread m)