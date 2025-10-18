from fastapi import APIRouter, Depends
from routes import get_db, correct_grammer_and_translate
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
    ipiranga_conn,
    metadata_by_dataset,
    filename_columns,
)
from utils.types import (
    SearchImagesRequestDTO,
    SelectImagesPerSectionRequestDTO,
    GenerateStoryRequestDTO,
    SelectImagesRVRequestDTO,
    SearchImagesResponse,
    SelectImagesResponse,
    GenerateStoryResponse,
)
import openai
import os
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

# Maritaca AI client
client = openai.OpenAI(
    api_key=os.getenv("MARITACA_API_KEY"),
    base_url="https://chat.maritaca.ai/api",
)


@router.post("/search-images")
async def search_images(
    body: SearchImagesRequestDTO, db=Depends(get_db)
) -> SearchImagesResponse:
    text = correct_grammer_and_translate(body.story, body.language.value)
    listArt = get_top_k_images_from_text(text, body.dataset.value, k=6)

    return {"images": listArt}


@router.post("/select-images-per-section")
async def select_images_per_section(
    body: SelectImagesPerSectionRequestDTO, db=Depends(get_db)
) -> SelectImagesResponse:
    story = correct_grammer_and_translate(body.story, body.language.value)

    # Split the Story into Segments
    sections = doTextSegmentation(body.segmentation, story, max_sections=8)
    results = []

    for section in sections:
        section_images = get_top_k_images_from_text(
            section, body.dataset.value, k=body.k
        )
        results.append({"section": section, "images": section_images})

    return {"sections": results}


@router.post("/generate-story")
async def generate_story(body: GenerateStoryRequestDTO) -> GenerateStoryResponse:
    data = body.selectedImagesByDataset

    cleaned_filenames_by_dataset = {}

    for key, urls in data.items():
        if key == "ipiranga":
            prefix = "https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items"
            cleaned_filenames_by_dataset[key] = [
                url.replace(prefix, "") for url in urls
            ]
        else:
            prefix = f"/art-images/{key}/"
            cleaned_filenames_by_dataset[key] = [
                url.replace(prefix, "") for url in urls
            ]

    art_descriptions = []

    for dataset, filenames in cleaned_filenames_by_dataset.items():
        if dataset == "ipiranga":
            cursor = ipiranga_conn.cursor()
            for name in filenames:
                cursor.execute(
                    "SELECT description FROM ipiranga_entries WHERE document = ?",
                    (name,),
                )
                row = cursor.fetchone()
                if row and row[0]:
                    art_descriptions.append(row[0])
                else:
                    print(
                        f"[Warning] No description found for {dataset} document: {name}"
                    )
        else:
            df = metadata_by_dataset[dataset]
            filename_col = filename_columns[dataset]

            for name in filenames:
                # Regular matching for wikiart and semart
                match = df.loc[df[filename_col] == name, "description"]
                if not match.empty:
                    art_descriptions.append(match.values[0])
                else:
                    print(
                        f"[Warning] No description found for {dataset} filename: {name}"
                    )

    base_prompt = (
        "Descriptions:\n" + "\n".join(f"- {desc}" for desc in art_descriptions) + "\n\n"
        "Write a story that takes inspiration on these scenes. Use 2–3 short paragraphs (approximately). "
        "Tell it like a simple, flowing story with a start, middle and an end. The paragraphs have to be conneced and follow a sequence of events."
    )

    messages = [{"role": "user", "content": base_prompt}]

    response = client.chat.completions.create(
        model="sabiazinho-3",
        messages=messages,
        max_tokens=1024,
        temperature=0.9,
    )

    story = response.choices[0].message.content.strip()

    return {"text": story}


@router.post("/select-images-rv")
async def select_images_rv(
    body: SelectImagesRVRequestDTO, db=Depends(get_db)
) -> SelectImagesResponse:
    # Split the Story into Segments
    sections = doTextSegmentation("conservative", body.story, max_sections=5)
    results = []

    # select only the sections with the index in the body.section list
    for section in sections[body.sections]:
        section_images = get_top_k_images_from_text(
            section,
            body.dataset.value,
            k=6,
        )
        results.append({"section": section, "images": section_images})

    return {"sections": results}
