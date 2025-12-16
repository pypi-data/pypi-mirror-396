# - Config file for the DGtal package
# It defines the following variables
#  DGTAL_INCLUDE_DIRS - include directories for DGtal
#  DGTAL_LIBRARY_DIRS - library directories for DGtal (normally not used!)
#  DGTAL_LIBRARIES    - libraries to link against
#  DGTAL_VERSION      - version of the DGtal library

####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was DGtalConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

####################################################################################
include(CMakeFindDependencyMacro)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_CURRENT_LIST_DIR})
set(DGTAL_VERSION "2.1.0")

#### Required dependencies  ####
find_package(Threads REQUIRED)
find_dependency(Boost REQUIRED
  
  )
find_dependency(ZLIB REQUIRED
  # NO_HINTS (no ZLIB_DIR or ZLIB_DIR-NOTFOUND)
  )

set(DGTAL_WITH_EIGEN 1)
if (NOT 0 OR NOT ON) 
  find_dependency(Eigen REQUIRED)
endif()
set(DGtalLibDependencies ${DGtalLibDependencies} Eigen3::Eigen)

if () 
  include(libigl)
  set(DGTAL_WITH_LIBIGL 1)
  set(DGtalLibDependencies ${DGtalLibDependencies} igl::core)
endif()

#### Optionnal dependencies  ####

if(0) #if ITK_FOUND_DGTAL
  set (DGTAL_WITH_ITK 1)
  find_dependency(ITK REQUIRED
    # NO_HINTS (no ITK_DIR or ITK_DIR-NOTFOUND)
    )
    include(${ITK_USE_FILE})
endif()

if(0) #if CAIRO_FOUND_DGTAL
  find_package(Cairo REQUIRED
    # NO_HINTS (no Cairo_DIR or Cairo_DIR-NOTFOUND)
    )
  set(DGTAL_WITH_CAIRO 1)
endif()

if(0) #if HDF5_FOUND_DGTAL
  find_dependency(HDF5 REQUIRED HL C
    # NO_HINTS (no HDF5_DIR or HDF5_DIR-NOTFOUND)
    )
  set (DGTAL_WITH_HDF5 1)
endif()

if (0) #if POLYSCOPE_FOUND_DGTAL
  find_dependency(glfw REQUIRED)
  find_dependency(glad REQUIRED)
  find_dependency(glm-header-only REQUIRED)
  find_dependency(glm REQUIRED)
  find_dependency(imgui REQUIRED)
  find_dependency(stb REQUIRED)
  find_dependency(nlohmann_json REQUIRED)
  find_dependency(MarchingCube REQUIRED)
  find_dependency(polyscope REQUIRED
    
    )
  set(DGTAL_WITH_POLYSCOPE_VIEWER 1)
endif (0)

if(0) #if OPENMP_FOUND_DGTAL
   include(openmp)
   set(DGtalLibDependencies ${DGtalLibDependencies} OpenMP::OpenMP_CXX)
  set(DGTAL_WITH_OPENMP 1)
endif()

if(0) #if CGAL_FOUND_DGTAL
  find_dependency(CGAL COMPONENTS Core
    # NO_HINTS (no CGAL_DIR or CGAL_DIR-NOTFOUND)
    )
  set (DGTAL_WITH_CGAL 1)
endif()

if(0) #if FFTW3_FOUND_DGTAL
  find_package(FFTW3 REQUIRED
    # NO_HINTS (no FFTW3_DIR or FFTW3_DIR-NOTFOUND)
    )
  set(DGTAL_WITH_FFTW3 1)
endif()

include("${CMAKE_CURRENT_LIST_DIR}/DGtalModulesTargets.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/DGtalTargets.cmake")

set(DGTAL_LIBRARIES DGtal::DGtal DGtal::DGTAL_LibBoard DGtal::DGTAL_BoostAddons DGtal::DGtal_STB ${DGtalLibDependencies})
get_target_property(DGTAL_INCLUDE_DIRS DGtal::DGtal INTERFACE_INCLUDE_DIRECTORIES)
