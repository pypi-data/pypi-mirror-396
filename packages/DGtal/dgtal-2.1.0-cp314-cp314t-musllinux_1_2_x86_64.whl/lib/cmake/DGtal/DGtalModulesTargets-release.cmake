#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "DGtal::DGTAL_LibBoard" for configuration "Release"
set_property(TARGET DGtal::DGTAL_LibBoard APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(DGtal::DGTAL_LibBoard PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libDGTAL_LibBoard.a"
  )

list(APPEND _cmake_import_check_targets DGtal::DGTAL_LibBoard )
list(APPEND _cmake_import_check_files_for_DGtal::DGTAL_LibBoard "${_IMPORT_PREFIX}/lib/libDGTAL_LibBoard.a" )

# Import target "DGtal::DGTAL_BoostAddons" for configuration "Release"
set_property(TARGET DGtal::DGTAL_BoostAddons APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(DGtal::DGTAL_BoostAddons PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libDGTAL_BoostAddons.a"
  )

list(APPEND _cmake_import_check_targets DGtal::DGTAL_BoostAddons )
list(APPEND _cmake_import_check_files_for_DGtal::DGTAL_BoostAddons "${_IMPORT_PREFIX}/lib/libDGTAL_BoostAddons.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
