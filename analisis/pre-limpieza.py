"""
LIMPIEZA PROFESIONAL DE DATOS - SALUD MENTAL
Detección de anomalías, outliers, inconsistencias y problemas de calidad
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ============================================
# 1. CARGAR DATOS
# ============================================
print("="*80)
print("LIMPIEZA PROFESIONAL DE DATOS - SALUD MENTAL")
print("="*80)

df = pd.read_excel(r"C:\Users\ruben\Desktop\hackaton\SaludMental.xls", 
                   sheet_name='enfermedadesMentalesDiagnostico')

print(f"\n✓ Dataset cargado: {df.shape[0]:,} filas x {df.shape[1]} columnas")

# Crear copia para trabajar
df_original = df.copy()
problemas = []  # Lista para registrar todos los problemas encontrados

# ============================================
# 2. ANÁLISIS DE VALORES NULOS
# ============================================
print("\n" + "="*80)
print("1. ANÁLISIS DE VALORES NULOS Y VACÍOS")
print("="*80)

nulos = df.isnull().sum()
nulos_pct = (nulos / len(df)) * 100

print("\n--- Columnas con valores nulos ---")
cols_con_nulos = nulos[nulos > 0].sort_values(ascending=False)
if len(cols_con_nulos) > 0:
    for col, count in cols_con_nulos.items():
        pct = nulos_pct[col]
        print(f"  {col}: {count:,} ({pct:.2f}%)")
        if pct > 50:
            problemas.append(f"⚠️ CRÍTICO: '{col}' tiene {pct:.2f}% de valores nulos")
        elif pct > 10:
            problemas.append(f"⚠️ '{col}' tiene {pct:.2f}% de valores nulos")
else:
    print("  ✓ No se encontraron valores nulos")

# Valores en blanco (strings vacíos)
print("\n--- Verificando strings vacíos ---")
for col in df.select_dtypes(include=['object']).columns:
    blancos = (df[col] == '').sum()
    if blancos > 0:
        print(f"  {col}: {blancos:,} valores vacíos")
        problemas.append(f"'{col}' contiene {blancos:,} strings vacíos")

# ============================================
# 3. DUPLICADOS
# ============================================
print("\n" + "="*80)
print("2. ANÁLISIS DE DUPLICADOS")
print("="*80)

duplicados_totales = df.duplicated().sum()
print(f"\nFilas completamente duplicadas: {duplicados_totales:,}")

if duplicados_totales > 0:
    problemas.append(f"⚠️ Encontradas {duplicados_totales:,} filas duplicadas")
    print("\nEjemplo de duplicados:")
    print(df[df.duplicated(keep=False)].head(2))

# Duplicados por ID de paciente
if 'CIP SNS Recodificado' in df.columns:
    dup_pacientes = df['CIP SNS Recodificado'].duplicated().sum()
    print(f"\nPacientes con múltiples registros: {dup_pacientes:,}")
    if dup_pacientes > 0:
        print("  ✓ Esto es normal (un paciente puede tener varios ingresos)")

# ============================================
# 4. VALIDACIÓN DE RANGOS LÓGICOS
# ============================================
print("\n" + "="*80)
print("3. VALIDACIÓN DE RANGOS LÓGICOS")
print("="*80)

# Edad
print("\n--- Edad ---")
print(f"Rango: {df['Edad'].min()} - {df['Edad'].max()} años")
edad_invalida = df[(df['Edad'] < 0) | (df['Edad'] > 120)]
if len(edad_invalida) > 0:
    problemas.append(f"⚠️ CRÍTICO: {len(edad_invalida)} registros con edad inválida")
    print(f"  ⚠️ {len(edad_invalida)} registros con edad fuera de rango válido (0-120)")
else:
    print("  ✓ Todas las edades están en rango válido")

# Edades extremas
edad_ninos = df[df['Edad'] < 18]
edad_ancianos = df[df['Edad'] > 90]
print(f"  • Menores de 18 años: {len(edad_ninos):,} ({len(edad_ninos)/len(df)*100:.2f}%)")
print(f"  • Mayores de 90 años: {len(edad_ancianos):,} ({len(edad_ancianos)/len(df)*100:.2f}%)")

# Estancia Días
print("\n--- Estancia Días ---")
print(f"Rango: {df['Estancia Días'].min()} - {df['Estancia Días'].max()} días")
estancia_invalida = df[df['Estancia Días'] < 0]
if len(estancia_invalida) > 0:
    problemas.append(f"⚠️ CRÍTICO: {len(estancia_invalida)} registros con estancia negativa")
    print(f"  ⚠️ {len(estancia_invalida)} registros con estancia negativa")
else:
    print("  ✓ No hay estancias negativas")

# Estancias muy largas (posibles outliers)
estancia_larga = df[df['Estancia Días'] > 365]
if len(estancia_larga) > 0:
    print(f"  ⚠️ {len(estancia_larga)} registros con estancia > 1 año (max: {df['Estancia Días'].max()} días)")
    problemas.append(f"{len(estancia_larga)} registros con estancia > 365 días")

# Estancias de 0 días
estancia_cero = df[df['Estancia Días'] == 0]
if len(estancia_cero) > 0:
    print(f"  • {len(estancia_cero)} registros con estancia de 0 días")

# Coste APR
print("\n--- Coste APR ---")
print(f"Rango: ${df['Coste APR'].min():,.2f} - ${df['Coste APR'].max():,.2f}")
coste_invalido = df[(df['Coste APR'] < 0) | (df['Coste APR'] > 1000000)]
if len(coste_invalido) > 0:
    problemas.append(f"⚠️ {len(coste_invalido)} registros con coste sospechoso")
    print(f"  ⚠️ {len(coste_invalido)} registros con coste fuera de rango esperado")
else:
    print("  ✓ Todos los costes están en rango razonable")

coste_cero = df[df['Coste APR'] == 0]
if len(coste_cero) > 0:
    print(f"  ⚠️ {len(coste_cero)} registros con coste = 0")
    problemas.append(f"{len(coste_cero)} registros con coste = 0")

# Severidad y Mortalidad
print("\n--- Nivel Severidad APR ---")
severidad_unica = df['Nivel Severidad APR'].unique()
print(f"Valores únicos: {sorted(severidad_unica)}")
severidad_invalida = df[(df['Nivel Severidad APR'] < 1) | (df['Nivel Severidad APR'] > 4)]
if len(severidad_invalida) > 0:
    problemas.append(f"⚠️ CRÍTICO: {len(severidad_invalida)} registros con severidad fuera de rango 1-4")

print("\n--- Riesgo Mortalidad APR ---")
mortalidad_unica = df['Riesgo Mortalidad APR'].unique()
print(f"Valores únicos: {sorted(mortalidad_unica)}")
mortalidad_invalida = df[(df['Riesgo Mortalidad APR'] < 1) | (df['Riesgo Mortalidad APR'] > 4)]
if len(mortalidad_invalida) > 0:
    problemas.append(f"⚠️ CRÍTICO: {len(mortalidad_invalida)} registros con mortalidad fuera de rango 1-4")

# Sexo
print("\n--- Sexo ---")
sexo_unico = df['Sexo'].value_counts()
print(sexo_unico)
sexo_invalido = df[~df['Sexo'].isin([1, 2])]
if len(sexo_invalido) > 0:
    problemas.append(f"⚠️ CRÍTICO: {len(sexo_invalido)} registros con sexo inválido")

# ============================================
# 5. DETECCIÓN DE OUTLIERS (MÉTODO IQR)
# ============================================
print("\n" + "="*80)
print("4. DETECCIÓN DE OUTLIERS (Método IQR)")
print("="*80)

def detectar_outliers_iqr(data, columna):
    Q1 = data[columna].quantile(0.25)
    Q3 = data[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    outliers = data[(data[columna] < limite_inferior) | (data[columna] > limite_superior)]
    return outliers, limite_inferior, limite_superior

columnas_numericas = ['Edad', 'Estancia Días', 'Coste APR', 'Peso Español APR']

for col in columnas_numericas:
    if col in df.columns:
        outliers, lim_inf, lim_sup = detectar_outliers_iqr(df, col)
        pct_outliers = (len(outliers) / len(df)) * 100
        print(f"\n--- {col} ---")
        print(f"Límites IQR: [{lim_inf:.2f}, {lim_sup:.2f}]")
        print(f"Outliers detectados: {len(outliers):,} ({pct_outliers:.2f}%)")
        if pct_outliers > 5:
            problemas.append(f"{col} tiene {pct_outliers:.2f}% de outliers")
        if len(outliers) > 0:
            print(f"  • Valor mínimo outlier: {outliers[col].min():.2f}")
            print(f"  • Valor máximo outlier: {outliers[col].max():.2f}")

# ============================================
# 6. CONSISTENCIA ENTRE FECHAS
# ============================================
print("\n" + "="*80)
print("5. VALIDACIÓN DE FECHAS Y CONSISTENCIA TEMPORAL")
print("="*80)

# Convertir fechas
df['Fecha de Ingreso'] = pd.to_datetime(df['Fecha de Ingreso'], errors='coerce')
df['Fecha de nacimiento'] = pd.to_datetime(df['Fecha de nacimiento'], errors='coerce')

# Validar edad calculada vs edad registrada
print("\n--- Validación de Edad ---")
df['Edad Calculada'] = (df['Fecha de Ingreso'] - df['Fecha de nacimiento']).dt.days / 365.25
df['Diferencia Edad'] = abs(df['Edad'] - df['Edad Calculada'])

edad_inconsistente = df[df['Diferencia Edad'] > 1]  # Más de 1 año de diferencia
if len(edad_inconsistente) > 0:
    print(f"  ⚠️ {len(edad_inconsistente):,} registros con discrepancia en edad > 1 año")
    problemas.append(f"{len(edad_inconsistente):,} registros con edad inconsistente")
else:
    print("  ✓ Las edades son consistentes con las fechas de nacimiento")

# Fecha de nacimiento futura o muy antigua
fn_invalida = df[
    (df['Fecha de nacimiento'] > datetime.now()) | 
    (df['Fecha de nacimiento'] < pd.to_datetime('1900-01-01'))
]
if len(fn_invalida) > 0:
    print(f"  ⚠️ {len(fn_invalida)} registros con fecha de nacimiento inválida")
    problemas.append(f"{len(fn_invalida)} registros con fecha nacimiento inválida")

# ============================================
# 7. ANÁLISIS DE DIAGNÓSTICOS
# ============================================
print("\n" + "="*80)
print("6. VALIDACIÓN DE DIAGNÓSTICOS")
print("="*80)

# Diagnósticos vacíos
diag_vacio = df[df['Diagnóstico Principal'].isnull()]
print(f"\n--- Diagnóstico Principal ---")
print(f"Registros sin diagnóstico: {len(diag_vacio):,}")
if len(diag_vacio) > 0:
    problemas.append(f"⚠️ CRÍTICO: {len(diag_vacio)} registros sin diagnóstico principal")

# Formato de códigos CIE-10 (deben empezar con letra)
diag_formato_invalido = df[~df['Diagnóstico Principal'].astype(str).str.match(r'^[A-Z]\d', na=False)]
print(f"Diagnósticos con formato sospechoso: {len(diag_formato_invalido):,}")

# Categoría vs Diagnóstico Principal - verificar consistencia
print("\n--- Consistencia Categoría vs Diagnóstico ---")
# Los códigos F son de salud mental
diag_f = df[df['Diagnóstico Principal'].astype(str).str.startswith('F', na=False)]
print(f"Diagnósticos con código F (Salud Mental): {len(diag_f):,} ({len(diag_f)/len(df)*100:.2f}%)")

diag_no_f = df[~df['Diagnóstico Principal'].astype(str).str.startswith('F', na=False)]
print(f"Diagnósticos SIN código F: {len(diag_no_f):,} ({len(diag_no_f)/len(df)*100:.2f}%)")
if len(diag_no_f) > 100:
    print(f"  ℹ️ Verificar si estos casos son correctos (enfermedades no mentales en dataset de salud mental)")

# ============================================
# 8. CORRELACIONES SOSPECHOSAS
# ============================================
print("\n" + "="*80)
print("7. ANÁLISIS DE CORRELACIONES Y RELACIONES LÓGICAS")
print("="*80)

# Correlación Estancia vs Coste (debería ser alta)
corr_estancia_coste = df['Estancia Días'].corr(df['Coste APR'])
print(f"\n--- Correlación Estancia-Coste: {corr_estancia_coste:.4f} ---")
if corr_estancia_coste < 0.3:
    problemas.append(f"⚠️ Correlación baja entre Estancia y Coste ({corr_estancia_coste:.4f})")
    print("  ⚠️ Correlación más baja de lo esperado")
else:
    print("  ✓ Correlación razonable")

# Severidad vs Coste (severidad alta debería tener coste alto)
print("\n--- Coste promedio por Nivel de Severidad ---")
coste_severidad = df.groupby('Nivel Severidad APR')['Coste APR'].mean().sort_index()
print(coste_severidad)
# Verificar si aumenta consistentemente
if not coste_severidad.is_monotonic_increasing:
    print("  ⚠️ El coste no aumenta consistentemente con la severidad")
    problemas.append("Coste no aumenta consistentemente con severidad")

# ============================================
# 9. VALORES ESTADÍSTICAMENTE EXTREMOS
# ============================================
print("\n" + "="*80)
print("8. VALORES ESTADÍSTICAMENTE EXTREMOS (Z-score > 3)")
print("="*80)

def detectar_extremos_zscore(data, columna, umbral=3):
    mean = data[columna].mean()
    std = data[columna].std()
    z_scores = np.abs((data[columna] - mean) / std)
    extremos = data[z_scores > umbral]
    return extremos

for col in ['Edad', 'Estancia Días', 'Coste APR']:
    extremos = detectar_extremos_zscore(df, col)
    pct_extremos = (len(extremos) / len(df)) * 100
    print(f"\n{col}: {len(extremos):,} valores extremos ({pct_extremos:.2f}%)")
    if len(extremos) > 0:
        print(f"  • Rango extremos: {extremos[col].min():.2f} - {extremos[col].max():.2f}")

# ============================================
# 10. PATRONES SOSPECHOSOS
# ============================================
print("\n" + "="*80)
print("9. DETECCIÓN DE PATRONES SOSPECHOSOS")
print("="*80)

# Valores repetidos excesivamente
print("\n--- Valores que se repiten sospechosamente ---")
for col in ['Coste APR', 'Estancia Días']:
    valor_mas_comun = df[col].mode()[0]
    veces_repetido = (df[col] == valor_mas_comun).sum()
    pct = (veces_repetido / len(df)) * 100
    if pct > 10:
        print(f"{col}: Valor {valor_mas_comun} se repite {veces_repetido:,} veces ({pct:.2f}%)")
        problemas.append(f"{col} tiene valor {valor_mas_comun} repetido {pct:.2f}% de veces")

# Números redondos sospechosos en costes
costes_redondos = df[df['Coste APR'] % 1000 == 0]
pct_redondos = (len(costes_redondos) / len(df)) * 100
print(f"\nCostes múltiplos de 1000: {len(costes_redondos):,} ({pct_redondos:.2f}%)")
if pct_redondos > 20:
    print("  ⚠️ Porcentaje alto de costes redondeados (posible estimación)")

# ============================================
# 11. REPORTE FINAL
# ============================================
print("\n" + "="*80)
print("REPORTE FINAL DE LIMPIEZA")
print("="*80)

print(f"\n📊 RESUMEN:")
print(f"  • Total de registros analizados: {len(df):,}")
print(f"  • Total de problemas detectados: {len(problemas)}")

if len(problemas) > 0:
    print("\n🔍 PROBLEMAS ENCONTRADOS:")
    for i, problema in enumerate(problemas, 1):
        print(f"{i}. {problema}")
else:
    print("\n✅ No se encontraron problemas críticos en los datos")

# Calcular puntuación de calidad
puntuacion_calidad = 100 - min(len(problemas) * 5, 100)
print(f"\n📈 PUNTUACIÓN DE CALIDAD DE DATOS: {puntuacion_calidad}/100")

if puntuacion_calidad >= 80:
    print("   ✓ Excelente calidad de datos")
elif puntuacion_calidad >= 60:
    print("   ⚠️ Calidad aceptable - requiere limpieza menor")
else:
    print("   ⚠️ Calidad baja - requiere limpieza significativa")

# ============================================
# 12. RECOMENDACIONES
# ============================================
print("\n" + "="*80)
print("RECOMENDACIONES DE LIMPIEZA")
print("="*80)

print("\n1. ACCIONES INMEDIATAS:")
if len(cols_con_nulos) > 0:
    print("   • Imputar o eliminar valores nulos en columnas críticas")
if duplicados_totales > 0:
    print("   • Revisar y eliminar registros duplicados")
if 'edad_invalida' in locals() and len(edad_invalida) > 0:
    print("   • Corregir o eliminar registros con edad inválida")

print("\n2. VALIDACIONES ADICIONALES:")
print("   • Verificar consistencia entre severidad y costes")
print("   • Revisar casos de estancia > 365 días")
print("   • Validar diagnósticos no-F en dataset de salud mental")

print("\n3. ANÁLISIS POSTERIOR:")
print("   • Investigar outliers en estancia y costes")
print("   • Validar pacientes con múltiples ingresos")
print("   • Comparar datos con estándares hospitalarios")

# ============================================
# 13. VISUALIZACIÓN DE PROBLEMAS
# ============================================
print("\n" + "="*80)
print("GENERANDO VISUALIZACIONES DE PROBLEMAS")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('ANÁLISIS DE CALIDAD DE DATOS', fontsize=16, fontweight='bold')

# 1. Distribución de valores nulos
if len(cols_con_nulos) > 0:
    top_nulos = cols_con_nulos.head(10)
    axes[0, 0].barh(range(len(top_nulos)), top_nulos.values, color='salmon')
    axes[0, 0].set_yticks(range(len(top_nulos)))
    axes[0, 0].set_yticklabels([col[:20] for col in top_nulos.index], fontsize=8)
    axes[0, 0].set_xlabel('Cantidad de Nulos')
    axes[0, 0].set_title('Top 10 Columnas con Valores Nulos')
else:
    axes[0, 0].text(0.5, 0.5, 'Sin valores nulos', ha='center', va='center')
    axes[0, 0].set_title('Valores Nulos')

# 2. Outliers en Estancia
axes[0, 1].boxplot(df['Estancia Días'])
axes[0, 1].set_ylabel('Días')
axes[0, 1].set_title('Outliers en Estancia')
axes[0, 1].set_xticklabels(['Estancia'])

# 3. Outliers en Coste
axes[0, 2].boxplot(df['Coste APR'])
axes[0, 2].set_ylabel('Coste')
axes[0, 2].set_title('Outliers en Coste')
axes[0, 2].set_xticklabels(['Coste'])

# 4. Distribución de Severidad
severidad_counts = df['Nivel Severidad APR'].value_counts().sort_index()
axes[1, 0].bar(severidad_counts.index, severidad_counts.values, color='steelblue')
axes[1, 0].set_xlabel('Nivel de Severidad')
axes[1, 0].set_ylabel('Frecuencia')
axes[1, 0].set_title('Distribución de Severidad')

# 5. Relación Severidad-Coste
axes[1, 1].scatter(df['Nivel Severidad APR'], df['Coste APR'], alpha=0.3, s=10)
axes[1, 1].set_xlabel('Nivel Severidad')
axes[1, 1].set_ylabel('Coste APR')
axes[1, 1].set_title(f'Severidad vs Coste (r={corr_estancia_coste:.2f})')

# 6. Estancias extremas
estancia_rangos = pd.cut(df['Estancia Días'], bins=[0, 7, 14, 30, 60, 365, 1000], 
                         labels=['0-7d', '8-14d', '15-30d', '31-60d', '61-365d', '>365d'])
estancia_dist = estancia_rangos.value_counts().sort_index()
axes[1, 2].bar(range(len(estancia_dist)), estancia_dist.values, color='coral')
axes[1, 2].set_xticks(range(len(estancia_dist)))
axes[1, 2].set_xticklabels(estancia_dist.index, rotation=45)
axes[1, 2].set_ylabel('Frecuencia')
axes[1, 2].set_title('Distribución de Estancias por Rangos')

plt.tight_layout()
plt.savefig('reporte_calidad_datos.png', dpi=150, bbox_inches='tight')
print("✓ Visualizaciones guardadas en 'reporte_calidad_datos.png'")
plt.show()

# ============================================
# 14. EXPORTAR REPORTE
# ============================================
print("\n" + "="*80)
print("EXPORTANDO REPORTE DE LIMPIEZA")
print("="*80)

# Crear DataFrame de problemas
if len(problemas) > 0:
    df_problemas = pd.DataFrame({'Problema': problemas})
    df_problemas.to_csv('problemas_detectados.csv', index=False, encoding='utf-8-sig')
    print("✓ Problemas guardados en 'problemas_detectados.csv'")

# Estadísticas de calidad
stats_calidad = {
    'Total_Registros': len(df),
    'Registros_Completos': len(df.dropna()),
    'Pct_Completos': len(df.dropna())/len(df)*100,
    'Duplicados': duplicados_totales,
    'Problemas_Detectados': len(problemas),
    'Puntuacion_Calidad': puntuacion_calidad
}

df_stats = pd.DataFrame([stats_calidad])
df_stats.to_csv('estadisticas_calidad.csv', index=False, encoding='utf-8-sig')
print("✓ Estadísticas guardadas en 'estadisticas_calidad.csv'")

print("\n" + "="*80)
print("✅ LIMPIEZA Y ANÁLISIS DE CALIDAD COMPLETADO")
print("="*80)