#include <iostream>
#include <tdscontrol/tds.hpp>
#include <tdscontrol/roots.hpp>
#include <iomanip>

int main(int argc, char const *argv[])
{
    tds::tds sys({1, -1}, {0, 1});
    const auto roots = tds::roots(sys, 15);
    std::cout << "Eigenvalues: ";
    std::cout << std::fixed << std::setprecision(16);
    for (auto &root: roots)
    {
        std::cout << root << ", ";
    }
    std::cout << "\n";
    
    return 0;
}
