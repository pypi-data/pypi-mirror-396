cmake_minimum_required(VERSION 4.0)

project(${SKBUILD_PROJECT_NAME} LANGUAGES NONE)

# control where the output ends up so it's relative to the python package
set(CMAKE_INSTALL_BINDIR "asphodel/lib")
set(CMAKE_INSTALL_LIBDIR  "asphodel/lib")
set(CMAKE_INSTALL_INCLUDEDIR "asphodel/include")
set(ASPHODEL_SKIP_VERSION_AUTOGEN ON)

# find python so we can use python -m ziglang
find_package(Python COMPONENTS Interpreter REQUIRED)

# setup zig to use python -m ziglang
set(ZIG_EXECUTABLE "${Python_EXECUTABLE};-m;ziglang" CACHE STRING "Zig executable via ziglang" FORCE)

if (SKBUILD_STATE STREQUAL "sdist")
  message(STATUS "sdist: pre-generating version_autogen.h")

  execute_process(
    COMMAND ${ZIG_EXECUTABLE} build version_autogen
            --prefix "${CMAKE_CURRENT_BINARY_DIR}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/lib/asphodel"
    RESULT_VARIABLE RETVAL
    OUTPUT_QUIET ERROR_QUIET
  )

  if (NOT RETVAL EQUAL 0)
    message(FATAL_ERROR "zig build version_autogen failed with code ${RETVAL}")
  endif()

  file(COPY "${CMAKE_CURRENT_BINARY_DIR}/version_autogen.h" DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/include")
else()
  # let the build system find the included version_autogen.h
  list(APPEND ASPHODEL_ZIG_ADDITIONAL_ARGS --search-prefix "${CMAKE_CURRENT_SOURCE_DIR}")
endif()

# try to determine the cross-compilation target
if(NOT ASPHODEL_ZIG_TARGET OR ASPHODEL_ZIG_TARGET STREQUAL "")
  if(APPLE)
    if(DEFINED ENV{MACOSX_DEPLOYMENT_TARGET} AND NOT "$ENV{MACOSX_DEPLOYMENT_TARGET}" STREQUAL "")
      if (DEFINED CMAKE_OSX_ARCHITECTURES AND NOT CMAKE_OSX_ARCHITECTURES STREQUAL "")
        # use CMAKE_OSX_ARCHITECTURES and env(MACOSX_DEPLOYMENT_TARGET) set by scikit-build-core
        if (CMAKE_OSX_ARCHITECTURES STREQUAL "arm64")
          set(ARCH "aarch64")
        else()
          set(ARCH "${CMAKE_OSX_ARCHITECTURES}")
        endif()
        set(ASPHODEL_ZIG_TARGET "${ARCH}-macos.$ENV{MACOSX_DEPLOYMENT_TARGET}")
      endif()
    endif()
  elseif(WIN32)
    # check if arm is in the SETUPTOOLS_EXT_SUFFIX environment variable
    if(DEFINED ENV{SETUPTOOLS_EXT_SUFFIX})
      string(TOLOWER "$ENV{SETUPTOOLS_EXT_SUFFIX}" _arch)
      if(_arch MATCHES "arm")
        set(ASPHODEL_ZIG_TARGET "aarch64-windows")
      else()
        set(ASPHODEL_ZIG_TARGET "x86_64-windows")
      endif()
    else()
      set(ASPHODEL_ZIG_TARGET "x86_64-windows")
    endif()
  else()
    message(STATUS "Could not determine specific platform. Set ASPHODEL_ZIG_TARGET manually if needed.")
  endif()
endif()

message(STATUS "ASPHODEL_ZIG_TARGET: ${ASPHODEL_ZIG_TARGET}")
message(STATUS "ASPHODEL_ZIG_CPU: ${ASPHODEL_ZIG_CPU}")

add_subdirectory(lib/asphodel)
