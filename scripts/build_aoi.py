#!/usr/bin/env python3
"""Build the tracked TSA boundary from the provincial FADM TSA layer.

The public ``FADM_TSA.gdb`` layer carries both the dissolved current TSA and its
supply-block components, plus retired historical versions. The model boundary is
the single current dissolved feature: the requested TSA number, no supply-block
code, and no retirement date.

The script writes a GeoPackage in EPSG:3005 and a small summary JSON so the AOI
area and provenance are recorded in the repository.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd

LAYER: str = "WHSE_ADMIN_BOUNDARIES_FADM_TSA"


def build_aoi(
    *,
    source: Path,
    tsa_number: str,
    out: Path,
    layer: str = LAYER,
    out_layer: str | None = None,
) -> dict[str, object]:
    """Select the current dissolved TSA boundary and write it to a GeoPackage.

    Parameters
    ----------
    source : Path
        Provincial FADM TSA file geodatabase.
    tsa_number : str
        Two-digit TSA code, such as ``"46"``.
    out : Path
        Destination GeoPackage.
    layer : str, optional
        Source layer name. The default is the FADM TSA layer.
    out_layer : str or None, optional
        Destination layer name. The default is ``tsa<number>_full``.

    Returns
    -------
    dict of str to object
        A JSON-ready summary with the source, TSA identity, gross area, bounds,
        and CRS.

    Raises
    ------
    ValueError
        When the source has no matching current dissolved feature, or more than
        one, or the selected geometry is empty.
    """
    frame = gpd.read_file(source, layer=layer)
    if "TSA_NUMBER" not in frame.columns or "TSB_NUMBER" not in frame.columns:
        raise ValueError("source layer is missing TSA_NUMBER or TSB_NUMBER")
    code = str(tsa_number).zfill(2)
    numbers = frame["TSA_NUMBER"].astype(str).str.zfill(2)
    selected = frame.loc[
        (numbers == code) & frame["TSB_NUMBER"].isna() & frame["RETIREMENT_DATE"].isna()
    ].copy()
    if len(selected) != 1:
        raise ValueError(
            f"expected one current dissolved TSA {code} feature, found {len(selected)}"
        )
    selected = selected.to_crs("EPSG:3005")
    if selected.geometry.is_empty.any():
        raise ValueError(f"TSA {code} boundary geometry is empty")
    dissolved = selected[["geometry"]].dissolve().reset_index(drop=True)
    area_ha = float(dissolved.geometry.area.sum()) / 10000.0
    name = str(selected["TSA_NUMBER_DESCRIPTION"].iloc[0])
    destination_layer = out_layer or f"tsa{code}_full"
    out.parent.mkdir(parents=True, exist_ok=True)
    dissolved.to_file(out, layer=destination_layer, driver="GPKG")
    bounds = [round(float(value), 4) for value in dissolved.total_bounds]
    return {
        "source": str(source),
        "source_layer": layer,
        "tsa_number": code,
        "tsa_name": name,
        "out": str(out),
        "out_layer": destination_layer,
        "crs": str(dissolved.crs),
        "features": len(dissolved),
        "gross_area_ha": round(area_ha, 4),
        "bounds_epsg3005": bounds,
    }


def main() -> None:
    """Write the TSA boundary and its summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--tsa-number", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--layer", default=LAYER)
    parser.add_argument("--out-layer", default=None)
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args()
    summary = build_aoi(
        source=args.source,
        tsa_number=args.tsa_number,
        out=args.out,
        layer=args.layer,
        out_layer=args.out_layer,
    )
    summary_path = args.summary or args.out.with_suffix(".summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
