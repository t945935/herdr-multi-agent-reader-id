#!/usr/bin/env python3
"""Dispatch to an already-started idle agent; verify a task-specific receipt."""
import argparse
import json
import os
import subprocess
import uuid
from pathlib import Path


def call(*args, timeout=310):
    done = subprocess.run(["herdr", *args], text=True, capture_output=True, timeout=timeout)
    if done.returncode:
        raise RuntimeError(done.stderr or done.stdout)
    return json.loads(done.stdout)["result"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("prompt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("HERDR_ENV") != "1":
        raise SystemExit("Jalankan dari dalam Herdr")
    agent = call("agent", "get", args.target)["agent"]
    if agent["agent_status"] not in {"idle", "done"}:
        raise SystemExit("Agen harus berstatus idle/done sebelum tugas dimulai")
    path = args.output.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit("Pilih jalur kuitansi baru; jangan gunakan ulang jalur tugas sebelumnya")
    task_id = uuid.uuid4().hex
    prompt = args.prompt.read_text() + (
        f"\n\nIni task_id={task_id}\ncompletion_path={path}\n"
        'Selesaikan tugas yang sebenarnya, lalu tulis JSON: {"task_id":"ID yang tercantum di atas","status":"completed",'
        '"summary":"hasil kerja spesifik dan verifikasi","artifacts":["jalur artefak yang sebenarnya"]}。'
        "Jika tidak dapat menyelesaikan tugas, gunakan status=blocked dan jelaskan alasannya pada summary. Jangan memulai agen lain."
    )
    settled = call("agent", "prompt", args.target, prompt, "--wait", "--timeout", "300000")
    state = settled["agent"]["agent_status"]
    if state not in {"idle", "done"} or not path.is_file():
        raise SystemExit("Agen berhenti tanpa kuitansi yang diterima; periksa agent get/read")
    receipt = json.loads(path.read_text())
    if receipt.get("task_id") != task_id or receipt.get("status") != "completed" or not receipt.get("summary"):
        raise SystemExit("Kuitansi tidak menerima tugas ini")
    for artifact in receipt.get("artifacts", []):
        candidate = Path(artifact)
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        if not candidate.is_file():
            raise SystemExit(f"Artefak tidak ditemukan: {artifact}")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
