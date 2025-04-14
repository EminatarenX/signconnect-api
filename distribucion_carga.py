# distribucion_carga.py
import numpy as np
import matplotlib.pyplot as plt

# Datos simulados: horas de clase por día
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
sin_optimizar = [8, 2, 6, 8, 0]  # Desbalanceado
optimizado_regular = [5, 4, 5, 5, 5]  # Bien balanceado
optimizado_irregular = [6, 6, 5, 4, 3]  # Razonablemente balanceado

# Crear figura y graficar los datos
plt.figure(figsize=(10, 6))

x = np.arange(len(dias))
width = 0.25

# Graficar barras para cada tipo de solución
plt.bar(x - width, sin_optimizar, width, label='Sin optimizar', color='lightcoral')
plt.bar(x, optimizado_regular, width, label='Optimizado (Regular)', color='lightgreen')
plt.bar(x + width, optimizado_irregular, width, label='Optimizado (Irregular)', color='lightskyblue')

# Configurar los ejes y etiquetas
plt.xlabel('Día de la semana', fontsize=12)
plt.ylabel('Horas de clase', fontsize=12)
plt.title('Distribución de Carga Académica por Día - UNICARGA', fontsize=14)
plt.xticks(x, dias)
plt.yticks(np.arange(0, 10, 1))

# Añadir valores sobre las barras
for i, v in enumerate(sin_optimizar):
    plt.text(i - width, v + 0.1, str(v), ha='center', va='bottom')
for i, v in enumerate(optimizado_regular):
    plt.text(i, v + 0.1, str(v), ha='center', va='bottom')
for i, v in enumerate(optimizado_irregular):
    plt.text(i + width, v + 0.1, str(v), ha='center', va='bottom')

# Añadir anotaciones explicativas
plt.annotate('Desbalance de carga', xy=(0 - width, 8), xytext=(-1, 9),
             arrowprops=dict(facecolor='red', shrink=0.05, alpha=0.7, width=1.5),
             fontsize=10, color='darkred')

plt.annotate('Carga equilibrada', xy=(2, 5), xytext=(2, 7),
             arrowprops=dict(facecolor='green', shrink=0.05, alpha=0.7, width=1.5),
             fontsize=10, color='darkgreen')

# Leyenda y cuadrícula
plt.legend(loc='upper right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('distribucion_carga_unicarga.png', dpi=300)
plt.show()