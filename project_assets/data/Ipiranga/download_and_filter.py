#!/usr/bin/env python3
import os, sys, json, sqlite3, asyncio, aiohttp, aiofiles, unicodedata, uuid, shutil
from typing import Any, Dict, List, Union, Optional

# -------------------- Config --------------------
BASE = "https://acervoonline.mp.usp.br/wp-json/tainacan/v2/items/"
PARAMS = {
    "perpage": "96",
    "order": "ASC",
    "orderby": "date",
    "metaquery[0][key]": "118209",
    "metaquery[0][value][0]": "image/jpeg",
    "metaquery[0][compare]": "IN",
    "exposer": "json-flat",
}
TOTAL_PAGES = 312

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "pages")
COMBINED_FILTERED = os.path.join(SCRIPT_DIR, "all_items_filtered.json")
DB_PATH = os.path.join(SCRIPT_DIR, "ipiranga.db")

CONCURRENCY = 10
TIMEOUT = 60

# Selected types to keep (filter out all others)
SELECTED_TYPES = {
    "Boudoir | Fotografia",
    "Cabinet-portrait | Fotografia",
    "Cartaz | Impresso",
    "Carte-de-visite | Fotografia",
    "Cartão panel | Fotografia",
    "Cartão postal | Fotografia",
    "Cartão postal | Fototipia | Impresso",
    "Cartão postal | Impresso",
    "Cartão postal | Impresso | Rede de pontos",
    "Desenho | Flexografico",
    "Diapositivo | Fotografia",
    "Estereoscopia | Fotografia",
    "Estereoscopia | Fotografia | Negativo de vidro",
    "Figurinha | Impresso",
    "Fotografia",
    "Fotografia | Fotopintura",
    "Fotografia | Negativo de vidro",
    "Fotografia | Negativo flexível",
    "Fotogravura | Impresso",
    "Fototipia | Impresso",
    "Gravura | Reprodução",
    "Impresso",
    "Impresso | Rede de pontos",
    "Impresso | Rotogravura",
    "Impresso | Xilogravura",
    "Pintura",
    "Reprodução",
    "Álbum | Cartão postal | Fotografia",
    "Álbum | Cartão postal | Impresso",
    "Álbum | Fotografia | Reprodução",
    "Álbum | Impresso",
}

os.makedirs(OUT_DIR, exist_ok=True)

# -------------------- Field extraction spec --------------------
# Top-level fields:
TOPLEVEL_FIELDS = ["externalId", "url", "document"]

# Original Portuguese field names to English column names mapping
FIELD_MAPPING = {
    "codigo": "code",
    "titulo": "title",
    "descricao": "description",
    "denominacao": "type",
    "autoria": "author",
    "orig_prod": "location",
    "seculo": "century",
    "fase": "phase",
    "decada": "decade",
    "data": "date",
    "periodo-2": "period",
    "tecnica": "technique",
    "altura_sm": "height_sm",
    "larg_sm": "width_sm",
    "altura-em-cm": "height",
    "largura-em-cm": "width",
    "cor-2": "color",
    "historico": "history",
    "ref_acervo": "collection_ref",
    "biblio": "bibliography",
    "colecao-2": "collection_alt",
}

DATA_SUBFIELDS = list(FIELD_MAPPING.values())


def to_col_name(key: str) -> str:
    out = []
    for ch in key:
        if ch.isalnum():
            out.append(ch.lower())
        else:
            out.append("_")
    name = "".join(out)
    while "__" in name:
        name = name.replace("__", "_")
    return name.strip("_")


COL_TOPLEVEL = [to_col_name(k) for k in TOPLEVEL_FIELDS]
COL_DATA = [to_col_name(k) for k in DATA_SUBFIELDS]

FLAT_COLUMNS = ["id"] + COL_TOPLEVEL + COL_DATA  # keep 'id' first, then externalId


# -------------------- Normalization --------------------
def normalize_items(data: Any) -> List[Dict[str, Any]]:
    """Accept list, or {items:[...]}, or fallback to [data]. Ensure list of dicts."""
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        items = data["items"]
    else:
        items = [data]
    out: List[Dict[str, Any]] = []
    for it in items:
        out.append(it if isinstance(it, dict) else {"value": it})
    return out


# -------------------- Pruning (clean-up) --------------------
JSONValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
_SENTINEL = object()
WRAPPER_ONLY_KEYS = {"label"}  # If dict ends with only these keys, drop it

_BAD_TOKENS = {
    "SEM DATA",
    "NAO HA",
    "NÃO HÁ",
    "NÃO ATRIBUÍDO",
}


def _norm_text(s: str) -> str:
    s2 = "".join(
        c
        for c in unicodedata.normalize("NFKD", s.strip().upper())
        if not unicodedata.combining(c)
    )
    return " ".join(s2.split())


def _is_bad_string(s: str) -> bool:
    if s == "":
        return True
    ns = _norm_text(s)
    return ns in _BAD_TOKENS


def _is_container_empty(x: Any) -> bool:
    return isinstance(x, (list, dict)) and len(x) == 0


def prune_struct(obj: JSONValue) -> JSONValue:
    if isinstance(obj, str):
        return _SENTINEL if _is_bad_string(obj) else obj

    if isinstance(obj, dict):
        new_d: Dict[str, Any] = {}
        for k, v in obj.items():
            pv = prune_struct(v)
            if pv is _SENTINEL:
                continue
            if pv is None or _is_container_empty(pv):
                continue
            new_d[k] = pv

        if len(new_d) == 0:
            return _SENTINEL
        if set(new_d.keys()).issubset(WRAPPER_ONLY_KEYS):
            return _SENTINEL

        return new_d

    if isinstance(obj, list):
        new_l: List[Any] = []
        for el in obj:
            pel = prune_struct(el)
            if pel is _SENTINEL:
                continue
            if pel is None or _is_container_empty(pel):
                continue
            new_l.append(pel)
        return _SENTINEL if len(new_l) == 0 else new_l

    # numbers, bool, None: keep (None is filtered by parent checks)
    return obj


# -------------------- Concurrent downloading --------------------
async def fetch_page(session: aiohttp.ClientSession, p: int, sem: asyncio.Semaphore):
    out_path = os.path.join(OUT_DIR, f"page_{p:03d}.json")
    if os.path.exists(out_path):
        async with aiofiles.open(out_path, "r", encoding="utf-8") as f:
            return json.loads(await f.read())

    params = {**PARAMS, "paged": str(p)}
    async with sem:
        for attempt in range(5):
            try:
                async with session.get(BASE, params=params, timeout=TIMEOUT) as resp:
                    if resp.status == 429:
                        wait = int(resp.headers.get("Retry-After", "5"))
                        await asyncio.sleep(wait)
                        continue
                    resp.raise_for_status()
                    data = await resp.json()
                    async with aiofiles.open(out_path, "w", encoding="utf-8") as f:
                        await f.write(json.dumps(data, ensure_ascii=False))
                    print(f"[{p}] saved")
                    return data
            except Exception as e:
                wait = 2**attempt
                print(f"[{p}] error: {e} – retrying in {wait}s", file=sys.stderr)
                await asyncio.sleep(wait)
        raise RuntimeError(f"Failed to download page {p}")


async def download_all_pages_and_filter() -> List[Dict[str, Any]]:
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession(
        headers={"User-Agent": "dataset-fetch/1.0"}
    ) as session:
        tasks = [fetch_page(session, p, sem) for p in range(1, TOTAL_PAGES + 1)]
        results = await asyncio.gather(*tasks)
    all_items: List[Dict[str, Any]] = []
    for data in results:
        all_items.extend(normalize_items(data))

    filtered: List[Dict[str, Any]] = []
    for it in all_items:
        pit = prune_struct(it)
        if pit is not _SENTINEL:
            filtered.append(pit)
    await write_json(COMBINED_FILTERED, filtered)
    return filtered


# -------------------- Persistence helpers --------------------
async def write_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False))


def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        # Only flat table with explicit columns (all TEXT)
        cols_sql = ", ".join([f'"{c}" TEXT' for c in FLAT_COLUMNS])
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS ipiranga_entries(
                {cols_sql},
                PRIMARY KEY(id)
            )
        """
        )
        # optional indexes
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_ipiranga_entries_title ON ipiranga_entries(title)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_ipiranga_entries_code ON ipiranga_entries(code)"
        )
        conn.commit()
        # pragmas
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        conn.commit()
    finally:
        conn.close()


# -------------------- Scalar coercion --------------------
PREFERRED_KEYS = ("value", "title", "name", "label")


def _coerce_scalar(value: Any) -> Optional[str]:
    if value is None:
        return None

    # direct scalars
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        s = value.strip()
        if _is_bad_string(s):
            return None
        return s if s != "" else None

    # dict: try preferred scalar keys
    if isinstance(value, dict):
        for key in PREFERRED_KEYS:
            if key in value:
                return _coerce_scalar(value[key])
        return None

    # list: flatten scalars of each element
    if isinstance(value, list):
        parts: List[str] = []
        for el in value:
            sv = _coerce_scalar(el)
            if sv is not None and sv != "":
                parts.append(sv)
        return " | ".join(parts) if parts else None

    # other types -> not supported
    return None


def extract_flat_row(item: Dict[str, Any]) -> Dict[str, Optional[str]]:
    row: Dict[str, Optional[str]] = {c: None for c in FLAT_COLUMNS}

    row["id"] = str(uuid.uuid4())

    # externalId: original id if present
    ext_id = None
    for candidate_key in ("id", "ID", "uuid", "slug"):
        if candidate_key in item and isinstance(item[candidate_key], (str, int)):
            ext_id = str(item[candidate_key])
            break
    row["externalid"] = ext_id

    # top-level fields (skip externalId)
    for orig, col in zip(TOPLEVEL_FIELDS[1:], COL_TOPLEVEL[1:]):
        val = _coerce_scalar(item.get(orig))
        if orig == "url" and isinstance(val, str):
            base_url = "https://acervoonline.mp.usp.br/"
            if val.startswith(base_url):
                val = val[len(base_url) :]
        if orig == "document" and isinstance(val, str):
            doc_base = (
                "https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items"
            )
            if val.startswith(doc_base):
                val = val[len(doc_base) :]
            val = val[:]
        row[col] = val

    data_obj = item.get("data")
    if isinstance(data_obj, dict):
        for orig_key, eng_key in FIELD_MAPPING.items():
            col = to_col_name(eng_key)
            row[col] = _coerce_scalar(data_obj.get(orig_key))

    for k, v in list(row.items()):
        if isinstance(v, str) and _is_bad_string(v):
            row[k] = None

    return row


def upsert_items_sqlite(raw_items: List[Dict[str, Any]]):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("BEGIN")

        # Insert/Upsert only flat rows
        cols = FLAT_COLUMNS
        placeholders = ", ".join(["?"] * len(cols))
        col_list_sql = ", ".join([f'"{c}"' for c in cols])
        insert_flat = (
            f"INSERT INTO ipiranga_entries({col_list_sql}) VALUES({placeholders}) ON CONFLICT(id) DO UPDATE SET "
            + ", ".join([f'"{c}"=excluded."{c}"' for c in cols])
        )

        filtered_count = 0
        total_count = 0

        for it in raw_items:
            total_count += 1
            row = extract_flat_row(it)

            # Filter by selected types - only save items with selected types
            item_type = row.get("type")
            if item_type and item_type in SELECTED_TYPES:
                # Also check that document field exists (has image)
                if row.get("document"):
                    cur.execute(insert_flat, [row[c] for c in cols])
                    filtered_count += 1

        conn.commit()
        print(
            f"Filtered items: {filtered_count} out of {total_count} total items saved to database"
        )
    finally:
        conn.close()


async def main():
    # 1) If COMBINED_FILTERED exists, skip downloading; otherwise download all pages and filter them.
    if os.path.exists(COMBINED_FILTERED):
        print(f"{COMBINED_FILTERED} already exists — skipping download.")
        async with aiofiles.open(COMBINED_FILTERED, "r", encoding="utf-8") as f:
            all_items = json.loads(await f.read())
        if not isinstance(all_items, list):
            all_items = normalize_items(all_items)
    else:
        print("Downloading pages…")
        all_items = await download_all_pages_and_filter()
        await write_json(COMBINED_FILTERED, all_items)
        print(f"Combined saved to {COMBINED_FILTERED} with {len(all_items)} items")

    # 2) Write to SQLite: only selected types with images
    print("Writing to SQLite (filtering by selected types)...")
    upsert_items_sqlite(all_items)
    print(
        f"SQLite ready at {DB_PATH} (table: 'ipiranga_entries' with selected types only)."
    )

    # 3) Clean up: delete the pages folder if it exists
    if os.path.exists(OUT_DIR):
        print(f"Cleaning up: deleting {OUT_DIR}")
        shutil.rmtree(OUT_DIR)


if __name__ == "__main__":
    asyncio.run(main())
