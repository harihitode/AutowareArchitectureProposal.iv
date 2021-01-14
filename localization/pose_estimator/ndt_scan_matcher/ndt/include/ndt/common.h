#ifndef NDT_SCAN_MATCHER_NDT_COMMON_H
#define NDT_SCAN_MATCHER_NDT_COMMON_H

#include <iostream>

namespace ndt
{
  // neighbor search methods
  enum class NeighborSearchMethod : int {
    BEGIN = 0,
    KDTREE = BEGIN,
    DIRECT26,
    DIRECT7,
    DIRECT1,
    END,
  };

  // enum item to string
  std::ostream & operator<<(std::ostream & os, const NeighborSearchMethod & nsm);

  // operators for range-iteration
  NeighborSearchMethod begin(NeighborSearchMethod);
  NeighborSearchMethod end(NeighborSearchMethod);
  NeighborSearchMethod operator*(NeighborSearchMethod nsm);
  NeighborSearchMethod operator++(NeighborSearchMethod & nsm);
}

#endif
