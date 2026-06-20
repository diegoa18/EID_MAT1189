import numpy as np
import matplotlib.pyplot as plt

LOCATIONS = {
    "Santiago": {"A": 1000, "theta_0": 33.4, "phi_0": 0.0},
    "Antofagasta": {"A": 1200, "theta_0": 23.6, "phi_0": 0.0},
    "Punta Arenas": {"A": 800, "theta_0": 53.1, "phi_0": 0.0}
}

class SolarPanelModel:
    def __init__(self, location="Santiago", A=None, theta_0=None, phi_0=None):
        """
        Inicializa el modelo del panel solar.
        Puede inicializarse con una ubicación predefinida o parámetros personalizados.
        """
        if location in LOCATIONS and A is None and theta_0 is None and phi_0 is None:
            data = LOCATIONS[location]
            self.A = data["A"]
            self.theta_0 = np.radians(data["theta_0"])
            self.phi_0 = np.radians(data["phi_0"])
            self.location_name = location
        else:
            self.A = A if A is not None else 1000
            self.theta_0 = np.radians(theta_0) if theta_0 is not None else 0
            self.phi_0 = np.radians(phi_0) if phi_0 is not None else 0
            self.location_name = "Custom"

    def energy(self, theta_deg, phi_deg):
        """
        Calcula la energía captada dados los ángulos (en grados).
        E(theta, phi) = A * cos(theta - theta_0) * cos(phi - phi_0)
        """
        theta = np.radians(theta_deg)
        phi = np.radians(phi_deg)
        e = self.A * np.cos(theta - self.theta_0) * np.cos(phi - self.phi_0)
        return max(0, e)

    def partial_derivatives(self, theta_deg, phi_deg):
        """
        Calcula las derivadas parciales dE/dtheta y dE/dphi en los ángulos dados (en grados).
        Retorna las derivadas con respecto a radianes, que corresponde al gradiente matemático estándar.
        """
        theta = np.radians(theta_deg)
        phi = np.radians(phi_deg)
        dE_dtheta = -self.A * np.sin(theta - self.theta_0) * np.cos(phi - self.phi_0)
        dE_dphi = -self.A * np.cos(theta - self.theta_0) * np.sin(phi - self.phi_0)
        return dE_dtheta, dE_dphi

    def gradient(self, theta_deg, phi_deg):
        """
        Retorna el vector gradiente [dE/dtheta, dE/dphi].
        """
        dE_dtheta, dE_dphi = self.partial_derivatives(theta_deg, phi_deg)
        return np.array([dE_dtheta, dE_dphi])

    def optimal_configuration(self):
        """
        Retorna los ángulos de configuración óptima (en grados) y la energía máxima posible.
        """
        return np.degrees(self.theta_0), np.degrees(self.phi_0), self.A

    def plot_surface_and_contour(self, theta_range=(0, 90), phi_range=(-90, 90), resolution=100):
        """
        Visualiza las gráficas de superficie y curvas de nivel para la función de energía.
        """
        theta_deg = np.linspace(theta_range[0], theta_range[1], resolution)
        phi_deg = np.linspace(phi_range[0], phi_range[1], resolution)
        
        Theta_deg, Phi_deg = np.meshgrid(theta_deg, phi_deg)
        
        Theta = np.radians(Theta_deg)
        Phi = np.radians(Phi_deg)
        
        E = self.A * np.cos(Theta - self.theta_0) * np.cos(Phi - self.phi_0)
        E[E < 0] = 0
        
        fig = plt.figure(figsize=(14, 6))
        
        ax1 = fig.add_subplot(121, projection='3d')
        surf = ax1.plot_surface(Theta_deg, Phi_deg, E, cmap='inferno', edgecolor='none', alpha=0.9)
        ax1.set_title(f"Superficie de Energía - {self.location_name}")
        ax1.set_xlabel("Inclinación ($\\theta$) [grados]")
        ax1.set_ylabel("Orientación ($\\phi$) [grados]")
        ax1.set_zlabel("Energía Captada")
        fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5)
        
        ax2 = fig.add_subplot(122)
        contour = ax2.contourf(Theta_deg, Phi_deg, E, levels=20, cmap='inferno')
        ax2.set_title(f"Curvas de Nivel de Energía - {self.location_name}")
        ax2.set_xlabel("Inclinación ($\\theta$) [grados]")
        ax2.set_ylabel("Orientación ($\\phi$) [grados]")
        fig.colorbar(contour, ax=ax2, label="Energía")
        
        opt_theta, opt_phi, _ = self.optimal_configuration()
        ax2.plot(opt_theta, opt_phi, 'r*', markersize=12, label='Configuración Óptima')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig("solar_optimization_plots.png")
        print("Gráficas guardadas como 'solar_optimization_plots.png'.")
        plt.show()

def main():
    print("--- Modelo de Optimización de Paneles Solares ---")
    model = SolarPanelModel(location="Santiago")
    
    opt_theta, opt_phi, max_energy = model.optimal_configuration()
    print(f"\n[+] Configuración Óptima para {model.location_name}:")
    print(f"    Inclinación óptima (theta): {opt_theta:.2f}°")
    print(f"    Orientación óptima (phi): {opt_phi:.2f}°")
    print(f"    Energía Máxima: {max_energy:.2f}")
    
    test_configs = [
        (opt_theta, opt_phi),
        (opt_theta + 10, opt_phi),
        (opt_theta, opt_phi - 15),
        (45, 45)
    ]
    
    print("\n[+] Comparación de distintas configuraciones de instalación:")
    print(f"{'Theta (°)':<12} | {'Phi (°)':<12} | {'Energía':<10} | {'Grad Theta':<15} | {'Grad Phi':<15}")
    print("-" * 75)
    for t, p in test_configs:
        e = model.energy(t, p)
        grad = model.gradient(t, p)
        print(f"{t:<12.2f} | {p:<12.2f} | {e:<10.2f} | {grad[0]:<15.2f} | {grad[1]:<15.2f}")
        
    print("\n[+] Prueba de sensibilidad con derivadas direccionales:")
    error_theta, error_phi = 2.0, 3.0
    print(f"    Si nos desviamos {error_theta}° en theta y {error_phi}° en phi desde el óptimo,")
    e_err = model.energy(opt_theta + error_theta, opt_phi + error_phi)
    print(f"    la energía captada será {e_err:.2f} (pérdida de {max_energy - e_err:.2f}).")
    
    print("\n[+] Generando gráficas de superficie y curvas de nivel...")
    model.plot_surface_and_contour()

if __name__ == '__main__':
    main()
