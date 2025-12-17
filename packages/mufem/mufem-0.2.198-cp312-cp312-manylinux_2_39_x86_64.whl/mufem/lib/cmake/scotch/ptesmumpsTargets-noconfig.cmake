#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCOTCH::ptesmumps" for configuration ""
set_property(TARGET SCOTCH::ptesmumps APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(SCOTCH::ptesmumps PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_NOCONFIG "SCOTCH::scotch"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libptesmumps.so.7.0.10"
  IMPORTED_SONAME_NOCONFIG "libptesmumps.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::ptesmumps )
list(APPEND _cmake_import_check_files_for_SCOTCH::ptesmumps "${_IMPORT_PREFIX}/lib/libptesmumps.so.7.0.10" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
