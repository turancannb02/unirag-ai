#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from unirag.rag import UniAdminRAG


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run batch evaluation on benchmark questions.")
    p.add_argument("--input", default="data/benchmarks/questions.csv", help="Input CSV with questions")
    p.add_argument("--output", default="data/reports/predictions.csv", help="Output CSV for manual scoring")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)
    required_cols = {"id", "category", "question"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    rag = UniAdminRAG()

    rows = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating"):
        result = rag.ask(str(row["question"]))
        citation_str = "; ".join(
            f"{c['source']}#p{c['page']} ({c['chunk_id']})" for c in result["citations"]
        )
        rows.append(
            {
                "id": row["id"],
                "category": row["category"],
                "question": row["question"],
                "reference_answer": row.get("reference_answer", ""),
                "model_answer": result["answer"],
                "citations": citation_str,
                "correctness_0_2": "",
                "completeness_0_2": "",
                "compliance_0_2": "",
                "citation_quality_0_2": "",
                "total_0_8": "",
                "notes": "",
            }
        )

    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"Wrote predictions for manual scoring: {out_path}")


if __name__ == "__main__":
    main()
