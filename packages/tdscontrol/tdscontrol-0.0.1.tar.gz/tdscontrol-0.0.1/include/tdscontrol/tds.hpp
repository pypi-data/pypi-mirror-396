#pragma once
#include <vector>

namespace tds
{
    class tds {
        private:
            std::vector<double> m_A;
            std::vector<double> m_hA;
        public:
            tds(std::vector<double> A, std::vector<double> hA);

            const std::vector<double> &A() const; 
            
            const std::vector<double> &hA() const; 

            const std::size_t mA() const {
                return m_A.size();
            }

            const std::size_t n() const {
                return 1;
            }
    };
    
} // namespace tds
