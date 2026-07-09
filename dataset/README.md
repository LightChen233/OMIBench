---
license: cc-by-4.0
task_categories:
- visual-question-answering
- multiple-choice
language:
- en
tags:
- science
- multimodal
- multi-image
- reasoning
- olympiad
- biology
- chemistry
- physics
- mathematics
size_categories:
- 1K<n<10K
configs:
- config_name: default
  data_files:
  - split: test
    path: test.jsonl
---

# OMI-Bench: Olympiad-level Multi-Image Science Benchmark

OMI-Bench is a **multimodal, multi-image** benchmark of olympiad-level science
questions across **Biology, Chemistry, Mathematics, and Physics**. Every
question is grounded in **two or more images** (diagrams, figures, structures,
experimental setups), making it a test of genuine multi-image scientific
reasoning rather than single-figure perception.

## Dataset at a glance

| | |
|---|---|
| Questions | **1,322** |
| Images | **2,837** (all questions are multi-image: 2–11 images each) |
| Subjects | Biology 251 · Chemistry 217 · Mathematics 430 · Physics 424 |
| Answer types | Multiple-choice 574 · Open-ended 748 |
| Multi-answer questions | 97 |
| Language | English |

## Schema

Each line in `test.jsonl` is one question:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique id, e.g. `biology-1` |
| `subject` | string | `biology` / `chemistry` / `mathematics` / `physics` |
| `answer_type` | string | `mcq` (has `choice_list`) or `open` |
| `question` | string | Question text. Images are referenced inline as `[IMAGE0]`, `[IMAGE1]`, … (0-based index into `image_list`). |
| `image_list` | list[str] | Image filenames under `images/`, in tag order |
| `choice_list` | list[str] | Present for `mcq`; options may themselves be images (`[IMAGEn]`) |
| `has_inline_choices` | bool | *(optional, 11 records)* `true` when a question has lettered options written **inside** the question text / a table / the figures rather than in `choice_list`; `answer` holds the chosen option letter(s). Treat these like MCQ when scoring. |
| `known_issue` | string | *(optional)* flags a residual source-data note such as `duplicate_choices:X,Y`, `option_A_contains_stem_statements`, `answer_contains_derivation`, or `restored_from_legacy_physics_json`. The `answer` key is still correct; the flag warns about presentation or provenance. |
| `answer` | list[str] | Gold answer(s). MCQ → option letters (`["C"]`); open → value(s) (`["0.5"]`). Length > 1 = multiple correct answers. |
| `solution` | string | Full worked reasoning chain toward the answer |
| `img_category` | string | *(optional)* fine-grained figure category, when available |

### Image placeholder convention
`[IMAGEn]` is a **global 0-based index** into `image_list`. Tags in the question
come first; for image-answer questions the option tags continue the numbering.
The union of all `[IMAGEn]` tags in a record covers exactly its `image_list`.

## Usage

```python
import json
from PIL import Image

rows = [json.loads(l) for l in open("test.jsonl")]
r = rows[0]
imgs = [Image.open(f"images/{name}") for name in r["image_list"]]
# render r["question"], substituting [IMAGE0..n] with imgs
```

> ⚠️ **Contamination note:** `solution` contains the full reasoning *and the
> answer*. For clean evaluation, prompt models with `question` (+ `choice_list`)
> only and score against `answer`; do not feed `solution`.

## Provenance & licensing

Items are aggregated from established multi-image benchmarks (**ReMI**,
**SeePhys**) and science-olympiad / exam materials, plus a small number of
CC-licensed third-party figures. Per-source attribution and licensing
obligations are documented in [`SOURCES.md`](SOURCES.md).

The dataset card is released under **CC BY 4.0**; individual source items retain
their upstream licenses and citation requirements (see `SOURCES.md`). If you use
OMI-Bench, please also cite the upstream ReMI and SeePhys benchmarks.

## Known limitations

- **Answers are inherited from the source materials and have not been
  independently re-verified for scientific correctness.** Structure,
  answerability, and image–question linkage were checked; the truth of each gold
  `answer` was not re-derived. Treat answer keys as source-provided.
- `solution` chains are model-/annotator-generated reasoning, not peer-reviewed
  proofs; they may contain errors even when the final `answer` is correct.
- Some open-ended answers are free-form strings (e.g. `"a) FALSE b) TRUE …"`),
  requiring answer-normalization for automatic scoring.
- 11 records carry lettered options inline (see `has_inline_choices`); a few
  physics answers encode tables as flattened text.
- English only.

## Changelog (release preparation)

- Added explicit `answer_type` field to every record.
- Removed an internal annotation field.
- Repaired 2 malformed multiple-choice records.
- Trimmed per-question `image_list`s to referenced images and re-indexed tags.
- Restored 9 legacy physics records from the older physics JSON export after
  cleaning formatting artifacts and raw image placeholders (`restored_records.csv`).
- Replaced 4 CC BY-NC-ND (NonCommercial/NoDerivatives) photos in
  biology-53/54/55/105 with newly generated, license-clean illustrations
  (`gpt-image-2`); records keep their multi-image layout. No questions dropped.
- Cleaned text-hygiene issues (stray control chars, leaked JSON fragments,
  legacy `<image_n>` tags, unpaired `$`); tagged 11 inline-choice records.
