#!/usr/bin/env python3
"""Route real cached Qwen32B outputs on eight reviewed development frames."""
import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "route_data"
RUNS = ROOT / "runs" / "route"
ACTIONS = ("native", "sam", "dino")
QUANTITIES = ("gold_objects", "predictions", "tp", "fn", "category_aware_tp",
              "matched_correct_category", "pixel_mask_comparisons")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def emit(value):
    print(json.dumps(value, indent=2, sort_keys=True))


def run_dir(name):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        raise ValueError("Use a 1–64 character run name with letters, numbers, '-' or '_'.")
    return RUNS / name


def write_once(path, value, compare_fields):
    """Publish a complete record atomically. A matching retry reuses the saved record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as f:
        filename = f.name
        json.dump(value, f, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    try:
        try:
            os.link(filename, path)
        except FileExistsError:
            prior = load(path)
            if any(prior.get(key) != value.get(key) for key in compare_fields):
                raise ValueError(f"{path.name} is already committed with a different value. Use a new run name.")
            return prior
        return value
    finally:
        os.unlink(filename)


def result_for(case, action, catalog):
    # Each action retrieves exactly one archived lane. Never open other candidates to choose a route.
    row = load(DATA / "private" / f"{case['case']}_{action}.json")
    if (any(row[key] != case[key] for key in
            ("case", "scene", "review_frame", "video_frame", "video_id", "split"))
            or row["action"] != action or row["layer"] != catalog["lanes"][action]
            or row["coverage"] != "DONE" or row["split"] != "development"):
        raise ValueError("Selected result does not match the requested case, lane, or eligibility rules.")
    c = row["counts"]
    if any(type(c[key]) is not int or c[key] < 0 for key in QUANTITIES):
        raise ValueError("Invalid archived counts.")
    if (c["tp"] + c["fn"] != c["gold_objects"] or c["tp"] > c["predictions"]
            or c["matched_correct_category"] > c["tp"]
            or c["category_aware_tp"] > min(c["predictions"], c["gold_objects"])
            or c["pixel_mask_comparisons"] != 0):
        raise ValueError("Archived counts violate box-evaluation invariants.")
    iou_sum = row["sum_matched_box_iou"]
    if not math.isfinite(iou_sum) or not (0.5 * c["tp"] - 1e-8 <= iou_sum <= c["tp"] + 1e-8):
        raise ValueError("Invalid box IoU sum for matches at IoU >= 0.50.")
    if action == "native" and c["predictions"] != case["initial_native"]["emitted_boxes"]:
        raise ValueError("Initial observation and cached native output disagree.")
    return row


def choose(catalog, case_id, action, run, reason, mode):
    if case_id not in catalog["cases"]:
        raise ValueError(f"Unknown case {case_id}. Run list to see the available IDs.")
    if not reason.strip():
        raise ValueError("Record a brief reason for this action.")
    folder = run_dir(run)
    write_once(folder / "policy.json", {"mode": mode, "source": catalog["source"]}, ("mode", "source"))
    case = catalog["cases"][case_id]
    result = result_for(case, action, catalog)
    # Store the digest of the actual retrieved result. Per-frame scores stay sealed until summary.
    record = {"case": case_id, "run": run, "action": action, "mode": mode, "reason": reason.strip(),
              "observation": case, "result_sha256": digest(result), "cached_lane_reads": 1,
              "stop_state": ("accepted_minimum_evidence" if result["counts"]["category_aware_tp"] > 0
                             else "escalate_no_correct_category_match"),
              "committed_utc": datetime.now(timezone.utc).isoformat()}
    receipt = write_once(folder / (case_id + ".json"), record,
                         ("case", "run", "action", "mode", "observation", "result_sha256", "reason"))
    return {key: receipt[key] for key in ("run", "case", "action", "reason", "stop_state", "result_sha256", "committed_utc")}


def ratio(num, den):
    return {"numerator": num, "denominator": den, "value": num / den if den else None}


def evaluate(catalog, name, mode):
    folder = run_dir(name)
    if not (folder / "policy.json").is_file():
        raise ValueError(f"No {mode} run '{name}' found.")
    metadata = load(folder / "policy.json")
    if metadata != {"mode": mode, "source": catalog["source"]}:
        raise ValueError(f"'{name}' is not the requested {mode} run on this data.")
    missing = [i for i in catalog["cases"] if not (folder / (i + ".json")).is_file()]
    if missing:
        raise ValueError("No scores released. Missing " + name + " decisions for " + ", ".join(missing) + ".")
    rows = {}
    counts = Counter()
    for cid, case in catalog["cases"].items():
        record = load(folder / (cid + ".json"))
        tag = record["action"]
        if (record["run"] != name or record["case"] != cid or record["observation"] != case
                or record["mode"] != mode or tag not in ACTIONS
                or (mode == "fixed" and tag != "native")):
            raise ValueError("A saved decision is inconsistent with this run.")
        result = result_for(case, tag, catalog)
        if record["result_sha256"] != digest(result):
            raise ValueError("A selected result has changed since the decision.")
        c = result["counts"]
        rows[cid] = {"action": tag, "reason": record["reason"], "counts": c,
                     "sum_matched_box_iou": result["sum_matched_box_iou"], "stop_state": record["stop_state"]}
        counts.update(c)
    cases = len(rows)
    score = {"gold_localization_recall": ratio(counts["tp"], counts["gold_objects"]),
             "category_aware_grounding_recall": ratio(counts["category_aware_tp"], counts["gold_objects"]),
             "gold_support_yield": ratio(counts["tp"], counts["predictions"]),
             "conditional_box_iou": ratio(sum(r["sum_matched_box_iou"] for r in rows.values()), counts["tp"]),
             "matched_category_agreement": ratio(counts["matched_correct_category"], counts["tp"])}
    return {"run": name, "cases": rows, "metrics": score, "decision_cases": cases,
            "selected_cached_lane_reads": cases, "new_vision_inference_calls": 0,
            "frames_passing_minimum_evidence": sum(r["stop_state"] == "accepted_minimum_evidence" for r in rows.values())}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List the frozen development batch.")
    sub.add_parser("inspect", help="Show the initial native model output counts only.").add_argument("id")
    ch = sub.add_parser("choose", help="Commit one route and execute its cached result lookup.")
    ch.add_argument("id")
    ch.add_argument("action", choices=ACTIONS)
    ch.add_argument("--run", required=True)
    ch.add_argument("--reason", required=True)
    sub.add_parser("baseline", help="Use the native route for every case.").add_argument("--run", required=True)
    sm = sub.add_parser("summary", help="Score two complete runs, after all choices are frozen.")
    sm.add_argument("--run", required=True)
    sm.add_argument("--baseline", required=True)
    args = cli.parse_args()
    catalog = load(DATA / "public" / "cases.json")
    if args.command == "list":
        emit({"cases": list(catalog["cases"]), "choices": catalog["lanes"],
              "selection": catalog["selection"], "common_development_frames": catalog["population_common_frames"],
              "source": catalog["source"], "budget": "one selected cached lane per case"})
    elif args.command == "inspect":
        if args.id not in catalog["cases"]:
            raise ValueError("Unknown case. Run list.")
        emit(catalog["cases"][args.id])
    elif args.command == "choose":
        emit(choose(catalog, args.id, args.action, args.run, args.reason, "agent"))
    elif args.command == "baseline":
        for cid in catalog["cases"]:
            choose(catalog, cid, "native", args.run, "Predeclared fixed policy: retain native Qwen32B boxes.", "fixed")
        emit({"run": args.run, "committed": len(catalog["cases"]), "policy": "always native"})
    else:
        if args.run == args.baseline:
            raise ValueError("The agent and fixed policy require separate run names.")
        agent = evaluate(catalog, args.run, "agent")
        fixed = evaluate(catalog, args.baseline, "fixed")
        paired = {}
        for cid, a in agent["cases"].items():
            b = fixed["cases"][cid]
            if a["counts"]["gold_objects"] != b["counts"]["gold_objects"]:
                raise ValueError("Paired Gold reference denominators differ.")
            paired[cid] = {"agent_action": a["action"], "agent_reason": a["reason"],
                           "localizations_gained_or_lost": a["counts"]["tp"] - b["counts"]["tp"],
                           "agent_missed_gold": a["counts"]["fn"], "baseline_missed_gold": b["counts"]["fn"]}
        emit({"experiment": "Cached Qwen32B routing; development batch.",
              "measurement": "Independent deterministic aggregation of archived human-Gold one-to-one box checks at IoU >= 0.50. No raw pixels, boxes or masks are present in this experiment.",
              "semantics": "Category-aware recall uses the archive's separately category-aware match count. Matched category agreement uses the category labels of geometric matches. Support yield is agreement with the reviewed inventory, which is incomplete.",
              "resource_unit": "One retrieved cached route per policy per frame. This budget excludes original inference costs, model deliberation, and read-only inspection calls.",
              "source": catalog["source"], "agent": agent, "baseline": fixed, "paired_frames": paired})


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as e:
        print(f"Route error: {e}", file=sys.stderr)
        sys.exit(2)
