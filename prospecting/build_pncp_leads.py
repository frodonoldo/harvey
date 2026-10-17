"""Build a small, auditable supplier prospect list from public PNCP contracts.

This only collects company-level public procurement records. It never sends messages.
"""
import csv
import json
import re
import time
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://pncp.gov.br/api/consulta/v1/contratos"
PAGES = (1, 30, 75, 150, 250, 400, 600, 850, 1100, 1400)
OUT = Path(__file__).parent
START = "20261001"
END = "20261015"


def fetch(page):
    query = urlencode({"dataInicial": START, "dataFinal": END, "pagina": page, "tamanhoPagina": 50})
    url = f"{BASE}?{query}"
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "SpiralisLeadResearch/1.0"})
    with urlopen(request, timeout=25) as response:
        return url, json.load(response)["data"]


def main():
    grouped = defaultdict(list)
    pages_ok = []
    for page in PAGES:
        try:
            url, records = fetch(page)
        except Exception as exc:
            print(f"page {page}: {exc}")
            continue
        pages_ok.append(page)
        for record in records:
            cnpj = record.get("niFornecedor") or ""
            name = record.get("nomeRazaoSocialFornecedor") or ""
            if record.get("tipoPessoa") != "PJ" or len(cnpj) != 14 or not name:
                continue
            record["_source_url"] = url
            grouped[cnpj].append(record)
        time.sleep(0.3)

    rows = []
    for cnpj, contracts in grouped.items():
        latest = max(contracts, key=lambda c: c.get("dataPublicacaoPncp") or "")
        uf = (latest.get("unidadeOrgao") or {}).get("ufSigla") or ""
        amount = latest.get("valorInicial") or 0
        # This is an outreach-priority heuristic, NOT a measured reply probability.
        score = 2  # verified recent PNCP supplier
        score += min(3, len(contracts) - 1)  # repeated appearances in sampled records
        score += 2 if 10000 <= amount <= 500000 else 1 if 5000 <= amount <= 2000000 else 0
        score += 1 if (latest.get("dataPublicacaoPncp") or "")[:10] >= "2026-10-10" else 0
        rows.append({
            "prioridade_pontos": score,
            "empresa": latest.get("nomeRazaoSocialFornecedor") or "",
            "cnpj": cnpj,
            "uf_contrato": uf,
            "contratos_na_amostra": len(contracts),
            "ultimo_contrato_publicado": (latest.get("dataPublicacaoPncp") or "")[:10],
            "valor_ultimo_contrato_brl": amount,
            "objeto_ultimo_contrato": re.sub(r"\s+", " ", latest.get("objetoContrato") or "").strip(),
            "numero_controle_pncp": latest.get("numeroControlePNCP") or "",
            "fonte_pncp": latest["_source_url"],
            "contato_empresarial_publico": "",
            "fonte_contato": "",
            "status_contato": "pendente de verificacao",
        })

    rows.sort(key=lambda r: (-r["prioridade_pontos"], -r["contratos_na_amostra"], r["empresa"]))
    # Ensure the seed spans multiple states instead of overrepresenting one source page.
    selected = []
    by_state = defaultdict(int)
    for row in rows:
        if by_state[row["uf_contrato"]] >= 4:
            continue
        selected.append(row)
        by_state[row["uf_contrato"]] += 1
        if len(selected) == 30:
            break

    OUT.mkdir(exist_ok=True)
    existing_path = OUT / "leads_pncp_iniciais.csv"
    existing = {}
    if existing_path.exists():
        with existing_path.open(newline="", encoding="utf-8-sig") as file:
            existing = {row["cnpj"]: row for row in csv.DictReader(file)}
    for row in selected:
        previous = existing.get(row["cnpj"], {})
        for field in ("contato_empresarial_publico", "fonte_contato", "status_contato"):
            if previous.get(field):
                row[field] = previous[field]
    with (OUT / "leads_pncp_iniciais.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=selected[0].keys())
        writer.writeheader()
        writer.writerows(selected)
    meta = {"source": BASE, "period": [START, END], "pages_requested": PAGES,
            "pages_successful": pages_ok, "contracts_sampled": sum(map(len, grouped.values())),
            "companies_sampled": len(grouped), "leads_selected": len(selected),
            "generated_on": date.today().isoformat()}
    (OUT / "amostra.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
