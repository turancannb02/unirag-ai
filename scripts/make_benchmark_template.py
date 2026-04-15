#!/usr/bin/env python3
from pathlib import Path

import pandas as pd


CATEGORIES = [
    "enrollment",
    "tuition_payment",
    "exam_registration",
    "transcript_requests",
    "semester_deadlines",
    "portal_login_support",
]


def main() -> None:
    rows = []
    idx = 1
    for cat in CATEGORIES:
        for i in range(1, 17):
            rows.append(
                {
                    "id": f"Q{idx:03d}",
                    "category": cat,
                    "question": f"[{cat}] Example question {i}: replace with real student admin question.",
                    "reference_answer": "",
                }
            )
            idx += 1

    # 96 questions; user can add 4 extra for 100.
    out = Path("data/benchmarks/questions.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Created benchmark template: {out}")


if __name__ == "__main__":
    main()
