import math
import numpy as np

class MultivariableModel:
    @staticmethod
    def calculate_energy(theta, phi, A, theta0, phi0):
        d_theta = math.radians(theta - theta0)
        d_phi = math.radians(phi - phi0)
        E = A * math.cos(d_theta) * math.cos(d_phi)
        dE_dtheta = -A * math.sin(d_theta) * math.cos(d_phi)
        dE_dphi = -A * math.cos(d_theta) * math.sin(d_phi)
        grad_mag = math.sqrt(dE_dtheta**2 + dE_dphi**2)
        grad_angle = math.degrees(math.atan2(dE_dphi, dE_dtheta))
        return E, dE_dtheta, dE_dphi, grad_mag, grad_angle

    @staticmethod
    def calculate_surface(A, theta0, phi0, res=40):
        theta = np.linspace(0, 90, res)
        phi = np.linspace(0, 360, res)
        Theta, Phi = np.meshgrid(theta, phi)
        E = A * np.cos(np.radians(Theta - theta0)) * np.cos(np.radians(Phi - phi0))
        return theta.tolist(), phi.tolist(), E.tolist()

    @staticmethod
    def calculate_optimal(latitude, power_gen):
        theta0 = abs(latitude)
        phi0 = 0.0 if latitude >= 0 else 180.0
        return theta0, phi0, power_gen

    @staticmethod
    def calculate_directional_derivative(theta, phi, A, theta0, phi0, alpha):
        _, dE_dtheta, dE_dphi, _, _ = MultivariableModel.calculate_energy(theta, phi, A, theta0, phi0)
        alpha_rad = math.radians(alpha)
        u_theta = math.cos(alpha_rad)
        u_phi = math.sin(alpha_rad)
        D = dE_dtheta * u_theta + dE_dphi * u_phi
        return D, alpha

    @staticmethod
    def calculate_hessian(theta, phi, A, theta0, phi0):
        d_theta = math.radians(theta - theta0)
        d_phi = math.radians(phi - phi0)
        
        d2E_dtheta2 = -A * math.cos(d_theta) * math.cos(d_phi)
        d2E_dphi2 = -A * math.cos(d_theta) * math.cos(d_phi)
        d2E_dthetadphi = A * math.sin(d_theta) * math.sin(d_phi)
        
        hessian_matrix = [
            [d2E_dtheta2, d2E_dthetadphi],
            [d2E_dthetadphi, d2E_dphi2]
        ]
        
        det = d2E_dtheta2 * d2E_dphi2 - d2E_dthetadphi**2
        
        is_critical = abs(math.sin(d_theta)) < 1e-5 and abs(math.sin(d_phi)) < 1e-5
        
        classification = "Ninguno (No es punto critico)"
        if is_critical:
            if det > 0 and d2E_dtheta2 < 0:
                classification = "Maximo local"
            elif det > 0 and d2E_dtheta2 > 0:
                classification = "Minimo local"
            elif det < 0:
                classification = "Punto de silla"
            else:
                classification = "Inconcluso"
                
        trace = d2E_dtheta2 + d2E_dphi2
        desc = max(0.0, trace**2 - 4 * det)
        eig1 = (trace + math.sqrt(desc)) / 2
        eig2 = (trace - math.sqrt(desc)) / 2
        
        return hessian_matrix, det, classification, is_critical, eig1, eig2
