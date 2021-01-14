#include <ndt/common.h>

using namespace ndt;

// enum item to string
std::ostream & ndt::operator<<(std::ostream & os, const NeighborSearchMethod & nsm) {
  switch (nsm) {
  case ndt::NeighborSearchMethod::KDTREE:
    os << "KDTREE"; break;
  case ndt::NeighborSearchMethod::DIRECT26:
    os << "DIRECT26"; break;
  case ndt::NeighborSearchMethod::DIRECT7:
    os << "DIRECT7"; break;
  case ndt::NeighborSearchMethod::DIRECT1:
    os << "DIRECT1"; break;
  default:
    os << "unknown"; break;
  }
  return os;
}

// operators for range-iteration
NeighborSearchMethod ndt::begin(NeighborSearchMethod) { return NeighborSearchMethod::BEGIN; }
NeighborSearchMethod ndt::end(NeighborSearchMethod) { return NeighborSearchMethod::END; }
NeighborSearchMethod ndt::operator*(NeighborSearchMethod nsm) { return nsm; }
NeighborSearchMethod ndt::operator++(NeighborSearchMethod & nsm) {
  return nsm = NeighborSearchMethod(std::underlying_type<NeighborSearchMethod>::type(nsm) + 1);
}
