"""Render a self-contained, post-run evidence sheet from recorded decisions and checks."""

import base64
from html import escape
import json
from pathlib import Path
import re
import struct


CSS = """
:root{color-scheme:light;--ink:#192d32;--muted:#4e6265;--paper:#fbfbf7;--line:#c7d3d0;
--accent:#006455;--negative:#a4402d}*{box-sizing:border-box}body{margin:0;background:var(--paper);
color:var(--ink);font:16px/1.5 system-ui,-apple-system,sans-serif}main{width:min(100% - 36px,900px);
margin:42px auto 65px}header{border-top:7px solid var(--accent);padding-top:22px}h1,h2,h3,p{margin:0 0 12px}
h1{font:600 clamp(29px,6vw,47px)/1.08 Georgia,serif;letter-spacing:-.035em}h2{font:600 25px/1.2 Georgia,serif}
h3{font-size:15px}p{max-width:740px}.sub{color:var(--muted);font-size:15px}.comparison{margin:28px 0}
table{border-collapse:collapse;width:100%;text-align:left;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}thead th{background:#e6eeeb;
font-size:13px;color:#254a46}tbody th{font-weight:500}.scroll{overflow-x:auto}
article{border:1px solid var(--line);border-left:4px solid var(--accent);background:white;border-radius:4px;
margin:18px 0;padding:20px 23px;break-inside:avoid}article.fail{border-left-color:var(--negative)}
.casehead{display:flex;justify-content:space-between;gap:10px;align-items:baseline}
.tag{font-size:14px;font-weight:650;color:var(--accent)}.fail .tag{color:var(--negative)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:16px 0}.box{background:#f3f6f3;
padding:13px;border-radius:4px;min-width:0}.key{font-weight:650;color:#284d47}
dt{font-size:13px;color:var(--muted)}dd{margin:0 0 7px;overflow-wrap:anywhere}
figure{max-width:460px;margin:15px 0}svg{background:#f5f6f4;border:1px solid var(--line);display:block;
width:100%;height:auto}figcaption{font-size:13px;color:var(--muted);margin-top:3px}
details{border-top:1px solid var(--line);padding:7px 0}summary{cursor:pointer;font-size:14px;
font-weight:550}pre{background:#f1f4f2;white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.45 ui-monospace,monospace;
padding:11px;border-radius:3px}code{font-family:ui-monospace,monospace}.foot{font-size:13px;color:var(--muted)}
@media(max-width:580px){main{width:calc(100% - 22px);margin-top:20px}article{padding:14px}.cols{grid-template-columns:1fr}}
@media print{body{background:white}main{width:100%;margin:0}article{break-inside:avoid}details:not([open]){display:none}}
"""

# Viewer input is the decision transcript, never an API transport or environment dump.
CREDENTIAL_FIELD = re.compile(r"^(?:api[_-]?key|authorization|access[_-]?token|refresh[_-]?token|secret|password)$", re.I)
TOKEN = re.compile(r"\b(?:Bearer\s+[^\s\"']+|sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,})", re.I)


def safe(value):
    if isinstance(value, dict):
        return {k: "[credential removed]" if CREDENTIAL_FIELD.match(str(k)) else safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [safe(v) for v in value]
    if isinstance(value, str):
        return TOKEN.sub("[credential removed]", value)
    return value


def h(value):
    return escape(str(value)) if value is not None else "—"


def table(headers, rows):
    heading = "".join(f"<th scope='col'>{h(label)}</th>" for label in headers)
    body = []
    for row in rows:
        cells = "".join(f"<td>{h(value)}</td>" for value in row[1:])
        body.append(f"<tr><th scope='row'>{h(row[0])}</th>{cells}</tr>")
    return f"<div class='scroll'><table><thead><tr>{heading}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"


def fields(pairs):
    return "<dl>" + "".join(f"<dt>{h(k)}</dt><dd>{h(v)}</dd>" for k, v in pairs) + "</dl>"


def panel(title, value):
    raw = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)
    return f"<details><summary>{h(title)}</summary><pre>{h(raw)}</pre></details>"


def ratio(entry):
    if not isinstance(entry, dict) or entry.get("value") is None:
        return "—"
    return f"{entry['value']:.1%} ({entry['numerator']:g}/{entry['denominator']:g})"


def rate(value):
    return "—" if value is None else f"{value:.1%}"


def comparison(mode, summary, events):
    if mode == "route":
        policies = [summary[k].get("metrics", {}) for k in ("agent", "baseline")]
        metrics = [("Gold localization recall", "gold_localization_recall"),
                   ("Category-aware grounding recall", "category_aware_grounding_recall"),
                   ("Gold-support yield", "gold_support_yield"),
                   ("IoU among matched boxes", "conditional_box_iou"),
                   ("Category agreement among geometric matches", "matched_category_agreement")]
        rows = [(label, *(ratio(p.get(key)) for p in policies)) for label, key in metrics]
    else:
        totals = summary.get("totals", {})
        decision_run = next((e.get("receipt", {}).get("run") for e in events if e.get("receipt", {}).get("run")), None)
        if decision_run not in totals:
            decision_run = next(iter(totals), None)
        base_run = next((name for name in totals if name != decision_run), None)
        policies = [totals.get(name, {}) for name in (decision_run, base_run)]
        rows = [("Correct / evaluated", *(f"{p.get('correct', '—')}/{p.get('cases', '—')}" for p in policies)),
                ("Correct among all cases", *(rate(p.get("correct_over_all_cases")) for p in policies)),
                ("Abstentions", *(p.get("abstentions", "—") for p in policies)),
                ("Geometry matches", *(p.get("geometry_matches", "—") for p in policies))]
        if mode == "category":
            rows.append(("Category agreement among geometric matches",
                         *(rate(p.get("matched_category_agreement")) for p in policies)))
    return table(["Measure", "Recorded decisions", "Fixed baseline"], rows)


def toy_figure(observation, selected):
    source = observation.get("frame_path")
    if not source or not Path(source).is_file():
        return ""
    data = Path(source).read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return ""
    width, height = struct.unpack(">II", data[16:24])
    uri = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
    mark = ""
    if selected and selected.get("box"):
        x, y, right, bottom = (float(i) for i in selected["box"])
        mark = (f"<rect x='{x:g}' y='{y:g}' width='{right-x:g}' height='{bottom-y:g}' "
                "fill='none' stroke='white' stroke-width='3'/>"
                f"<rect x='{x:g}' y='{y:g}' width='{right-x:g}' height='{bottom-y:g}' "
                "fill='none' stroke='#172c31' stroke-width='1.3' stroke-dasharray='4 2'/>")
    legend = "Dashed outline shows the committed prediction." if mark else "The run emitted no box."
    return (f"<figure><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' role='img' "
            f"aria-label='Synthetic input frame and committed box'><image width='{width}' height='{height}' "
            f"href='{uri}'/>{mark}</svg><figcaption>{legend}</figcaption></figure>")


def case_card(event, mode, summary, comparisons):
    cid = str(event["case"])
    observation = event.get("observation") or {}
    receipt = event.get("receipt") or {}
    choice = event.get("choice")
    paired = comparisons.get(cid, {})
    image = ""
    if mode == "route":
        observed = observation.get("initial_native", {})
        a = summary["agent"].get("cases", {}).get(cid, {})
        b = summary["baseline"].get("cases", {}).get(cid, {})
        stats_a, stats_b = a.get("counts", {}), b.get("counts", {})
        missed = paired.get("agent_missed_gold")
        if stats_a.get("gold_objects") == 0:
            status = "No reviewed target in frame"
        elif missed is None:
            status = "Recorded"
        elif missed == 0:
            status = "All Gold objects matched"
        else:
            status = f"{missed} Gold object{'s' if missed != 1 else ''} missed"
        failed = bool(missed)
        input_fields = [("Video frame", observation.get("video_frame")),
                        ("Initial native boxes", observed.get("emitted_boxes")),
                        ("Entities grounded", observed.get("generator_counts", {}).get("entity_grounded"))]
        output_fields = [("Selected route", choice), ("Fixed route", b.get("action"))]
        rows = [(title, stats_a.get(key), stats_b.get(key)) for title, key in
                (("Gold objects", "gold_objects"), ("Emitted boxes", "predictions"),
                 ("Localized", "tp"), ("Category-aware matches", "category_aware_tp"), ("Missed", "fn"))]
        scored = {"recorded_route": a, "fixed_route": b, "paired_frame": paired}
    else:
        verifier = receipt.get("check") or {}
        success = paired.get("agent_correct", verifier.get("correct"))
        status = "Pass" if success is True else ("Fail" if success is False else "Unscored")
        failed = success is False
        ev = observation.get("evidence") or {}
        input_fields = [("Query", observation.get("query"))]
        if mode == "category":
            input_fields += [("Detector description", ev.get("detector_description")),
                             ("Native category", ev.get("native_category"))]
        else:
            input_fields += [("Foreground components", len(observation.get("candidates", [])))]
            image = toy_figure(observation, receipt.get("candidate"))
        output_fields = [("Committed choice", choice), ("Fixed choice", paired.get("baseline_choice"))]
        if mode == "category":
            output_fields.append(("Reviewed category", verifier.get("reference_category")))
            output_fields.append(("Matches Gold category", verifier.get("category_agreement")))
        rows = [("Box IoU", *("—" if v is None else f"{v:.3f}" for v in
                              (paired.get("agent_iou"), paired.get("baseline_iou")))),
                ("Passed check", *(("Yes" if flag else "No") if flag is not None else "—" for flag in
                                   (success, paired.get("baseline_correct"))))]
        scored = {"verifier": verifier, "paired_case": paired}
    result = (f"<article class='{'fail' if failed else 'pass'}'><div class='casehead'><h2>{h(cid)}</h2>"
              f"<span class='tag'>{h(status)}</span></div>{image}<div class='cols'>"
              f"<div class='box'><h3>Tool input and observation</h3>{fields(input_fields)}</div>"
              f"<div class='box'><h3>Decision</h3>{fields(output_fields)}</div></div>")
    if event.get("reason"):
        result += f"<p><span class='key'>Rationale</span> &nbsp;{h(event['reason'])}</p>"
    result += table(["Check", "Recorded decision", "Fixed baseline"], rows)
    result += panel("Exact public tool output", observation)
    if event.get("prompt"):
        result += panel("Exact agent input", event["prompt"])
    if event.get("raw_response"):
        result += panel("Recorded response", event["raw_response"])
    result += panel("Committed action and tool receipt", {"choice": choice, "reason": event.get("reason"), "receipt": receipt})
    return result + panel("Independent check and baseline", scored) + "</article>"


def render(report_dir, mode, events, summary):
    """Create DEMO_EVIDENCE.html. Frames are embedded so the finished page works offline."""
    titles = {"route": "Grounding route selection", "category": "Category remapping", "toy": "Foreground component selection"}
    if mode not in titles:
        raise ValueError(f"Unknown demo mode {mode!r}.")
    events, summary = safe(events), safe(summary)
    descriptions = {
        "route": "Reviewed development frames from the Qwen32B archive. Each policy selects one cached route per frame. "
                 "The independent comparison uses archived one-to-one box matches at IoU ≥ 0.50.",
        "category": "Previously localized Qwen32B detections from a selected audit slice. Each choice preserves the predicted "
                    "box. A case passes when box IoU exceeds 0.50 and the chosen category agrees with the reviewed label.",
        "toy": "Connected components from synthetic images. A case passes when the emitted component box overlaps the "
               "independent target box at IoU above 0.50. The fixed baseline chooses the largest foreground component."}
    comparisons = summary.get("paired_frames", {}) if mode == "route" else {
        str(row["case"]): row for row in summary.get("cases", [])}
    title = titles[mode]
    body = (f"<header><h1>{title}</h1><p class='sub'>{h(descriptions[mode])}</p></header>"
            f"<section class='comparison'><h2>Paired results</h2>{comparison(mode, summary, events)}</section>"
            + "".join(case_card(event, mode, summary, comparisons) for event in events)
            + panel("Full comparison output", summary))
    target = Path(report_dir) / "DEMO_EVIDENCE.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' "
                      f"content='width=device-width,initial-scale=1'><title>{title} | Demo evidence</title>"
                      f"<style>{CSS}</style></head><body><main>{body}</main></body></html>", encoding="utf-8")
    return target
