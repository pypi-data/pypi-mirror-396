#pragma once

#include <cmath>

namespace tds
{
   inline double cheb(const double x, const std::size_t N){
        // Faster using polynomial and more accurate.
        return std::cos(N * std::acos(x));
   } 
} // namespace tds
