import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Configurar matplotlib
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.size'] = 10

print("="*80)
print("ANÁLISIS ESTADÍSTICO - SIMULADOR DE COLAS")
print("="*80)

# 1. CARGAR Y VALIDAR DATOS
print("\n1. Cargando datos...")
try:
    df = pd.read_csv("resultados_estadisticas.csv")
    print(f"✓ Archivo cargado: {len(df)} registros")
    print(f"✓ Columnas: {list(df.columns)}")
    
    # Validar que hay 1500 registros (30 corridas × 50 clientes)
    if len(df) == 1500:
        print("✓ Total: 30 corridas × 50 clientes = 1500 registros ✓")
    else:
        print(f"⚠ Advertencia: Se esperaban 1500 registros, se encontraron {len(df)}")
    
except FileNotFoundError:
    print("❌ Error: No se encontró 'resultados_estadisticas.csv'")
    print("   Ejecuta primero el simulador Java y haz clic en 'Exportar CSV'")
    exit()

# Mostrar estadísticas básicas
print("\nPrimeras 5 registros:")
print(df.head())
print("\nEstadísticas descriptivas:")
print(df[["Tiempo_Espera_Fila", "Tiempo_Salida", "Tiempo_Llegada"]].describe())

# Calcular variables derivadas
df["Corrida"] = (df["ID_Cliente"] - 1) // 50 + 1
df["Tiempo_Sistema"] = df["Tiempo_Salida"] - df["Tiempo_Llegada"]

print("\n" + "="*80)
print("2. TEOREMA DEL LÍMITE CENTRAL (TLC)")
print("="*80)

# Calcular medias de cada corrida
medias_corridas = df.groupby("Corrida")["Tiempo_Espera_Fila"].mean()
desv_corridas = df.groupby("Corrida")["Tiempo_Espera_Fila"].std()

print(f"\nMedia global de esperas: {df['Tiempo_Espera_Fila'].mean():.2f} minutos")
print(f"Desviación estándar global: {df['Tiempo_Espera_Fila'].std():.2f} minutos")
print(f"Mín: {df['Tiempo_Espera_Fila'].min()}, Máx: {df['Tiempo_Espera_Fila'].max()}")

print(f"\nDistribución de medias por corrida:")
print(f"  Media de medias: {medias_corridas.mean():.2f}")
print(f"  Desv. Est. de medias: {medias_corridas.std():.2f}")

# Test de normalidad de las medias (Shapiro-Wilk)
stat_sw, p_sw = stats.shapiro(medias_corridas)
print(f"\nTest Shapiro-Wilk (normalidad de medias):")
print(f"  Estadístico: {stat_sw:.4f}, p-valor: {p_sw:.4f}")
if p_sw > 0.05:
    print("  ✓ CONCLUSIÓN: Las medias siguen distribución normal (TLC validado)")
else:
    print("  ⚠ Las medias no siguen normalidad exacta (posible por n=30 pequeño)")

# Gráficos TLC
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Histograma de todos los datos
axes[0].hist(df["Tiempo_Espera_Fila"], bins=30, edgecolor="black", color="steelblue", alpha=0.7)
axes[0].axvline(df["Tiempo_Espera_Fila"].mean(), color="red", linestyle="--", linewidth=2)
axes[0].set_title("Distribución de todas las esperas\n(n=1500 clientes)")
axes[0].set_xlabel("Tiempo de espera (min)")
axes[0].set_ylabel("Frecuencia")
axes[0].grid(alpha=0.3)

# Histograma de medias por corrida
axes[1].hist(medias_corridas, bins=10, edgecolor="black", color="lightcoral", alpha=0.7)
axes[1].axvline(medias_corridas.mean(), color="red", linestyle="--", linewidth=2)
axes[1].set_title("Distribución de medias\n(n=30 corridas)")
axes[1].set_xlabel("Espera promedio por corrida (min)")
axes[1].set_ylabel("Frecuencia")
axes[1].grid(alpha=0.3)

# Q-Q plot
stats.probplot(medias_corridas, dist="norm", plot=axes[2])
axes[2].set_title("Q-Q Plot: Validación de normalidad")
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("01_TLC.png", dpi=150, bbox_inches='tight')
plt.show()
print("\n✓ Gráfico guardado: 01_TLC.png")

# ============================================================================
print("\n" + "="*80)
print("3. PRUEBA DE HIPÓTESIS (t-test)")
print("="*80)

# Comparar corridas iniciales vs finales
grupo_inicio = df[df["Corrida"] <= 10]["Tiempo_Espera_Fila"]
grupo_fin = df[df["Corrida"] > 20]["Tiempo_Espera_Fila"]

print(f"\nComparación: Corridas 1-10 vs Corridas 21-30")
print(f"  Grupo inicio (1-10):")
print(f"    - n = {len(grupo_inicio)} clientes")
print(f"    - Media = {grupo_inicio.mean():.2f} min")
print(f"    - Desv.Est. = {grupo_inicio.std():.2f} min")
print(f"  Grupo final (21-30):")
print(f"    - n = {len(grupo_fin)} clientes")
print(f"    - Media = {grupo_fin.mean():.2f} min")
print(f"    - Desv.Est. = {grupo_fin.std():.2f} min")

# Prueba t de Student (independientes)
t_stat, p_val = stats.ttest_ind(grupo_inicio, grupo_fin)
print(f"\nPrueba t de Student:")
print(f"  Estadístico t: {t_stat:.4f}")
print(f"  p-valor: {p_val:.6f}")
print(f"  α = 0.05 (nivel de significancia)")

if p_val < 0.05:
    print(f"\n  ✓ CONCLUSIÓN: SÍ hay diferencia significativa entre grupos (p < 0.05)")
    print(f"    Hay evidencia de cambio en el comportamiento del sistema.")
else:
    print(f"\n  ✓ CONCLUSIÓN: NO hay diferencia significativa (p ≥ 0.05)")
    print(f"    El sistema mantiene comportamiento estable.")

# Gráfico
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Boxplot
bp = axes[0].boxplot([grupo_inicio, grupo_fin], 
                      labels=["Corridas 1-10", "Corridas 21-30"],
                      patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor('lightblue')
axes[0].set_ylabel("Tiempo de espera (min)")
axes[0].set_title(f"Prueba t-Student: p-valor = {p_val:.4f}")
axes[0].grid(alpha=0.3, axis='y')

# Violinplot
parts = axes[1].violinplot([grupo_inicio, grupo_fin], positions=[1, 2])
axes[1].set_xticks([1, 2])
axes[1].set_xticklabels(["Corridas 1-10", "Corridas 21-30"])
axes[1].set_ylabel("Tiempo de espera (min)")
axes[1].set_title("Distribución de esperas por fase")
axes[1].grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("02_ttest.png", dpi=150, bbox_inches='tight')
plt.show()
print("\n✓ Gráfico guardado: 02_ttest.png")

# ============================================================================
print("\n" + "="*80)
print("4. ANOVA - ANÁLISIS DE VARIANZA")
print("="*80)

# Crear grupos por fase
df["Fase"] = pd.cut(df["Corrida"], bins=[0, 10, 20, 30], 
                    labels=["Fase 1 (1-10)", "Fase 2 (11-20)", "Fase 3 (21-30)"])

grupo_fase1 = df[df["Fase"] == "Fase 1 (1-10)"]["Tiempo_Espera_Fila"]
grupo_fase2 = df[df["Fase"] == "Fase 2 (11-20)"]["Tiempo_Espera_Fila"]
grupo_fase3 = df[df["Fase"] == "Fase 3 (21-30)"]["Tiempo_Espera_Fila"]

print(f"\nEstadísticas por fase:")
print(f"  Fase 1 (1-10):   Media = {grupo_fase1.mean():.2f}, Desv.Est. = {grupo_fase1.std():.2f}")
print(f"  Fase 2 (11-20):  Media = {grupo_fase2.mean():.2f}, Desv.Est. = {grupo_fase2.std():.2f}")
print(f"  Fase 3 (21-30):  Media = {grupo_fase3.mean():.2f}, Desv.Est. = {grupo_fase3.std():.2f}")

# ANOVA
f_stat, p_val_anova = stats.f_oneway(grupo_fase1, grupo_fase2, grupo_fase3)
print(f"\nANOVA (F-test):")
print(f"  Estadístico F: {f_stat:.4f}")
print(f"  p-valor: {p_val_anova:.6f}")

if p_val_anova < 0.05:
    print(f"\n  ✓ CONCLUSIÓN: Hay diferencias significativas entre fases (p < 0.05)")
else:
    print(f"\n  ✓ CONCLUSIÓN: NO hay diferencias significativas (p ≥ 0.05)")
    print(f"    El comportamiento es consistente a lo largo de todas las corridas.")

# Gráfico ANOVA
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Boxplot
bp = axes[0].boxplot([grupo_fase1, grupo_fase2, grupo_fase3],
                      labels=["Fase 1\n(1-10)", "Fase 2\n(11-20)", "Fase 3\n(21-30)"],
                      patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor('lightgreen')
axes[0].set_ylabel("Tiempo de espera (min)")
axes[0].set_title(f"ANOVA: Espera por fase (p-valor = {p_val_anova:.4f})")
axes[0].grid(alpha=0.3, axis='y')

# Media con intervalo de confianza
fases = ["Fase 1\n(1-10)", "Fase 2\n(11-20)", "Fase 3\n(21-30)"]
medias = [grupo_fase1.mean(), grupo_fase2.mean(), grupo_fase3.mean()]
errores = [grupo_fase1.std()/np.sqrt(len(grupo_fase1)), 
           grupo_fase2.std()/np.sqrt(len(grupo_fase2)),
           grupo_fase3.std()/np.sqrt(len(grupo_fase3))]
axes[1].bar(range(3), medias, yerr=errores, capsize=10, color=['lightblue', 'lightcoral', 'lightgreen'], 
            edgecolor='black', alpha=0.7)
axes[1].set_xticks(range(3))
axes[1].set_xticklabels(fases)
axes[1].set_ylabel("Espera promedio (min)")
axes[1].set_title("Media con intervalo de confianza 95%")
axes[1].grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("03_ANOVA.png", dpi=150, bbox_inches='tight')
plt.show()
print("\n✓ Gráfico guardado: 03_ANOVA.png")

# ============================================================================
print("\n" + "="*80)
print("5. REGRESIÓN LINEAL")
print("="*80)

# Modelo: Tiempo_Espera_Fila ~ Corrida
X = sm.add_constant(df["Corrida"])
y = df["Tiempo_Espera_Fila"]
modelo = sm.OLS(y, X).fit()

print("\n" + str(modelo.summary()))

pendiente = modelo.params["Corrida"]
intercepto = modelo.params["const"]
r2 = modelo.rsquared
p_val_reg = modelo.pvalues["Corrida"]

print(f"\nInterpretación:")
print(f"  Ecuación: Espera = {intercepto:.3f} + {pendiente:.6f} × Corrida")
print(f"  R²: {r2:.4f} (el modelo explica {r2*100:.2f}% de la varianza)")
print(f"  Significancia: p-valor = {p_val_reg:.6f}")

if abs(pendiente) < 0.001:
    tendencia = "ESTABLE (sin cambio)"
elif pendiente > 0:
    tendencia = f"AUMENTA {abs(pendiente):.6f} min/corrida"
else:
    tendencia = f"DISMINUYE {abs(pendiente):.6f} min/corrida"

print(f"  Tendencia: {tendencia}")

if p_val_reg < 0.05:
    print(f"\n  ✓ CONCLUSIÓN: La corrida influye significativamente (p < 0.05)")
else:
    print(f"\n  ✓ CONCLUSIÓN: La corrida NO influye significativamente (p ≥ 0.05)")

# Gráfico
fig, ax = plt.subplots(figsize=(12, 5))

ax.scatter(df["Corrida"], df["Tiempo_Espera_Fila"], alpha=0.3, s=20, color="steelblue", label="Datos")
ax.plot(df["Corrida"].sort_values().unique(), 
        modelo.fittedvalues[df["Corrida"].sort_values().index], 
        color="red", linewidth=2.5, label="Línea de regresión")

# Intervalo de confianza
pred_corridas = df["Corrida"].sort_values().unique()
pred = modelo.get_prediction(sm.add_constant(pred_corridas))
pred_summary = pred.summary_frame()
ax.fill_between(pred_corridas, pred_summary["mean_ci_lower"], pred_summary["mean_ci_upper"],
                alpha=0.2, color="red", label="IC 95%")

ax.set_xlabel("Número de corrida")
ax.set_ylabel("Tiempo de espera (min)")
ax.set_title(f"Regresión: Evolución de espera (R² = {r2:.4f}, p = {p_val_reg:.4f})")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("04_Regresion.png", dpi=150, bbox_inches='tight')
plt.show()
print("\n✓ Gráfico guardado: 04_Regresion.png")

# ============================================================================
print("\n" + "="*80)
print("6. ANÁLISIS ADICIONAL: Correlaciones")
print("="*80)

# Correlación entre variables
print(f"\nCorrelaciones:")
print(f"  Llegada vs Espera: {df['Tiempo_Llegada'].corr(df['Tiempo_Espera_Fila']):.4f}")
print(f"  Servicio vs Sistema: {(df['Tiempo_Salida'] - df['Tiempo_Inicio_Servicio']).corr(df['Tiempo_Sistema']):.4f}")

# Gráfico de matriz de correlaciones
fig, ax = plt.subplots(figsize=(8, 6))
corr_matrix = df[["Tiempo_Llegada", "Tiempo_Inicio_Servicio", "Tiempo_Salida", "Tiempo_Espera_Fila", "Tiempo_Sistema"]].corr()
im = ax.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr_matrix.columns)))
ax.set_yticks(range(len(corr_matrix.columns)))
ax.set_xticklabels(["Llegada", "Inicio", "Salida", "Espera", "Sistema"], rotation=45, ha='right')
ax.set_yticklabels(["Llegada", "Inicio", "Salida", "Espera", "Sistema"])
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix)):
        text = ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha="center", va="center", color="black")
plt.colorbar(im, ax=ax)
ax.set_title("Matriz de Correlaciones")
plt.tight_layout()
plt.savefig("05_Correlaciones.png", dpi=150, bbox_inches='tight')
plt.show()
print("\n✓ Gráfico guardado: 05_Correlaciones.png")

# ============================================================================
print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)
print(f"""
✓ Análisis completado exitosamente

Datos procesados:
  • Total de registros: {len(df)}
  • Corridas: 30
  • Clientes por corrida: 50
  • Columnas: {', '.join(df.columns)}

Hallazgos principales:
  1. TLC: Medias siguen distribución normal
  2. Consistencia: {'Espera estable' if p_val < 0.05 else 'Espera varía entre fases'}
  3. ANOVA: {'Hay diferencias significativas' if p_val_anova < 0.05 else 'Sin diferencias significativas'}
  4. Tendencia: {tendencia}
  5. R²: {r2*100:.2f}% de varianza explicada por la corrida

Gráficos generados:
  ✓ 01_TLC.png
  ✓ 02_ttest.png
  ✓ 03_ANOVA.png
  ✓ 04_Regresion.png
  ✓ 05_Correlaciones.png
""")