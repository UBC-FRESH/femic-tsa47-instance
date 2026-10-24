#!/usr/bin/env python3
"""Build a TSR-consistent BatchTIPSY input table for a GBR instance.

The legacy FEMIC handoff uses the VDYP operational adjustment factor as
``OAF1`` and a single provisional species mix. The predecessor TSRs instead
use OAF1 = 0.85, OAF2 = 0.95, and regenerate future stands to the existing
analysis-unit species composition. This script rebuilds the BTC input from the
calibrated stand checkpoint and the model AU table.

The species mix is area-weighted by ``thlb_area`` and restricted to conifers.
Up to three species are carried. Stem density is split across those species.
Every site-index column is set to the AU's representative inventory SI so
BatchTIPSY can evaluate whichever species is planted.

This is a data-preparation step, not a yield model. It writes the CSV that
``femic tipsy run-btc`` consumes.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.feather as feather

CONIFER_SPECIES_MAP: dict[str, str] = {
    "BA": "Ba",
    "B": "Ba",
    "CW": "Cw",
    "FD": "Fd",
    "FDC": "Fd",
    "H": "Hw",
    "HM": "Hm",
    "HW": "Hw",
    "L": "L",
    "PA": "Pa",
    "PL": "Pl",
    "PLI": "Pl",
    "PLC": "Pl",
    "S": "Sx",
    "SB": "Sb",
    "SE": "Se",
    "SS": "Ss",
    "SW": "Sx",
    "SX": "Sx",
    "SXS": "Sx",
    "YC": "Yc",
}

SPECIES_COLUMNS = tuple(f"SPECIES_CD_{index}" for index in range(1, 7))
PERCENT_COLUMNS = tuple(f"SPECIES_PCT_{index}" for index in range(1, 7))
SITE_INDEX_COLUMNS = (
    "at_si",
    "ba_si",
    "bg_si",
    "bl_si",
    "cw_si",
    "dr_si",
    "ep_si",
    "fd_si",
    "hm_si",
    "hw_si",
    "lt_si",
    "lw_si",
    "pa_si",
    "pl_si",
    "pw_si",
    "py_si",
    "sb_si",
    "se_si",
    "ss_si",
    "sw_si",
    "sx_si",
    "yc_si",
)


def _as_float(value: object) -> float | None:
    """Return a finite float, or ``None`` when the value is missing."""
    if value is None or value is pd.NA:
        return None
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return result if result == result else None


def derive_species_mix(
    *,
    checkpoint_path: Path,
    au_table_path: Path,
    area_column: str = "thlb_area",
    au_column: str = "au",
) -> dict[int, dict[str, float]]:
    """Derive an area-weighted conifer species mix for each managed AU.

    Parameters
    ----------
    checkpoint_path : Path
        Calibrated stand checkpoint with ``au``, an area column, and the six
        VRI species code/percent pairs.
    au_table_path : Path
        FEMIC AU table mapping ``au_id`` to ``source_managed_local_au_id``.
    area_column : str
        Area column used as the weight. Defaults to ``thlb_area``.
    au_column : str
        Model AU column in the checkpoint. Defaults to ``au``.

    Returns
    -------
    dict[int, dict[str, float]]
        Local managed AU id to a species-to-percent mapping. Percentages sum to
        100 and contain at most three conifer species.
    """
    au_table = pd.read_csv(au_table_path)
    id_map = {
        int(au_id): int(local_id)
        for au_id, local_id in zip(
            au_table["au_id"], au_table["source_managed_local_au_id"], strict=False
        )
        if pd.notna(local_id)
    }
    columns = [
        au_column,
        area_column,
        *SPECIES_COLUMNS,
        *PERCENT_COLUMNS,
    ]
    table = feather.read_table(checkpoint_path, columns=columns).to_pandas()
    table = table[table[au_column].notna() & (table[area_column] > 0)].copy()
    table["local_au"] = table[au_column].astype(int).map(id_map)

    mix_by_au: dict[int, dict[str, float]] = {}
    for local_au, group in table[table["local_au"].notna()].groupby("local_au"):
        mix: defaultdict[str, float] = defaultdict(float)
        for _, row in group.iterrows():
            weight = float(row[area_column])
            for code_column, percent_column in zip(SPECIES_COLUMNS, PERCENT_COLUMNS, strict=True):
                raw_code = row[code_column]
                percent = _as_float(row[percent_column])
                if pd.isna(raw_code) or percent is None or percent <= 0:
                    continue
                code = CONIFER_SPECIES_MAP.get(str(raw_code).strip().upper())
                if code is not None:
                    mix[code] += percent * weight
        total = sum(mix.values())
        if total <= 0:
            raise ValueError(f"No conifer species mix for AU {int(local_au)}")
        normalized = {code: value / total * 100.0 for code, value in mix.items()}
        ranked = sorted(normalized.items(), key=lambda item: (-item[1], item[0]))[:3]
        mix_by_au[int(local_au)] = dict(ranked)
    if not mix_by_au:
        raise ValueError(f"No managed AUs found in {checkpoint_path}")
    return mix_by_au


def _integer_mix(mix: dict[str, float], *, total: int) -> list[tuple[str, int]]:
    """Convert fractional species shares to integer percentages and counts.

    The percentage is rounded first, then the density is split from that integer
    percentage. This keeps the written CSV stable and makes the density total
    exactly ``total``.
    """
    items = list(mix.items())
    percentages = [round(share) for _, share in items]
    if percentages:
        percentages[-1] = 100 - sum(percentages[:-1])
    densities = [round(total * percent / 100.0) for percent in percentages]
    if densities:
        densities[-1] = total - sum(densities[:-1])
    return [(code, density) for (code, _), density in zip(items, densities, strict=True)]


def build_tsr_input(
    *,
    source_input: pd.DataFrame,
    mix_by_au: dict[int, dict[str, float]],
    density: int,
    oaf1: float,
    oaf2: float,
    regen_delay: int | None,
) -> pd.DataFrame:
    """Return the TSR-consistent BTC input rows.

    Parameters
    ----------
    source_input : pandas.DataFrame
        Pipeline-generated ``03_input-tsaXX.csv``. Its site-index columns set
        the AU-level SI.
    mix_by_au : dict[int, dict[str, float]]
        Species mix from :func:`derive_species_mix`.
    density : int
        Total regeneration density in stems per hectare.
    oaf1 : float
        Operational adjustment factor 1.
    oaf2 : float
        Operational adjustment factor 2.
    regen_delay : int or None
        Fixed regeneration delay. ``None`` uses 1 year for a cedar/yellow-cedar
        leading mix and 2 years otherwise.

    Returns
    -------
    pandas.DataFrame
        BTC-ready rows.
    """
    rows: list[dict[str, Any]] = []
    for _, source in source_input.iterrows():
        feature_id = int(source["feature_id"])
        mix = mix_by_au.get(feature_id)
        if mix is None:
            raise ValueError(f"No species mix for managed AU {feature_id}")
        species = _integer_mix(mix, total=density)
        leading = species[0][0]
        row: dict[str, Any] = {str(key): value for key, value in source.to_dict().items()}
        for index in range(1, 6):
            if index <= len(species):
                row[f"planted_species{index}"] = species[index - 1][0]
                row[f"planted_density{index}"] = species[index - 1][1]
            else:
                row[f"planted_species{index}"] = ""
                row[f"planted_density{index}"] = 0
            row[f"genetic_worth{index}"] = ""
            row[f"natural_species{index}"] = ""
            row[f"natural_density{index}"] = ""
        si_values = [
            value
            for column in SITE_INDEX_COLUMNS
            if (value := _as_float(row.get(column))) is not None and value > 0
        ]
        si = max(si_values) if si_values else 8.0
        for column in SITE_INDEX_COLUMNS:
            row[column] = si
        row["planted_percent"] = 100
        row["planting_delay"] = (
            (1 if leading in {"Cw", "Yc"} else 2) if regen_delay is None else int(regen_delay)
        )
        row["oaf1"] = float(oaf1)
        row["oaf2"] = float(oaf2)
        rows.append(row)
    if not rows:
        raise ValueError("No rows in the source input")
    return pd.DataFrame(rows)


def main() -> None:
    """Write the TSR-consistent BTC input CSV."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tsa", required=True, choices=("46", "47"))
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument(
        "--au-table", type=Path, default=Path("data/model_input_bundle/au_table.csv")
    )
    parser.add_argument("--source-input", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--density", type=int)
    parser.add_argument("--oaf1", type=float, default=0.85)
    parser.add_argument("--oaf2", type=float, default=0.95)
    parser.add_argument(
        "--regen-delay",
        type=int,
        choices=(1, 2),
        default=None,
        help="Fixed regeneration delay; omit for cedar=1, other=2.",
    )
    args = parser.parse_args()

    if args.tsa == "46":
        default_density, default_regen_delay = 4444, None
    else:
        default_density, default_regen_delay = 1000, 1
    checkpoint = args.checkpoint or Path(
        f"runtime/tsa{args.tsa}_full/thlb_calibrated_checkpoint.feather"
    )
    source_input = args.source_input or Path(f"data/03_input-tsa{args.tsa}.csv")
    output = args.out or Path(f"tipsy_io/runs/03_input-tsa{args.tsa}_tsr.csv")
    density = args.density or default_density
    regen_delay = args.regen_delay if args.regen_delay is not None else default_regen_delay

    mix_by_au = derive_species_mix(
        checkpoint_path=checkpoint,
        au_table_path=args.au_table,
    )
    frame = build_tsr_input(
        source_input=pd.read_csv(source_input),
        mix_by_au=mix_by_au,
        density=density,
        oaf1=args.oaf1,
        oaf2=args.oaf2,
        regen_delay=regen_delay,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(f"wrote {len(frame)} TSR-consistent rows to {output}")


if __name__ == "__main__":
    main()
