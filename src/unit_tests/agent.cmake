# Find the fortishield shared library
find_library(FORTISHIELDEXT NAMES libfortishieldext.dylib HINTS "${SRC_FOLDER}")
if(FORTISHIELDEXT)
  set(uname "Darwin")
else()
  set(uname "Linux")
endif()
find_library(FORTISHIELDEXT NAMES libfortishieldext.so HINTS "${SRC_FOLDER}")

if(NOT FORTISHIELDEXT)
    message(FATAL_ERROR "libfortishieldext not found! Aborting...")
endif()

# # Add compiling flags and set tests dependencies
if(${uname} STREQUAL "Darwin")
    set(TEST_DEPS ${FORTISHIELDLIB} ${FORTISHIELDEXT} -lpthread -ldl -fprofile-arcs -ftest-coverage)
    add_compile_options(-ggdb -O0 -g -coverage -DTEST_AGENT -I/usr/local/include -DENABLE_SYSC -DFORTISHIELD_UNIT_TESTING)
else()
    add_compile_options(-ggdb -O0 -g -coverage -DTEST_AGENT -DENABLE_AUDIT -DINOTIFY_ENABLED -fsanitize=address -fsanitize=undefined)
    link_libraries(-fsanitize=address -fsanitize=undefined)
    set(TEST_DEPS ${FORTISHIELDLIB} ${FORTISHIELDEXT} -lpthread -lcmocka -ldl -fprofile-arcs -ftest-coverage)
endif()

if(NOT ${uname} STREQUAL "Darwin")
  add_subdirectory(client-agent)
  add_subdirectory(logcollector)
  add_subdirectory(os_execd)
endif()

add_subdirectory(fortishield_modules)
