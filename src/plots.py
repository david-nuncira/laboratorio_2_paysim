from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_figures(df: pd.DataFrame, hourly: pd.DataFrame, figures_dir: str | Path) -> list[str]:
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    paths: list[str] = []
    sample = df.sample(min(len(df), 100_000), random_state=42)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(sample["monto"].dropna(), bins=50, stat="density", color="#2166ac", ax=ax)
    ax.set_title("Distribución del monto")
    ax.set_xlabel("Monto")
    path = figures_dir / "histograma_monto.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(9, 2.8))
    sns.boxplot(x=sample["monto"], color="#67a9cf", ax=ax)
    ax.set_title("Boxplot del monto")
    path = figures_dir / "boxplot_monto.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(sample["step"].dropna(), bins=min(50, int(sample["step"].nunique())), discrete=True, color="#1b7837", ax=ax)
    ax.set_title("Distribución del step")
    ax.set_xlabel("Step horario")
    path = figures_dir / "histograma_step.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(9, 2.8))
    sns.boxplot(x=sample["step"], color="#7fbf7b", ax=ax)
    ax.set_title("Boxplot del step")
    path = figures_dir / "boxplot_step.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(hourly["transacciones_hora"], bins=min(40, max(10, int(hourly.shape[0] ** 0.5))), color="#762a83", ax=ax)
    ax.set_title("Distribución del número de transacciones por hora")
    ax.set_xlabel("Transacciones por step")
    path = figures_dir / "histograma_transacciones_hora.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(9, 2.8))
    sns.boxplot(x=hourly["transacciones_hora"], color="#af8dc3", ax=ax)
    ax.set_title("Boxplot del número de transacciones por hora")
    path = figures_dir / "boxplot_transacciones_hora.png"
    _save(fig, path); paths.append(str(path))

    type_counts = df["tipo_transaccion"].astype("string").value_counts().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=type_counts.values, y=type_counts.index, color="#ef8a62", ax=ax)
    ax.set_title("Frecuencia por tipo de transacción")
    ax.set_xlabel("Frecuencia")
    ax.set_ylabel("Tipo de transacción")
    path = figures_dir / "barras_tipo_transaccion.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(data=sample, x="step", y="monto", alpha=0.18, s=12, color="#5e3c99", ax=ax)
    ax.set_title("Relación entre step y monto")
    path = figures_dir / "scatter_step_monto.png"
    _save(fig, path); paths.append(str(path))

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=hourly, x="step", y="transacciones_hora", color="#2166ac", linewidth=1.0, ax=ax)
    ax.set_title("Transacciones por step")
    ax.set_xlabel("Step")
    path = figures_dir / "serie_transacciones_hora.png"
    _save(fig, path); paths.append(str(path))

    profile = hourly.groupby("hora_dia", observed=True)["transacciones_hora"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=profile, x="hora_dia", y="transacciones_hora", color="#4393c3", ax=ax)
    ax.set_title("Perfil promedio intradía")
    ax.set_xlabel("Fase horaria (step % 24; sin hora civil verificada)")
    ax.set_ylabel("Promedio de transacciones")
    path = figures_dir / "perfil_intradia.png"
    _save(fig, path); paths.append(str(path))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    sns.histplot(np.log1p(sample.monto), bins=50, ax=axes[0], color='#2166ac')
    axes[0].set(title='Monto transformado', xlabel='log(1 + monto)')
    sns.boxplot(data=sample, x='tipo_transaccion', y='monto', ax=axes[1], color='#67a9cf', showfliers=False)
    axes[1].set_yscale('symlog'); axes[1].tick_params(axis='x', rotation=35)
    axes[1].set(title='Monto por tipo (sin puntos extremos)', xlabel='Tipo', ylabel='Monto (escala symlog)')
    path=figures_dir/'monto_transformado_grupos.png'
    _save(fig,path); paths.append(str(path))

    fig, axes=plt.subplots(1,2,figsize=(11,4))
    for ax,(x,y) in zip(axes,[('monto_promedio','monto_mediano'),('monto_total','monto_promedio')]):
        ax.scatter(hourly[x],hourly[y],s=12,alpha=.6,color='#2166ac')
        ax.set(xlabel=x,ylabel=y,title='Unidad: hora')
    path=figures_dir/'scatter_montos_horarios.png'
    _save(fig,path); paths.append(str(path))

    fig,ax=plt.subplots(figsize=(10,4))
    plot_acf(hourly.transacciones_hora.dropna(),lags=min(72,len(hourly)-1),ax=ax,zero=False)
    ax.set(title='Autocorrelación del conteo horario',xlabel='Rezago (horas)')
    path=figures_dir/'acf_conteo.png'
    _save(fig,path); paths.append(str(path))

    fig,axes=plt.subplots(1,2,figsize=(11,4))
    sns.histplot(hourly.monto_promedio,bins=40,ax=axes[0],color='#2166ac')
    sns.boxplot(x=hourly.monto_promedio,ax=axes[1],color='#67a9cf')
    axes[0].set(title='Media del monto por hora',xlabel='monto_promedio'); axes[1].set(title='Boxplot por hora',xlabel='monto_promedio')
    path=figures_dir/'distribucion_monto_promedio.png'
    _save(fig,path); paths.append(str(path))

    fig,ax=plt.subplots(figsize=(8,4))
    freq=df.tipo_cuenta_destino.value_counts()
    ax.bar(freq.index.astype(str),freq.values,color='#2166ac')
    ax.set(title='Frecuencia por tipo de destino',ylabel='Transacciones')
    path=figures_dir/'barras_tipo_destino.png'
    _save(fig,path); paths.append(str(path))

    return paths

