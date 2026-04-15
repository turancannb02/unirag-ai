#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate manual rubric scores.")
    p.add_argument("--input", default="data/reports/predictions_scored.csv", help="Scored CSV")
    p.add_argument("--output", default="data/reports/summary.md", help="Summary markdown")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)

    df = pd.read_csv(in_path)
    score_cols = [
        "correctness_0_2",
        "completeness_0_2",
        "compliance_0_2",
        "citation_quality_0_2",
    ]

    for c in score_cols:
        if c not in df.columns:
            raise ValueError(f"Missing column: {c}")
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["total_0_8"] = df[score_cols].sum(axis=1)

    n = len(df)
    max_total = n * 8
    obtained = float(df["total_0_8"].sum())
    pct = (obtained / max_total * 100) if max_total else 0.0
    avg = (obtained / n) if n else 0.0

    by_cat = df.groupby("category", as_index=False)["total_0_8"].mean().sort_values("total_0_8", ascending=False)

    lines = []
    lines.append("# UniAdmin-AI Evaluation Summary")
    lines.append("")
    lines.append(f"- Questions evaluated: {n}")
    lines.append(f"- Total score: {obtained:.1f} / {max_total}")
    lines.append(f"- Overall performance: {pct:.2f}% of maximum")
    lines.append(f"- Average per question: {avg:.2f} / 8.00")
    lines.append("")
    lines.append("## Category Breakdown (Average Total Score /8)")
    lines.append("")
    for _, r in by_cat.iterrows():
        lines.append(f"- {r['category']}: {r['total_0_8']:.2f}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote summary: {out_path}")


if __name__ == "__main__":
    main()
