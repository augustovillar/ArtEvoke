from fastapi import APIRouter, Depends, HTTPException, Request
from routes import get_db
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
)
from api_types.common import (
    SearchImagesRequestDTO,
    SelectImagesPerSectionRequestDTO,
    GenerateStoryRequestDTO,
    SearchImagesResponse,
    SelectImagesResponse,
    GenerateStoryResponse,
    Dataset,
)
from clients import get_maritaca_client
import logging
from sqlalchemy.orm import Session, joinedload
from orm import CatalogItem
from utils.auth import get_current_user

def correct_grammer_and_translate(text, src_language):
    return text


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
    catalog_item_ids = body.selectedImageIds
    art_descriptions = []

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


@router.post("/images")
async def get_images(
    request: Request,
    ids: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if user is authenticated
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    ids_list = ids.get("ids", [])
    if not ids_list:
        return {"urls": {}}
    
    base_url = str(request.base_url).rstrip('/')
    
    # Query the CatalogItems with joins to get image_file from related tables
    catalog_items = (
        db.query(CatalogItem)
        .options(
            joinedload(CatalogItem.ipiranga),
            joinedload(CatalogItem.wikiart),
            joinedload(CatalogItem.semart),
        )
        .filter(CatalogItem.id.in_(ids_list))
        .all()
    )
    
    urls = {}
    for item in catalog_items:
        image_url = None
        if item.source == Dataset.semart and item.semart:
            image_url = f"{base_url}/art-images/semart/{item.semart.image_file}"
        elif item.source == Dataset.wikiart and item.wikiart:
            image_url = f"{base_url}/art-images/wikiart/{item.wikiart.image_file}"
        elif item.source == Dataset.ipiranga and item.ipiranga:
            image_url = f"https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items{item.ipiranga.image_file}"
        
        if image_url:
            urls[str(item.id)] = image_url
    
    return {"urls": urls}

