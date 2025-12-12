cmake_minimum_required(VERSION 3.15)
project(languageRecognizer LANGUAGES CXX)

# --- C++ Standard ---
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python3 COMPONENTS Interpreter Development)

find_package(pybind11 REQUIRED)
pybind11_add_module(simpleLanguageRecognizer pyLanguageRecognizer.cpp LanguageRecognizer.cpp)
#add_subdirectory(external/pybind11)

#find_package(TBB REQUIRED)
#target_link_libraries(simpleLanguageRecognizer PRIVATE TBB::tbb)

# --- Python Integration ---
# Find the interpreter first to get its exact version.
# scikit-build-core ensures this finds the Python that's running the build.

# Now, perform an EXACT search for the development components of that specific version.
# This is more robust in complex environments like manylinux containers.

# --- Platform-Specific Compiler and Linker Options ---
if(MSVC)
    # --- Windows (MSVC) Specific Configuration ---

    # Set the generator platform to x64 for Visual Studio.
    # This setting is specific to the MSVC generator and has no effect on Linux.
    #set(CMAKE_GENERATOR_PLATFORM x64)
	if (CMAKE_GENERATOR MATCHES "Visual Studio")
        set(CMAKE_GENERATOR_PLATFORM x64)
    endif()

    # Set C++ exception handling model and MSVC runtime library.
    target_compile_options(simpleLanguageRecognizer PRIVATE /EHsc)
    set_property(TARGET simpleLanguageRecognizer PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:DebugDLL>")

    # Add specific architecture optimization flags (e.g., AVX2 support for MSVC)
    target_compile_options(simpleLanguageRecognizer PRIVATE /arch:AVX2)
elseif(APPLE)
	set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64")
    set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0") # Use macOS 11.0 (Big Sur) as minimum for arm64

    # 2. Base Options (Applies to all non-MSVC)
    target_compile_options(simpleLanguageRecognizer PRIVATE -fPIC)
    target_compile_options(simpleLanguageRecognizer PRIVATE -Wall -Wextra)
    target_compile_options(simpleLanguageRecognizer PRIVATE $<$<CONFIG:Release>:-O3 -DNDEBUG>)
    target_compile_options(simpleLanguageRecognizer PRIVATE $<$<CONFIG:Debug>:-g>)

    # 3. Architecture-Specific Optimizations
    # We must use -Xarch_ to pass flags only to a specific architecture's compile step.
    # This adds -mavx2 *only* for the x86_64 slice of the universal binary.
    message(STATUS "Enabling -mavx2 for x86_64 slice of universal2 build.")
    target_compile_options(simpleLanguageRecognizer PRIVATE -Xarch_x86_64 -mavx2)
else()
    # --- Linux (GCC/Clang) Specific Configuration ---

    # 1. Base Options (Applies to all non-MSVC)
    target_compile_options(simpleLanguageRecognizer PRIVATE -fPIC)
    target_compile_options(simpleLanguageRecognizer PRIVATE -Wall -Wextra)
    target_compile_options(simpleLanguageRecognizer PRIVATE $<$<CONFIG:Release>:-O3 -DNDEBUG>)
    target_compile_options(simpleLanguageRecognizer PRIVATE $<$<CONFIG:Debug>:-g>)

    # 2. Architecture-Specific Optimizations (Conditional Check)
    # Check if the system is x86 or x64 (where AVX2 is supported).
    if (CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|amd64")
        message(STATUS "Enabling -mavx2 for x86/x64 architecture.")
        target_compile_options(simpleLanguageRecognizer PRIVATE PRIVATE -mavx2)
    else()
        message(STATUS "Skipping -mavx2 flag for non-x86 architecture (${CMAKE_SYSTEM_PROCESSOR}).")
        # ARM/AARCH64 (Raspberry Pi), PowerPC, etc. will fall here.
    endif()
endif()

# --- Output Properties for Python Module ---
# Ensure the output file has the proper extension and no "lib" prefix.
set_target_properties(simpleLanguageRecognizer PROPERTIES PREFIX "")
if(WIN32)
    set_target_properties(simpleLanguageRecognizer PROPERTIES SUFFIX ".pyd")
else()
    # On Linux and macOS, Python extension modules are ".so" (shared object) files.
    set_target_properties(simpleLanguageRecognizer PROPERTIES SUFFIX ".so")
endif()

# --- Installation ---
# This command is used by scikit-build and cibuildwheel.
install(TARGETS simpleLanguageRecognizer
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .
    ARCHIVE DESTINATION .
)

# --- Debugging Information ---
# This section works on all platforms and helps diagnose configuration issues.
# (You can remove this for cleaner output once your build is stable)
message(STATUS "--- CMake Configuration for simpleLanguageRecognizer ---")
message(STATUS "CMAKE_SYSTEM_NAME: ${CMAKE_SYSTEM_NAME}")
message(STATUS "CMAKE_CXX_COMPILER_ID: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "Python3_EXECUTABLE: ${Python3_EXECUTABLE}")
message(STATUS "Python3_LIBRARIES: ${Python3_LIBRARIES}")
message(STATUS "--- End CMake Configuration for simpleLanguageRecognizer ---")