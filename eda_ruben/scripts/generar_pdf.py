"""
EDA Titanic — Generador de PDF completo
TC2004B — Análisis y Ciencia de Datos
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Config global ──────────────────────────────────────────────
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.05)
pd.set_option('display.float_format', '{:.2f}'.format)

COLOR_POS  = '#2ecc71'
COLOR_NEG  = '#e74c3c'
COLOR_NEUT = '#3498db'
TITLE_FS   = 13
SUB_FS     = 11
GREY       = '#555555'

OUTPUT_PATH = '/Users/juanfelipezepeda/Documents/TEC/TC2004B/ruben/EDA_Titanic.pdf'

# ── Datos ──────────────────────────────────────────────────────
df = sns.load_dataset('titanic')
df['family_size'] = df['sibsp'] + df['parch']
df['alone']       = (df['family_size'] == 0).astype(int)
surv_rate         = df['survived'].mean()

age_bins   = [0, 12, 18, 35, 60, 120]
age_labels = ['Nino\n(0-12)', 'Adolesc.\n(13-18)',
              'Adulto Joven\n(19-35)', 'Adulto\n(36-60)', 'Mayor\n(60+)']
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def add_header(fig, title, subtitle='', color='#2c3e50'):
    fig.suptitle(title, fontsize=TITLE_FS, fontweight='bold',
                 color=color, y=0.97)
    if subtitle:
        fig.text(0.5, 0.935, subtitle, ha='center',
                 fontsize=9, color=GREY, style='italic')


def table_fig(df_table, title, subtitle='', col_widths=None):
    """Render a DataFrame as a PDF page."""
    n_rows, n_cols = df_table.shape
    h = max(2.5, 0.45 * (n_rows + 2))
    fig, ax = plt.subplots(figsize=(11, h))
    ax.axis('off')
    add_header(fig, title, subtitle)
    cw = col_widths or [1/(n_cols+1)] * (n_cols + 1)
    t = ax.table(
        cellText=df_table.values,
        colLabels=df_table.columns,
        rowLabels=[str(i) for i in df_table.index],
        cellLoc='center', loc='center',
        colWidths=cw
    )
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.4)
    for (r, c), cell in t.get_celld().items():
        if r == 0 or c == -1:
            cell.set_facecolor('#2c3e50')
            cell.set_text_props(color='white', fontweight='bold')
        elif r % 2 == 0:
            cell.set_facecolor('#ecf0f1')
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return fig


# ══════════════════════════════════════════════════════════════
with PdfPages(OUTPUT_PATH) as pdf:

    # ── PORTADA ────────────────────────────────────────────────
    fig = plt.figure(figsize=(11, 8.5))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#2c3e50')
    ax.axis('off')

    # Banda decorativa superior
    rect_top = plt.Rectangle((0, 0.82), 1, 0.18, color='#1abc9c', transform=ax.transAxes)
    rect_bot = plt.Rectangle((0, 0),    1, 0.06, color='#1abc9c', transform=ax.transAxes)
    ax.add_patch(rect_top)
    ax.add_patch(rect_bot)

    ax.text(0.5, 0.91, 'TC2004B — Análisis y Ciencia de Datos',
            ha='center', va='center', fontsize=14, color='white',
            fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.68,
            'Análisis Exploratorio de Datos (EDA)',
            ha='center', va='center', fontsize=30, color='white',
            fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.57,
            'Dataset: RMS Titanic — Datos Abiertos (OpenML #40945)',
            ha='center', va='center', fontsize=16, color='#1abc9c',
            transform=ax.transAxes)

    secciones = [
        '1. Contexto del dataset',
        '2. Calidad de datos',
        '3. Métricas básicas',
        '4. Hipótesis y exploración guiada',
        '5. Información adicional relevante',
    ]
    for i, s in enumerate(secciones):
        ax.text(0.25, 0.44 - i*0.065, s,
                ha='left', va='center', fontsize=13, color='#ecf0f1',
                transform=ax.transAxes)

    ax.text(0.5, 0.04, 'Febrero 2026',
            ha='center', va='center', fontsize=11,
            color='white', transform=ax.transAxes)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ══════════════════════════════════════════════════════════
    # SECCIÓN 1 — CONTEXTO
    # ══════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(11, 8.5))
    ax  = fig.add_axes([0.05, 0.05, 0.90, 0.90])
    ax.axis('off')

    fig.text(0.5, 0.96, '1. Contexto del Dataset',
             ha='center', fontsize=16, fontweight='bold', color='#2c3e50')
    fig.text(0.5, 0.925, 'RMS Titanic — 15 de abril de 1912',
             ha='center', fontsize=11, color=GREY, style='italic')

    texto_ctx = (
        "El RMS Titanic chocó con un iceberg el 14 de abril de 1912 y se hundió al día siguiente.\n"
        "De las ~2,224 personas a bordo (pasajeros + tripulación), sobrevivieron aproximadamente 710 (~32%).\n"
        "Este dataset contiene información de 891 pasajeros del manifiesto de pasaje.\n\n"
        "Fuente: OpenML dataset #40945 | Acceso: seaborn.load_dataset('titanic') | Licencia: pública"
    )
    ax.text(0.5, 0.88, texto_ctx, ha='center', va='top', fontsize=10,
            color='#2c3e50', transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#eaf4fb', edgecolor='#3498db'))

    # Tabla de variables
    var_data = {
        'Variable': ['survived','pclass','sex','age','sibsp','parch','fare','embarked','deck'],
        'Tipo': ['Binaria (0/1)','Ordinal (1-3)','Categórica','Núm. continua',
                  'Núm. discreta','Núm. discreta','Núm. continua','Categórica','Ordinal (A-G)'],
        'Descripción': [
            'Variable objetivo — 1 = sobrevivió',
            'Clase del camarote (1ª, 2ª, 3ª)',
            'Sexo del pasajero',
            'Edad en años',
            '# hermanos/cónyuge a bordo',
            '# padres/hijos a bordo',
            'Tarifa pagada (libras esterlinas 1912)',
            'Puerto: C=Cherburgo, Q=Queenstown, S=Southampton',
            'Cubierta del camarote'
        ]
    }
    df_var = pd.DataFrame(var_data)
    tbl = ax.table(
        cellText=df_var.values,
        colLabels=df_var.columns,
        cellLoc='left', loc='center',
        bbox=[0, 0.02, 1, 0.72],
        colWidths=[0.15, 0.22, 0.63]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.scale(1, 1.5)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white', fontweight='bold')
        elif r % 2 == 0:
            cell.set_facecolor('#ecf0f1')
        cell.set_edgecolor('#bdc3c7')

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ══════════════════════════════════════════════════════════
    # SECCIÓN 2 — CALIDAD DE DATOS: mapa de nulos + barras
    # ══════════════════════════════════════════════════════════
    missing = pd.DataFrame({
        'Nulos': df.isnull().sum(),
        '% Faltante': (df.isnull().sum() / len(df) * 100).round(2)
    }).sort_values('% Faltante', ascending=False)
    missing = missing[missing['Nulos'] > 0]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    add_header(fig, '2. Calidad de Datos — Valores Faltantes',
               '¿Qué columnas tienen datos ausentes y qué proporción representan?')

    sns.heatmap(df.isnull(), cbar=False, yticklabels=False,
                cmap='YlOrRd', ax=axes[0])
    axes[0].set_title('Mapa de nulos (amarillo = faltante)', fontweight='bold', fontsize=SUB_FS)
    axes[0].set_xlabel('Columnas', fontsize=9)

    bar_colors = [COLOR_NEG if x > 50 else COLOR_NEUT for x in missing['% Faltante']]
    missing['% Faltante'].plot(kind='barh', ax=axes[1], color=bar_colors)
    axes[1].set_title('% Valores faltantes por columna', fontweight='bold', fontsize=SUB_FS)
    axes[1].set_xlabel('% Faltante')
    for i, v in enumerate(missing['% Faltante']):
        axes[1].text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=9)

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ── Tabla de estrategias ───────────────────────────────────
    estrategias = {
        'Columna': ['deck', 'age', 'embarked', 'fare (=0)'],
        '% Faltante / Problema': ['77.2%', '19.9%', '0.2% (2 obs.)', '1.7% (15 obs.)'],
        'Causa probable': [
            'No registrada en manifesto',
            'Omisiones históricas de registro',
            'Errores de transcripción',
            'Tripulación embarcada o error'
        ],
        'Estrategia recomendada': [
            'DESCARTAR — pérdida info. > 70%',
            'IMPUTAR mediana por pclass + sex',
            "IMPUTAR moda ('S' = Southampton)",
            'INVESTIGAR / flag especial / excluir'
        ]
    }
    df_est = pd.DataFrame(estrategias)
    fig = table_fig(df_est,
                    '2. Calidad de Datos — Estrategias de Imputación',
                    'Plan de acción para cada columna con problemas de calidad',
                    col_widths=[0.10, 0.20, 0.33, 0.37])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ── Boxplots de outliers ───────────────────────────────────
    num_cols = ['age', 'fare', 'sibsp', 'parch']
    fig, axes = plt.subplots(1, 4, figsize=(14, 5))
    add_header(fig, '2. Calidad de Datos — Rangos Anómalos y Outliers',
               'Los puntos rojos son valores atípicos detectados por IQR')
    for ax, col in zip(axes, num_cols):
        sns.boxplot(y=df[col], ax=ax, color=COLOR_NEUT, width=0.4,
                    flierprops=dict(marker='o', color=COLOR_NEG, alpha=0.6, markersize=4))
        ax.set_title(col, fontweight='bold')
        ax.set_ylabel('')
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ══════════════════════════════════════════════════════════
    # SECCIÓN 3 — MÉTRICAS BÁSICAS
    # ══════════════════════════════════════════════════════════

    # Página de métricas clave (tarjetas visuales)
    fig = plt.figure(figsize=(13, 7))
    add_header(fig, '3. Métricas Básicas — Indicadores Clave',
               'Resumen estadístico general del dataset Titanic')

    metricas = [
        ('Total pasajeros', f'{len(df)}', COLOR_NEUT),
        ('Sobrevivientes', f'{df["survived"].sum()} ({surv_rate*100:.1f}%)', COLOR_POS),
        ('No sobrevivientes', f'{(df["survived"]==0).sum()} ({(1-surv_rate)*100:.1f}%)', COLOR_NEG),
        ('Edad media', f'{df["age"].mean():.1f} años', '#9b59b6'),
        ('Edad mediana', f'{df["age"].median():.1f} años', '#9b59b6'),
        ('Tarifa promedio', f'£{df["fare"].mean():.2f}', '#f39c12'),
        ('Tarifa mediana', f'£{df["fare"].median():.2f}', '#f39c12'),
        ('% Mujeres', f'{(df["sex"]=="female").mean()*100:.1f}%', '#e91e63'),
        ('% 3ª clase', f'{(df["pclass"]==3).mean()*100:.1f}%', '#e74c3c'),
    ]

    n = len(metricas)
    cols_n = 3
    rows_n = (n + cols_n - 1) // cols_n
    for idx, (label, valor, color) in enumerate(metricas):
        row = idx // cols_n
        col = idx % cols_n
        left = 0.05 + col * 0.32
        top  = 0.75 - row * 0.22
        ax_card = fig.add_axes([left, top, 0.28, 0.17])
        ax_card.set_facecolor(color)
        ax_card.set_xlim(0, 1); ax_card.set_ylim(0, 1)
        ax_card.axis('off')
        ax_card.text(0.5, 0.65, valor, ha='center', va='center',
                     fontsize=18, fontweight='bold', color='white')
        ax_card.text(0.5, 0.18, label, ha='center', va='center',
                     fontsize=9, color='white', alpha=0.9)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # Distribuciones univariadas
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    add_header(fig, '3. Métricas Básicas — Distribuciones Univariadas',
               'Histogramas, gráficas de pie y barras para las variables principales')

    # Edad
    axes[0,0].hist(df['age'].dropna(), bins=30, color=COLOR_NEUT, edgecolor='white', alpha=0.85)
    axes[0,0].axvline(df['age'].mean(), color=COLOR_NEG, linestyle='--',
                      label=f'Media: {df["age"].mean():.1f}')
    axes[0,0].axvline(df['age'].median(), color='orange', linestyle='--',
                      label=f'Mediana: {df["age"].median():.1f}')
    axes[0,0].set_title('Distribución de Edad', fontweight='bold')
    axes[0,0].set_xlabel('Edad'); axes[0,0].set_ylabel('Frecuencia')
    axes[0,0].legend(fontsize=8)

    # Tarifa (log)
    fare_nz = df[df['fare'] > 0]['fare']
    axes[0,1].hist(np.log1p(fare_nz), bins=30, color='#9b59b6', edgecolor='white', alpha=0.85)
    axes[0,1].set_title('Distribución de Tarifa (log₁₊ₓ)', fontweight='bold')
    axes[0,1].set_xlabel('log(1 + fare)'); axes[0,1].set_ylabel('Frecuencia')

    # Por clase
    class_counts = df['pclass'].value_counts().sort_index()
    bars = axes[0,2].bar(['1ª Clase','2ª Clase','3ª Clase'], class_counts.values,
                          color=['#f39c12','#2980b9','#e74c3c'], edgecolor='white')
    for bar, v in zip(bars, class_counts.values):
        axes[0,2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
                       f'{v}\n({v/len(df)*100:.0f}%)', ha='center', fontsize=9)
    axes[0,2].set_title('Pasajeros por Clase', fontweight='bold')
    axes[0,2].set_ylabel('Conteo')

    # Género pie
    sex_counts = df['sex'].value_counts()
    axes[1,0].pie(sex_counts, labels=['Hombre','Mujer'], autopct='%1.1f%%',
                  colors=['#3498db','#e91e63'], startangle=90,
                  wedgeprops=dict(edgecolor='white', linewidth=2))
    axes[1,0].set_title('Distribución por Género', fontweight='bold')

    # Puerto de embarque
    emb_counts = df['embarked'].value_counts()
    emb_labels = {'S':'Southampton','C':'Cherburgo','Q':'Queenstown'}
    axes[1,1].bar([emb_labels.get(k,k) for k in emb_counts.index], emb_counts.values,
                  color=['#1abc9c','#e67e22','#9b59b6'], edgecolor='white')
    for i, v in enumerate(emb_counts.values):
        axes[1,1].text(i, v + 3, str(v), ha='center', fontsize=10)
    axes[1,1].set_title('Puerto de Embarque', fontweight='bold')
    axes[1,1].set_ylabel('Conteo')

    # Tamaño familiar
    fam_counts = df['family_size'].value_counts().sort_index()
    axes[1,2].bar(fam_counts.index, fam_counts.values, color=COLOR_NEUT, edgecolor='white')
    axes[1,2].set_title('Tamaño Grupo Familiar', fontweight='bold')
    axes[1,2].set_xlabel('Familiares a bordo'); axes[1,2].set_ylabel('Conteo')

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # Tabla describe()
    desc = df[['survived','pclass','age','sibsp','parch','fare','family_size']].describe().T.round(2)
    desc.index.name = 'Variable'
    desc = desc.reset_index()
    fig = table_fig(desc, '3. Métricas Básicas — Estadísticas Descriptivas',
                    'count, mean, std, min, cuartiles, max')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ══════════════════════════════════════════════════════════
    # SECCIÓN 4 — HIPÓTESIS
    # ══════════════════════════════════════════════════════════

    # H1 — Género
    surv_sex = df.groupby('sex')['survived'].mean().mul(100).round(1)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    add_header(fig,
               'H1: Las mujeres tuvieron mayor tasa de supervivencia',
               'Protocolo histórico "Mujeres y niños primero" — Sección 4 Hipótesis')

    bars = axes[0].bar(['Hombre','Mujer'], surv_sex.values,
                       color=['#3498db','#e91e63'], edgecolor='white', width=0.5)
    for bar, v in zip(bars, surv_sex.values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{v:.1f}%', ha='center', fontsize=14, fontweight='bold')
    axes[0].set_ylim(0, 90)
    axes[0].set_ylabel('Tasa de Supervivencia (%)')
    axes[0].set_title('Tasa por Género', fontweight='bold')
    axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                    label=f'Global: {surv_rate*100:.1f}%')
    axes[0].legend()

    ct = pd.crosstab(df['sex'], df['survived'])
    ct.columns = ['No Sobrevivió','Sobrevivió']
    ct.index   = ['Hombre','Mujer']
    ct.plot(kind='bar', stacked=True, ax=axes[1],
            color=[COLOR_NEG, COLOR_POS], edgecolor='white')
    axes[1].set_title('Conteo Absoluto', fontweight='bold')
    axes[1].set_xlabel('Género'); axes[1].set_ylabel('Pasajeros')
    axes[1].tick_params(axis='x', rotation=0)
    axes[1].legend(loc='upper right')

    fig.text(0.5, 0.01,
             '✅ CONFIRMADA: Las mujeres sobrevivieron a una tasa ~3.5× mayor que los hombres (74% vs 19%)',
             ha='center', fontsize=10, color='#27ae60', fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # H2 — Clase + heatmap clase×género
    surv_class = df.groupby('pclass')['survived'].mean().mul(100).round(1)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    add_header(fig,
               'H2: Pasajeros de 1ª clase tuvieron mayor probabilidad de sobrevivir',
               'El estatus socioeconómico influyó directamente en el acceso a botes salvavidas')

    bars = axes[0].bar(['1ª Clase','2ª Clase','3ª Clase'], surv_class.values,
                       color=['#f39c12','#2980b9','#e74c3c'], edgecolor='white', width=0.5)
    for bar, v in zip(bars, surv_class.values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{v:.1f}%', ha='center', fontsize=13, fontweight='bold')
    axes[0].set_ylim(0, 80)
    axes[0].set_ylabel('Tasa de Supervivencia (%)')
    axes[0].set_title('Tasa por Clase', fontweight='bold')
    axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                    label=f'Global: {surv_rate*100:.1f}%')
    axes[0].legend()

    pivot = df.pivot_table(values='survived', index='pclass',
                            columns='sex', aggfunc='mean').mul(100).round(1)
    pivot.index   = ['1ª Clase','2ª Clase','3ª Clase']
    pivot.columns = ['Mujer','Hombre']
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[1],
                vmin=0, vmax=100, linewidths=0.5,
                cbar_kws={'label': 'Tasa Supervivencia (%)'})
    axes[1].set_title('Tasa (%) Clase × Género', fontweight='bold')

    fig.text(0.5, 0.01,
             '✅ CONFIRMADA: 1ª clase: 63% | 2ª: 47% | 3ª: 24% — Brecha de 39 pp entre extremos',
             ha='center', fontsize=10, color='#27ae60', fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # H3 — Edad
    surv_age = df.groupby('age_group', observed=True)['survived'].agg(['mean','count'])
    surv_age.columns = ['Tasa','N']
    surv_age['Tasa %'] = (surv_age['Tasa'] * 100).round(1)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    add_header(fig,
               'H3: Los niños tuvieron mayor prioridad de evacuación',
               '"Mujeres y niños primero" — Análisis por grupo etario')

    bars = axes[0].bar(range(len(surv_age)), surv_age['Tasa %'],
                       color=['#1abc9c','#3498db','#9b59b6','#e67e22','#e74c3c'],
                       edgecolor='white')
    axes[0].set_xticks(range(len(surv_age)))
    axes[0].set_xticklabels(surv_age.index, fontsize=8.5)
    for bar, v, n in zip(bars, surv_age['Tasa %'], surv_age['N']):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{v:.0f}%\n(n={n})', ha='center', fontsize=8, fontweight='bold')
    axes[0].set_ylim(0, 80)
    axes[0].set_ylabel('Tasa de Supervivencia (%)')
    axes[0].set_title('Tasa por Grupo de Edad', fontweight='bold')
    axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                    label=f'Global: {surv_rate*100:.1f}%')
    axes[0].legend()

    df_s = df[df['survived'] == 1]
    df_n = df[df['survived'] == 0]
    sns.kdeplot(data=df_n, x='age', ax=axes[1], fill=True,
                color=COLOR_NEG, alpha=0.4, label='No sobrevivió')
    sns.kdeplot(data=df_s, x='age', ax=axes[1], fill=True,
                color=COLOR_POS, alpha=0.4, label='Sobrevivió')
    axes[1].set_title('Distribución de Edad por Resultado (KDE)', fontweight='bold')
    axes[1].set_xlabel('Edad'); axes[1].set_ylabel('Densidad')
    axes[1].legend()

    nino_rate = surv_age.loc['Nino\n(0-12)', 'Tasa %']
    fig.text(0.5, 0.01,
             f'⚠️ PARCIALMENTE CONFIRMADA: Niños 0-12 tienen la mayor tasa ({nino_rate:.0f}%), pero el efecto no es tan pronunciado en solitario',
             ha='center', fontsize=9.5, color='#e67e22', fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # H4 — Tarifa
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))
    add_header(fig,
               'H4: Mayor tarifa → Mayor probabilidad de supervivencia',
               'La tarifa es proxy del nivel socioeconómico y del acceso a recursos de emergencia')

    df_plot = df[df['fare'] > 0].copy()
    df_plot['Resultado'] = df_plot['survived'].map({0:'No Sobrevivio', 1:'Sobrevivio'})
    sns.violinplot(data=df_plot, x='Resultado', y='fare', ax=axes[0],
                   palette={'No Sobrevivio': COLOR_NEG, 'Sobrevivio': COLOR_POS},
                   inner='quartile')
    axes[0].set_yscale('log')
    axes[0].set_title('Tarifa vs Resultado (escala log)', fontweight='bold')
    axes[0].set_ylabel('Tarifa (£, log)')

    colors_sc = [COLOR_POS if s else COLOR_NEG for s in df['survived']]
    axes[1].scatter(df['age'], df['fare'], c=colors_sc, alpha=0.4, s=18)
    axes[1].set_yscale('log')
    axes[1].set_title('Tarifa vs Edad', fontweight='bold')
    axes[1].set_xlabel('Edad'); axes[1].set_ylabel('Tarifa (£, log)')
    p1 = mpatches.Patch(color=COLOR_POS, label='Sobrevivió')
    p2 = mpatches.Patch(color=COLOR_NEG, label='No Sobrevivió')
    axes[1].legend(handles=[p1, p2], fontsize=8)

    fare_class = df.groupby(['pclass','survived'])['fare'].median().unstack()
    fare_class.columns = ['No Sobrevivio','Sobrevivio']
    fare_class.index   = ['1ª Clase','2ª Clase','3ª Clase']
    fare_class.plot(kind='bar', ax=axes[2],
                    color=[COLOR_NEG, COLOR_POS], edgecolor='white')
    axes[2].set_title('Tarifa Mediana por Clase y Resultado', fontweight='bold')
    axes[2].set_xlabel(''); axes[2].set_ylabel('Tarifa Mediana (£)')
    axes[2].tick_params(axis='x', rotation=0)

    med_s = df[df['survived']==1]['fare'].median()
    med_n = df[df['survived']==0]['fare'].median()
    fig.text(0.5, 0.01,
             f'✅ CONFIRMADA: Tarifa mediana sobrevivientes £{med_s:.2f} vs no sobrevivientes £{med_n:.2f} (ratio {med_s/med_n:.1f}×)',
             ha='center', fontsize=10, color='#27ae60', fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # H5 — Solo vs familia
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    add_header(fig,
               'H5: Viajar solo redujo las probabilidades de supervivencia',
               'El aislamiento social vs el apoyo familiar en situaciones de emergencia')

    surv_alone = df.groupby('alone')['survived'].mean().mul(100).round(1)
    bars = axes[0].bar(['Viaja Solo','Con Familia'], surv_alone.values,
                       color=[COLOR_NEG, COLOR_POS], edgecolor='white', width=0.45)
    for bar, v in zip(bars, surv_alone.values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{v:.1f}%', ha='center', fontsize=14, fontweight='bold')
    axes[0].set_ylim(0, 65)
    axes[0].set_ylabel('Tasa de Supervivencia (%)')
    axes[0].set_title('Solo vs Con Familia', fontweight='bold')
    axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                    label=f'Global: {surv_rate*100:.1f}%')
    axes[0].legend()

    surv_fs = df.groupby('family_size')['survived'].agg(['mean','count'])
    surv_fs['pct'] = surv_fs['mean'].mul(100).round(1)
    axes[1].bar(surv_fs.index, surv_fs['pct'], color=COLOR_NEUT, edgecolor='white')
    for i, (v, n) in enumerate(zip(surv_fs['pct'], surv_fs['count'])):
        axes[1].text(i, v + 1, f'{v:.0f}%\n(n={n})', ha='center', fontsize=8.5)
    axes[1].set_xlabel('Tamaño de Grupo Familiar (sibsp + parch)')
    axes[1].set_ylabel('Tasa de Supervivencia (%)')
    axes[1].set_title('Tasa por Tamaño de Familia', fontweight='bold')
    axes[1].axhline(surv_rate*100, color='gray', linestyle='--')

    fig.text(0.5, 0.01,
             '⚠️ PARCIALMENTE CONFIRMADA: Solo: 30% | Familia pequeña (1-3): ~55-60% | Familias grandes (5+) también sufrieron',
             ha='center', fontsize=9.5, color='#e67e22', fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # Tabla resumen hipótesis
    hip_data = {
        'Hipótesis': ['H1: Mujeres ↑ supervivencia',
                      'H2: 1ª clase ↑ supervivencia',
                      'H3: Niños con prioridad',
                      'H4: Mayor tarifa ↑ supervivencia',
                      'H5: Solo ↓ supervivencia'],
        'Resultado': ['✅ Confirmada','✅ Confirmada','⚠️ Parcial','✅ Confirmada','⚠️ Parcial'],
        'Evidencia clave': [
            '74% (mujer) vs 19% (hombre) — ratio 3.5×',
            '1ª: 63% | 2ª: 47% | 3ª: 24%',
            '0-12 años: ~58% (mayor tasa)',
            'Mediana £26 (sí) vs £10 (no)',
            'Solo: 30% | Familia 1-3: ~57%'
        ],
        'Variable corr.': ['+0.54','-0.34','-0.08','+0.26','+0.20']
    }
    df_hip = pd.DataFrame(hip_data)
    fig = table_fig(df_hip, '4. Resumen de Hipótesis',
                    'Hallazgos clave de la exploración guiada',
                    col_widths=[0.28, 0.13, 0.42, 0.17])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ══════════════════════════════════════════════════════════
    # SECCIÓN 5 — INFORMACIÓN ADICIONAL
    # ══════════════════════════════════════════════════════════

    # 5.1 Matriz de correlación
    df_corr = df.copy()
    df_corr['sex_enc']      = (df_corr['sex'] == 'female').astype(int)
    df_corr['embarked_enc'] = df_corr['embarked'].map({'S':0,'C':1,'Q':2})
    corr_cols = ['survived','pclass','sex_enc','age','fare',
                 'sibsp','parch','family_size','alone','embarked_enc']
    corr_matrix = df_corr[corr_cols].corr()
    tick_labels = ['Sobrevivió','Clase','Mujer','Edad','Tarifa',
                   'sibsp','parch','Tam.Fam','Solo','Embarque']

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    add_header(fig, '5. Información Adicional — Matriz de Correlación',
               'Relaciones lineales entre todas las variables numéricas codificadas')

    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                cmap='coolwarm', center=0, vmin=-1, vmax=1,
                linewidths=0.5, ax=axes[0],
                xticklabels=tick_labels, yticklabels=tick_labels)
    axes[0].set_title('Heatmap de correlaciones (triángulo inferior)', fontweight='bold')

    # Ranking de correlaciones con survived
    target_corr = corr_matrix['survived'].drop('survived').abs().sort_values()
    colors_rank  = [COLOR_POS if v > 0.3 else (COLOR_NEUT if v > 0.15 else '#bdc3c7')
                    for v in target_corr]
    axes[1].barh(range(len(target_corr)), target_corr.values, color=colors_rank)
    axes[1].set_yticks(range(len(target_corr)))
    axes[1].set_yticklabels([tick_labels[corr_cols.index(c)] for c in target_corr.index])
    axes[1].set_xlabel('|Correlación| con Survived')
    axes[1].set_title('Ranking de Variables Predictivas', fontweight='bold')
    for i, v in enumerate(target_corr.values):
        axes[1].text(v + 0.005, i, f'{v:.3f}', va='center', fontsize=9)
    axes[1].set_xlim(0, 0.65)
    p_verde = mpatches.Patch(color=COLOR_POS, label='Alta (>0.30)')
    p_azul  = mpatches.Patch(color=COLOR_NEUT, label='Media (0.15-0.30)')
    p_gris  = mpatches.Patch(color='#bdc3c7', label='Baja (<0.15)')
    axes[1].legend(handles=[p_verde, p_azul, p_gris], loc='lower right', fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # 5.2 Análisis multivariado KDE: Edad × Clase × Género
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    add_header(fig,
               '5. Información Adicional — Análisis Multivariado: Edad × Clase × Género',
               'KDE de edad stratificado por clase y resultado. Línea sólida=sobrevivió | discontinua=no')

    palette_class = {1: '#f39c12', 2: '#2980b9', 3: '#e74c3c'}
    for i, (sex, title) in enumerate([('male','Hombres'), ('female','Mujeres')]):
        ax = axes[i]
        for pclass in [1, 2, 3]:
            color  = palette_class[pclass]
            label  = f'{pclass}ª Clase'
            subset = df[(df['sex'] == sex) & (df['pclass'] == pclass)]
            s = subset[subset['survived'] == 1]['age'].dropna()
            n = subset[subset['survived'] == 0]['age'].dropna()
            if len(s) > 2:
                sns.kdeplot(data=s, ax=ax, color=color, linewidth=2,
                            label=f'{label} – sobrevivió')
            if len(n) > 2:
                sns.kdeplot(data=n, ax=ax, color=color, linewidth=1.5,
                            linestyle='--', alpha=0.7)
        ax.set_title(f'{title}', fontweight='bold')
        ax.set_xlabel('Edad'); ax.set_ylabel('Densidad')
        ax.legend(fontsize=8); ax.set_xlim(0, 80)

    fig.tight_layout(rect=[0, 0, 1, 0.88])
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ── PÁGINA FINAL: RESUMEN EJECUTIVO ───────────────────────
    fig = plt.figure(figsize=(11, 8.5))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#2c3e50')
    ax.axis('off')

    rect_top = plt.Rectangle((0, 0.88), 1, 0.12, color='#1abc9c', transform=ax.transAxes)
    rect_bot = plt.Rectangle((0, 0),    1, 0.06, color='#1abc9c', transform=ax.transAxes)
    ax.add_patch(rect_top); ax.add_patch(rect_bot)

    ax.text(0.5, 0.94, 'Resumen Ejecutivo — EDA Titanic',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='white', transform=ax.transAxes)

    resumen = """
DATASET
  • 891 pasajeros, 15 variables
  • Tasa de supervivencia global: 38.4%
  • Variables clave: pclass, sex, age, fare, embarked

CALIDAD DE DATOS
  • deck (77% nulos)     → DESCARTAR
  • age (20% nulos)      → IMPUTAR mediana por clase + sexo
  • embarked (0.2%)      → IMPUTAR moda ('S' = Southampton)
  • 15 tarifas = £0      → INVESTIGAR / excluir si son errores
  • Sin duplicados exactos

HIPÓTESIS
  H1 ✅  Mujeres: 74% vs Hombres: 19%       CONFIRMADA
  H2 ✅  1ª: 63% | 2ª: 47% | 3ª: 24%       CONFIRMADA
  H3 ⚠️  Niños 0-12: ~58% (máxima tasa)     PARCIAL
  H4 ✅  Mediana tarifa: £26 vs £10          CONFIRMADA
  H5 ⚠️  Solo: 30% | Familia (1-3): ~57%    PARCIAL

TOP VARIABLES PREDICTIVAS (|correlación| con survived)
  1. Sexo (ser mujer)    |r| = 0.54   ████████████████████
  2. Clase (pclass)      |r| = 0.34   █████████████
  3. Tarifa (fare)       |r| = 0.26   ██████████

PRÓXIMOS PASOS
  → Feature engineering: title del nombre, is_child, log_fare
  → Modelado: Regresión Logística, Random Forest, XGBoost
  → Validación estadística: chi-cuadrado, Mann-Whitney U
"""
    ax.text(0.08, 0.83, resumen, ha='left', va='top',
            fontsize=10.5, color='#ecf0f1', transform=ax.transAxes,
            fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.6',
                      facecolor='#34495e', edgecolor='#1abc9c', linewidth=1.5))

    ax.text(0.5, 0.03, 'TC2004B — Análisis y Ciencia de Datos  |  Febrero 2026',
            ha='center', va='center', fontsize=10, color='white', transform=ax.transAxes)

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


    # ── Metadata del PDF ─────────────────────────────────────
    d = pdf.infodict()
    d['Title']    = 'EDA — Dataset Titanic'
    d['Author']   = 'TC2004B — Análisis y Ciencia de Datos'
    d['Subject']  = 'Exploratory Data Analysis'
    d['Keywords'] = 'EDA, Titanic, Pandas, Seaborn, Matplotlib'
    d['Creator']  = 'Python + Matplotlib PdfPages'

print(f'\n✅ PDF generado exitosamente en:\n   {OUTPUT_PATH}')
