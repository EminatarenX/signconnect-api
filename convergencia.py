# convergencia_unicarga.py
import numpy as np
import matplotlib.pyplot as plt

# Número de generaciones a simular
num_generations = 35

# Generar datos simulados
np.random.seed(42)

# Caso 1: Estudiante regular (convergencia rápida)
x = np.arange(num_generations)
max_fit_1 = 0.93 * (1 - np.exp(-x / 8)) + np.random.normal(0, 0.01, num_generations)
avg_fit_1 = max_fit_1 - 0.2 * np.exp(-x / 12) - 0.05

# Caso 2: Estudiante semi-irregular
max_fit_2 = 0.89 * (1 - np.exp(-x / 12)) + np.random.normal(0, 0.015, num_generations)
avg_fit_2 = max_fit_2 - 0.2 * np.exp(-x / 18) - 0.05

# Caso 3: Estudiante irregular
max_fit_3 = 0.86 * (1 - np.exp(-x / 16)) + np.random.normal(0, 0.02, num_generations)
avg_fit_3 = max_fit_3 - 0.2 * np.exp(-x / 24) - 0.05

# Asegurar que todos los valores están en rango [0,1]
max_fit_1 = np.clip(max_fit_1, 0, 1)
avg_fit_1 = np.clip(avg_fit_1, 0, 1)
max_fit_2 = np.clip(max_fit_2, 0, 1)
avg_fit_2 = np.clip(avg_fit_2, 0, 1)
max_fit_3 = np.clip(max_fit_3, 0, 1)
avg_fit_3 = np.clip(avg_fit_3, 0, 1)

# Crear la figura
plt.figure(figsize=(10, 6))

# Graficar los datos
generations = np.arange(1, num_generations + 1)

# Caso 1: Estudiante regular
plt.plot(generations, max_fit_1, 'b-', linewidth=2, label='Máximo (Estudiante Regular)')
plt.plot(generations, avg_fit_1, 'b--', alpha=0.6, linewidth=1.5, label='Promedio (Estudiante Regular)')

# Caso 2: Estudiante semi-irregular
plt.plot(generations, max_fit_2, 'g-', linewidth=2, label='Máximo (Estudiante Semi-irregular)')
plt.plot(generations, avg_fit_2, 'g--', alpha=0.6, linewidth=1.5, label='Promedio (Estudiante Semi-irregular)')

# Caso 3: Estudiante irregular
plt.plot(generations, max_fit_3, 'r-', linewidth=2, label='Máximo (Estudiante Irregular)')
plt.plot(generations, avg_fit_3, 'r--', alpha=0.6, linewidth=1.5, label='Promedio (Estudiante Irregular)')

# Añadir línea vertical en generación 30
plt.axvline(x=30, color='gray', linestyle=':', alpha=0.7, label='Generación predeterminada (30)')

# Configurar los ejes
plt.xlabel('Generación')
plt.ylabel('Valor de Fitness')
plt.title('Evolución de la Aptitud (Fitness) - Algoritmo Genético UNICARGA')
plt.xlim(1, num_generations)
plt.ylim(0.4, 1.0)
plt.grid(True, linestyle='--', alpha=0.7)

# Añadir anotaciones explicativas
plt.annotate('Convergencia típica', xy=(20, 0.87), xytext=(12, 0.75),
             arrowprops=dict(facecolor='black', shrink=0.05, alpha=0.7, width=1.5),
             fontsize=11)

plt.annotate('Mejoras marginales', xy=(30, 0.9), xytext=(25, 0.98),
             arrowprops=dict(facecolor='black', shrink=0.05, alpha=0.7, width=1.5),
             fontsize=11)

# Leyenda
plt.legend(loc='lower right', frameon=True, framealpha=0.9)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('convergencia_fitness_unicarga.png', dpi=300)
plt.show()