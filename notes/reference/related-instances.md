# Related Great Bear Rainforest instances

The GBR North (TSA 46) and GBR South (TSA 47) models are **deliberately
related but independent**.

| Repository | Boundary | Primary use |
| --- | --- | --- |
| `UBC-FRESH/femic-tsa46-instance` | full TSA 46 | GBR North AAC/THLB benchmark |
| `UBC-FRESH/femic-tsa47-instance` (this repo) | full TSA 47 | GBR South AAC/THLB benchmark |

## Shared inputs, separate runtimes

Both instances consume the same public BC inventory and FEMIC/VDYP export lane.
They do **not** share a compiled matrix, a run directory, or a web service.

- TSA 46 was created from the former North Coast and Mid Coast TSAs.
- TSA 47 was created from the mainland portions of the former Kingcome and
  Strathcona TSAs.
- The two AACs are separate legal determinations: 803,000 m3/yr for GBR North
  and 830,500 m3/yr for GBR South.

## Use them together or separately

Use this repository alone when the question is:

- can the GBR South land base sustain 830,500 m3/yr?
- how do the former Kingcome and Strathcona land bases compare?

Use `femic-tsa46-instance` alone when the question is:

- can the GBR North land base sustain 803,000 m3/yr?
- how does the GBR North THLB compare with the predecessor TSA netdowns?

Neither repository imports the other. Record any shared assumption in both
notes.
