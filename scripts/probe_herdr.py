#!/usr/bin/env python3
"""Kumpulkan bukti CLI; secara opsional uji hanya panel saudara yang baru dibuat."""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Buat dan tutup panel shell pengujian")
    parser.add_argument("--agents", choices=["pi", "codex", "opencode"], help="Jalankan juga dua agen pengujian")
    parser.add_argument("--receipts", action="store_true", help="Verifikasi kuitansi khusus tugas dengan scripts/team.py")
    args = parser.parse_args()
    if args.receipts and not args.agents:
        parser.error("--receipts memerlukan --agents")
    if os.environ.get("HERDR_ENV") != "1":
        raise SystemExit("Jalankan pemeriksaan ini dari panel yang dikelola Herdr")
    records, owned = [], []

    def command(*argv, timeout=30):
        started = datetime.now(timezone.utc).isoformat()
        p = subprocess.run(["herdr", *argv], text=True, capture_output=True, timeout=timeout)
        record = {"command": ["herdr", *argv], "started_at": started,
                  "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
        records.append(record)
        # Bare command groups print usage on stderr and return 2 on Herdr 0.9.3.
        discovery_help = len(argv) == 1 and argv[0] in {"agent", "pane", "workspace", "tab"} and p.returncode == 2
        if p.returncode and not discovery_help:
            raise RuntimeError(p.stderr or p.stdout)
        try:
            return json.loads(p.stdout)["result"]
        except (ValueError, KeyError, TypeError):
            return p.stdout

    success, failure = False, None
    try:
        for argv in [("--version",), ("status",), ("agent",), ("pane",), ("workspace",),
                     ("tab",), ("agent", "list"), ("pane", "current", "--current")]:
            command(*argv)
        if args.live:
            pane = command("pane", "split", "--current", "--direction", "right", "--cwd", str(ROOT), "--no-focus")["pane"]["pane_id"]
            owned.append(pane)
            marker = "ID_SHELL_" + str(time.time_ns())
            command("pane", "run", pane, f"python3 -c 'print(\"{marker}\")'")
            command("pane", "wait-output", pane, "--regex", "^" + marker + "$", "--timeout", "10000")
            shell_output = command("pane", "read", pane, "--source", "recent-unwrapped", "--lines", "20")
            if marker not in [line.strip() for line in str(shell_output).splitlines()]:
                raise RuntimeError("Penanda muncul sebagai gema masukan tetapi tidak teramati sebagai satu baris keluaran utuh")
            if args.agents:
                second = command("pane", "split", pane, "--direction", "down", "--cwd", str(ROOT), "--no-focus")["pane"]["pane_id"]
                owned.append(second)
                suffix = str(time.time_ns())[-7:]
                names = ["book_check_a_" + suffix, "book_check_b_" + suffix]
                for name, target in zip(names, [pane, second]):
                    command("agent", "start", name, "--kind", args.agents, "--pane", target, "--timeout", "30000", timeout=40)
                # Fixed acceptance tokens test prompt delivery; they do not assert code-review quality.
                prompts = ["Balas hanya AGEN_ID_A_OK. Ini tes komunikasi paket pembaca. Jangan gunakan alat, membaca/menulis berkas, atau memulai agen.",
                           "Balas hanya AGEN_ID_B_OK. Ini tes komunikasi paket pembaca. Jangan gunakan alat, membaca/menulis berkas, atau memulai agen."]
                for name, prompt in zip(names, prompts):
                    command("agent", "prompt", name, prompt)
                for name, token in zip(names, ["AGEN_ID_A_OK", "AGEN_ID_B_OK"]):
                    state = command("agent", "wait", name, "--timeout", "90000", timeout=100)
                    if state.get("agent", {}).get("agent_status") == "blocked":
                        raise RuntimeError("Agen terblokir; diperlukan tindakan pengguna")
                    command("pane", "wait-output", owned[names.index(name)], "--match", token, "--timeout", "90000", timeout=100)
                    transcript = command("agent", "read", name, "--source", "recent-unwrapped", "--lines", "60")
                    if token not in str(transcript):
                        raise RuntimeError("Token balasan yang diharapkan tidak ditemukan")
                if args.receipts:
                    for name in names:
                        output = ROOT / "reports" / (name + "-receipt.json")
                        argv = [sys.executable, str(ROOT / "scripts/team.py"), name,
                                str(ROOT / "examples/prompts/receipt-smoke.md"), "--output", str(output)]
                        done = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=310)
                        records.append({"command": argv, "returncode": done.returncode,
                                        "stdout": done.stdout, "stderr": done.stderr})
                        if done.returncode:
                            raise RuntimeError(done.stderr or done.stdout)
        success = True
    except Exception as exc:
        failure = str(exc)
    finally:
        for pane in reversed(owned):
            try:
                command("pane", "close", pane)
            except Exception as exc:
                failure = (failure or "") + " cleanup: " + str(exc)
                success = False
        report = {"captured_at": datetime.now(timezone.utc).isoformat(), "success": success,
                  "live_shell": args.live, "agent_kind": args.agents, "task_receipts": args.receipts,
                  "error": failure, "commands": records}
        out = ROOT / "reports" / "herdr-probe.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"success": success, "commands": len(records), "report": str(out), "error": failure}, ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
