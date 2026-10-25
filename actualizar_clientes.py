"""
Atualiza clientes.json com as mudanças do usuario:
  - ICIS C.A.: estado -> Rechazado
  - IDEO: estado -> En Negociación + data de hoje
  - Adicionar prospectos Nexora (computadora e negocios)
  - Reforocar prospectos para prompt de sincronizacao
"""
import json
from pathlib import Path

P = Path(__file__).parent / "clientes.json"
prospectos = Path(__file__).parent / "prospectos.json"

# 1. Ler clientes.json
with open(P, "r", encoding="utf-8") as f:
    clientes = json.load(f)

# 2. Ajustar estados
for c in clientes:
    if c["id"] == 12:
        c["estado"] = "Rechazado"
    elif c["id"] == 27:
        c["estado"] = "En Negociación"
        c["fecha"] = "2026-10-24"

# 3. Agregar prospectos
nuevos = [
    {
        "id": 47,
        "empresa": "Computer Plaza S.A.",
        "nicho": "computacion",
        "contacto": "",
        "email": "",
        "telefono": "+58 261 7998120",
        "estado": "EnNegociación",
        "fecha": "2026-10-24"
    },
    {
        "id": 48,
        "empresa": "Compudell S.A.",
        "nicho": "computacion",
        "contacto": "",
        "email": "",
        "telefono": "+58 261 7592315",
        "estado": "EnNegociación",
        "fecha": "2026-10-24"
    },
    {
        "id": 49,
        "empresa": "Tech Shop Centro Comercial",
        "nicho": "computacion",
        "contacto": "",
        "email": "",
        "telefono": "+58 424 6915687",
        "estado": "EnNegociación",
        "fecha": "2026-10-24"
    },
    {
        "id": 50,
        "empresa": "ElectroMax Comercios Varios",
        "nicho": "negocio",
        "contacto": "",
        "email": "",
        "telefono": "+58 261 8152176",
        "estado": "EnNegociación",
        "fecha": "2026-10-24"
    },
    {
        "id": 51,
        "empresa": "Abras Inicial Comercio",
        "nicho": "negocio",
        "contacto": "",
        "email": "",
        "telefono": "+58 414 6005123",
        "estado": "EnNegociación",
        "fecha": "2026-10-24"
    },
]

for n in nuevos:
    c_id_max = max(c["id"] for c in clientes)
    n["id"] = c_id_max + nuevos.index(n) + 1
    clientes.append(n)

# 4. Salvar
with open(P, "w", encoding="utf-8") as f:
    json.dump(clientes, f, ensure_ascii=False, indent=2)

print("OK")
