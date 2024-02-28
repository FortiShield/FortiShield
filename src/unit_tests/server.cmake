# Find the fortishield shared library
find_library(FORTISHIELDEXT NAMES libfortishieldext.so HINTS "${SRC_FOLDER}")
set(uname "Linux")

if(NOT FORTISHIELDEXT)
    message(FATAL_ERROR "libfortishieldext not found! Aborting...")
endif()

# Add compiling flags
add_compile_options(-ggdb -O0 -g -coverage -DTEST_SERVER -DENABLE_AUDIT -DINOTIFY_ENABLED -fsanitize=address -fsanitize=undefined)
link_libraries(-fsanitize=address -fsanitize=undefined)
# Set tests dependencies
set(TEST_DEPS ${FORTISHIELDLIB} ${FORTISHIELDEXT} -lpthread -ldl -lcmocka -fprofile-arcs -ftest-coverage)

add_subdirectory(analysisd)
add_subdirectory(remoted)
add_subdirectory(fortishield_db)
add_subdirectory(os_auth)
add_subdirectory(os_crypto)
add_subdirectory(fortishield_modules)
add_subdirectory(monitord)
add_subdirectory(logcollector)
add_subdirectory(os_execd)
add_subdirectory(os_integrator)
add_subdirectory(addagent)
add_subdirectory(os_maild)
add_subdirectory(os_csyslogd)