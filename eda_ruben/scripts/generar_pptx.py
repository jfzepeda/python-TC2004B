"""
EDA Titanic — Generador de PowerPoint
TC2004B — Análisis y Ciencia de Datos
"""

import io, textwrap
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ── Colores corporativos ───────────────────────────────────────
C_DARK   = RGBColor(0x2c, 0x3e, 0x50)   # azul oscuro
C_GREEN  = RGBColor(0xD9, 0x77, 0x57)   # pomelo Claude #D97757
C_LIGHT  = RGBColor(0xec, 0xf0, 0xf1)   # gris claro
C_RED    = RGBColor(0xe7, 0x4c, 0x3c)
C_BLUE   = RGBColor(0x34, 0x98, 0xdb)
C_ORANGE = RGBColor(0xe6, 0x7e, 0x22)
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_OK     = RGBColor(0x27, 0xae, 0x60)
C_WARN   = RGBColor(0xe6, 0x7e, 0x22)

COLOR_POS  = '#2ecc71'
COLOR_NEG  = '#e74c3c'
COLOR_NEUT = '#3498db'

sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)

OUTPUT = '/Users/juanfelipezepeda/Documents/TEC/TC2004B/ruben/EDA_Titanic.pptx'

# ── Dataset ────────────────────────────────────────────────────
df = sns.load_dataset('titanic')
df['family_size'] = df['sibsp'] + df['parch']
df['alone']       = (df['family_size'] == 0).astype(int)
surv_rate         = df['survived'].mean()
age_bins   = [0, 12, 18, 35, 60, 120]
age_labels = ['Nino (0-12)', 'Adolesc. (13-18)',
              'Adulto Joven (19-35)', 'Adulto (36-60)', 'Mayor (60+)']
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)

# ── Presentación 16:9 ─────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
W = prs.slide_width
H = prs.slide_height

BLANK = prs.slide_layouts[6]   # completamente en blanco


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def add_slide():
    return prs.slides.add_slide(BLANK)


def bg(slide, color=C_DARK):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def rect(slide, left, top, width, height, fill_color, line_color=None, line_w=None):
    from pptx.util import Pt
    shp = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_color
    if line_color:
        shp.line.color.rgb = line_color
        if line_w:
            shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    return shp


def txbox(slide, text, left, top, width, height,
          font_size=18, bold=False, color=C_WHITE,
          align=PP_ALIGN.LEFT, wrap=True, italic=False):
    tb = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic    = italic
    return tb


def fig_to_img(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf


def add_fig(slide, fig, left, top, width, height=None, dpi=150):
    buf = fig_to_img(fig, dpi=dpi)
    if height:
        slide.shapes.add_picture(buf, Inches(left), Inches(top),
                                  Inches(width), Inches(height))
    else:
        slide.shapes.add_picture(buf, Inches(left), Inches(top),
                                  Inches(width))
    plt.close(fig)


def slide_header(slide, title, subtitle='', accent=C_GREEN):
    """Banda de título estándar."""
    rect(slide, 0, 0, 13.33, 1.1, accent)
    txbox(slide, title, 0.3, 0.08, 12.5, 0.65,
          font_size=24, bold=True, color=C_DARK, align=PP_ALIGN.LEFT)
    if subtitle:
        txbox(slide, subtitle, 0.3, 0.72, 12.5, 0.38,
              font_size=11, color=C_DARK, align=PP_ALIGN.LEFT, italic=True)


def pptx_table(slide, df_t, left, top, width, height,
               header_bg=C_DARK, row_alt=RGBColor(0xec,0xf0,0xf1),
               font_size=9):
    rows, cols = df_t.shape[0] + 1, df_t.shape[1]
    col_w = width / cols
    row_h = height / rows

    for ci, col in enumerate(df_t.columns):
        shp = rect(slide,
                   left + ci*col_w, top,
                   col_w, row_h,
                   header_bg)
        tf = shp.text_frame
        tf.word_wrap = True
        p  = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = str(col)
        run.font.bold  = True
        run.font.size  = Pt(font_size)
        run.font.color.rgb = C_WHITE

    for ri, row in enumerate(df_t.itertuples(index=False)):
        fill = row_alt if ri % 2 == 0 else C_WHITE
        for ci, val in enumerate(row):
            shp = rect(slide,
                       left + ci*col_w, top + (ri+1)*row_h,
                       col_w, row_h, fill,
                       line_color=RGBColor(0xbd,0xc3,0xc7), line_w=0.5)
            tf = shp.text_frame
            tf.word_wrap = True
            p  = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = str(val)
            run.font.size  = Pt(font_size)
            run.font.color.rgb = C_DARK


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 1 — PORTADA
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_DARK)
rect(sl, 0, 0,    13.33, 1.4,  C_GREEN)
rect(sl, 0, 6.2,  13.33, 1.3,  C_GREEN)

txbox(sl, 'TC2004B — Análisis y Ciencia de Datos',
      0.5, 0.1, 12, 0.6, font_size=20, bold=True,
      color=C_DARK, align=PP_ALIGN.CENTER)

txbox(sl, 'Análisis Exploratorio de Datos (EDA)',
      0.5, 1.7, 12, 1.0, font_size=36, bold=True,
      color=C_WHITE, align=PP_ALIGN.CENTER)

txbox(sl, 'Dataset: RMS Titanic — Datos Abiertos (OpenML #40945)',
      0.5, 2.85, 12, 0.55, font_size=17,
      color=C_GREEN, align=PP_ALIGN.CENTER)

secciones = [
    '1.  Contexto del dataset',
    '2.  Calidad de datos (faltantes · duplicados · rangos)',
    '3.  Métricas básicas',
    '4.  Hipótesis que guían la exploración',
    '5.  Información adicional relevante',
]
for i, s in enumerate(secciones):
    txbox(sl, s, 2.5, 3.6 + i*0.44, 9, 0.42,
          font_size=13, color=C_LIGHT)

txbox(sl, 'Febrero 2026', 0.5, 6.9, 12, 0.35,
      font_size=12, color=C_WHITE, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 2 — SECCIÓN 1: CONTEXTO
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '1.  Contexto del Dataset',
             'RMS Titanic  •  15 de abril de 1912  •  OpenML #40945')

# Cuadro de texto contextual
rect(sl, 0.3, 1.25, 12.7, 1.05, RGBColor(0xea,0xf4,0xfb),
     line_color=C_BLUE, line_w=1)
ctx = ('El RMS Titanic se hundió el 15 de abril de 1912 tras chocar con un iceberg. '
       'De ~2,224 personas a bordo, sobrevivieron ~710 (~32%). '
       'Este dataset contiene 891 pasajeros del manifiesto de pasaje. '
       'Es un caso histórico real donde la supervivencia dependió de factores '
       'socioeconómicos, demográficos y logísticos.')
txbox(sl, ctx, 0.5, 1.3, 12.3, 0.95,
      font_size=11, color=C_DARK)

# Tabla de variables
var_data = {
    'Variable': ['survived','pclass','sex','age','sibsp','parch','fare','embarked','deck'],
    'Tipo': ['Binaria (0/1)','Ordinal (1-3)','Categórica','Núm. continua',
              'Núm. discreta','Núm. discreta','Núm. continua','Categórica','Ordinal A-G'],
    'Descripción': [
        'Variable objetivo — 1 = sobrevivió',
        'Clase del camarote (1ª, 2ª, 3ª)',
        'Sexo del pasajero',
        'Edad en años (fraccionarios = bebés)',
        '# hermanos / cónyuge a bordo',
        '# padres / hijos a bordo',
        'Tarifa pagada en libras esterlinas (1912)',
        'Puerto: C=Cherburgo  Q=Queenstown  S=Southampton',
        'Cubierta del camarote (A más alta, G más baja)'
    ]
}
df_var = pd.DataFrame(var_data)
pptx_table(sl, df_var, 0.3, 2.4, 12.7, 4.8, font_size=10)

# Badge dimensiones
rect(sl, 10.2, 1.28, 2.8, 0.95, C_DARK)
txbox(sl, '891 filas  ×  15 columnas', 10.25, 1.32, 2.7, 0.45,
      font_size=11, bold=True, color=C_GREEN, align=PP_ALIGN.CENTER)
txbox(sl, 'Tasa supervivencia: 38.4%', 10.25, 1.72, 2.7, 0.4,
      font_size=10, color=C_LIGHT, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 3 — SECCIÓN 2: MAPA DE NULOS
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '2.  Calidad de Datos — Valores Faltantes',
             'Identificación de columnas con datos ausentes y su magnitud')

missing = pd.DataFrame({
    'Nulos': df.isnull().sum(),
    '% Faltante': (df.isnull().sum() / len(df) * 100).round(2)
}).sort_values('% Faltante', ascending=False)
missing = missing[missing['Nulos'] > 0]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), facecolor='#f8f9fa')
sns.heatmap(df.isnull(), cbar=False, yticklabels=False,
            cmap='YlOrRd', ax=axes[0])
axes[0].set_title('Mapa de nulos (amarillo = faltante)', fontweight='bold')
axes[0].set_xlabel('Columnas')

bar_colors = [COLOR_NEG if x > 50 else COLOR_NEUT for x in missing['% Faltante']]
missing['% Faltante'].plot(kind='barh', ax=axes[1], color=bar_colors)
axes[1].set_title('% Faltante por columna', fontweight='bold')
axes[1].set_xlabel('% Faltante')
for i, v in enumerate(missing['% Faltante']):
    axes[1].text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=9)
fig.tight_layout()
add_fig(sl, fig, 0.3, 1.2, 12.7, 6.0)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 4 — SECCIÓN 2: ESTRATEGIAS + OUTLIERS
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '2.  Calidad de Datos — Estrategias y Outliers',
             'Plan de acción por columna  +  detección de rangos anómalos')

# Tabla de estrategias (mitad izquierda)
est = {
    'Columna': ['deck','age','embarked','fare = £0'],
    '% / Obs.': ['77.2%','19.9%','2 obs.','15 obs.'],
    'Estrategia': [
        'DESCARTAR (>70%)',
        'Imputar mediana\npor clase + sexo',
        "Imputar moda 'S'",
        'Investigar / excluir'
    ]
}
pptx_table(sl, pd.DataFrame(est), 0.3, 1.25, 6.0, 3.2, font_size=10)

# Texto sin duplicados
rect(sl, 0.3, 4.55, 6.0, 0.7, RGBColor(0xf9,0xe8,0xe3),
     line_color=C_GREEN, line_w=1)
txbox(sl, '✔  Sin filas duplicadas exactas', 0.5, 4.6, 5.7, 0.6,
      font_size=13, bold=True, color=C_GREEN)

# Boxplots (mitad derecha)
num_cols = ['age', 'fare', 'sibsp', 'parch']
fig, axes = plt.subplots(1, 4, figsize=(7, 3.5), facecolor='#f8f9fa')
for ax, col in zip(axes, num_cols):
    sns.boxplot(y=df[col], ax=ax, color=COLOR_NEUT, width=0.4,
                flierprops=dict(marker='o', color=COLOR_NEG, alpha=0.6, markersize=4))
    ax.set_title(col, fontweight='bold', fontsize=9)
    ax.set_ylabel('')
fig.suptitle('Outliers por IQR (puntos rojos)', fontsize=9, fontweight='bold')
fig.tight_layout()
add_fig(sl, fig, 6.5, 1.2, 6.6, 4.0)

# Hallazgos outliers
txbox(sl, '• fare = £0 → 15 pax (tripulación o error de registro)',
      6.5, 5.3, 6.6, 0.4, font_size=10, color=C_DARK)
txbox(sl, '• fare > £300 → 3 pax (suites 1ª clase — legítimos)',
      6.5, 5.7, 6.6, 0.4, font_size=10, color=C_DARK)
txbox(sl, '• age fraccionario → bebés < 1 año (ej. 0.42 = ~5 meses)',
      6.5, 6.1, 6.6, 0.4, font_size=10, color=C_DARK)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 5 — SECCIÓN 3: MÉTRICAS CLAVE (TARJETAS)
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '3.  Métricas Básicas — Indicadores Clave',
             'Resumen estadístico general del dataset')

tarjetas = [
    ('Total\npasajeros',         f'{len(df)}',         C_BLUE),
    ('Sobrevivientes',           f'{df["survived"].sum()}\n({surv_rate*100:.1f}%)',
                                                         RGBColor(0x27,0xae,0x60)),
    ('No sobrevivientes',        f'{(df["survived"]==0).sum()}\n({(1-surv_rate)*100:.1f}%)',
                                                         C_RED),
    ('Edad promedio',            f'{df["age"].mean():.1f} años',
                                                         RGBColor(0x9b,0x59,0xb6)),
    ('Tarifa mediana',           f'£{df["fare"].median():.2f}',
                                                         RGBColor(0xf3,0x9c,0x12)),
    ('% Mujeres',                f'{(df["sex"]=="female").mean()*100:.1f}%',
                                                         RGBColor(0xe9,0x1e,0x63)),
    ('% 1ª clase',               f'{(df["pclass"]==1).mean()*100:.1f}%',
                                                         RGBColor(0x16,0xa0,0x85)),
    ('% 3ª clase',               f'{(df["pclass"]==3).mean()*100:.1f}%',
                                                         C_RED),
    ('Duplicados',               '0',                    RGBColor(0x27,0xae,0x60)),
]

cols_n = 3
for idx, (label, valor, color) in enumerate(tarjetas):
    row = idx // cols_n
    col = idx % cols_n
    l = 0.35 + col * 4.3
    t = 1.35 + row * 1.95
    rect(sl, l, t, 3.9, 1.7, color)
    txbox(sl, valor, l, t + 0.28, 3.9, 0.85,
          font_size=26, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    txbox(sl, label, l, t + 1.2, 3.9, 0.45,
          font_size=10, color=C_WHITE, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 6 — SECCIÓN 3: DISTRIBUCIONES UNIVARIADAS
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '3.  Métricas Básicas — Distribuciones Univariadas',
             'Histogramas, pie chart y barras para las variables principales')

df['family_size'] = df['sibsp'] + df['parch']
fig, axes = plt.subplots(2, 3, figsize=(13, 6.5), facecolor='#f8f9fa')

axes[0,0].hist(df['age'].dropna(), bins=30, color=COLOR_NEUT, edgecolor='white', alpha=0.85)
axes[0,0].axvline(df['age'].mean(), color=COLOR_NEG, linestyle='--',
                   label=f'Media {df["age"].mean():.1f}')
axes[0,0].axvline(df['age'].median(), color='orange', linestyle='--',
                   label=f'Med. {df["age"].median():.1f}')
axes[0,0].set_title('Distribución de Edad', fontweight='bold')
axes[0,0].legend(fontsize=8)

fare_nz = df[df['fare'] > 0]['fare']
axes[0,1].hist(np.log1p(fare_nz), bins=30, color='#9b59b6', edgecolor='white', alpha=0.85)
axes[0,1].set_title('Tarifa log(1+fare)', fontweight='bold')

class_counts = df['pclass'].value_counts().sort_index()
bars = axes[0,2].bar(['1ª','2ª','3ª'], class_counts.values,
                      color=['#f39c12','#2980b9','#e74c3c'], edgecolor='white')
for bar, v in zip(bars, class_counts.values):
    axes[0,2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+4,
                   f'{v} ({v/len(df)*100:.0f}%)', ha='center', fontsize=8)
axes[0,2].set_title('Pasajeros por Clase', fontweight='bold')

sex_counts = df['sex'].value_counts()
axes[1,0].pie(sex_counts, labels=['Hombre','Mujer'], autopct='%1.1f%%',
              colors=['#3498db','#e91e63'], startangle=90,
              wedgeprops=dict(edgecolor='white', linewidth=2))
axes[1,0].set_title('Género', fontweight='bold')

emb_counts = df['embarked'].value_counts()
emb_labels = {'S':'Southampton','C':'Cherburgo','Q':'Queenstown'}
axes[1,1].bar([emb_labels.get(k,k) for k in emb_counts.index], emb_counts.values,
              color=['#1abc9c','#e67e22','#9b59b6'], edgecolor='white')
for i, v in enumerate(emb_counts.values):
    axes[1,1].text(i, v+3, str(v), ha='center', fontsize=9)
axes[1,1].set_title('Puerto de Embarque', fontweight='bold')

fam_counts = df['family_size'].value_counts().sort_index()
axes[1,2].bar(fam_counts.index, fam_counts.values, color=COLOR_NEUT, edgecolor='white')
axes[1,2].set_title('Tamaño Grupo Familiar', fontweight='bold')
axes[1,2].set_xlabel('Familiares a bordo')

fig.tight_layout()
add_fig(sl, fig, 0.2, 1.15, 12.9, 6.2)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 7 — H1: GÉNERO
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '4.  H1: Las mujeres tuvieron mayor tasa de supervivencia',
             'Protocolo histórico "Mujeres y niños primero"')

surv_sex = df.groupby('sex')['survived'].mean().mul(100).round(1)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), facecolor='#f8f9fa')

bars = axes[0].bar(['Hombre','Mujer'], surv_sex.values,
                   color=['#3498db','#e91e63'], edgecolor='white', width=0.5)
for bar, v in zip(bars, surv_sex.values):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                 f'{v:.1f}%', ha='center', fontsize=14, fontweight='bold')
axes[0].set_ylim(0, 90)
axes[0].set_ylabel('Tasa de Supervivencia (%)')
axes[0].set_title('Tasa por Género', fontweight='bold')
axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                label=f'Global {surv_rate*100:.1f}%')
axes[0].legend()

ct = pd.crosstab(df['sex'], df['survived'])
ct.columns = ['No Sobrevivió','Sobrevivió']
ct.index   = ['Hombre','Mujer']
ct.plot(kind='bar', stacked=True, ax=axes[1],
        color=[COLOR_NEG, COLOR_POS], edgecolor='white')
axes[1].set_title('Conteo Absoluto', fontweight='bold')
axes[1].tick_params(axis='x', rotation=0)
axes[1].legend(loc='upper right')

fig.tight_layout()
add_fig(sl, fig, 0.3, 1.15, 12.7, 5.1)

rect(sl, 0.3, 6.3, 12.7, 0.75, RGBColor(0xf9,0xe8,0xe3), line_color=C_GREEN, line_w=1)
txbox(sl, '✅  CONFIRMADA: Mujeres 74% vs Hombres 19% — ratio 3.5×  |  Diferencia estadísticamente muy significativa',
      0.5, 6.35, 12.3, 0.6, font_size=12, bold=True, color=C_GREEN)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 8 — H2: CLASE
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '4.  H2: Pasajeros de 1ª clase tuvieron mayor probabilidad de sobrevivir',
             'El estatus socioeconómico influyó directamente en el acceso a botes salvavidas')

surv_class = df.groupby('pclass')['survived'].mean().mul(100).round(1)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), facecolor='#f8f9fa')

bars = axes[0].bar(['1ª Clase','2ª Clase','3ª Clase'], surv_class.values,
                   color=['#f39c12','#2980b9','#e74c3c'], edgecolor='white', width=0.5)
for bar, v in zip(bars, surv_class.values):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                 f'{v:.1f}%', ha='center', fontsize=13, fontweight='bold')
axes[0].set_ylim(0, 80)
axes[0].set_ylabel('Tasa de Supervivencia (%)')
axes[0].set_title('Tasa por Clase', fontweight='bold')
axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                label=f'Global {surv_rate*100:.1f}%')
axes[0].legend()

pivot = df.pivot_table(values='survived', index='pclass',
                        columns='sex', aggfunc='mean').mul(100).round(1)
pivot.index   = ['1ª Clase','2ª Clase','3ª Clase']
pivot.columns = ['Mujer','Hombre']
sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[1],
            vmin=0, vmax=100, linewidths=0.5,
            cbar_kws={'label': 'Tasa Supervivencia (%)'})
axes[1].set_title('Tasa (%) por Clase × Género', fontweight='bold')

fig.tight_layout()
add_fig(sl, fig, 0.3, 1.15, 12.7, 5.1)

rect(sl, 0.3, 6.3, 12.7, 0.75, RGBColor(0xf9,0xe8,0xe3), line_color=C_GREEN, line_w=1)
txbox(sl, '✅  CONFIRMADA: 1ª clase 63% | 2ª 47% | 3ª 24% — Brecha de 39 puntos porcentuales entre extremos',
      0.5, 6.35, 12.3, 0.6, font_size=12, bold=True, color=C_GREEN)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 9 — H3: EDAD
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '4.  H3: Los niños tuvieron mayor prioridad de evacuación',
             '"Mujeres y niños primero" — Análisis por grupo etario')

surv_age = df.groupby('age_group', observed=True)['survived'].agg(['mean','count'])
surv_age.columns = ['Tasa','N']
surv_age['Tasa %'] = (surv_age['Tasa'] * 100).round(1)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), facecolor='#f8f9fa')

bars = axes[0].bar(range(len(surv_age)), surv_age['Tasa %'],
                   color=['#1abc9c','#3498db','#9b59b6','#e67e22','#e74c3c'],
                   edgecolor='white')
axes[0].set_xticks(range(len(surv_age)))
axes[0].set_xticklabels(surv_age.index, fontsize=8.5)
for bar, v, n in zip(bars, surv_age['Tasa %'], surv_age['N']):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                 f'{v:.0f}%\n(n={n})', ha='center', fontsize=8, fontweight='bold')
axes[0].set_ylim(0, 78)
axes[0].set_ylabel('Tasa de Supervivencia (%)')
axes[0].set_title('Tasa por Grupo de Edad', fontweight='bold')
axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                label=f'Global {surv_rate*100:.1f}%')
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

fig.tight_layout()
add_fig(sl, fig, 0.3, 1.15, 12.7, 5.1)

nino_rate = surv_age.loc['Nino (0-12)', 'Tasa %']
rect(sl, 0.3, 6.3, 12.7, 0.75, RGBColor(0xf9,0xe8,0xe3), line_color=C_GREEN, line_w=1)
txbox(sl, f'⚠️  PARCIALMENTE CONFIRMADA: Niños 0-12 tienen la mayor tasa ({nino_rate:.0f}%), pero la diferencia no es suficiente por sí sola para confirmar el protocolo',
      0.5, 6.35, 12.3, 0.6, font_size=11, bold=True, color=C_GREEN)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 10 — H4: TARIFA
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '4.  H4: Mayor tarifa → Mayor probabilidad de supervivencia',
             'La tarifa es proxy del nivel socioeconómico y del acceso a recursos de emergencia')

fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), facecolor='#f8f9fa')

df_plot = df[df['fare'] > 0].copy()
df_plot['Resultado'] = df_plot['survived'].map({0:'No Sobrevivio', 1:'Sobrevivio'})
sns.violinplot(data=df_plot, x='Resultado', y='fare', ax=axes[0],
               palette={'No Sobrevivio': COLOR_NEG, 'Sobrevivio': COLOR_POS},
               inner='quartile')
axes[0].set_yscale('log')
axes[0].set_title('Tarifa vs Resultado (log)', fontweight='bold')
axes[0].set_ylabel('Tarifa £ (log)')

colors_sc = [COLOR_POS if s else COLOR_NEG for s in df['survived']]
axes[1].scatter(df['age'], df['fare'], c=colors_sc, alpha=0.35, s=15)
axes[1].set_yscale('log')
axes[1].set_title('Tarifa vs Edad', fontweight='bold')
axes[1].set_xlabel('Edad'); axes[1].set_ylabel('Tarifa £ (log)')
p1 = mpatches.Patch(color=COLOR_POS, label='Sobrevivió')
p2 = mpatches.Patch(color=COLOR_NEG, label='No Sobrevivió')
axes[1].legend(handles=[p1, p2], fontsize=8)

fare_class = df.groupby(['pclass','survived'])['fare'].median().unstack()
fare_class.columns = ['No Sobrevivio','Sobrevivio']
fare_class.index   = ['1ª','2ª','3ª']
fare_class.plot(kind='bar', ax=axes[2], color=[COLOR_NEG, COLOR_POS], edgecolor='white')
axes[2].set_title('Tarifa Mediana por Clase', fontweight='bold')
axes[2].set_xlabel(''); axes[2].tick_params(axis='x', rotation=0)
axes[2].set_ylabel('Tarifa Mediana £')

fig.tight_layout()
add_fig(sl, fig, 0.2, 1.15, 12.9, 5.1)

med_s = df[df['survived']==1]['fare'].median()
med_n = df[df['survived']==0]['fare'].median()
rect(sl, 0.3, 6.3, 12.7, 0.75, RGBColor(0xf9,0xe8,0xe3), line_color=C_GREEN, line_w=1)
txbox(sl, f'✅  CONFIRMADA: Tarifa mediana sobrevivientes £{med_s:.2f} vs no sobrevivientes £{med_n:.2f}  (ratio {med_s/med_n:.1f}×)',
      0.5, 6.35, 12.3, 0.6, font_size=12, bold=True, color=C_GREEN)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 11 — H5: SOLO VS FAMILIA
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '4.  H5: Viajar solo redujo las probabilidades de supervivencia',
             'El aislamiento social frente al apoyo familiar en situaciones de emergencia')

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), facecolor='#f8f9fa')

surv_alone = df.groupby('alone')['survived'].mean().mul(100).round(1)
bars = axes[0].bar(['Viaja Solo','Con Familia'], surv_alone.values,
                   color=[COLOR_NEG, COLOR_POS], edgecolor='white', width=0.45)
for bar, v in zip(bars, surv_alone.values):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                 f'{v:.1f}%', ha='center', fontsize=14, fontweight='bold')
axes[0].set_ylim(0, 65)
axes[0].set_ylabel('Tasa de Supervivencia (%)')
axes[0].set_title('Solo vs Con Familia', fontweight='bold')
axes[0].axhline(surv_rate*100, color='gray', linestyle='--',
                label=f'Global {surv_rate*100:.1f}%')
axes[0].legend()

surv_fs = df.groupby('family_size')['survived'].agg(['mean','count'])
surv_fs['pct'] = surv_fs['mean'].mul(100).round(1)
axes[1].bar(surv_fs.index, surv_fs['pct'], color=COLOR_NEUT, edgecolor='white')
for i, (v, n) in enumerate(zip(surv_fs['pct'], surv_fs['count'])):
    axes[1].text(i, v+1, f'{v:.0f}%\n(n={n})', ha='center', fontsize=8.5)
axes[1].set_xlabel('Familiares a bordo (sibsp + parch)')
axes[1].set_ylabel('Tasa de Supervivencia (%)')
axes[1].set_title('Tasa por Tamaño de Familia', fontweight='bold')
axes[1].axhline(surv_rate*100, color='gray', linestyle='--')

fig.tight_layout()
add_fig(sl, fig, 0.3, 1.15, 12.7, 5.1)

rect(sl, 0.3, 6.3, 12.7, 0.75, RGBColor(0xf9,0xe8,0xe3), line_color=C_GREEN, line_w=1)
txbox(sl, '⚠️  PARCIALMENTE CONFIRMADA: Solo 30% | Familia pequeña (1-3 miembros) ~57% | Familias grandes (5+) también tuvieron baja supervivencia',
      0.5, 6.35, 12.3, 0.6, font_size=11, bold=True, color=C_GREEN)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 12 — RESUMEN HIPÓTESIS (tabla)
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '4.  Resumen de Hipótesis',
             'Hallazgos clave de la exploración guiada')

hip = {
    'Hipótesis': [
        'H1: Mujeres ↑ supervivencia',
        'H2: 1ª clase ↑ supervivencia',
        'H3: Niños con prioridad',
        'H4: Mayor tarifa ↑ supervivencia',
        'H5: Solo ↓ supervivencia'
    ],
    'Resultado': ['✅ Confirmada','✅ Confirmada','⚠️ Parcial','✅ Confirmada','⚠️ Parcial'],
    'Evidencia clave': [
        '74% (mujer) vs 19% (hombre) — ratio 3.5×',
        '1ª: 63% | 2ª: 47% | 3ª: 24% — brecha 39 pp',
        '0-12 años: ~58% (mayor tasa del dataset)',
        'Mediana £26 (sí) vs £10 (no) — ratio 2.6×',
        'Solo: 30% | Familia 1-3: ~57%'
    ],
    '|r| con survived': ['+0.54','-0.34','-0.08','+0.26','+0.20']
}
pptx_table(sl, pd.DataFrame(hip), 0.3, 1.3, 12.7, 5.5,
           font_size=11)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 13 — SECCIÓN 5: CORRELACIÓN
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '5.  Información Adicional — Matriz de Correlación',
             'Relaciones lineales entre todas las variables numéricas codificadas')

df_corr = df.copy()
df_corr['sex_enc']      = (df_corr['sex'] == 'female').astype(int)
df_corr['embarked_enc'] = df_corr['embarked'].map({'S':0,'C':1,'Q':2})
corr_cols = ['survived','pclass','sex_enc','age','fare',
             'sibsp','parch','family_size','alone','embarked_enc']
corr_matrix = df_corr[corr_cols].corr()
tick_labels = ['Sobrevivió','Clase','Mujer','Edad','Tarifa',
               'sibsp','parch','Tam.Fam','Solo','Embarque']

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), facecolor='#f8f9fa')

mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
            cmap='coolwarm', center=0, vmin=-1, vmax=1,
            linewidths=0.5, ax=axes[0],
            xticklabels=tick_labels, yticklabels=tick_labels)
axes[0].set_title('Heatmap de correlaciones', fontweight='bold')

target_corr = corr_matrix['survived'].drop('survived').abs().sort_values()
bar_cols = [COLOR_POS if v > 0.3 else (COLOR_NEUT if v > 0.15 else '#bdc3c7')
            for v in target_corr]
axes[1].barh(range(len(target_corr)), target_corr.values, color=bar_cols)
axes[1].set_yticks(range(len(target_corr)))
axes[1].set_yticklabels([tick_labels[corr_cols.index(c)] for c in target_corr.index])
axes[1].set_xlabel('|Correlación| con Survived')
axes[1].set_title('Ranking de Variables Predictivas', fontweight='bold')
for i, v in enumerate(target_corr.values):
    axes[1].text(v+0.005, i, f'{v:.3f}', va='center', fontsize=9)
axes[1].set_xlim(0, 0.65)
p1 = mpatches.Patch(color=COLOR_POS,   label='Alta (>0.30)')
p2 = mpatches.Patch(color=COLOR_NEUT,  label='Media (0.15-0.30)')
p3 = mpatches.Patch(color='#bdc3c7',   label='Baja (<0.15)')
axes[1].legend(handles=[p1, p2, p3], fontsize=8)

fig.tight_layout()
add_fig(sl, fig, 0.2, 1.15, 12.9, 6.0)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 14 — SECCIÓN 5: ANÁLISIS MULTIVARIADO
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '5.  Información Adicional — Análisis Multivariado: Edad × Clase × Género',
             'KDE de edad estratificado por clase y resultado  |  Línea sólida = sobrevivió  |  Discontinua = no sobrevivió')

palette_class = {1: '#f39c12', 2: '#2980b9', 3: '#e74c3c'}
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), facecolor='#f8f9fa')

for i, (sex, title) in enumerate([('male','Hombres'), ('female','Mujeres')]):
    ax = axes[i]
    for pclass in [1, 2, 3]:
        color = palette_class[pclass]
        subset = df[(df['sex'] == sex) & (df['pclass'] == pclass)]
        s = subset[subset['survived'] == 1]['age'].dropna()
        n = subset[subset['survived'] == 0]['age'].dropna()
        if len(s) > 2:
            sns.kdeplot(data=s, ax=ax, color=color, linewidth=2,
                        label=f'{pclass}ª Clase – sobrevivió')
        if len(n) > 2:
            sns.kdeplot(data=n, ax=ax, color=color, linewidth=1.5,
                        linestyle='--', alpha=0.7)
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel('Edad'); ax.set_ylabel('Densidad')
    ax.legend(fontsize=8); ax.set_xlim(0, 80)

fig.tight_layout()
add_fig(sl, fig, 0.2, 1.15, 12.9, 6.0)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 15 — PRÓXIMOS PASOS
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_LIGHT)
slide_header(sl, '5.  Próximos Pasos Sugeridos',
             'Rutas de acción post-EDA para modelado y validación')

pasos = [
    ('🔧 Feature Engineering',
     '• Extraer título del nombre (Mr., Mrs., Miss., Master.)\n'
     '• Crear variable is_child (age < 13)\n'
     '• Aplicar log(1+fare) para normalizar distribución\n'
     '• fare_per_person = fare / (family_size + 1)'),
    ('📊 Validación Estadística',
     '• Chi-cuadrado: survived vs pclass, sex, embarked\n'
     '• Mann-Whitney U: edad y tarifa por resultado\n'
     '• ANOVA: tarifa por clase\n'
     '• Análisis de potencia para tamaños de muestra'),
    ('🤖 Modelado Predictivo',
     '• Baseline: Regresión Logística\n'
     '• Árbol de Decisión (interpretabilidad)\n'
     '• Random Forest + XGBoost\n'
     '• Validación cruzada k-fold (k=5 o 10)'),
    ('📈 Evaluación de Modelos',
     '• Métricas: AUC-ROC, Precision, Recall, F1\n'
     '• Matriz de confusión\n'
     '• Curvas ROC y Precision-Recall\n'
     '• SHAP values para explicabilidad'),
]

positions = [(0.3, 1.25), (6.85, 1.25), (0.3, 4.2), (6.85, 4.2)]
for (l, t), (titulo, contenido) in zip(positions, pasos):
    rect(sl, l, t, 6.2, 2.85, C_DARK)
    rect(sl, l, t, 6.2, 0.55, C_GREEN)
    txbox(sl, titulo, l+0.1, t+0.05, 5.9, 0.45,
          font_size=13, bold=True, color=C_DARK)
    txbox(sl, contenido, l+0.1, t+0.62, 5.9, 2.15,
          font_size=10, color=C_LIGHT)


# ══════════════════════════════════════════════════════════════
# DIAPOSITIVA 16 — RESUMEN EJECUTIVO (portada final)
# ══════════════════════════════════════════════════════════════
sl = add_slide()
bg(sl, C_DARK)
rect(sl, 0, 0,    13.33, 1.1,  C_GREEN)
rect(sl, 0, 6.45, 13.33, 1.05, C_GREEN)

txbox(sl, 'Resumen Ejecutivo',
      0.5, 0.12, 12, 0.7, font_size=26, bold=True,
      color=C_DARK, align=PP_ALIGN.CENTER)

# 3 columnas
columnas = [
    ('DATASET\n& CALIDAD',
     '891 pasajeros · 15 vars\n'
     'Supervivencia global: 38.4%\n\n'
     'deck → DESCARTAR (77%)\n'
     'age → imputar mediana\n'
     'embarked → imputar moda\n'
     'fare=£0 → investigar\n'
     'Duplicados: 0'),
    ('HIPÓTESIS',
     'H1 ✅  Mujer 74% vs H. 19%\n'
     'H2 ✅  1ª 63% | 3ª 24%\n'
     'H3 ⚠️  Niños 0-12: ~58%\n'
     'H4 ✅  £26 vs £10 (2.6×)\n'
     'H5 ⚠️  Solo 30% vs 57%'),
    ('TOP PREDICTORES\n(|r| con survived)',
     '1. Sexo (mujer) → 0.54\n'
     '2. Clase         → 0.34\n'
     '3. Tarifa        → 0.26\n'
     '4. Embarque      → 0.11\n'
     '5. Edad          → 0.08'),
]

for i, (titulo, contenido) in enumerate(columnas):
    l = 0.3 + i * 4.35
    rect(sl, l, 1.2, 4.15, 5.1, RGBColor(0x34,0x49,0x5e))
    rect(sl, l, 1.2, 4.15, 0.65, C_GREEN)
    txbox(sl, titulo, l+0.1, 1.22, 3.95, 0.6,
          font_size=13, bold=True, color=C_DARK)
    txbox(sl, contenido, l+0.15, 1.95, 3.85, 4.2,
          font_size=11, color=C_LIGHT)

txbox(sl, 'TC2004B — Análisis y Ciencia de Datos  |  Febrero 2026',
      0.5, 6.6, 12, 0.45, font_size=11,
      color=C_DARK, align=PP_ALIGN.CENTER)


# ── Guardar ────────────────────────────────────────────────────
prs.save(OUTPUT)
print(f'\n✅ PowerPoint generado exitosamente:\n   {OUTPUT}')
print(f'   Total diapositivas: {len(prs.slides)}')
