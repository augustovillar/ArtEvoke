import json, lzma, sys, os

# Folders with images to check
ADDITIONAL_FOLDERS = [
    "/DATA/public/siamese/dataset_mrbab/art-foto/sculpt19/intranet",
    "/DATA/public/siamese/dataset_mrbab/art-foto/mod/intranet",
]

def get_actual_filename(folder, target_fname):
    target_lower = target_fname.lower()

    if os.path.exists(os.path.join(folder, target_fname)):
        return target_fname

    try:
        for fname in os.listdir(folder):
            if fname.lower() == target_lower:
                return fname
    except FileNotFoundError:
        return None

    if '.' not in target_fname:
        for ext in [".jpg", ".jpeg", ".png"]:
            alt_target = target_lower + ext
            for fname in os.listdir(folder):
                if fname.lower() == alt_target:
                    return fname
    return None


def normalize_path_components(image_link):
    return (
        image_link
        .replace("file:///", "")                 
        .replace("\\", "/")                      
        .replace("/Intranet/", "/intranet/")
        .replace("/IntrAnet/", "/intranet/")
        .replace("/Mod/", "/mod/")
        .replace("/MOD/", "/mod/")
        .replace("/Old/", "/old/")
        .replace("/OLD/", "/old/")
        .replace("/Art-Foto/", "/art-foto/")
        .replace("/Rubensdatabase/", "/rubensdatabase/")
    )


def process(input_file, output_file):
    # Load input data
    if input_file.endswith(".xz"):
        with lzma.open(input_file, "rt") as f:
            data = json.load(f)
    else:
        with open(input_file, "r") as f:
            data = json.load(f)

    filtered_data = {}
    new_index = 0
    existing_links = set()

    print("Verifying existing image paths...")
    for rec in data:
        images = rec.get("relatedVisualDocumentation", [])
        image_link = None

        if images and isinstance(images, list):
            image_link = images[0].get("imageIntranetLink")
            
        if not image_link:
            continue

        normalized_link = normalize_path_components(image_link)
        full_existing_path = os.path.join("/DATA/public/siamese/dataset_mrbab", normalized_link.lstrip("/"))

        if not os.path.exists(full_existing_path):
            folder = os.path.dirname(full_existing_path)
            fname = os.path.basename(full_existing_path)
            corrected_name = get_actual_filename(folder, fname)

            if corrected_name:
                full_existing_path = os.path.join(folder, corrected_name)
            else:
                print(f"⚠️  File not found: {full_existing_path}")


        subject = rec.get("subjectMatter")

        new_rec = {
            "recordID": rec.get("recordID"),
            "titleText": rec.get("objectWork", {}).get("titleText"),
            "imageLinkHigh": full_existing_path,
            "creatorDescription": rec.get("objectWork", {}).get("creatorDescription"),
            "measurementsDescription": rec.get("objectWork", {}).get("measurementsDescription"),
            "subjectMatter": subject if isinstance(subject, dict) else {}
        }

        filtered_data[str(new_index)] = new_rec
        existing_links.add(full_existing_path.split("/")[-1].lower())
        new_index += 1

    print("Scanning additional folders for missing images...")

    # Add missing files from folders
    for folder in ADDITIONAL_FOLDERS:
        for fname in os.listdir(folder):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            full_path = os.path.join(folder, fname)
            if full_path.split("/")[-1].lower() not in existing_links:
                new_rec = {
                    "recordID": None,
                    "titleText": None,
                    "imageLinkHigh": full_path,
                    "creatorDescription": None,
                    "measurementsDescription": None,
                    "subjectMatter": {}
                }
                filtered_data[str(new_index)] = new_rec
                existing_links.add(full_path)
                new_index += 1

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! {new_index} records written to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py input.json[.xz] output.json")
    else:
        process(sys.argv[1], "descriptions/" +sys.argv[2])
