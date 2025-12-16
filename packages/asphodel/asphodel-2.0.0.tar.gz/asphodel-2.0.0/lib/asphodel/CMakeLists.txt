cmake_minimum_required(VERSION 3.10...4.0)

if(NOT CMAKE_BUILD_TYPE)
	set(CMAKE_BUILD_TYPE Release)
endif()

project(Asphodel LANGUAGES NONE)

option(STATIC_LIB "STATIC_LIB" OFF)
option(ASPHODEL_USB_DEVICE "ASPHODEL_USB_DEVICE" ON)
option(ASPHODEL_TCP_DEVICE "ASPHODEL_TCP_DEVICE" ON)
option(ASPHODEL_BUILD_EXAMPLES "ASPHODEL_BUILD_EXAMPLES" OFF)
option(ASPHODEL_SKIP_VERSION_AUTOGEN "ASPHODEL_SKIP_VERSION_AUTOGEN" OFF)

set(ASPHODEL_ZIG_TARGET "" CACHE STRING "zig -Dtarget value, e.g. x86_64-linux-gnu")
set(ASPHODEL_ZIG_CPU "" CACHE STRING "zig -Dcpu value, e.g. baseline")
if(NOT ASPHODEL_ZIG_CPU)
set(ASPHODEL_ZIG_CPU baseline CACHE STRING "" FORCE)
endif()
set(ASPHODEL_ZIG_ADDITIONAL_ARGS "" CACHE STRING "Extra args to pass to zig (semicolon-separated)")

find_program(ZIG_EXECUTABLE zig REQUIRED)

set(ASPHODEL_OUTDIR "${CMAKE_CURRENT_BINARY_DIR}/zig-out")
set(ASPHODEL_BYPRODUCTS "")

if (STATIC_LIB)
    add_library(asphodel STATIC IMPORTED GLOBAL)
    set (ASPHODEL_OUTPUT "${ASPHODEL_OUTDIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}asphodel${CMAKE_STATIC_LIBRARY_SUFFIX}")
else()
    # shared .so/.dylib/.dll
    add_library(asphodel SHARED IMPORTED GLOBAL)
    if (WIN32)
        # zig always uses asphodel.dll and asphodel.lib on windows, even with GNU libc
        set (ASPHODEL_OUTPUT "${ASPHODEL_OUTDIR}/bin/asphodel.dll")
        set (ASPHODEL_IMPLIB "${ASPHODEL_OUTDIR}/lib/asphodel.lib")
        set_target_properties(asphodel PROPERTIES IMPORTED_IMPLIB "${ASPHODEL_IMPLIB}")
        list(APPEND ASPHODEL_BYPRODUCTS "${ASPHODEL_IMPLIB}")
    else()
        set (ASPHODEL_OUTPUT "${ASPHODEL_OUTDIR}/lib/${CMAKE_SHARED_LIBRARY_PREFIX}asphodel${CMAKE_SHARED_LIBRARY_SUFFIX}")
    endif()
endif()
set_target_properties(asphodel PROPERTIES IMPORTED_LOCATION "${ASPHODEL_OUTPUT}")
list(APPEND ASPHODEL_BYPRODUCTS "${ASPHODEL_OUTPUT}")

# a stamp that will be touched each build
set (ASPHODEL_STAMP "${CMAKE_CURRENT_BINARY_DIR}/zig_build.stamp")

add_custom_command(
    OUTPUT "${ASPHODEL_STAMP}"
    BYPRODUCTS ${ASPHODEL_BYPRODUCTS}
    COMMAND ${ZIG_EXECUTABLE} build
    --summary none
    -Dstatic=$<IF:$<BOOL:${STATIC_LIB}>,true,false>
    -Ddisable_usb=$<IF:$<BOOL:${ASPHODEL_USB_DEVICE}>,false,true>
    -Ddisable_tcp=$<IF:$<BOOL:${ASPHODEL_TCP_DEVICE}>,false,true>
    -Dbuild_examples=$<IF:$<BOOL:${ASPHODEL_BUILD_EXAMPLES}>,true,false>
    -Dskip_version_autogen=$<IF:$<BOOL:${ASPHODEL_SKIP_VERSION_AUTOGEN}>,true,false>
    $<$<BOOL:${ASPHODEL_ZIG_TARGET}>:-Dtarget=${ASPHODEL_ZIG_TARGET}>
    $<$<BOOL:${ASPHODEL_ZIG_CPU}>:-Dcpu=${ASPHODEL_ZIG_CPU}>
    $<$<CONFIG:Debug>:-Doptimize=ReleaseSafe>
    $<$<CONFIG:Release>:-Doptimize=ReleaseSafe>
    $<$<CONFIG:MinSizeRel>:-Doptimize=ReleaseSmall>
    --prefix ${ASPHODEL_OUTDIR}
    ${ASPHODEL_ZIG_ADDITIONAL_ARGS}
    COMMENT "Building asphodel via zig"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(zig_build ALL DEPENDS "${ASPHODEL_STAMP}")

add_dependencies(asphodel zig_build)

target_include_directories(asphodel INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/inc")

install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/inc/" TYPE INCLUDE)
if (STATIC_LIB)
    install(FILES "${ASPHODEL_OUTPUT}" TYPE LIB)
else()
    if (WIN32)
        install(FILES "${ASPHODEL_OUTDIR}/bin/asphodel.dll" TYPE BIN)
        install(FILES "${ASPHODEL_OUTDIR}/lib/asphodel.lib" TYPE LIB)
    else()
        install(FILES "${ASPHODEL_OUTPUT}" TYPE LIB)
    endif()
endif()
