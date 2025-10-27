from fastapi import APIRouter, Depends
from routes import get_db
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
)
from api_types.common import (
    SelectImagesRVRequestDTO,
    SelectImagesResponse,
)

router = APIRouter()


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
