#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCOTCH::ptscotcherrexit" for configuration ""
set_property(TARGET SCOTCH::ptscotcherrexit APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(SCOTCH::ptscotcherrexit PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libptscotcherrexit.so.7.0.10"
  IMPORTED_SONAME_NOCONFIG "libptscotcherrexit.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::ptscotcherrexit )
list(APPEND _cmake_import_check_files_for_SCOTCH::ptscotcherrexit "${_IMPORT_PREFIX}/lib/libptscotcherrexit.so.7.0.10" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
