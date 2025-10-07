import os
import pandas as pd
import kagglehub
import shutil
import uuid

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_DATASET = os.path.join(SCRIPT_DIR, "Images")
INPUT_CSV = os.path.join(SCRIPT_DIR, "WikiArt.csv")
OUTPUT_SQL = os.path.join(SCRIPT_DIR, "WikiArt_insert.sql")

genres_selected = {
    "New_Realism",
    "Realism",
    "Baroque",
    "Impressionism",
    "Northern_Renaissance",
    "Romanticism",
    "Mannerism_Late_Renaissance",
    "Pointillism",
    "Contemporary_Realism",
    "Early_Renaissance",
    "High_Renaissance",
    "Naive_Art_Primitivism",
    "Post_Impressionism",
    "Ukiyo_e",
}
# I would like to add this: Art_nouveau_modern, expressionism, fauvism


# wikiart_to_ipiranga = {
#     "id": "id",
#     "filename": "filename",
#     "artist": "author",
#     "genre": "type",
#     "description": "description",
#     "width": "width",
#     "height": "height",
#     "description_generated": "description_generated",
# }


def download_and_unzip():
    print("Downloading WikiArt dataset...")
    # path = kagglehub.dataset_download("steubk/wikiart")
    # print(f"Dataset downloaded to: {path}")
    path = os.path.expanduser("~/.cache/kagglehub/datasets/steubk/wikiart/versions/1")

    if os.path.exists(PATH_DATASET):
        print(f"Removing existing folder: {PATH_DATASET}")
        shutil.rmtree(PATH_DATASET)

    shutil.copytree(path, PATH_DATASET)
    print(f"Moved dataset to: {PATH_DATASET}")


def remove_unwanted_files():
    for item in os.listdir(PATH_DATASET):
        item_path = os.path.join(PATH_DATASET, item)

        if os.path.isdir(item_path) and item not in genres_selected:
            print(f"Deleting unwanted genre folder: {item_path}")
            shutil.rmtree(item_path)

    os.remove(os.path.join(PATH_DATASET, "wclasses.csv"))
    shutil.move(
        os.path.join(PATH_DATASET, "classes.csv"),
        os.path.join(SCRIPT_DIR, "classes.csv"),
    )


def filter_dataset():
    df1 = pd.read_csv(os.path.join(SCRIPT_DIR, "classes.csv"))

    df1 = df1[df1["filename"].apply(lambda f: any(g in f for g in genres_selected))]

    df1["file_exists"] = df1["filename"].apply(
        lambda f: os.path.exists(os.path.join(PATH_DATASET, f))
    )
    df1 = df1[df1["file_exists"]]

    df1["basename"] = df1["filename"].apply(lambda x: x.split("/")[-1])
    df_keep = df1.drop_duplicates(subset="basename", keep="first")
    df_duplicates = df1[~df1.index.isin(df_keep.index)]

    deleted_count = 0
    for _, row in df_duplicates.iterrows():
        full_path = os.path.join(PATH_DATASET, row["filename"])
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted_count += 1

    df_keep.drop(columns=["file_exists", "basename"], errors="ignore").drop(
        columns=["subset", "genre_count"], errors="ignore"
    ).to_csv(INPUT_CSV, index=False)

    os.remove(os.path.join(SCRIPT_DIR, "classes.csv"))

    print(f"Final dataset size: {len(df_keep)}")
    print(f"Deleted {deleted_count} duplicated files.")


def escape_sql_string(value):
    """Escape single quotes and backslashes for SQL INSERT statements"""
    if pd.isna(value) or value is None:
        return "NULL"
    value = str(value)
    value = value.replace("\\", "\\\\").replace("'", "''")
    return f"'{value}'"


def process_genre(genre_value):
    """Convert genre array to semicolon-separated string"""
    if pd.isna(genre_value) or genre_value is None:
        return "NULL"

    # If it's already a string representation of an array like "['Baroque']"
    if isinstance(genre_value, str):
        # Remove brackets and quotes, then split by comma
        genre_value = genre_value.strip("[]").replace("'", "").replace('"', "")
        genres = [g.strip() for g in genre_value.split(",") if g.strip()]
        result = ";".join(genres)
        return f"'{result}'"

    # If it's a list
    if isinstance(genre_value, list):
        result = ";".join(str(g) for g in genre_value)
        return f"'{result}'"

    # Otherwise just escape as string
    return escape_sql_string(genre_value)


def generate_sql_inserts():
    """Generate SQL INSERT statements from the filtered CSV"""
    print("Generating SQL INSERT statements...")

    df = pd.read_csv(INPUT_CSV)

    # Add deterministic UUID for each item based on filename
    # Using UUID5 with DNS namespace to ensure same filename always gets same UUID
    df["id"] = df["filename"].apply(lambda f: str(uuid.uuid5(uuid.NAMESPACE_DNS, f)))

    # Reorder columns to have id first
    cols = ["id"] + [col for col in df.columns if col != "id"]
    df = df[cols]

    # Save updated CSV with id
    df.to_csv(INPUT_CSV, index=False)

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        # Write table creation statement
        f.write("-- WikiArt Dataset SQL Import\n")
        f.write("-- Generated automatically from download_and_filter.py\n")
        f.write(f"-- Total records: {len(df)}\n\n")

        f.write("CREATE TABLE IF NOT EXISTS WikiArt (\n")
        f.write("    id CHAR(36) PRIMARY KEY,\n")
        f.write("    filename VARCHAR(50),\n")
        f.write("    artist VARCHAR(50),\n")
        f.write("    genre VARCHAR(50),\n")
        f.write("    description TEXT,\n")
        f.write("    width INT,\n")
        f.write("    height INT,\n")
        f.write("    description_generated TEXT,\n")
        f.write("    INDEX idx_artist (artist),\n")
        f.write("    INDEX idx_genre (genre)\n")
        f.write(
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n\n"
        )

        # Write INSERT statements in batches
        batch_size = 100
        total_rows = len(df)

        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i : i + batch_size]

            f.write(
                "INSERT INTO WikiArt (id, filename, artist, genre, description, width, height, description_generated) VALUES\n"
            )

            values = []
            for _, row in batch.iterrows():
                id_val = escape_sql_string(row.get("id"))
                filename = escape_sql_string(row.get("filename"))
                artist = escape_sql_string(row.get("artist"))
                genre = process_genre(row.get("genre"))
                description = escape_sql_string(row.get("description", ""))
                width = int(row.get("width")) if pd.notna(row.get("width")) else "NULL"
                height = (
                    int(row.get("height")) if pd.notna(row.get("height")) else "NULL"
                )
                description_generated = escape_sql_string(
                    row.get("description_generated", "")
                )

                values.append(
                    f"    ({id_val}, {filename}, {artist}, {genre}, {description}, {width}, {height}, {description_generated})"
                )

            f.write(",\n".join(values))
            f.write(";\n\n")

        print(f"SQL file generated: {OUTPUT_SQL}")
        print(
            f"Total INSERT statements: {(total_rows + batch_size - 1) // batch_size} batches"
        )
        print(f"Total records: {total_rows}")


if __name__ == "__main__":
    download_and_unzip()
    remove_unwanted_files()
    filter_dataset()
    generate_sql_inserts()
