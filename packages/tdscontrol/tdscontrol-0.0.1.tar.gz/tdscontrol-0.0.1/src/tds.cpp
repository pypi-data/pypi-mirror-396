#include <tdscontrol/tds.hpp>
#include "assertions.hpp"

namespace tds
{
    tds::tds(std::vector<double> A, std::vector<double> hA) 
    : m_A(A), m_hA(hA)
    {
        TDS_CONTROL_PRECONDITION(A.size() == m_hA.size(), "Number of elements in A and hA do not match!");
    }

    const std::vector<double> &tds::A() const {
        return m_A;
    }
    
    const std::vector<double> &tds::hA() const {
        return m_hA;
    }
    
} // namespace tds
