#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "DGtal::DGtal" for configuration "Release"
set_property(TARGET DGtal::DGtal APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(DGtal::DGtal PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libDGtal.a"
  )

list(APPEND _cmake_import_check_targets DGtal::DGtal )
list(APPEND _cmake_import_check_files_for_DGtal::DGtal "${_IMPORT_PREFIX}/lib/libDGtal.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
