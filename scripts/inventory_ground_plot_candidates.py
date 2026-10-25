#!/usr/bin/env python3
"""Inventory FAIB ground-plot candidates for a pre-registered validation test.

The public FAIB header and visit tables identify plot programs and remeasurement
history, but they do not identify management origin. This script reports the
available counts so the validation plan can decide whether a confirmatory test is
possible.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

OUTPUT_COLUMNS = (
    "source",
    "tsa",
    "sample_type",
    "sites",
    "visits",
    "remeasured_sites",
    "young_sites",
    "age_known_visits",
    "management_origin_field",
)


def _age_series(visits: pd.DataFrame) -> pd.Series[Any]:
    """Return the projected age, falling back to the first age field."""
    age = pd.to_numeric(visits["PROJ_AGE_ADJ"], errors="coerce")
    if "PROJ_AGE_1" in visits:
        age = age.fillna(pd.to_numeric(visits["PROJ_AGE_1"], errors="coerce"))
    return age


def inventory_source(
    *,
    header: pd.DataFrame,
    visits: pd.DataFrame,
    tsa: int,
    source: str,
) -> pd.DataFrame:
    """Return candidate counts for one plot source and TSA.

    Parameters
    ----------
    header : pandas.DataFrame
        FAIB site header with ``SITE_IDENTIFIER``, ``TSA``, and
        ``SAMPLE_ESTABLISHMENT_TYPE``.
    visits : pandas.DataFrame
        FAIB visit table with ``SITE_IDENTIFIER`` and an age column.
    tsa : int
        Timber supply area number to keep.
    source : str
        Source label, ``PSP`` or ``NONPSP``.

    Returns
    -------
    pandas.DataFrame
        One row per sample type plus an ``ALL`` row.
    """
    selected = header[pd.to_numeric(header["TSA"], errors="coerce") == tsa].copy()
    site_ids = set(selected["SITE_IDENTIFIER"])
    frame = visits[visits["SITE_IDENTIFIER"].isin(site_ids)].copy()
    frame = frame.drop(columns=["SAMPLE_ESTABLISHMENT_TYPE"], errors="ignore")
    frame = frame.merge(
        selected[["SITE_IDENTIFIER", "SAMPLE_ESTABLISHMENT_TYPE"]],
        on="SITE_IDENTIFIER",
        how="left",
    )
    frame["age"] = _age_series(frame)
    records: list[dict[str, Any]] = []
    for sample_type, group in selected.groupby("SAMPLE_ESTABLISHMENT_TYPE"):
        sample_visits = frame[frame["SAMPLE_ESTABLISHMENT_TYPE"] == sample_type]
        visit_counts = sample_visits.groupby("SITE_IDENTIFIER").size()
        records.append(
            {
                "source": source,
                "tsa": tsa,
                "sample_type": sample_type,
                "sites": len(group),
                "visits": len(sample_visits),
                "remeasured_sites": int((visit_counts >= 2).sum()),
                "young_sites": int(
                    sample_visits.loc[
                        (sample_visits["age"] >= 5) & (sample_visits["age"] <= 80),
                        "SITE_IDENTIFIER",
                    ].nunique()
                ),
                "age_known_visits": int(sample_visits["age"].notna().sum()),
                "management_origin_field": "absent",
            }
        )
    result = pd.DataFrame(records, columns=OUTPUT_COLUMNS)
    total = {
        "source": source,
        "tsa": tsa,
        "sample_type": "ALL",
        "sites": int(result["sites"].sum()),
        "visits": int(result["visits"].sum()),
        "remeasured_sites": int(result["remeasured_sites"].sum()),
        "young_sites": int(result["young_sites"].sum()),
        "age_known_visits": int(result["age_known_visits"].sum()),
        "management_origin_field": "absent",
    }
    return pd.concat([result, pd.DataFrame([total])], ignore_index=True)


def main() -> None:
    """Write the candidate inventory table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, type=int, choices=(46, 47))
    parser.add_argument("--psp-header", type=Path, required=True)
    parser.add_argument("--psp-visits", type=Path, required=True)
    parser.add_argument("--nonpsp-header", type=Path, required=True)
    parser.add_argument("--nonpsp-visits", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    psp = inventory_source(
        header=pd.read_csv(args.psp_header, low_memory=False),
        visits=pd.read_csv(args.psp_visits, low_memory=False),
        tsa=args.tsa,
        source="PSP",
    )
    nonpsp = inventory_source(
        header=pd.read_csv(args.nonpsp_header, low_memory=False),
        visits=pd.read_csv(args.nonpsp_visits, low_memory=False),
        tsa=args.tsa,
        source="NONPSP",
    )
    result = pd.concat([psp, nonpsp], ignore_index=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(f"wrote {len(result)} inventory rows to {args.out}")


if __name__ == "__main__":
    main()
