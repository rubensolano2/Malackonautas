"""
ANÁLISIS EXPLORATORIO DE DATOS (ADA) - SALUD MENTAL
Solo con: pandas, numpy y matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# 1. CARGAR DATOS
# ============================================
print("="*80)
print("ANÁLISIS EXPLORATORIO DE DATOS - SALUD MENTAL")
print("="*80)

# Cargar archivo - usa la ruta completa que tengas
df = pd.read_excel(r"C:\Users\ruben\Desktop\hackaton\SaludMental.xls", 
                   sheet_name='enfermedadesMentalesDiagnostico')

print(f"\n✓ Datos cargados: {df.shape[0]:,} filas x {df.shape[1]} columnas")

# ============================================
# 2. INFORMACIÓN BÁSICA
# ============================================
print("\n" + "="*80)
print("INFORMACIÓN BÁSICA")
print("="*80)

print("\n--- Columnas del dataset ---")
print(df.columns.tolist())

print("\n--- Tipos de datos ---")
print(df.dtypes)

print("\n--- Primeras 3 filas ---")
print(df.head(3))

# ============================================
# 3. VALORES NULOS
# ============================================
print("\n" + "="*80)
print("VALORES NULOS")
print("="*80)

nulos = df.isnull().sum()
nulos_pct = (nulos / len(df)) * 100

print("\nColumnas con valores nulos:")
for col in df.columns:
    if nulos[col] > 0:
        print(f"{col}: {nulos[col]:,} ({nulos_pct[col]:.2f}%)")

print(f"\nDuplicados: {df.duplicated().sum():,}")

# ============================================
# 4. ESTADÍSTICAS NUMÉRICAS
# ============================================
print("\n" + "="*80)
print("ESTADÍSTICAS DE VARIABLES NUMÉRICAS")
print("="*80)

print(df.describe())

# ============================================
# 5. ANÁLISIS DEMOGRÁFICO
# ============================================
print("\n" + "="*80)
print("ANÁLISIS DEMOGRÁFICO")
print("="*80)

# Sexo
print("\n--- Distribución por Sexo ---")
print(df['Sexo'].value_counts())
print("\nPorcentaje:")
print(df['Sexo'].value_counts(normalize=True) * 100)

# Edad
print("\n--- Edad ---")
print(f"Mínima: {df['Edad'].min()}")
print(f"Máxima: {df['Edad'].max()}")
print(f"Media: {df['Edad'].mean():.2f}")
print(f"Mediana: {df['Edad'].median():.2f}")

# Comunidades
print("\n--- Top 10 Comunidades Autónomas ---")
print(df['Comunidad Autónoma'].value_counts().head(10))

# ============================================
# 6. ANÁLISIS CLÍNICO
# ============================================
print("\n" + "="*80)
print("ANÁLISIS CLÍNICO")
print("="*80)

# Categorías
print("\n--- Top 10 Categorías de Diagnóstico ---")
top_cat = df['Categoría'].value_counts().head(10)
print(top_cat)
print("\nPorcentaje:")
print((top_cat / len(df) * 100).round(2))

# Diagnósticos
print("\n--- Top 10 Diagnósticos Principales ---")
print(df['Diagnóstico Principal'].value_counts().head(10))

# Estancia
print("\n--- Estancia Hospitalaria (días) ---")
print(f"Mínima: {df['Estancia Días'].min()}")
print(f"Máxima: {df['Estancia Días'].max()}")
print(f"Media: {df['Estancia Días'].mean():.2f}")
print(f"Mediana: {df['Estancia Días'].median():.2f}")

# Severidad
print("\n--- Nivel de Severidad APR ---")
print(df['Nivel Severidad APR'].value_counts().sort_index())

# Mortalidad
print("\n--- Riesgo de Mortalidad APR ---")
print(df['Riesgo Mortalidad APR'].value_counts().sort_index())

# ============================================
# 7. ANÁLISIS ECONÓMICO
# ============================================
print("\n" + "="*80)
print("ANÁLISIS ECONÓMICO")
print("="*80)

print("\n--- Costes APR ---")
print(f"Total: ${df['Coste APR'].sum():,.2f}")
print(f"Media: ${df['Coste APR'].mean():,.2f}")
print(f"Mediana: ${df['Coste APR'].median():,.2f}")
print(f"Mínimo: ${df['Coste APR'].min():,.2f}")
print(f"Máximo: ${df['Coste APR'].max():,.2f}")

# Coste por categoría
print("\n--- Coste por Categoría (Top 10) ---")
coste_cat = df.groupby('Categoría')['Coste APR'].agg(['mean', 'sum', 'count'])
coste_cat = coste_cat.sort_values('sum', ascending=False).head(10)
print(coste_cat)

# ============================================
# 8. ANÁLISIS TEMPORAL
# ============================================
print("\n" + "="*80)
print("ANÁLISIS TEMPORAL")
print("="*80)

df['Mes de Ingreso'] = pd.to_datetime(df['Mes de Ingreso'])
df['Año'] = df['Mes de Ingreso'].dt.year

print("\n--- Casos por Año ---")
print(df['Año'].value_counts().sort_index())

# ============================================
# 9. SERVICIOS
# ============================================
print("\n" + "="*80)
print("SERVICIOS")
print("="*80)

print("\n--- Distribución por Servicio ---")
print(df['Servicio'].value_counts())

# ============================================
# 10. CORRELACIONES
# ============================================
print("\n" + "="*80)
print("CORRELACIONES")
print("="*80)

# Variables principales
vars_num = ['Edad', 'Estancia Días', 'Coste APR', 'Nivel Severidad APR', 'Riesgo Mortalidad APR']

print("\n--- Correlaciones entre variables principales ---")
corr_matrix = df[vars_num].corr()
print(corr_matrix)

# ============================================
# 11. ANÁLISIS POR SEXO
# ============================================
print("\n" + "="*80)
print("COMPARACIÓN POR SEXO")
print("="*80)

print("\n--- Estadísticas por Sexo ---")
for sexo in [1, 2]:
    print(f"\nSexo {sexo}:")
    subset = df[df['Sexo'] == sexo]
    print(f"  Casos: {len(subset):,}")
    print(f"  Edad media: {subset['Edad'].mean():.2f}")
    print(f"  Estancia media: {subset['Estancia Días'].mean():.2f}")
    print(f"  Coste medio: ${subset['Coste APR'].mean():,.2f}")

# ============================================
# 12. RESUMEN Y HALLAZGOS
# ============================================
print("\n" + "="*80)
print("RESUMEN Y HALLAZGOS CLAVE")
print("="*80)

print(f"\n✓ Total de registros: {len(df):,}")
print(f"✓ Período: {df['Mes de Ingreso'].min().strftime('%Y-%m')} a {df['Mes de Ingreso'].max().strftime('%Y-%m')}")
print(f"✓ Edad promedio: {df['Edad'].mean():.1f} años")
print(f"✓ Estancia media: {df['Estancia Días'].mean():.1f} días")
print(f"✓ Coste total: ${df['Coste APR'].sum():,.2f}")
print(f"✓ Coste promedio: ${df['Coste APR'].mean():,.2f}")

# Grupos de riesgo
alto_riesgo = df[df['Riesgo Mortalidad APR'] >= 3]
print(f"\n✓ Pacientes alto riesgo mortalidad: {len(alto_riesgo):,} ({len(alto_riesgo)/len(df)*100:.2f}%)")

alta_severidad = df[df['Nivel Severidad APR'] >= 3]
print(f"✓ Casos alta severidad: {len(alta_severidad):,} ({len(alta_severidad)/len(df)*100:.2f}%)")

# ============================================
# 13. GRÁFICOS
# ============================================
print("\n" + "="*80)
print("GENERANDO GRÁFICOS")
print("="*80)

fig, axes = plt.subplots(3, 3, figsize=(15, 12))

# 1. Edad
axes[0, 0].hist(df['Edad'], bins=50, color='steelblue', edgecolor='black')
axes[0, 0].axvline(df['Edad'].mean(), color='red', linestyle='--', label='Media')
axes[0, 0].set_title('Distribución de Edad')
axes[0, 0].set_xlabel('Edad')
axes[0, 0].set_ylabel('Frecuencia')
axes[0, 0].legend()

# 2. Sexo
df['Sexo'].value_counts().plot(kind='bar', ax=axes[0, 1], color=['skyblue', 'pink'])
axes[0, 1].set_title('Distribución por Sexo')
axes[0, 1].set_xlabel('Sexo (1=H, 2=M)')
axes[0, 1].set_ylabel('Frecuencia')

# 3. Categorías
top_5_cat = df['Categoría'].value_counts().head(5)
axes[0, 2].barh(range(len(top_5_cat)), top_5_cat.values)
axes[0, 2].set_yticks(range(len(top_5_cat)))
axes[0, 2].set_yticklabels([c[:30] + '...' if len(c) > 30 else c for c in top_5_cat.index])
axes[0, 2].set_title('Top 5 Categorías')
axes[0, 2].set_xlabel('Casos')

# 4. Estancia
axes[1, 0].hist(df['Estancia Días'], bins=50, color='green', edgecolor='black')
axes[1, 0].axvline(df['Estancia Días'].mean(), color='red', linestyle='--', label='Media')
axes[1, 0].set_title('Distribución de Estancia')
axes[1, 0].set_xlabel('Días')
axes[1, 0].set_ylabel('Frecuencia')
axes[1, 0].set_xlim(0, 100)
axes[1, 0].legend()

# 5. Costes
axes[1, 1].hist(df['Coste APR'], bins=50, color='orange', edgecolor='black')
axes[1, 1].axvline(df['Coste APR'].mean(), color='red', linestyle='--', label='Media')
axes[1, 1].set_title('Distribución de Costes')
axes[1, 1].set_xlabel('Coste APR')
axes[1, 1].set_ylabel('Frecuencia')
axes[1, 1].legend()

# 6. Severidad
df['Nivel Severidad APR'].value_counts().sort_index().plot(kind='bar', ax=axes[1, 2], color='coral')
axes[1, 2].set_title('Nivel de Severidad')
axes[1, 2].set_xlabel('Nivel')
axes[1, 2].set_ylabel('Frecuencia')

# 7. Mortalidad
df['Riesgo Mortalidad APR'].value_counts().sort_index().plot(kind='bar', ax=axes[2, 0], color='crimson')
axes[2, 0].set_title('Riesgo de Mortalidad')
axes[2, 0].set_xlabel('Nivel')
axes[2, 0].set_ylabel('Frecuencia')

# 8. Casos por año
df['Año'].value_counts().sort_index().plot(kind='line', marker='o', ax=axes[2, 1], color='purple')
axes[2, 1].set_title('Casos por Año')
axes[2, 1].set_xlabel('Año')
axes[2, 1].set_ylabel('Casos')
axes[2, 1].grid(True)

# 9. Edad vs Estancia
axes[2, 2].scatter(df['Edad'], df['Estancia Días'], alpha=0.3, s=10)
axes[2, 2].set_title('Edad vs Estancia')
axes[2, 2].set_xlabel('Edad')
axes[2, 2].set_ylabel('Estancia (días)')
axes[2, 2].set_ylim(0, 100)

plt.tight_layout()
plt.savefig('analisis_salud_mental.png', dpi=150, bbox_inches='tight')
print("\n✓ Gráficos guardados en 'analisis_salud_mental.png'")
plt.show()

# ============================================
# 14. EXPORTAR RESULTADOS
# ============================================
print("\n" + "="*80)
print("EXPORTANDO RESULTADOS")
print("="*80)

# Resumen
resumen = pd.DataFrame({
    'Métrica': ['Total Registros', 'Edad Media', 'Estancia Media', 
                'Coste Total', 'Coste Medio'],
    'Valor': [len(df), df['Edad'].mean(), df['Estancia Días'].mean(),
              df['Coste APR'].sum(), df['Coste APR'].mean()]
})
resumen.to_csv('resumen.csv', index=False)
print("✓ Resumen guardado en 'resumen.csv'")

# Top categorías
df['Categoría'].value_counts().to_csv('categorias.csv')
print("✓ Categorías guardadas en 'categorias.csv'")

print("\n" + "="*80)
print("✅ ANÁLISIS COMPLETADO")
print("="*80)