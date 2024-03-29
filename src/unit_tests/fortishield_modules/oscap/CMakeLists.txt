# Copyright (C) 2015, Fortishield Inc.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

# Tests list and flags
list(APPEND tests_names "test_wm_oscap")
list(APPEND tests_flags "-Wl,--wrap=time,--wrap=w_time_delay,--wrap=w_sleep_until,--wrap=_mwarn,--wrap=_minfo,--wrap=_merror \
                         -Wl,--wrap=_mtwarn,--wrap=_mtinfo,--wrap=_mterror,--wrap=wm_exec,--wrap=StartMQ,--wrap=FOREVER \
                         -Wl,--wrap=wm_sendmsg,--wrap=SendMSG,--wrap=atexit,--wrap=wm_state_io")
list(APPEND use_shared_libs 1)

list(APPEND shared_libs "../scheduling/wmodules_scheduling_helpers.h")
list(APPEND shared_libs "../scheduling/wmodules_scheduling_helpers.c")

# Generate fortishield modules library
file(GLOB oscap ../../../fortishield_modules/*.o)
list(REMOVE_ITEM oscap ../../../fortishield_modules/main.o)

add_library(OSCAP_O STATIC ${oscap})

set_source_files_properties(
  ${oscap}
  PROPERTIES
  EXTERNAL_OBJECT true
  GENERATED true
  )

set_target_properties(
  OSCAP_O
  PROPERTIES
  LINKER_LANGUAGE C
  )

target_link_libraries(OSCAP_O ${FORTISHIELDLIB} ${FORTISHIELDEXT} -lpthread)


# Compiling tests
list(LENGTH tests_names count)
math(EXPR count "${count} - 1")
foreach(counter RANGE ${count})
    list(GET tests_names ${counter} test_name)
    list(GET tests_flags ${counter} test_flags)
    list(GET use_shared_libs ${counter} use_libs)

    if(use_libs EQUAL "1")
      add_executable(${test_name} ${test_name}.c ${shared_libs})
    else ()
      add_executable(${test_name} ${test_name}.c)
    endif()

    target_link_libraries(
        ${test_name}
        ${FORTISHIELDLIB}
        ${FORTISHIELDEXT}
        OSCAP_O
        -ldl
        -lcmocka
        -fprofile-arcs
        -ftest-coverage
    )
    if(NOT test_flags STREQUAL " ")
        target_link_libraries(
            ${test_name}
            ${test_flags}
        )
    endif()
    add_test(${test_name} ${test_name})
endforeach()
