from fastapi import APIRouter, Depends
from routes import get_db
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
)
from api_types.common import (
    Dataset,
    SelectImagesRVRequestDTO,
    SectionVRResponseDTO,
)

router = APIRouter()


@router.post("/select-images-rv")
async def select_images_rv(
    body: SelectImagesRVRequestDTO, db=Depends(get_db)
) -> SectionVRResponseDTO:
    # Split the Story into Segments
    sections = doTextSegmentation("conservative", body.story, max_sections=5)

    section_images = get_top_k_images_from_text(
        sections[body.section_number],
        Dataset.wikiart,
        k=6,
    )

    return {"section": sections[body.section_number], "images": section_images, "sectionsQuantity": len(sections)}
