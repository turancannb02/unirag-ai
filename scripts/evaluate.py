#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from tqdm import tqdm

from unirag.rag import UniAdminRAG


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run batch evaluation on benchmark questions.")
    p.add_argument("--input", default="data/benchmarks/questions.csv", help="Input CSV with questions")
    p.add_argument("--output", default="data/reports/predictions.csv", help="Output CSV for manual scoring")
    p.add_argument("--resume", action="store_true", help="Skip already-answered questions in output file")
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

    # Resume: load already-completed rows and skip them
    completed_ids: set[str] = set()
    existing_rows: list[dict] = []
    if args.resume and out_path.exists():
        existing_df = pd.read_csv(out_path)
        # Only count rows that didn't error out
        done = existing_df[~existing_df["model_answer"].astype(str).str.startswith("ERROR")]
        completed_ids = {str(x) for x in done["id"].tolist()}
        existing_rows = existing_df.to_dict("records")
        print(f"Resuming: {len(completed_ids)} already completed, {len(df) - len(completed_ids)} remaining.")

    rag = UniAdminRAG()

    rows: list[dict] = list(existing_rows)
    errors = 0

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating"):
        if str(row["id"]) in completed_ids:
            continue

        try:
            result = rag.ask(str(row["question"]))
            citation_str = "; ".join(
                f"{c['source']}#p{c['page']} ({c['chunk_id']})" for c in result["citations"]
            )
            model_answer = result["answer"]
        except Exception as e:
            print(f"\nERROR on {row['id']}: {e}")
            model_answer = f"ERROR: {e}"
            citation_str = ""
            errors += 1

        rows.append(
            {
                "id": row["id"],
                "category": row["category"],
                "question": row["question"],
                "reference_answer": row.get("reference_answer", ""),
                "model_answer": model_answer,
                "citations": citation_str,
                "correctness_0_2": "",
                "completeness_0_2": "",
                "compliance_0_2": "",
                "citation_quality_0_2": "",
                "total_0_8": "",
                "notes": "",
            }
        )

        # Save after every question so crashes lose at most one answer
        pd.DataFrame(rows).to_csv(out_path, index=False)

    print(f"\nDone. {len(rows)} rows written to {out_path}")
    if errors:
        print(f"  {errors} questions errored — re-run with --resume to retry them.")
    else:
        print("  No errors.")


if __name__ == "__main__":
    main()