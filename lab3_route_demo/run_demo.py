#!/usr/bin/env python3
"""Run one Lab 3 experiment with a live Claude Code decision and a fixed comparator."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from evidence_view import render

ROOT = Path(__file__).resolve().parent
MODES = {
    "route": "Choose which cached grounding configuration to use for this Dylan development frame. 'native' keeps Qwen32B, 'sam' uses Qwen→SAM, and 'dino' uses Qwen→DINO→SAM. The goal is to cover reviewed objects with correctly grounded boxes. You only see native output counts and generator diagnostics. Make one decision with the information available. Counts alone do not establish box quality.",
    "category": "Use the original Qwen box and description to choose the canonical category of the entity described. Keep or change its original category, or abstain if the evidence is insufficient. This is an exact-category task with a fixed box.",
    "toy": "Locate the requested plate from a real connected-components detector's measurements on a schematic image. Pick one component ID, or abstain if the actual target cannot be isolated adequately. Use image coordinates: x increases to the right and y down. Exact RGB categories, boxes and pixel areas are detector outputs.",
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        try:
            json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            temp.unlink()
            raise
    os.replace(temp, path)


def local_json(args):
    cmd = [sys.executable] + [str(a) for a in args]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise ValueError(proc.stderr.strip() or proc.stdout.strip() or f"Tool exited {proc.returncode}.")
    return json.loads(proc.stdout)


def tool_paths(mode):
    if mode == "route":
        return ["route.py"], []
    if mode == "toy":
        return ["lab.py", "--data", "toy_data"], ["repair"]
    return ["lab.py", "--data", "category_data"], ["category"]


def public_prompt(mode, case, obs, allowed):
    public = dict(obs)
    public.pop("frame_path", None)
    if mode == "category":
        # All category choices share the same authentic box, so transmit it just once.
        public["prediction_box"] = public.pop("candidates")[0]["box"]
    payload = {"case": case, "observation": public, "allowed_choices": allowed}
    return (MODES[mode] + "\nYou control one local choose tool. Use only this observation. "
            "Return exactly one JSON object with case, choice, reason. The value of choice must be one "
            "of the allowed IDs. Write one sentence identifying the evidence or uncertainty behind your action. "
            "The executor will commit the choice, run the independent checker and stop this case.\n\n"
            + json.dumps(payload, ensure_ascii=False, indent=2))


def parse_action(raw, case, allowed):
    text = raw.strip()
    if text.startswith("```") and text.endswith("```"):
        text = "\n".join(text.splitlines()[1:-1])
    obj = json.loads(text)
    if (not isinstance(obj, dict) or obj.get("case") != case or obj.get("choice") not in allowed
            or not isinstance(obj.get("reason"), str) or not obj["reason"].strip()):
        raise ValueError(f"Expected case {case}, one of {allowed}, and a nonempty reason.")
    return obj["choice"], obj["reason"].strip()


def manual_turn(prompt):
    print("\nSend the entire prompt below to a fresh model conversation. Keep the original response.\n")
    print(prompt)
    print("\nPaste the complete model response below. Finish with a line containing only END.")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines), {"transport": "manual relay"}


def cli_turn(exe, prompt, model):
    # A fresh working directory and an empty tool catalog keep the private verifier out of the model context.
    args = [exe, "-p", "--output-format", "json", "--tools", "", "--strict-mcp-config",
            "--mcp-config", '{"mcpServers":{}}', "--no-session-persistence"]
    if model:
        args.extend(["--model", model])
    with tempfile.TemporaryDirectory(prefix="lab3-decision-") as cwd:
        proc = subprocess.run(args, cwd=cwd, input=prompt, capture_output=True, text=True, timeout=180)
    if proc.returncode:
        message = (proc.stderr or proc.stdout or f"exit code {proc.returncode}").strip()
        raise ValueError("Claude Code returned an error: " + message[:1000])
    envelope = json.loads(proc.stdout)
    result = envelope.get("result")
    if envelope.get("is_error") or not isinstance(result, str):
        raise ValueError("Claude Code did not return a text decision: " + str(result)[:500])
    meta = {k: envelope.get(k) for k in ("usage", "duration_ms", "total_cost_usd", "modelUsage", "model") if k in envelope}
    return result, meta


def run(args):
    mode = args.mode
    folder = ROOT / "evidence" / mode
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("A run for this option is already active. See the original terminal.")
        run_locked(args, folder)


def run_locked(args, folder):
    mode = args.mode
    invocation, scope = tool_paths(mode)
    if mode == "toy":
        subprocess.run([sys.executable, str(ROOT / "toy_detector.py")], cwd=ROOT, check=True)
    case_list = local_json(invocation + ["list"] + scope)
    ids = case_list["cases"] if mode == "route" else [item["id"] for item in case_list]
    manifest = folder / "run.json"
    exe = shutil.which("claude")
    if manifest.exists():
        config = json.loads(manifest.read_text())
        if config["manual"] != args.manual or config["model_requested"] != args.model:
            if (folder / "decisions").exists() or (folder / "format_failures").exists():
                raise ValueError("This run used different transport/model settings. Continue with the original settings or extract a fresh copy for a separately named replication.")
            manifest.unlink()
    if not manifest.exists():
        if not args.manual and not exe:
            raise ValueError("Claude Code is unavailable in this shell. Use a shell with your signed-in CLI or see README for --manual.")
        version = None if args.manual else subprocess.check_output([exe, "--version"], text=True).strip()
        config = {"mode": mode, "manual": args.manual, "model_requested": args.model, "claude_version": version,
                  "case_ids": ids, "budget": "one committed action per case; independent terminal check",
                  "model_interface": "manual relay" if args.manual else "installed Claude Code in print mode, built-in and MCP tools disabled; Python dispatches the selected action"}
        save(manifest, config)
    events = []
    for case in ids:
        obs = local_json(invocation + ["inspect", case])
        allowed = ["native", "sam", "dino"] if mode == "route" else obs["allowed_choices"]
        prompt = public_prompt(mode, case, obs, allowed)
        decision_file = folder / "decisions" / f"{case}.json"
        if decision_file.exists():
            event = json.loads(decision_file.read_text())
            if event["prompt"] != prompt:
                raise ValueError("Case input differs from previously committed prompt: " + case)
        else:
            print(f"Reading tool output and requesting a decision for {case} ...", flush=True)
            if not args.manual and not exe:
                raise ValueError("Claude Code is unavailable in this shell.")
            reply, meta = manual_turn(prompt) if args.manual else cli_turn(exe, prompt, args.model)
            try:
                choice, reason = parse_action(reply, case, allowed)
            except (KeyError, TypeError, ValueError) as error:
                failures = folder / "format_failures"
                failures.mkdir(exist_ok=True)
                name = f"{case}_{len(list(failures.glob(case + '_*.json'))) + 1}.json"
                save(failures / name, {"case": case, "prompt": prompt, "raw_response": reply, "metadata": meta, "error": str(error)})
                raise ValueError(f"Invalid decision format on {case}. Original reply archived under format_failures. Rerun to request a new response before any scoring on this case.")
            event = {"case": case, "observation": obs, "prompt": prompt, "choice": choice, "reason": reason,
                     "raw_response": reply, "model_metadata": meta}
            save(decision_file, event)
        # Dispatch the genuine model decision. Its hidden result is never an input for another case.
        receipt = local_json(invocation + ["choose", case, event["choice"], "--run", "agent", "--reason", event["reason"]])
        event["receipt"] = receipt
        events.append(event)
        save(folder / "transcript.json", events)
        print(f"{case}: {event['choice']} (committed)", flush=True)
    local_json(invocation + ["baseline"] + scope + ["--run", "fixed"])
    summary = local_json(invocation + ["summary"] + scope + ["--run", "agent", "--baseline", "fixed"])
    save(folder / "comparison.json", summary)
    render(folder, mode, events, summary)
    print(f"Completed {len(ids)} paired cases. Open {folder / 'DEMO_EVIDENCE.html'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=list(MODES))
    parser.add_argument("--manual", action="store_true", help="Relay prompts and real responses through an existing LLM session.")
    parser.add_argument("--model", help="For Claude Code, pass a valid model name or alias. For manual mode record the model shown by the UI.")
    args = parser.parse_args()
    if args.manual and not args.model:
        parser.error("With --manual, supply --model and the name shown in your model interface.")
    run(args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, EOFError, subprocess.SubprocessError) as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(1)
