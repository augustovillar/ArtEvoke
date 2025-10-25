from fastapi import APIRouter, Depends
from routes import get_db, correct_grammer_and_translate
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
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
from clients import get_maritaca_client
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Maritaca AI client
client = get_maritaca_client()


@router.post("/search-images")
async def search_images(
    body: SearchImagesRequestDTO, db=Depends(get_db)
) -> SearchImagesResponse:
    text = correct_grammer_and_translate(body.story, body.language.value)
    listArt = get_top_k_images_from_text(text, body.dataset, k=6)

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
            section, body.dataset, k=body.k
        )
        results.append({"section": section, "images": section_images})

    return {"sections": results}


@router.post("/generate-story")
async def generate_story(body: GenerateStoryRequestDTO, db=Depends(get_db)) -> GenerateStoryResponse:
    from orm import CatalogItem, SemArt, WikiArt, Ipiranga
    from utils.types import Dataset
    
    data = body.selectedImagesByDataset
    art_descriptions = []

    for dataset_name, catalog_item_ids in data.items():
        # Convert string to Dataset enum
        try:
            if dataset_name == "semart":
                dataset = Dataset.semart
            elif dataset_name == "wikiart":
                dataset = Dataset.wikiart
            elif dataset_name == "ipiranga":
                dataset = Dataset.ipiranga
            else:
                print(f"[Warning] Unknown dataset: {dataset_name}")
                continue
        except:
            print(f"[Warning] Invalid dataset: {dataset_name}")
            continue

        # Get descriptions from catalog items
        for catalog_item_id in catalog_item_ids:
            try:
                # Query the catalog item
                catalog_item = db.query(CatalogItem).filter(
                    CatalogItem.id == catalog_item_id
                ).first()
                
                if not catalog_item:
                    print(f"[Warning] No catalog item found for ID: {catalog_item_id}")
                    continue
                
                # Get description based on source
                description = None
                if catalog_item.source == Dataset.semart and catalog_item.semart:
                    description = catalog_item.semart.description
                elif catalog_item.source == Dataset.wikiart and catalog_item.wikiart:
                    description = catalog_item.wikiart.description
                elif catalog_item.source == Dataset.ipiranga and catalog_item.ipiranga:
                    description = catalog_item.ipiranga.description
                
                if description:
                    art_descriptions.append(description)
                else:
                    print(f"[Warning] No description found for catalog item: {catalog_item_id}")
                    
            except Exception as e:
                print(f"[Error] Failed to get description for {catalog_item_id}: {e}")

    if not art_descriptions:
        # Fallback story if no descriptions found
        base_prompt = "Write a short, creative story about art and imagination."
    else:
        base_prompt = (
            "Descriptions:\n" + "\n".join(f"- {desc}" for desc in art_descriptions) + "\n\n"
            "Write a story that takes inspiration on these scenes. Use 2–3 short paragraphs (approximately). "
            "Tell it like a simple, flowing story with a start, middle and an end. The paragraphs have to be connected and follow a sequence of events."
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
