/**
* @file   NeighborhoodTables.h
* @author Pablo Hernandez-Cerdan. Institute of Fundamental Sciences.
* Massey University. Palmerston North, New Zealand
* @date 2018/01/01
*
* Configuration header for DGtal look up tables.

* You can use loadTable(table)
* @see NeighborhoodConfigurations.h
*
**/
#pragma once
#include <string>

namespace DGtal {
  namespace simplicity  {
  ///Path to the DGtal look up tables. Compressed with zlib.
  inline const std::string tableDir = "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables";
  inline const std::string tableSimple26_6 =
    "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/simplicity_table26_6.zlib";
  inline const std::string tableSimple18_6 =
    "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/simplicity_table18_6.zlib";
  inline const std::string tableSimple6_26 =
    "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/simplicity_table6_26.zlib";
  inline const std::string tableSimple6_18 =
    "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/simplicity_table6_18.zlib";
  inline const std::string tableSimple8_4 =
    "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/simplicity_table8_4.zlib";
  inline const std::string tableSimple4_8 =
    "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/simplicity_table4_8.zlib";
  } // simplicity namespace

  namespace isthmusicity {
    inline const std::string tableIsthmus =
      "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/isthmusicity_table26_6.zlib";
    inline const std::string tableOneIsthmus =
      "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/isthmusicityOne_table26_6.zlib";
    inline const std::string tableTwoIsthmus =
      "/tmp/tmp1wocpc3f/wheel/platlib/include/DGtal/topology/tables/isthmusicityTwo_table26_6.zlib";
  } // isthmusicity namespace
} // DGtal namespace


