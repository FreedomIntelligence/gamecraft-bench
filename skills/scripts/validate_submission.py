#!/usr/bin/env python3
"""Preflight a GameCraft-style Godot submission.

Uses only the Python standard library. Static checks are deterministic; when a
Godot executable is available, the benchmark build gate is run as well.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SUPPORTED_EVENT_TYPES = {
    "mouse_click",
    "mouse_down",
    "mouse_up",
    "mouse_move",
    "key_press",
    "key_down",
    "key_up",
    "wait",
}
SUPPORTED_BUTTONS = {"left", "right"}
SUPPORTED_SPECIAL_KEYS = {
    "ESCAPE",
    "ENTER",
    "SPACE",
    "TAB",
    "BACKSPACE",
    "DELETE",
    "SHIFT",
    "CTRL",
    "ALT",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
FONT_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
AUDIO_EXTENSIONS = {".wav", ".ogg", ".mp3"}
TEXT_EXTENSIONS = {".gd", ".cs", ".tscn", ".tres", ".godot", ".cfg", ".shader"}
RESOURCE_PATTERN = re.compile(r"res://[A-Za-z0-9_@. /+-]+\.[A-Za-z0-9_+-]+")


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.findings: list[Finding] = []
        self.build: dict[str, Any] = {"attempted": False}

    def add(self, severity: str, code: str, message: str, path: Path | None = None) -> None:
        display_path: str | None = None
        if path is not None:
            try:
                display_path = str(path.relative_to(self.root))
            except ValueError:
                display_path = str(path)
        self.findings.append(Finding(severity, code, message, display_path))

    def error(self, code: str, message: str, path: Path | None = None) -> None:
        self.add("error", code, message, path)

    def warning(self, code: str, message: str, path: Path | None = None) -> None:
        self.add("warning", code, message, path)

    def info(self, code: str, message: str, path: Path | None = None) -> None:
        self.add("info", code, message, path)

    def counts(self) -> dict[str, int]:
        return {
            severity: sum(item.severity == severity for item in self.findings)
            for severity in ("error", "warning", "info")
        }


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def parse_project_setting(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip('"')


def check_structure(root: Path, report: Report) -> str:
    project = root / "project.godot"
    if not project.is_file():
        report.error("PROJECT_MISSING", "project.godot is required.", project)
        return ""

    text = read_text(project)
    main_scene = parse_project_setting(text, "run/main_scene")
    if not main_scene:
        report.error("MAIN_SCENE_UNSET", "run/main_scene is not configured.", project)
    elif main_scene.startswith("res://"):
        scene_path = root / main_scene.removeprefix("res://")
        if not scene_path.is_file():
            report.error("MAIN_SCENE_MISSING", f"Configured main scene does not exist: {main_scene}", scene_path)
    elif main_scene.startswith("uid://"):
        report.warning(
            "MAIN_SCENE_UID",
            "run/main_scene uses a UID; confirm the imported UID resolves in a fresh workspace.",
            project,
        )
    else:
        report.warning("MAIN_SCENE_UNUSUAL", f"Unusual run/main_scene value: {main_scene}", project)

    if not (root / "Main.tscn").is_file():
        report.warning("MAIN_TSCN_ABSENT", "Benchmark tasks conventionally require Main.tscn at project root.", root)

    width = parse_project_setting(text, "window/size/viewport_width")
    height = parse_project_setting(text, "window/size/viewport_height")
    if width != "1280" or height != "720":
        report.warning(
            "VIEWPORT_SETTING",
            f"Expected viewport 1280x720; found {width or 'unset'}x{height or 'unset'}.",
            project,
        )

    stretch = parse_project_setting(text, "window/stretch/mode")
    if not stretch:
        report.warning("STRETCH_UNSET", "Set an explicit window stretch mode and inspect at 1280x720.", project)

    return text


def valid_keycode(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(re.fullmatch(r"[A-Z0-9]", value)) or value in SUPPORTED_SPECIAL_KEYS


def require_int(event: dict[str, Any], key: str) -> bool:
    return isinstance(event.get(key), int) and not isinstance(event.get(key), bool)


def validate_trace(path: Path, report: Report) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report.error("TRACE_JSON", f"Cannot parse trace JSON: {exc}", path)
        return None

    if not isinstance(payload, dict):
        report.error("TRACE_ROOT", "Trace root must be a JSON object.", path)
        return None

    scenario = payload.get("scenario")
    if scenario is not None and (not isinstance(scenario, str) or not scenario.strip()):
        report.error("TRACE_SCENARIO", "scenario must be a non-empty string when present.", path)

    duration = payload.get("duration_frames")
    if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
        report.error("TRACE_DURATION", "duration_frames must be a positive integer.", path)
        duration = 0
    elif duration > 600:
        report.error("TRACE_TOO_LONG", f"duration_frames is {duration}; maximum is 600.", path)

    events = payload.get("events")
    if not isinstance(events, list):
        report.error("TRACE_EVENTS", "events must be a list.", path)
        return scenario if isinstance(scenario, str) else None
    if not events:
        report.warning("TRACE_EMPTY", "Trace contains no input or wait events.", path)

    last_frame = -1
    held_keys: set[str] = set()
    held_buttons: set[str] = set()

    for index, raw_event in enumerate(events):
        prefix = f"event {index}"
        if not isinstance(raw_event, dict):
            report.error("EVENT_OBJECT", f"{prefix} must be an object.", path)
            continue
        event = raw_event
        event_type = event.get("type")
        if event_type not in SUPPORTED_EVENT_TYPES:
            report.error("EVENT_TYPE", f"{prefix} has unsupported type: {event_type!r}.", path)
            continue
        if not require_int(event, "frame") or event["frame"] < 0:
            report.error("EVENT_FRAME", f"{prefix} frame must be a non-negative integer.", path)
            continue
        frame = event["frame"]
        if frame < last_frame:
            report.error("EVENT_ORDER", f"{prefix} occurs before the previous event.", path)
        last_frame = frame
        if duration and frame > duration:
            report.error("EVENT_AFTER_END", f"{prefix} occurs at frame {frame}, after duration {duration}.", path)

        if event_type.startswith("mouse_"):
            if not require_int(event, "x") or not require_int(event, "y"):
                report.error("MOUSE_COORDS", f"{prefix} requires integer x and y.", path)
            else:
                x, y = event["x"], event["y"]
                if not (0 <= x < 1280 and 0 <= y < 720):
                    report.error("MOUSE_BOUNDS", f"{prefix} coordinate ({x}, {y}) is outside 1280x720.", path)
            if event_type in {"mouse_click", "mouse_down", "mouse_up"}:
                button = event.get("button")
                if button not in SUPPORTED_BUTTONS:
                    report.error("MOUSE_BUTTON", f"{prefix} button must be left or right.", path)
                elif event_type == "mouse_down":
                    if button in held_buttons:
                        report.warning("MOUSE_REPEAT_DOWN", f"{prefix} presses {button} while already held.", path)
                    held_buttons.add(button)
                elif event_type == "mouse_up":
                    if button not in held_buttons:
                        report.warning("MOUSE_UP_WITHOUT_DOWN", f"{prefix} releases {button} without a matching down.", path)
                    held_buttons.discard(button)

        if event_type.startswith("key_"):
            keycode = event.get("keycode")
            if not valid_keycode(keycode):
                report.error("KEYCODE", f"{prefix} has unsupported keycode: {keycode!r}.", path)
            elif event_type == "key_down":
                if keycode in held_keys:
                    report.warning("KEY_REPEAT_DOWN", f"{prefix} presses {keycode} while already held.", path)
                held_keys.add(keycode)
            elif event_type == "key_up":
                if keycode not in held_keys:
                    report.warning("KEY_UP_WITHOUT_DOWN", f"{prefix} releases {keycode} without a matching down.", path)
                held_keys.discard(keycode)

    if held_keys:
        report.warning("KEYS_HELD_AT_END", f"Held keys are not released: {sorted(held_keys)}.", path)
    if held_buttons:
        report.warning("BUTTONS_HELD_AT_END", f"Held mouse buttons are not released: {sorted(held_buttons)}.", path)
    if duration and last_frame >= 0 and duration - last_frame > 240:
        report.warning(
            "TRACE_IDLE_TAIL",
            f"Trace has more than 8 seconds of idle tail ({duration - last_frame} frames).",
            path,
        )

    return scenario if isinstance(scenario, str) and scenario.strip() else None


def check_traces(root: Path, report: Report) -> set[str]:
    trace_dir = root / "demo_outputs"
    if not trace_dir.is_dir():
        report.error("TRACE_DIR_MISSING", "demo_outputs/ is required.", trace_dir)
        return set()

    traces = sorted(trace_dir.glob("*.json"))
    if not traces:
        report.error("NO_TRACES", "At least one demo_outputs/*.json trace is required.", trace_dir)
        return set()
    if len(traces) > 10:
        report.warning(
            "TOO_MANY_TRACES",
            f"Found {len(traces)} traces; only the first 10 filenames are evaluated.",
            trace_dir,
        )
    if any(not re.match(r"^\d{3}[_-]", path.name) for path in traces[:10]):
        report.info("TRACE_NAMING", "Use zero-padded numeric prefixes to make evaluation order explicit.", trace_dir)

    scenarios: set[str] = set()
    for trace in traces:
        scenario = validate_trace(trace, report)
        if scenario:
            scenarios.add(scenario)
    return scenarios


def project_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if ".godot" in path.parts or path.stat().st_size > 2_000_000:
            continue
        files.append(path)
    return files


def check_scenarios(root: Path, scenarios: set[str], text_files: list[Path], report: Report) -> None:
    if not scenarios:
        return
    combined = "\n".join(read_text(path) for path in text_files if path.suffix.lower() in {".gd", ".cs"})
    if "get_cmdline_user_args" not in combined and "GetCmdlineUserArgs" not in combined:
        report.warning(
            "SCENARIO_ARGS_UNSEEN",
            "Scenario traces exist, but no command-line user-argument parser was detected.",
            root,
        )
    if "--scenario" not in combined:
        report.warning(
            "SCENARIO_FLAG_UNSEEN",
            "Scenario traces exist, but the --scenario flag was not found in project scripts.",
            root,
        )
    for scenario in sorted(scenarios):
        if scenario not in combined:
            report.warning(
                "SCENARIO_ID_UNSEEN",
                f"Scenario id {scenario!r} was not found literally in project scripts.",
                root,
            )


def check_resource_references(root: Path, text_files: list[Path], report: Report) -> None:
    missing: dict[str, Path] = {}
    for source in text_files:
        for reference in RESOURCE_PATTERN.findall(read_text(source)):
            relative = reference.removeprefix("res://")
            target = root / relative
            if not target.exists():
                missing.setdefault(reference, source)
    for reference, source in sorted(missing.items()):
        report.warning("RESOURCE_REF_MISSING", f"Static resource reference does not exist: {reference}", source)


def check_presentation(root: Path, text_files: list[Path], report: Report) -> None:
    all_files = [path for path in root.rglob("*") if path.is_file() and ".godot" not in path.parts]
    images = [path for path in all_files if path.suffix.lower() in IMAGE_EXTENSIONS]
    fonts = [path for path in all_files if path.suffix.lower() in FONT_EXTENSIONS]
    audio = [path for path in all_files if path.suffix.lower() in AUDIO_EXTENSIONS]
    report.info(
        "ASSET_COUNTS",
        f"Project contains {len(images)} image, {len(fonts)} font, and {len(audio)} audio assets.",
        root,
    )
    if len(images) < 3:
        report.warning(
            "LOW_IMAGE_ASSET_COUNT",
            "Very few image assets detected; inspect for placeholder-heavy presentation.",
            root,
        )

    combined = "\n".join(read_text(path) for path in text_files)
    raw_shape_count = len(re.findall(r"\b(draw_rect|draw_circle|draw_polygon|ColorRect|Polygon2D)\b", combined))
    if raw_shape_count >= 8 and len(images) < 8:
        report.warning(
            "PLACEHOLDER_RISK",
            f"Detected {raw_shape_count} raw-shape references but only {len(images)} image assets; inspect art quality.",
            root,
        )

    ui_count = len(re.findall(r"\b(Button|Panel|ProgressBar|OptionButton|CheckButton)\b", combined))
    theme_signal = bool(re.search(r"\bTheme\b|theme_override|\.theme\s*=|theme\s*=\s*ExtResource", combined))
    if ui_count >= 4 and not theme_signal:
        report.warning(
            "DEFAULT_UI_RISK",
            f"Detected {ui_count} UI-control references without an obvious shared Theme; inspect for default widgets.",
            root,
        )

    license_files = [path for path in all_files if re.search(r"(?i)(license|copying|attribution)", path.name)]
    if images and not license_files:
        report.info(
            "NO_LICENSE_FILE",
            "No license/attribution file detected; preserve notices required by copied asset packs.",
            root,
        )


def runtime_error_lines(output: str) -> list[str]:
    return [
        line.strip()
        for line in output.splitlines()
        if re.search(r"\b(SCRIPT ERROR|Parse Error|ERROR:)\b", line, re.IGNORECASE)
    ]


def run_build_gate(
    root: Path, report: Report, godot_arg: str, timeout_seconds: float
) -> tuple[str | None, bool]:
    godot = shutil.which(godot_arg) if "/" not in godot_arg else godot_arg
    if not godot or not Path(godot).exists():
        report.error(
            "GODOT_UNAVAILABLE",
            f"Godot executable not found: {godot_arg}; build readiness is unverified. "
            "Use --no-run only for an explicitly static-only audit.",
            root,
        )
        report.build = {"attempted": False, "reason": "godot unavailable"}
        return None, False

    command = [str(godot), "--headless", "--path", str(root), "--quit-after", "5"]
    report.build = {"attempted": True, "command": command}
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        report.error("BUILD_TIMEOUT", f"Build gate timed out after {timeout_seconds:g}s.", root)
        report.build.update({"timed_out": True, "stdout": exc.stdout or "", "stderr": exc.stderr or ""})
        return str(godot), False
    except OSError as exc:
        report.error("BUILD_EXEC", f"Could not execute Godot: {exc}", root)
        report.build.update({"execution_error": str(exc)})
        return str(godot), False

    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    report.build.update({"returncode": result.returncode, "output": output[-12000:]})
    if result.returncode != 0:
        report.error("BUILD_FAILED", f"Godot build gate exited with code {result.returncode}.", root)
    error_lines = runtime_error_lines(output)
    if error_lines:
        report.error("BUILD_LOG_ERRORS", f"Godot reported errors; first: {error_lines[0][:300]}", root)
    warning_lines = [line.strip() for line in output.splitlines() if "WARNING:" in line.upper()]
    if warning_lines:
        report.warning("BUILD_LOG_WARNINGS", f"Godot reported {len(warning_lines)} warning line(s).", root)
    if result.returncode == 0 and not error_lines:
        report.info("BUILD_PASSED", "Godot build gate passed.", root)
    return str(godot), result.returncode == 0 and not error_lines


def run_scenario_gates(
    root: Path,
    scenarios: set[str],
    report: Report,
    godot: str,
    timeout_seconds: float,
) -> None:
    results: list[dict[str, Any]] = []
    report.build["scenarios"] = results
    for scenario in sorted(scenarios):
        command = [
            godot,
            "--headless",
            "--path",
            str(root),
            "--quit-after",
            "5",
            "--",
            "--scenario",
            scenario,
        ]
        entry: dict[str, Any] = {"scenario": scenario, "command": command}
        results.append(entry)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            entry.update({"timed_out": True, "stdout": exc.stdout or "", "stderr": exc.stderr or ""})
            report.error(
                "SCENARIO_TIMEOUT",
                f"Scenario {scenario!r} timed out after {timeout_seconds:g}s.",
                root,
            )
            continue
        except OSError as exc:
            entry["execution_error"] = str(exc)
            report.error("SCENARIO_EXEC", f"Could not run scenario {scenario!r}: {exc}", root)
            continue

        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        errors = runtime_error_lines(output)
        entry.update({"returncode": result.returncode, "output": output[-12000:]})
        if result.returncode != 0:
            report.error(
                "SCENARIO_FAILED",
                f"Scenario {scenario!r} exited with code {result.returncode}.",
                root,
            )
        if errors:
            report.error(
                "SCENARIO_LOG_ERRORS",
                f"Scenario {scenario!r} reported errors; first: {errors[0][:300]}",
                root,
            )
        if result.returncode == 0 and not errors:
            report.info("SCENARIO_PASSED", f"Scenario {scenario!r} smoke launch passed.", root)


def render_human(report: Report) -> None:
    labels = {"error": "ERROR", "warning": "WARN", "info": "INFO"}
    for finding in report.findings:
        where = f" [{finding.path}]" if finding.path else ""
        print(f"{labels[finding.severity]:5} {finding.code}{where}: {finding.message}")
    counts = report.counts()
    print(f"\nSummary: {counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info item(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Godot project directory, usually /workspace/game")
    parser.add_argument("--godot", default="godot", help="Godot executable name or absolute path")
    parser.add_argument("--timeout", type=float, default=20.0, help="Build-gate timeout in seconds")
    parser.add_argument("--no-run", action="store_true", help="Skip the Godot build gate")
    parser.add_argument(
        "--no-scenario-run",
        action="store_true",
        help="Skip smoke-launching scenarios named by traces",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return failure when warnings remain")
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    report = Report(root)
    if not root.is_dir():
        report.error("PROJECT_DIR", "Project directory does not exist.", root)
    else:
        check_structure(root, report)
        scenarios = check_traces(root, report)
        text_files = project_text_files(root)
        check_scenarios(root, scenarios, text_files, report)
        check_resource_references(root, text_files, report)
        check_presentation(root, text_files, report)
        if not args.no_run:
            godot, build_ok = run_build_gate(root, report, args.godot, args.timeout)
            if godot and build_ok and scenarios and not args.no_scenario_run:
                run_scenario_gates(root, scenarios, report, godot, args.timeout)

    counts = report.counts()
    if args.json:
        payload = {
            "ok": counts["error"] == 0 and (not args.strict or counts["warning"] == 0),
            "project": str(root),
            "counts": counts,
            "findings": [asdict(item) for item in report.findings],
            "build": report.build,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        render_human(report)

    return 1 if counts["error"] or (args.strict and counts["warning"]) else 0


if __name__ == "__main__":
    sys.exit(main())
