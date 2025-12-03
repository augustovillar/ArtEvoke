from fastapi import APIRouter, Depends, HTTPException, Request
from routes import get_db
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
    get_top_k_images_for_sections,
)
from api_types.common import (
    SearchImagesRequestDTO,
    SelectImagesPerSectionRequestDTO,
    SearchImagesResponse,
    SelectImagesResponse,
    Dataset,
)
import logging
from sqlalchemy.orm import Session, joinedload
from orm import CatalogItem
from utils.auth import get_current_user
from utils.spell_check import check_and_correct_text


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search-images")
async def search_images(
    body: SearchImagesRequestDTO, db=Depends(get_db)
) -> SearchImagesResponse:
    text = check_and_correct_text(body.story, body.language)
    listArt = get_top_k_images_from_text(text, body.dataset, k=6)

    return {"images": listArt}


@router.post("/select-images-per-section")
async def select_images_per_section(
    body: SelectImagesPerSectionRequestDTO, db=Depends(get_db)
) -> SelectImagesResponse:
    story = check_and_correct_text(body.story, body.language)

    sections = doTextSegmentation(body.segmentation, story, max_sections=8)
    # Batched embeddings: one embeddings API call for all sections
    results = get_top_k_images_for_sections(
        sections, body.dataset, k=body.k
    )

    return {"sections": results}


@router.post("/images")
async def get_images(
    request: Request,
    ids: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ids_list = ids.get("ids", [])
    if not ids_list:
        return {"urls": {}}
    
    base_url = str(request.base_url).rstrip('/')
    
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

