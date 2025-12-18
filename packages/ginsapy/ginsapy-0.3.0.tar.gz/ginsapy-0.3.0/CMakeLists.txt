################################################################################
# CMakeLists.txt
#
# Copyright (C) 2024, Gantner Instruments GmbH. All rights reserved.
################################################################################
cmake_minimum_required(VERSION 3.19)

#-------------------------------------------------------------------------------
# Project
#-------------------------------------------------------------------------------
project(ginsapy LANGUAGES NONE)

set(GINS_INSTALL_SUFFIX "appdata/api/Python/examples/${PROJECT_NAME}"
    CACHE PATH "Allow to change the default installation suffix.")

option(GINS_GINSAPY_ENABLE_DOC "Enable to build the documentation" OFF)
if(GINS_GINSAPY_ENABLE_DOC)
    add_subdirectory(doc)
endif()

# Option to control whether dependencies are installed
# This installs the package with its requirements and is necessary for generated documentation
option(GINS_GINSAPY_INSTALL_PYTHON_DEPENDENCIES "Install required Python dependencies" OFF)

if (GINS_GINSAPY_INSTALL_PYTHON_DEPENDENCIES)
    find_package(Python REQUIRED)

    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m pip install -e ${CMAKE_CURRENT_LIST_DIR} --no-deps
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    )
endif()

#-------------------------------------------------------------------------------
# Installation
#-------------------------------------------------------------------------------

option(GINS_GINSAPY_INSTALL_EXAMPLES "Enable to install the examples" ON)

if(GINS_GINSAPY_INSTALL_EXAMPLES)

    install(DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/src
        DESTINATION ${GINS_INSTALL_SUFFIX}
        COMPONENT example
        PATTERN "*__pycache__*" EXCLUDE
    )

    install(FILES 
            README.md
            requirements.txt
            pyproject.toml
            startup.py
            CHANGELOG.md
        DESTINATION ${GINS_INSTALL_SUFFIX}
        COMPONENT example
    )

endif()
