# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/components/bootloader/subproject

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM_CAM/build/bootloader

# Utility rule file for size.

# Include the progress variables for this target.
include CMakeFiles/size.dir/progress.make

CMakeFiles/size: bootloader.elf
	/home/mkuczyns/.espressif/python_env/idf4.2_py3.8_env/bin/python /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/tools/idf_size.py --target esp32 /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM_CAM/build/bootloader/bootloader.map

size: CMakeFiles/size
size: CMakeFiles/size.dir/build.make

.PHONY : size

# Rule to build all files generated by this target.
CMakeFiles/size.dir/build: size

.PHONY : CMakeFiles/size.dir/build

CMakeFiles/size.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/size.dir/cmake_clean.cmake
.PHONY : CMakeFiles/size.dir/clean

CMakeFiles/size.dir/depend:
	cd /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM_CAM/build/bootloader && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/components/bootloader/subproject /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/components/bootloader/subproject /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM_CAM/build/bootloader /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM_CAM/build/bootloader /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM_CAM/build/bootloader/CMakeFiles/size.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/size.dir/depend

