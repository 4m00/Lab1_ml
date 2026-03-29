"""
Построение графиков по результатам бенчмарка.
Запуск: python benchmark_graphics.py
Читает benchmark_results.json, созданный benchmark.py
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

APPROACHES = ["SQLAlchemy ORM", "Django ORM", "Raw SQL"]
COLORS     = {"SQLAlchemy ORM": "#4C72B0", "Django ORM": "#DD8452", "Raw SQL": "#55A868"}
SIZES      = [1000, 10000, 100000]

plt.rcParams.update({
    "font.family":    "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
})


def load(path="benchmark_results.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


# ── График 1: Сравнение подходов по каждому запросу ──────────
def plot_bar_by_query(data: dict, size: int):
    res     = data[size]
    queries = list(res.keys())
    x, w    = np.arange(len(queries)), 0.25

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, ap in enumerate(APPROACHES):
        vals = [res[q][ap] for q in queries]
        bars = ax.bar(x + i * w, vals, w, label=ap,
                      color=COLORS[ap], alpha=0.85)
        ax.bar_label(bars, fmt="%.4f", fontsize=7, padding=2)

    ax.set_title(f"Сравнение ORM vs Raw SQL  (MS SQL Server, {size:,} записей)")
    ax.set_ylabel("Среднее время (сек)")
    ax.set_xlabel("Тип запроса")
    ax.set_xticks(x + w);  ax.set_xticklabels(queries, rotation=15, ha="right")
    ax.legend()
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.4f"))
    plt.tight_layout()
    fname = f"graph1_bar_{size}.png"
    plt.savefig(fname, dpi=150); plt.close()
    print(f"✅ {fname}")


# ── График 2: Масштабируемость ────────────────────────────────
def plot_scaling(data: dict, query_name: str):
    fig, ax = plt.subplots(figsize=(8, 4))
    for ap in APPROACHES:
        vals = [data[s][query_name][ap] for s in SIZES]
        ax.plot(SIZES, vals, marker="o", label=ap, color=COLORS[ap], lw=2)
        for x, y in zip(SIZES, vals):
            ax.annotate(f"{y:.5f}", (x, y),
                        textcoords="offset points", xytext=(0, 7),
                        fontsize=7, ha="center")

    ax.set_title(f"Масштабируемость: «{query_name}»")
    ax.set_xlabel("Объём данных")
    ax.set_ylabel("Среднее время (сек)")
    ax.set_xscale("log")
    ax.set_xticks(SIZES); ax.set_xticklabels([f"{s:,}" for s in SIZES])
    ax.legend(); plt.tight_layout()
    safe  = query_name.replace(" ", "_").replace("(", "").replace(")", "")
    fname = f"graph2_scaling_{safe}.png"
    plt.savefig(fname, dpi=150); plt.close()
    print(f"✅ {fname}")


# ── График 3: Тепловая карта накладных расходов ───────────────
def plot_heatmap(data: dict, size: int):
    res     = data[size]
    queries = list(res.keys())
    raw_v   = np.array([res[q]["Raw SQL"] for q in queries])

    matrix = np.array([
        ((np.array([res[q][ap] for q in queries]) - raw_v) / raw_v * 100).round(1)
        for ap in ["SQLAlchemy ORM", "Django ORM"]
    ])

    fig, ax = plt.subplots(figsize=(10, 3))
    im = ax.imshow(matrix, cmap="RdYlGn_r", aspect="auto",
                   vmin=0, vmax=max(matrix.max(), 10))
    ax.set_xticks(range(len(queries)))
    ax.set_xticklabels(queries, rotation=15, ha="right", fontsize=9)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["SQLAlchemy ORM", "Django ORM"])
    ax.set_title(f"Накладные расходы ORM vs Raw SQL, %  ({size:,} записей)")
    for i in range(2):
        for j in range(len(queries)):
            ax.text(j, i, f"{matrix[i,j]:.0f}%",
                    ha="center", va="center", fontsize=9)
    plt.colorbar(im, ax=ax, label="%")
    plt.tight_layout()
    fname = f"graph3_heatmap_{size}.png"
    plt.savefig(fname, dpi=150); plt.close()
    print(f"✅ {fname}")


# ── График 4: Сводный по всем объёмам ────────────────────────
def plot_all_sizes(data: dict):
    queries = list(data[1000].keys())
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
    for ax, size in zip(axes, SIZES):
        res = data[size]
        x, w = np.arange(len(queries)), 0.25
        for i, ap in enumerate(APPROACHES):
            ax.bar(x + i * w, [res[q][ap] for q in queries], w,
                   label=ap, color=COLORS[ap], alpha=0.85)
        ax.set_title(f"{size:,} записей")
        ax.set_ylabel("Время (сек)")
        ax.set_xticks(x + w)
        ax.set_xticklabels(queries, rotation=20, ha="right", fontsize=7)
        if size == 1000:
            ax.legend(fontsize=8)
    plt.suptitle("Производительность при разных объёмах данных (MS SQL Server)",
                 fontsize=13)
    plt.tight_layout()
    fname = "graph4_all_sizes.png"
    plt.savefig(fname, dpi=150); plt.close()
    print(f"✅ {fname}")


if __name__ == "__main__":
    data = load()
    print("📊 Построение графиков...")

    for size in SIZES:
        plot_bar_by_query(data, size)

    for q in list(data[1000].keys()):
        plot_scaling(data, q)

    plot_heatmap(data, 1000)
    plot_heatmap(data, 100000)
    plot_all_sizes(data)

    print("\n✅ Все графики сохранены в текущей папке.")
