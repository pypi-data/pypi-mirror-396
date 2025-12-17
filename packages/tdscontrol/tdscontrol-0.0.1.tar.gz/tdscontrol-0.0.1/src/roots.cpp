#include <tdscontrol/roots.hpp>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues>
#include <algorithm>
#include "cheb.hpp"


namespace tds
{

   std::vector<std::complex<double>> roots(const tds& sys, unsigned int N)
   {
      Eigen::MatrixXd Sigma;
      Eigen::MatrixXd Pi;
      Eigen::GeneralizedEigenSolver<Eigen::MatrixXd> ges;

      const double tau_m = *std::max_element(sys.hA().cbegin(), sys.hA().cend());

      // Set-up Sigma
      Sigma = Eigen::MatrixXd::Identity(N + 1, N +1); 
      for (std::size_t i = 0; i <= N; i++)
      {
         double Ri = 0; 
         for(std::size_t k = 0; k < sys.mA(); k++){
            Ri += sys.A()[k] * cheb(-2.0*sys.hA()[k]/tau_m + 1.0, i);
         }
         Sigma(0, i) = Ri;
      }
      
      // Set-up Pi
      Pi = Eigen::MatrixXd::Zero(N+1, N+1);
      Pi.row(0) = 4.0 / tau_m * Eigen::MatrixXd::Ones(1, N+1);
      for (std::size_t i = 1; i <= N; i++)
      {
         Pi(i, i-1) = 1.0 / static_cast<double>(i);
         if (i < N) {
            Pi(i, i + 1) = -1.0 / static_cast<double>(i);
         }
      }
      Pi(1, 0) = 2.0;
      Pi = tau_m / 4.0 * Pi;

      ges.compute(Sigma, Pi);
      std::vector<std::complex<double>> res;
      Eigen::VectorXcd ev = ges.eigenvalues();
      for (size_t i = 0; i < ges.eigenvalues().size(); i++)
      {
         res.push_back(ges.eigenvalues()[i]);
      }
      return res;
   }
    
} // namespace tds
