from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from engine import build_hourly, load_dataset, run_full_analysis
from plots import generate_figures


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta el análisis completo del Laboratorio 2.")
    parser.add_argument("--data", default=str(ROOT / "data" / "transacciones.csv"), help="Ruta del CSV PaySim adaptado")
    parser.add_argument("--output", default=str(ROOT / "results"), help="Carpeta de resultados")
    args = parser.parse_args()
    output = Path(args.output)
    print(f"Cargando datos desde: {args.data}")
    df = load_dataset(args.data)
    results = run_full_analysis(args.data, output, df=df)
    hourly = build_hourly(df)
    figure_paths = generate_figures(df, hourly, output / "figures")
    (output / "figure_manifest.txt").write_text("\n".join(figure_paths), encoding="utf-8")
    print(f"Filas analizadas: {results['metadata']['rows']}")
    print(f"Muestra correlación transaccional: {results['metadata']['sample_n_for_correlations']}")
    print(f"Figuras generadas: {len(figure_paths)}")
    print(f"Resultados: {output.resolve()}")


if __name__ == "__main__":
    main()

