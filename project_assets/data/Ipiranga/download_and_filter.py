#!/usr/bin/env python3
import os, sys, json, asyncio, aiohttp, aiofiles, unicodedata, uuid, shutil, csv
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
OUTPUT_SQL = os.path.join(SCRIPT_DIR, "B_Ipiranga.sql")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "Ipiranga.csv")

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
    "codigo": "inventory_code",
    "titulo": "title",
    "descricao": "description",
    "denominacao": "type",
    "autoria": "artist_name",
    "orig_prod": "location",
    "fase": "phase",
    "data": "date",
    "periodo-2": "period",
    "tecnica": "technique",
    "altura-em-cm": "height",
    "largura-em-cm": "width",
    "cor-2": "color",
    "historico": "history",
    "colecao-2": "collection_alt_name",
}

DATA_SUBFIELDS = list(FIELD_MAPPING.values())

IPIRANGA_RENAME = {
    "id": "id",
    "external_id": "external_id",
    "document": "image_file",
    "code": "inventory_code",
    "title": "title",
    "description": "description",
    "type": "type",
    "author": "artist_name",
    "location": "location",
    "date": "date",
    "period": "period",
    "technique": "technique",
    "height": "height",
    "width": "width",
    "color": "color",
    "history": "history",
    "collection_alt": "collection_alt_name",
    "description_generated": "description_generated",
}

COLUMN_RENAME = IPIRANGA_RENAME.copy()


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

FLAT_COLUMNS = (
    ["id"]
    + [COLUMN_RENAME.get(c, c) for c in COL_TOPLEVEL]
    + [COLUMN_RENAME.get(c, c) for c in COL_DATA]
)  # keep 'id' first, then externalId


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

    # row["id"] = str(uuid.uuid4())  # Remove random UUID

    # externalId: original id if present
    ext_id = None
    for candidate_key in ("id", "ID", "uuid", "slug"):
        if candidate_key in item and isinstance(item[candidate_key], (str, int)):
            ext_id = str(item[candidate_key])
            break
    row["external_id"] = ext_id

    # top-level fields (skip externalId)
    for orig, col in zip(TOPLEVEL_FIELDS[1:], COL_TOPLEVEL[1:]):
        val = _coerce_scalar(item.get(orig))
        if orig == "image_file" and isinstance(val, str):
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
        new_col = COLUMN_RENAME.get(col, col)

        row[new_col] = val

    if row["image_file"]:
        row["id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, row["image_file"]))

    data_obj = item.get("data")
    if isinstance(data_obj, dict):
        for orig_key, eng_key in FIELD_MAPPING.items():
            col = to_col_name(eng_key)
            row[col] = _coerce_scalar(data_obj.get(orig_key))

    for k, v in list(row.items()):
        if isinstance(v, str) and _is_bad_string(v):
            row[k] = None

    return row


def escape_sql_string(value):
    """Escape single quotes and backslashes for SQL INSERT statements"""
    if value is None or value == "":
        return "NULL"
    value = str(value)
    value = value.replace("\\", "\\\\").replace("'", "''")
    return f"'{value}'"


def generate_sql_inserts(raw_items: List[Dict[str, Any]]):
    """Generate SQL INSERT statements directly from filtered items"""
    print("Generating SQL INSERT statements for Ipiranga...")

    # Filter and extract rows
    filtered_rows = []
    filtered_count = 0
    total_count = 0

    for it in raw_items:
        total_count += 1
        row = extract_flat_row(it)

        # Filter by selected types - only save items with selected types
        item_type = row.get("type")
        if item_type and item_type in SELECTED_TYPES:
            # Also check that document field exists (has image)
            if row.get("image_file"):
                filtered_rows.append(row)
                filtered_count += 1

    print(
        f"Filtered items: {filtered_count} out of {total_count} total items will be saved to SQL"
    )

    if len(filtered_rows) == 0:
        print("No items to export!")
        return

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        # Write table creation statement matching your schema
        f.write("-- Ipiranga Dataset SQL Import\n")
        f.write("-- Generated automatically from download_and_filter.py\n")
        f.write(f"-- Total records: {len(filtered_rows)}\n\n")

        # Write INSERT statements in batches
        batch_size = 100
        total_rows = len(filtered_rows)

        for i in range(0, total_rows, batch_size):
            batch = filtered_rows[i : i + batch_size]

            f.write(
                "INSERT INTO Ipiranga (id, external_id, image_file, inventory_code, title, description, type, artist_name, location, date, period, technique, height, width, color, history, collection_alt_name, description_generated) VALUES\n"
            )

            values = []
            for row_dict in batch:
                # Map fields to match schema
                id_val = escape_sql_string(row_dict.get("id"))
                external_id = escape_sql_string(row_dict.get("external_id"))
                image_file = escape_sql_string(row_dict.get("image_file"))
                inventory_code = escape_sql_string(row_dict.get("inventory_code"))
                title = escape_sql_string(row_dict.get("title"))
                description = escape_sql_string(row_dict.get("description"))
                type_val = escape_sql_string(row_dict.get("type"))
                artist_name = escape_sql_string(row_dict.get("artist_name"))
                location = escape_sql_string(row_dict.get("location"))
                date_val = escape_sql_string(row_dict.get("date"))
                period = escape_sql_string(row_dict.get("period"))
                technique = escape_sql_string(row_dict.get("technique"))
                height = escape_sql_string(row_dict.get("height"))
                width = escape_sql_string(row_dict.get("width"))
                color = escape_sql_string(row_dict.get("color"))
                history = escape_sql_string(row_dict.get("history"))
                collection_alt_name = escape_sql_string(
                    row_dict.get("collection_alt_name")
                )
                description_generated = "NULL"

                values.append(
                    f"    ({id_val}, {external_id}, {image_file}, {inventory_code}, {title}, {description}, {type_val}, {artist_name}, {location}, {date_val}, {period}, {technique}, {height}, {width}, {color}, {history}, {collection_alt_name}, {description_generated})"
                )
            f.write(",\n".join(values))
            f.write(";\n\n")

        print(f"SQL file generated: {OUTPUT_SQL}")
        print(
            f"Total INSERT statements: {(total_rows + batch_size - 1) // batch_size} batches"
        )
        print(f"Total records: {total_rows}")


def generate_csv(raw_items: List[Dict[str, Any]]):
    """Generate CSV file from filtered items with all columns matching SQL schema"""
    print("Generating CSV file for Ipiranga...")

    filtered_rows = []
    filtered_count = 0
    total_count = 0

    for it in raw_items:
        total_count += 1
        row = extract_flat_row(it)

        item_type = row.get("type")
        if item_type and item_type in SELECTED_TYPES:
            if row.get("image_file"):
                filtered_rows.append(row)
                filtered_count += 1

    print(f"Filtered items for CSV: {filtered_count} out of {total_count} total items")

    if len(filtered_rows) == 0:
        print("No items to export to CSV!")
        return

    # Define CSV columns matching the SQL schema
    csv_columns = [
        "id",
        "external_id",
        "image_file",
        "inventory_code",
        "title",
        "description",
        "type",
        "artist_name",
        "location",
        "date",
        "period",
        "technique",
        "height",
        "width",
        "color",
        "history",
        "collection_alt_name",
        "description_generated",
    ]

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()

        for row_dict in filtered_rows:
            csv_row = {col: row_dict.get(col, "") or "" for col in csv_columns}
            csv_row["description_generated"] = ""
            writer.writerow(csv_row)

    print(f"CSV file generated: {OUTPUT_CSV}")
    print(f"Total records in CSV: {len(filtered_rows)}")


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

    # 2) Generate SQL INSERT statements directly (with filtering)
    print("Generating SQL INSERT file with filtering...")
    generate_sql_inserts(all_items)

    # 3) Generate CSV file (with same filtering)
    print("Generating CSV file with filtering...")
    generate_csv(all_items)

    # 4) Clean up: delete the pages folder if it exists
    if os.path.exists(OUT_DIR):
        print(f"Cleaning up: deleting {OUT_DIR}")
        shutil.rmtree(OUT_DIR)


if __name__ == "__main__":
    asyncio.run(main())
