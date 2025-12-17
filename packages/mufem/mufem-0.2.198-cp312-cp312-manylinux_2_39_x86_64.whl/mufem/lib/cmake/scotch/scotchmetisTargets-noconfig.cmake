#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCOTCH::scotchmetisv3" for configuration ""
set_property(TARGET SCOTCH::scotchmetisv3 APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(SCOTCH::scotchmetisv3 PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_NOCONFIG "SCOTCH::scotch"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libscotchmetisv3.so.7.0.10"
  IMPORTED_SONAME_NOCONFIG "libscotchmetisv3.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::scotchmetisv3 )
list(APPEND _cmake_import_check_files_for_SCOTCH::scotchmetisv3 "${_IMPORT_PREFIX}/lib/libscotchmetisv3.so.7.0.10" )

# Import target "SCOTCH::scotchmetisv5" for configuration ""
set_property(TARGET SCOTCH::scotchmetisv5 APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(SCOTCH::scotchmetisv5 PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_NOCONFIG "SCOTCH::scotch"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libscotchmetisv5.so.7.0.10"
  IMPORTED_SONAME_NOCONFIG "libscotchmetisv5.so.7.0"
  )

list(APPEND _cmake_import_check_targets SCOTCH::scotchmetisv5 )
list(APPEND _cmake_import_check_files_for_SCOTCH::scotchmetisv5 "${_IMPORT_PREFIX}/lib/libscotchmetisv5.so.7.0.10" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
