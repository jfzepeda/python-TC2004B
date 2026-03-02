# python-TC2004B

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![Build](https://img.shields.io/badge/build-%E2%9C%93-brightgreen)

Proyecto de ejemplo en Python para la materia/curso **TC2004B**. Contiene ejercicios de análisis de datos y machine learning aplicados a un caso de predicción de precios de vivienda (*Su Casita*), usando el dataset de Sacramento.

## Tabla de contenidos
- [Requisitos](#requisitos)
- [Instalación](#instalación-rápida)
- [Uso](#uso)
- [Ejemplos](#ejemplos)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Contribuir](#contribuir)
- [Tests](#tests)
- [Formato y calidad de código](#formato-y-calidad-de-código)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Requisitos
- Python 3.10+
- Pip
- (Opcional) virtualenv, poetry o pipenv
- (Opcional) [Quarto](https://quarto.org/) para renderizar los notebooks `.qmd`

## Instalación (rápida)
Clona el repositorio:
```bash
git clone https://github.com/jfzepeda/python-TC2004B.git
cd python-TC2004B
```

Crear y activar entorno virtual (recomendado):
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso
Para ejecutar o renderizar los notebooks de Quarto:
```bash
quarto render su_casita/notebooks/su_casita.qmd
```

También puedes abrir los notebooks directamente en JupyterLab o VS Code con soporte para `.qmd`.

Para usar las funciones utilitarias desde un script Python:
```python
import pandas as pd
from su_casita.scripts.funciones import create_train_test

df = pd.read_csv("su_casita/data/sacramento.csv")
train, test = create_train_test(df, test_ratio=0.2, seed=42)
```

## Ejemplos
- **Dataset**: `su_casita/data/sacramento.csv` — precios de viviendas en Sacramento, CA.
- **Comando** para explorar el notebook principal:
```bash
quarto preview su_casita/notebooks/su_casita.qmd
```
- **Salida**: notebook HTML con análisis exploratorio y modelos de predicción de precios.

## Estructura del proyecto
```
python-TC2004B/
├── su_casita/
│   ├── data/
│   │   └── sacramento.csv       # Dataset de viviendas (Sacramento)
│   ├── figures/                 # Gráficas generadas
│   ├── notebooks/
│   │   ├── casita.qmd           # Notebook Quarto del proyecto
│   │   └── su_casita.qmd        # Notebook Quarto principal
│   └── scripts/
│       └── funciones.py         # Funciones utilitarias (ej. train/test split)
├── requirements.txt
├── README.md
└── .gitignore
```

## Contribuir
- Haz fork del repo.
- Crea una branch descriptiva: `git checkout -b feat/mi-cambio`
- Haz commits claros y atómicos.
- Abre un Pull Request describiendo el cambio.

Por favor sigue las convenciones de estilo del proyecto y documenta cualquier función nueva.

## Tests
Este proyecto no incluye una suite de tests automatizados por ahora. Si deseas contribuir con pruebas, se recomienda usar pytest:
```bash
pip install pytest
pytest -q
```

## Formato y calidad de código
Recomendaciones:
- **Formateo**: Black
```bash
pip install black
black .
```
- **Linter**: Flake8 / pylint
- **Tipado**: mypy (opcional)

## Licencia
Este repositorio no tiene licencia especificada. Contacta al autor para más información.

## Contacto
- **Autor**: jfzepeda
- GitHub: [https://github.com/jfzepeda](https://github.com/jfzepeda)
