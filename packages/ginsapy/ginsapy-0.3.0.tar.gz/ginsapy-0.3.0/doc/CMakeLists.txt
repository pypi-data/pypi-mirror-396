################################################################################
# CMakeLists.txt
#
# Copyright (C) 2024, Gantner Instruments GmbH. All rights reserved.
################################################################################

option(GINS_GINSAPY_VIRTUALENV "Use the virtual environment handling from cmake!" OFF)

if(NOT DEFINED ENV{VIRTUAL_ENV})
    
    if (GINS_GINSAPY_VIRTUALENV)

        # If not passed, then we set our own virtual env path
        set(VENV_PATH "${CMAKE_CURRENT_BINARY_DIR}/venv")

        # Search for python version to activate the virtual environment
        find_package(Python REQUIRED)
        execute_process(COMMAND "${Python_EXECUTABLE}" -m venv "${VENV_PATH}")
        set(ENV{VIRTUAL_ENV} ${VENV_PATH})
        set(Python_FIND_VIRTUALENV FIRST)
        unset(Python_EXECUTABLE)

        # Use python version from virtualenv
        find_package(Python REQUIRED)
        execute_process(COMMAND "${Python_EXECUTABLE}" -m pip install -r
            ${CMAKE_CURRENT_LIST_DIR}/requirements.txt)

    else()
        message(FATAL_ERROR "Virtual python environment needs to be sourced first!")
    endif()

endif()

find_program(SPHINX_EXEC sphinx-build REQUIRED
    HINTS $ENV{VIRTUAL_ENV}/bin/ $ENV{VIRTUAL_ENV}/Scripts/
    NO_DEFAULT_PATH
)

add_custom_target(${PROJECT_NAME}-doc ALL
    COMMAND ${SPHINX_EXEC} -M html ${CMAKE_CURRENT_LIST_DIR}/source ${CMAKE_CURRENT_BINARY_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMENT "Building documentation ..."
)

#-------------------------------------------------------------------------------
# Installation
#-------------------------------------------------------------------------------

install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/html/
    DESTINATION html
    COMPONENT doc
)
