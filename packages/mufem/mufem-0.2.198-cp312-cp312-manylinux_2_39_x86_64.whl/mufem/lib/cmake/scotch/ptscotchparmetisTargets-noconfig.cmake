#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCOTCH::ptscotchparmetisv3" for configuration ""
set_property(TARGET SCOTCH::ptscotchparmetisv3 APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(SCOTCH::ptscotchparmetisv3 PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_NOCONFIG "SCOTCH::scotch;SCOTCH::ptscotch"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libptscotchparmetisv3.so.7.0.10"
  IMPORTED_SONAME_NOCONFIG "libptscotchparmetisv3.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::ptscotchparmetisv3 )
list(APPEND _cmake_import_check_files_for_SCOTCH::ptscotchparmetisv3 "${_IMPORT_PREFIX}/lib/libptscotchparmetisv3.so.7.0.10" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
