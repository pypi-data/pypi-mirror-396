#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "adaptive::adaptive_core" for configuration "Release"
set_property(TARGET adaptive::adaptive_core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(adaptive::adaptive_core PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/adaptive_core.lib"
  )

list(APPEND _cmake_import_check_targets adaptive::adaptive_core )
list(APPEND _cmake_import_check_files_for_adaptive::adaptive_core "${_IMPORT_PREFIX}/lib/adaptive_core.lib" )

# Import target "adaptive::adaptive_c" for configuration "Release"
set_property(TARGET adaptive::adaptive_c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(adaptive::adaptive_c PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/adaptive_c.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/adaptive_c.dll"
  )

list(APPEND _cmake_import_check_targets adaptive::adaptive_c )
list(APPEND _cmake_import_check_files_for_adaptive::adaptive_c "${_IMPORT_PREFIX}/lib/adaptive_c.lib" "${_IMPORT_PREFIX}/bin/adaptive_c.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
