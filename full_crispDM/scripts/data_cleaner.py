"""
DataCleaner - Limpieza automática de datasets
Autor: Senior Full Stack Developer
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import json
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Union
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data_cleaner.log"),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
@dataclass
class CleanerConfig:
    """Configuración central del proceso de limpieza."""
    # Valores nulos
    missing_threshold: float = 0.5        # Eliminar columna si > 50% son nulos
    fill_numeric_strategy: str = "median" # mean | median | mode | zero
    fill_categorical_strategy: str = "mode"  # mode | unknown | drop

    # Duplicados
    remove_duplicates: bool = True
    duplicate_subset: Optional[list] = None  # None = todas las columnas

    # Outliers
    remove_outliers: bool = True
    outlier_method: str = "iqr"           # iqr | zscore
    zscore_threshold: float = 3.0
    iqr_multiplier: float = 1.5

    # Tipos de datos
    infer_types: bool = True
    date_formats: list = field(default_factory=lambda: [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"
    ])

    # Texto
    strip_whitespace: bool = True
    normalize_strings: bool = True        # lowercase + strip
    remove_special_chars: bool = False

    # Columnas
    drop_columns: list = field(default_factory=list)
    rename_columns: dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# REPORTE DE LIMPIEZA
# ─────────────────────────────────────────────
@dataclass
class CleaningReport:
    """Registro de todas las operaciones realizadas."""
    original_shape: tuple = (0, 0)
    final_shape: tuple = (0, 0)
    operations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    execution_time: float = 0.0

    def add_operation(self, op: str, detail: str = ""):
        entry = {"operation": op, "detail": detail, "timestamp": datetime.now().isoformat()}
        self.operations.append(entry)
        logger.info(f"[OP] {op}: {detail}")

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        logger.warning(f"[WARN] {msg}")

    def summary(self) -> dict:
        rows_removed = self.original_shape[0] - self.final_shape[0]
        cols_removed = self.original_shape[1] - self.final_shape[1]
        return {
            "original_shape": self.original_shape,
            "final_shape": self.final_shape,
            "rows_removed": rows_removed,
            "cols_removed": cols_removed,
            "operations_count": len(self.operations),
            "warnings_count": len(self.warnings),
            "execution_time_seconds": round(self.execution_time, 3),
        }


# ─────────────────────────────────────────────
# CLASE PRINCIPAL
# ─────────────────────────────────────────────
class DataCleaner:
    """
    Pipeline de limpieza de datos reutilizable y configurable.

    Uso básico:
        cleaner = DataCleaner()
        df_clean = cleaner.clean("dataset.csv")
        cleaner.save(df_clean, "dataset_clean.csv")
        cleaner.report()
    """

    SUPPORTED_FORMATS = {".csv", ".xlsx", ".xls", ".json", ".parquet"}

    def __init__(self, config: Optional[CleanerConfig] = None):
        self.config = config or CleanerConfig()
        self.report = CleaningReport()
        self._df_original: Optional[pd.DataFrame] = None

    # ──────────────────────────────────────────
    # ENTRADA / SALIDA
    # ──────────────────────────────────────────
    def load(self, source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
        """Carga datos desde archivo o DataFrame."""
        if isinstance(source, pd.DataFrame):
            return source.copy()

        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")

        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato no soportado: {suffix}. Use: {self.SUPPORTED_FORMATS}")

        loaders = {
            ".csv": pd.read_csv,
            ".json": pd.read_json,
            ".parquet": pd.read_parquet,
            ".xlsx": pd.read_excel,
            ".xls": pd.read_excel,
        }

        df = loaders[suffix](path)
        logger.info(f"Dataset cargado: {path.name} → {df.shape[0]} filas, {df.shape[1]} columnas")
        return df

    def save(self, df: pd.DataFrame, output_path: Union[str, Path]) -> Path:
        """Guarda el DataFrame limpio en el formato indicado."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        suffix = path.suffix.lower()
        savers = {
            ".csv": lambda: df.to_csv(path, index=False),
            ".json": lambda: df.to_json(path, orient="records", indent=2),
            ".parquet": lambda: df.to_parquet(path, index=False),
            ".xlsx": lambda: df.to_excel(path, index=False),
        }

        if suffix not in savers:
            raise ValueError(f"Formato de salida no soportado: {suffix}")

        savers[suffix]()
        logger.info(f"Dataset guardado: {path}")
        return path

    # ──────────────────────────────────────────
    # PIPELINE PRINCIPAL
    # ──────────────────────────────────────────
    def clean(self, source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
        """Ejecuta el pipeline completo de limpieza."""
        start = datetime.now()

        df = self.load(source)
        self._df_original = df.copy()
        self.report = CleaningReport(original_shape=df.shape)

        # Pipeline ordenado
        steps = [
            self._drop_configured_columns,
            self._rename_columns,
            self._strip_whitespace,
            self._infer_types,
            self._handle_missing_columns,   # columnas con demasiados nulos
            self._handle_missing_values,    # imputación
            self._remove_duplicates,
            self._normalize_strings,
            self._remove_outliers,
        ]

        for step in steps:
            try:
                df = step(df)
            except Exception as e:
                self.report.add_warning(f"Error en {step.__name__}: {e}")
                logger.exception(f"Paso fallido: {step.__name__}")

        self.report.final_shape = df.shape
        self.report.execution_time = (datetime.now() - start).total_seconds()

        logger.info(f"Limpieza completada en {self.report.execution_time:.2f}s → {df.shape}")
        return df

    # ──────────────────────────────────────────
    # PASOS DEL PIPELINE
    # ──────────────────────────────────────────
    def _drop_configured_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = [c for c in self.config.drop_columns if c in df.columns]
        if cols:
            df = df.drop(columns=cols)
            self.report.add_operation("drop_columns", f"Eliminadas: {cols}")
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {k: v for k, v in self.config.rename_columns.items() if k in df.columns}
        if rename_map:
            df = df.rename(columns=rename_map)
            self.report.add_operation("rename_columns", str(rename_map))
        # Limpiar nombres de columnas por defecto
        df.columns = [re.sub(r"\s+", "_", str(c)).strip().lower() for c in df.columns]
        return df

    def _strip_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.config.strip_whitespace:
            return df
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
        # Convertir strings vacíos a NaN
        df[str_cols] = df[str_cols].replace("", np.nan)
        self.report.add_operation("strip_whitespace", f"{len(str_cols)} columnas procesadas")
        return df

    def _infer_types(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.config.infer_types:
            return df

        converted = []
        for col in df.columns:
            if df[col].dtype == object:
                # Intentar numérico
                numeric = pd.to_numeric(df[col], errors="coerce")
                if numeric.notna().sum() / max(df[col].notna().sum(), 1) > 0.8:
                    df[col] = numeric
                    converted.append(f"{col}→numeric")
                    continue

                # Intentar fecha
                for fmt in self.config.date_formats:
                    try:
                        parsed = pd.to_datetime(df[col], format=fmt, errors="coerce")
                        if parsed.notna().sum() / max(df[col].notna().sum(), 1) > 0.8:
                            df[col] = parsed
                            converted.append(f"{col}→datetime")
                            break
                    except Exception:
                        continue

        if converted:
            self.report.add_operation("infer_types", f"Convertidas: {converted}")
        return df

    def _handle_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        threshold = self.config.missing_threshold
        missing_ratio = df.isnull().mean()
        cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()

        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            self.report.add_operation(
                "drop_high_missing_cols",
                f"Eliminadas ({threshold*100:.0f}% umbral): {cols_to_drop}"
            )
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include=np.number).columns
        cat_cols = df.select_dtypes(include="object").columns

        # Numéricos
        strategy = self.config.fill_numeric_strategy
        for col in numeric_cols:
            if df[col].isnull().any():
                if strategy == "mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == "mode":
                    df[col] = df[col].fillna(df[col].mode()[0])
                elif strategy == "zero":
                    df[col] = df[col].fillna(0)

        # Categóricos
        cat_strategy = self.config.fill_categorical_strategy
        for col in cat_cols:
            if df[col].isnull().any():
                if cat_strategy == "mode" and not df[col].mode().empty:
                    df[col] = df[col].fillna(df[col].mode()[0])
                elif cat_strategy == "unknown":
                    df[col] = df[col].fillna("Unknown")
                elif cat_strategy == "drop":
                    df = df.dropna(subset=[col])

        self.report.add_operation(
            "handle_missing",
            f"Numérico: {strategy} | Categórico: {cat_strategy}"
        )
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.config.remove_duplicates:
            return df

        before = len(df)
        df = df.drop_duplicates(subset=self.config.duplicate_subset, keep="first")
        removed = before - len(df)

        if removed:
            self.report.add_operation("remove_duplicates", f"{removed} filas eliminadas")
        return df

    def _normalize_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.config.normalize_strings:
            return df

        str_cols = df.select_dtypes(include="object").columns
        for col in str_cols:
            df[col] = df[col].str.lower().str.strip()
            if self.config.remove_special_chars:
                df[col] = df[col].str.replace(r"[^\w\s]", "", regex=True)

        self.report.add_operation("normalize_strings", f"{len(str_cols)} columnas normalizadas")
        return df

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.config.remove_outliers:
            return df

        numeric_cols = df.select_dtypes(include=np.number).columns
        before = len(df)
        method = self.config.outlier_method

        if method == "iqr":
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                mult = self.config.iqr_multiplier
                df = df[(df[col] >= Q1 - mult * IQR) & (df[col] <= Q3 + mult * IQR)]

        elif method == "zscore":
            for col in numeric_cols:
                mean, std = df[col].mean(), df[col].std()
                if std > 0:
                    z = (df[col] - mean) / std
                    df = df[abs(z) <= self.config.zscore_threshold]

        removed = before - len(df)
        if removed:
            self.report.add_operation("remove_outliers", f"{removed} filas eliminadas ({method})")
        return df

    # ──────────────────────────────────────────
    # REPORTE
    # ──────────────────────────────────────────
    def report_summary(self, as_json: bool = False) -> Union[dict, str]:
        summary = self.report.summary()
        summary["operations"] = self.report.operations
        summary["warnings"] = self.report.warnings
        return json.dumps(summary, indent=2) if as_json else summary

    def print_report(self):
        print("\n" + "=" * 55)
        print("  DATA CLEANING REPORT")
        print("=" * 55)
        s = self.report.summary()
        print(f"  Forma original : {s['original_shape']}")
        print(f"  Forma final    : {s['final_shape']}")
        print(f"  Filas removidas: {s['rows_removed']}")
        print(f"  Cols removidas : {s['cols_removed']}")
        print(f"  Operaciones    : {s['operations_count']}")
        print(f"  Warnings       : {s['warnings_count']}")
        print(f"  Tiempo         : {s['execution_time_seconds']}s")
        print("-" * 55)
        for op in self.report.operations:
            print(f"  ✔ {op['operation']}: {op['detail']}")
        if self.report.warnings:
            print("\n  WARNINGS:")
            for w in self.report.warnings:
                print(f"  ⚠ {w}")
        print("=" * 55 + "\n")


# ─────────────────────────────────────────────
# EJECUCIÓN DIRECTA (CLI SIMPLE)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python data_cleaner.py <input_file> [output_file]")
        print("Ejemplo: python data_cleaner.py dataset.csv dataset_clean.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"clean_{Path(input_file).name}"

    # Configuración customizable
    config = CleanerConfig(
        missing_threshold=0.5,
        fill_numeric_strategy="median",
        fill_categorical_strategy="mode",
        remove_duplicates=True,
        remove_outliers=True,
        outlier_method="iqr",
        normalize_strings=True,
    )

    cleaner = DataCleaner(config=config)
    df_clean = cleaner.clean(input_file)
    cleaner.save(df_clean, output_file)
    cleaner.print_report()