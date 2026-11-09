"""Chapter 8: memvalidasi bukti klaim-ke-sumber dan menghasilkan laporan yang dapat diaudit."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def validate(data):
    if not isinstance(data, dict) or not data.get("question"):
        raise ValueError("Pertanyaan riset wajib diisi")
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        raise ValueError("Sumber wajib tersedia")
    by_id = {}
    for source in sources:
        if not {"id", "url", "title", "accessed", "kind"} <= source.keys():
            raise ValueError("Sumber tidak lengkap")
        parsed = urlparse(source["url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL sumber harus menggunakan HTTP(S)")
        if source["id"] in by_id:
            raise ValueError("ID sumber duplikat")
        by_id[source["id"]] = source
    claims = data.get("claims", [])
    if not claims:
        raise ValueError("Klaim wajib tersedia")
    for claim in claims:
        if not claim.get("text") or claim.get("status") not in {"supported", "uncertain", "conflict"}:
            raise ValueError("Klaim tidak valid")
        evidence = claim.get("evidence", [])
        if claim["status"] == "supported" and not evidence:
            raise ValueError("Klaim berstatus supported memerlukan bukti")
        for item in evidence:
            if item.get("source") not in by_id or not item.get("quote"):
                raise ValueError("Bukti memerlukan sumber yang dikenal dan kutipan")
    return by_id


def render(data):
    sources = validate(data)
    lines = ["# " + data["question"], "", "## Temuan dan Bukti", ""]
    for claim in data["claims"]:
        lines.extend([f"### {claim['text']}", "", "Status: " + claim["status"], ""])
        for evidence in claim.get("evidence", []):
            source = sources[evidence["source"]]
            lines.extend([f"> {evidence['quote']}", "", f"Sumber: [{source['title']}]({source['url']})", ""])
    lines.extend(["## Sumber", ""])
    for source in sources.values():
        lines.append(f"- {source['id']}：[{source['title']}]({source['url']})；{source['kind']}；diakses {source['accessed']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = render(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(args.output)
