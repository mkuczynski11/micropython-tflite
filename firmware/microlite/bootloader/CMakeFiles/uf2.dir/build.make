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
CMAKE_BINARY_DIR = /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader

# Utility rule file for uf2.

# Include the progress variables for this target.
include CMakeFiles/uf2.dir/progress.make

CMakeFiles/uf2: /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/components/bootloader/subproject/bootloader
	/home/mkuczyns/.espressif/python_env/idf4.3_py3.8_env/bin/python /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/tools/mkuf2.py write -o /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader/uf2.bin --json /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader/flasher_args.json --chip-id 0x1c5f21b0

uf2: CMakeFiles/uf2
uf2: CMakeFiles/uf2.dir/build.make

.PHONY : uf2

# Rule to build all files generated by this target.
CMakeFiles/uf2.dir/build: uf2

.PHONY : CMakeFiles/uf2.dir/build

CMakeFiles/uf2.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/uf2.dir/cmake_clean.cmake
.PHONY : CMakeFiles/uf2.dir/clean

CMakeFiles/uf2.dir/depend:
	cd /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/components/bootloader/subproject /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/esp-idf/components/bootloader/subproject /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader /home/mkuczyns/desktop/micropython_drivers/micropython-tflite/tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM/build/bootloader/CMakeFiles/uf2.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/uf2.dir/depend

