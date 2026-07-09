# OMI-Bench: Olympiad-level Multi-Image Science Benchmark

[![Dataset](https://img.shields.io/badge/Dataset-OMI--Bench-blue)](dataset/README.md)
[![Paper](https://img.shields.io/badge/arXiv-2604.20806-b31b1b.svg)](https://arxiv.org/abs/2604.20806)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](LICENSE)
[![Dataset License](https://img.shields.io/badge/Dataset%20Card-CC%20BY%204.0-lightgrey.svg)](dataset/README.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

OMI-Bench is a multimodal, multi-image benchmark for olympiad-level science reasoning across **Biology**, **Chemistry**, **Mathematics**, and **Physics**. Every question is grounded in two or more images, making the benchmark focus on genuine multi-image scientific reasoning rather than single-figure perception.

## News

- OMI-Bench has an arXiv preprint: [arXiv:2604.20806](https://arxiv.org/abs/2604.20806).
- This repository is cleaned for public release with one canonical CLI entry point: [`omi_bench.py`](omi_bench.py).
- The benchmark contains **1,322** questions and **2,837** referenced images across four science domains.
- The release statistics are aligned with the arXiv dataset snapshot; 9 legacy physics records were repaired from the older physics JSON export before release, as documented in [`restored_records.csv`](restored_records.csv).

## Dataset at a Glance

| Split | Questions | Images | Biology | Chemistry | Mathematics | Physics |
|---|---:|---:|---:|---:|---:|---:|
| test | 1,322 | 2,837 | 251 | 217 | 430 | 424 |

| Answer Type | Count |
|---|---:|
| Multiple-choice | 574 |
| Open-ended | 748 |
| Multi-answer | 97 |

The arXiv preprint reports **1,322** total samples, **748** open-ended samples, and **424** physics samples in the dataset statistics figure. This repository release matches those counts after repairing 9 legacy physics records that had formatting artifacts in an older JSON export.

Each record uses `[IMAGE0]`, `[IMAGE1]`, ... placeholders in the question text. These placeholders are 0-based indices into the record-level `image_list`.

## Installation

```bash
git clone https://github.com/LightChen233/OMIBench.git
cd OMIBench
python -m pip install -r requirements.txt
```

The public repository intentionally keeps dependencies minimal. Historical data-cleaning scripts, editor apps, raw intermediate files, and experiment outputs are not part of the tracked release package.

## Quick Start

Print dataset statistics:

```bash
python omi_bench.py info
```

Validate the canonical dataset split:

```bash
python omi_bench.py validate
```

Sample records as JSONL:

```bash
python omi_bench.py sample -n 3 --subject physics
```

Regenerate the referenced-image manifest:

```bash
python omi_bench.py manifest --output dataset/referenced_images.txt
```

Create a blank prediction file and evaluate model outputs:

```bash
python omi_bench.py make-submission --output predictions.jsonl
python omi_bench.py evaluate predictions.jsonl --output eval_details.json
```

Prediction files are JSONL with one record per line. The evaluator accepts any
of `prediction`, `answer`, `response`, or `output` as the model-output field:

```json
{"id": "biology-1", "prediction": "C"}
{"id": "physics-57-2", "prediction": "\\boxed{[-12\\pi R^2\\varepsilon_0E_0, 12\\pi R^2\\varepsilon_0E_0]}"}
```

The built-in evaluator is intentionally lightweight: it extracts option letters
for multiple-choice questions and applies normalized exact/substring matching
for open-ended answers. For paper-grade semantic scoring, use a stronger judge
or manual review on top of the exported `eval_details.json`.

## Load the Dataset

The canonical cleaned split is stored as [`dataset/test.jsonl`](dataset/test.jsonl).

```python
import json
from PIL import Image

rows = [json.loads(line) for line in open("dataset/test.jsonl")]
record = rows[0]
images = [Image.open(f"dataset/images/{name}") for name in record["image_list"]]

print(record["id"])
print(record["question"])
print(record["answer"])
```

> **Clean evaluation note:** `solution` contains full reasoning and answer information. Prompt models with `question`, `image_list`, and `choice_list` only; score against `answer`.

## File Structure

```text
root
├── omi_bench.py              # Single public CLI entry point
├── dataset/
│   ├── README.md             # Hugging Face style dataset card
│   ├── SOURCES.md            # Source attribution and redistribution notes
│   ├── test.jsonl            # Canonical cleaned benchmark split
│   └── referenced_images.txt # Exact image manifest for the release split
├── restored_records.csv      # Legacy physics records repaired for release
├── CITATION.cff              # Machine-readable citation metadata
├── LICENSE                   # MIT license for repository code
└── .github/                  # CI, issue templates, and PR template
```

## What Is Not Tracked

The repository ignores local-only development artifacts, including:

- raw and intermediate data folders such as `origin_dataset/` and `processed_data/`;
- generated model outputs under `experiments/`;
- local data editor and model-testing workspaces;
- image release builds such as `hf_upload/`, `hf_parquet/`, and archives.

This keeps the GitHub repository small and focused. Large data assets can be distributed through Hugging Face, GitHub Releases, Zenodo, or another artifact host.

## Hugging Face

The dataset is available on Hugging Face:

```python
from datasets import load_dataset

ds = load_dataset("LightChen2333/OMIBench", split="test")
print(ds[0]["id"], ds[0]["question"], ds[0]["images"])
```

## Provenance and Licensing Notes

OMI-Bench aggregates items from established multi-image benchmarks, olympiad-style science materials, and selected third-party figures. Please read [`dataset/SOURCES.md`](dataset/SOURCES.md) before redistribution or commercial use.

- The code in this repository is released under the MIT License.
- The dataset card is marked CC BY 4.0 in [`dataset/README.md`](dataset/README.md).
- Individual dataset items and images may retain upstream licenses, terms, or citation requirements.
- Some source families require final redistribution-rights confirmation before a fully public dataset release.

## Citation

If you find OMI-Bench useful for your research, please cite the arXiv paper and the upstream sources listed in [`dataset/SOURCES.md`](dataset/SOURCES.md). A machine-readable citation template is provided in [`CITATION.cff`](CITATION.cff).

```bibtex
@misc{chen2026omibench,
  title         = {OMIBench: Benchmarking Olympiad-Level Multi-Image Reasoning in Large Vision-Language Model},
  author        = {Chen, Qiguang and Luan, Chengyu and Wu, Jiajun and Yu, Qiming and Yang, Yi and Li, Yizhuo and Tong, Jingqi and Feng, Xiachong and Qin, Libo and Che, Wanxiang},
  year          = {2026},
  eprint        = {2604.20806},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2604.20806},
  url           = {https://arxiv.org/abs/2604.20806}
}
```

## Contributing

Contributions are welcome. Useful contributions include data fixes, source attribution improvements, evaluation scripts, documentation, and reproducibility reports. Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request.
