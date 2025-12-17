#pragma once
#include <tdscontrol/tds.hpp>
#include <vector>
#include <complex>

namespace tds
{
   std::vector<std::complex<double>> roots(const tds& system, unsigned int N);
} // namespace tds
