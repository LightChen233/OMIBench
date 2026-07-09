# OMI-Bench — Sources & Attribution

This dataset aggregates science-olympiad-style multimodal questions across
Biology, Chemistry, Mathematics, and Physics. Items are drawn from several
upstream sources. This file documents provenance and the attribution/licensing
obligations that carry over to any redistribution.

> **Action required before public release:** confirm you have the right to
> redistribute every source below. Items flagged **⚠ RESTRICTIVE** must be
> regenerated, removed, or cleared with the rights holder — a CC BY-NC-ND
> license does **not** permit the redistribution of cropped derivatives.

## 1. Record provenance (by ID prefix)

| Source | ID pattern | Records | Notes / citation obligation |
|---|---|---|---|
| ReMI benchmark | `physics-ReMI-*` | 109 | Established multi-image reasoning benchmark. **Cite upstream** and inherit its license. |
| SeePhys benchmark | `physics-see-*` | 33 | Established physics VQA benchmark. **Cite upstream** and inherit its license. |
| Olympiad / exam scans | `biology-*`, `chemistry-*`, `math-*`, `physics-*`, `physics-mcq-*` | ~1171 | Questions transcribed / cropped from science-olympiad and exam materials (IBO, and other national/international olympiads). Verify each exam's reuse terms. |

## 2. Image file families

| File family | Count | Meaning |
|---|---|---|
| `*_bytes_img_*.png` | 755 | Extracted from an upstream HF parquet (see repo `get_data.py` → `LARG/OMIBench`). |
| `<uuid>_*.jpg` | 1065 | Region crops from source-document scans. |
| `batch-*.jpg` | 1011 | Pages/figures extracted from exam PDFs. |
| `chem_*.png` | 537 | Chemistry figures (structures, mechanisms). |
| `physics_remi_*` | 218 | ReMI benchmark images. |
| `physics_seephys_*` | 179 | SeePhys benchmark images. |
| `inbo_*.jpg` | 4 | International Biology Olympiad figures. |

## 3. Third-party figures with embedded CC attributions

These records contain figures whose license was recorded in the source text.

### ✅ CC BY 4.0 — redistribution OK **with attribution**
| Records | Attribution |
|---|---|
| biology-113, 114, 115, 116, 117 | Raquel Álvarez-Ocaña et al. (2023), "…of Drosophila and Oviposition Choice Assay", CC BY 4.0 |

### ✅ RESOLVED — formerly CC BY-NC-ND (NonCommercial + NoDerivatives)
These records previously embedded CC BY-NC-ND Flickr photos (not redistributable
as cropped derivatives). Each restricted photo has been **replaced with a newly
generated, license-clean illustration** (`gpt-image-2`) depicting the same
phenomenon; the credit caption was replaced with a neutral "(illustration)"
label. The records keep their original two-image layout and remain answerable.
No questions were dropped.

| Records | Replaced image | Now uses | Formerly attributed to |
|---|---|---|---|
| biology-53, 54, 55 | girdled-birch photo | `gen_girdled_birch_tree.png` (AI-generated) | Dave Bonta, Flickr, CC BY-NC-ND 2.0 |
| biology-105 | leafcutter-ants photo | `gen_leafcutter_ants.png` (AI-generated) | pluckytree, Flickr, CC BY-NC-ND 2.0 DEED |

The two `gen_*.png` illustrations are AI-generated and carry no third-party
license restriction.

## 4. Root dataset reference

`get_data.py` in the code repo loads `LARG/OMIBench` from the Hugging Face Hub.
If this release is the same project's re-publication, state the relationship
explicitly (self-derived vs. third-party) in the dataset card.

## 5. Removed content

- An image attributed to *de Souza Guerreiro et al. 2023*
  (`https://doi.org/10.1002/advs.202205007`, CC BY 4.0) was flagged for removal
  upstream and is **not present** in the current release.
- 9 legacy physics records with formatting artifacts in an older JSON export
  were repaired and restored for release (see `../restored_records.csv`).
