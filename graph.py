import pandas as pd
import matplotlib.pyplot as plt
import sys

# Cargar los datos desde el archivo CSV
df = pd.read_csv(sys.argv[1], delimiter=';')

df = df.iloc[1:-1]

# Crear el gráfico de líneas
plt.figure(figsize=(10, 6))
plt.plot(df['TIME'], df['CPU'])

# Configurar las etiquetas del eje X para mostrar solo el inicio y el final
plt.xticks([df['TIME'].iloc[0], df['TIME'].iloc[-1]], labels=[df['TIME'].iloc[0], df['TIME'].iloc[-1]])

plt.xlabel('TIME')
plt.ylabel('CPU')
plt.ylim(df['CPU'].min(), df['CPU'].max() + 1)  # Ajuste dinámico con un margen de 5 unidades
plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
plt.title('CPU Usage')
plt.suptitle(f"Average CPU usage: {round(df['CPU'].mean(), 2)}%, Standard deviation: {round(df['CPU'].std(), 2)}")

# Guardar el gráfico en un archivo
plt.savefig(sys.argv[2])
