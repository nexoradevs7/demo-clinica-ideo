def cargar_desde_json(ruta, nicho_filtro=None):
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)
    prospectos = []
    for item in data.get("prospectos", []):
        p = Prospecto(**{k: v for k, v in item.items() if k in Prospecto.__dataclass_fields__})
        if nicho_filtro and p.nicho != nicho_filtro:
            continue
        prospectos.append(p)
    return prospectos