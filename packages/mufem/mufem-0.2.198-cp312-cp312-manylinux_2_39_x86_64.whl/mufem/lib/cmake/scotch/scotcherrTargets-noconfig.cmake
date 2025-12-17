#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCOTCH::scotcherr" for configuration ""
set_property(TARGET SCOTCH::scotcherr APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(SCOTCH::scotcherr PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libscotcherr.so.7.0.10"
  IMPORTED_SONAME_NOCONFIG "libscotcherr.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::scotcherr )
list(APPEND _cmake_import_check_files_for_SCOTCH::scotcherr "${_IMPORT_PREFIX}/lib/libscotcherr.so.7.0.10" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
