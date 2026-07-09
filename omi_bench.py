#!/usr/bin/env python3
"""Single public entry point for OMI-Bench utilities."""

from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import sys
import unicodedata
from pathlib import Path

TAG_PATTERN = re.compile(r"\[IMAGE(\d+)\]")
LETTERS = "ABCDEFGHIJ"
ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "dataset"
TEST_FILE = DATASET_DIR / "test.jsonl"
IMAGE_DIR = DATASET_DIR / "images"


def load_records(path: Path = TEST_FILE) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def used_image_indices(record: dict) -> set[int]:
    indices = {int(match) for match in TAG_PATTERN.findall(record.get("question") or "")}
    for choice in record.get("choice_list") or []:
        indices.update(int(match) for match in TAG_PATTERN.findall(str(choice)))
    return indices


def summarize(records: list[dict]) -> dict:
    subject_counts = collections.Counter(record["subject"] for record in records)
    answer_type_counts = collections.Counter(record["answer_type"] for record in records)
    referenced_images = {image for record in records for image in record.get("image_list", [])}
    multi_answer = sum(1 for record in records if len(record.get("answer") or []) > 1)
    return {
        "records": len(records),
        "images": len(referenced_images),
        "subjects": dict(subject_counts),
        "answer_types": dict(answer_type_counts),
        "multi_answer": multi_answer,
    }


def validate(write_manifest: bool = True) -> int:
    records = load_records()
    images_on_disk = set(os.listdir(IMAGE_DIR)) if IMAGE_DIR.exists() else set()
    errors: list[str] = []
    referenced_images: set[str] = set()

    ids = [record.get("id") for record in records]
    duplicate_ids = [key for key, value in collections.Counter(ids).items() if value > 1]
    if duplicate_ids:
        errors.append(f"duplicate ids: {duplicate_ids[:10]}")

    required_fields = ["id", "subject", "answer_type", "question", "image_list", "answer", "solution"]
    multi_image = 0
    single_image = 0

    for record in records:
        record_id = record.get("id", "<missing-id>")
        for field in required_fields:
            if field not in record:
                errors.append(f"{record_id}: missing field {field}")

        if not (record.get("question") or "").strip():
            errors.append(f"{record_id}: empty question")
        if not (record.get("solution") or "").strip():
            errors.append(f"{record_id}: empty solution")
        if not record.get("answer"):
            errors.append(f"{record_id}: empty answer")
        if record.get("answer_type") not in {"mcq", "open"}:
            errors.append(f"{record_id}: bad answer_type {record.get('answer_type')!r}")

        image_list = record.get("image_list") or []
        referenced_images.update(image_list)
        if len(image_list) > 1:
            multi_image += 1
        elif len(image_list) == 1:
            single_image += 1

        if images_on_disk:
            for image in image_list:
                if image not in images_on_disk:
                    errors.append(f"{record_id}: image not on disk: {image}")

        expected_indices = set(range(len(image_list)))
        actual_indices = used_image_indices(record)
        if (actual_indices or image_list) and actual_indices != expected_indices:
            errors.append(f"{record_id}: tag/image mismatch tags={sorted(actual_indices)} n={len(image_list)}")

        if record.get("answer_type") == "mcq":
            choices = record.get("choice_list") or []
            if len(choices) < 2:
                errors.append(f"{record_id}: mcq with <2 choices")
            for answer in record.get("answer") or []:
                if len(answer) == 1 and answer in LETTERS and LETTERS.index(answer) >= len(choices):
                    errors.append(f"{record_id}: answer {answer} out of range ({len(choices)} choices)")

    if write_manifest:
        manifest_path = DATASET_DIR / "referenced_images.txt"
        with manifest_path.open("w", encoding="utf-8") as handle:
            for image in sorted(referenced_images):
                handle.write(image + "\n")

    summary = summarize(records)
    print("=" * 60)
    print("RECORDS:", summary["records"])
    print("  by subject    :", summary["subjects"])
    print("  by answer_type:", summary["answer_types"])
    print("  multi-answer  :", summary["multi_answer"])
    print("  multi-image   :", multi_image, "| single-image:", single_image)
    if images_on_disk:
        print("IMAGES: referenced=%d  on_disk=%d  orphan=%d" % (
            len(referenced_images), len(images_on_disk), len(images_on_disk - referenced_images)
        ))
    else:
        print("IMAGES: referenced=%d  on_disk=not available" % len(referenced_images))
    print("=" * 60)

    if errors:
        print("ERRORS:", len(errors))
        for error in errors[:40]:
            print("  ✗", error)
        return 1

    print("✅ ALL HARD CHECKS PASSED")
    return 0


def cmd_info(_: argparse.Namespace) -> int:
    summary = summarize(load_records())
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    return validate(write_manifest=not args.no_manifest)


def cmd_sample(args: argparse.Namespace) -> int:
    records = load_records()
    if args.subject:
        records = [record for record in records if record["subject"] == args.subject]
    if not records:
        print("No records matched the requested filters.", file=sys.stderr)
        return 1
    rng = random.Random(args.seed)
    for record in rng.sample(records, min(args.n, len(records))):
        print(json.dumps(record, ensure_ascii=False))
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    records = load_records()
    referenced_images = sorted({image for record in records for image in record.get("image_list", [])})
    output = Path(args.output)
    output.write_text("".join(f"{image}\n" for image in referenced_images), encoding="utf-8")
    print(f"Wrote {len(referenced_images)} image names to {output}")
    return 0


def normalize_answer(text: object) -> str:
    value = "" if text is None else str(text)
    value = unicodedata.normalize("NFKC", value)
    value = value.lower().strip()
    value = re.sub(r"\\boxed\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\$+", "", value)
    value = value.replace("\\pi", "pi")
    value = re.sub(r"\\(?:mathrm|text|operatorname)\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\[a-zA-Z]+", "", value)
    value = value.replace("−", "-").replace("–", "-").replace("—", "-")
    value = re.sub(r"[^a-z0-9.+\-/*=<>%]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_mcq_answer(prediction: object, choices: list[str] | None = None) -> str:
    text = "" if prediction is None else str(prediction).strip()
    if not text:
        return ""
    compact = re.sub(r"[^A-Ja-j]", "", text)
    if compact and len(compact) <= 5:
        return "".join(dict.fromkeys(compact.upper()))
    boxed = re.findall(r"\\boxed\s*\{\s*([A-Ja-j])\s*\}", text)
    if boxed:
        return boxed[-1].upper()
    patterns = [
        r"(?:final\s+answer|answer|option|choice)\s*(?:is|:)?\s*\(?\s*([A-Ja-j])\s*\)?",
        r"\(([A-Ja-j])\)",
        r"\b([A-Ja-j])\b",
    ]
    tail = "\n".join(text.splitlines()[-5:])
    for pattern in patterns:
        matches = re.findall(pattern, tail, flags=re.IGNORECASE)
        if matches:
            return matches[-1].upper()
    if choices:
        normalized_prediction = normalize_answer(text)
        best_index = -1
        best_position = -1
        for index, choice in enumerate(choices):
            normalized_choice = normalize_answer(choice)
            if normalized_choice and normalized_choice in normalized_prediction:
                position = normalized_prediction.rfind(normalized_choice)
                if position > best_position:
                    best_index = index
                    best_position = position
        if best_index >= 0 and best_index < len(LETTERS):
            return LETTERS[best_index]
    return ""


def open_answer_matches(prediction: object, gold_answers: list[object]) -> bool:
    normalized_prediction = normalize_answer(prediction)
    if not normalized_prediction:
        return False
    for gold in gold_answers:
        normalized_gold = normalize_answer(gold)
        if not normalized_gold:
            continue
        if normalized_prediction == normalized_gold:
            return True
        if len(normalized_gold) >= 3 and normalized_gold in normalized_prediction:
            return True
    return False


def read_predictions(path: Path) -> dict[str, object]:
    predictions: dict[str, object] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            record_id = row.get("id") or row.get("qid") or row.get("question_id")
            if not record_id:
                raise ValueError(f"{path}:{line_number}: missing id/qid/question_id")
            if "prediction" in row:
                prediction = row["prediction"]
            elif "answer" in row:
                prediction = row["answer"]
            elif "response" in row:
                prediction = row["response"]
            elif "output" in row:
                prediction = row["output"]
            else:
                raise ValueError(f"{path}:{line_number}: missing prediction/answer/response/output")
            predictions[str(record_id)] = prediction
    return predictions


def evaluate_predictions(predictions: dict[str, object], records: list[dict]) -> dict:
    totals = collections.defaultdict(lambda: {"correct": 0, "total": 0})
    missing: list[str] = []
    wrong: list[dict] = []
    for record in records:
        record_id = record["id"]
        if record_id not in predictions:
            missing.append(record_id)
            prediction = ""
        else:
            prediction = predictions[record_id]

        if record["answer_type"] == "mcq":
            extracted = extract_mcq_answer(prediction, record.get("choice_list") or [])
            gold = {"".join(dict.fromkeys(re.sub(r"[^A-Ja-j]", "", str(answer)).upper())) for answer in record.get("answer", [])}
            correct = bool(extracted and extracted in gold)
        else:
            extracted = str(prediction)
            correct = open_answer_matches(prediction, record.get("answer", []))

        for key in ["total", record["subject"], record["answer_type"]]:
            totals[key]["total"] += 1
            totals[key]["correct"] += int(correct)
        if not correct:
            wrong.append({
                "id": record_id,
                "subject": record["subject"],
                "answer_type": record["answer_type"],
                "gold": record.get("answer", []),
                "prediction": prediction,
                "extracted": extracted,
            })

    metrics = {}
    for key, value in totals.items():
        total = value["total"]
        correct = value["correct"]
        metrics[key] = {"correct": correct, "total": total, "accuracy": correct / total if total else 0.0}
    return {"metrics": metrics, "missing": missing, "wrong": wrong}


def cmd_evaluate(args: argparse.Namespace) -> int:
    records = load_records(Path(args.data))
    predictions = read_predictions(Path(args.predictions))
    result = evaluate_predictions(predictions, records)
    print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))
    print(f"missing_predictions: {len(result['missing'])}")
    print(f"wrong_predictions: {len(result['wrong'])}")
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote_details: {args.output}")
    return 0


def cmd_make_submission(args: argparse.Namespace) -> int:
    records = load_records(Path(args.data))
    with Path(args.output).open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps({"id": record["id"], "prediction": ""}, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} blank predictions to {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OMI-Bench command-line utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Print dataset statistics")
    info_parser.set_defaults(func=cmd_info)

    validate_parser = subparsers.add_parser("validate", help="Run dataset integrity checks")
    validate_parser.add_argument("--no-manifest", action="store_true", help="Do not rewrite dataset/referenced_images.txt")
    validate_parser.set_defaults(func=cmd_validate)

    sample_parser = subparsers.add_parser("sample", help="Print random JSONL records")
    sample_parser.add_argument("-n", type=int, default=1, help="Number of records to print")
    sample_parser.add_argument("--subject", choices=["biology", "chemistry", "mathematics", "physics"], help="Filter by subject")
    sample_parser.add_argument("--seed", type=int, default=0, help="Random seed")
    sample_parser.set_defaults(func=cmd_sample)

    manifest_parser = subparsers.add_parser("manifest", help="Write the referenced image manifest")
    manifest_parser.add_argument("--output", default=str(DATASET_DIR / "referenced_images.txt"), help="Output manifest path")
    manifest_parser.set_defaults(func=cmd_manifest)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate JSONL predictions with lightweight exact matching")
    evaluate_parser.add_argument("predictions", help="JSONL with id and prediction/answer/response/output fields")
    evaluate_parser.add_argument("--data", default=str(TEST_FILE), help="Reference dataset JSONL")
    evaluate_parser.add_argument("--output", help="Optional path for detailed JSON results")
    evaluate_parser.set_defaults(func=cmd_evaluate)

    submission_parser = subparsers.add_parser("make-submission", help="Create a blank prediction JSONL template")
    submission_parser.add_argument("--data", default=str(TEST_FILE), help="Reference dataset JSONL")
    submission_parser.add_argument("--output", default="predictions.jsonl", help="Output JSONL path")
    submission_parser.set_defaults(func=cmd_make_submission)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
