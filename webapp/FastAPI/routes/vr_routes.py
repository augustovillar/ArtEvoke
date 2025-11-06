from fastapi import APIRouter, Depends
from routes import get_db
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
)
from api_types.common import (
    SelectImagesResponse,
    SelectImagesRVRequestDTO,
    ImproveTextRequestDTO,
    ImproveTextResponseDTO,
)
from clients import get_maritaca_client
import os

router = APIRouter()

client = get_maritaca_client()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")


def load_vr_prompt() -> str:
    """Load the VR text correction prompt."""
    filepath = os.path.join(PROMPTS_DIR, "vr_correct_text.md")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


@router.post("/select-images-rv")
async def select_images_rv(
    body: SelectImagesRVRequestDTO, db=Depends(get_db)
) -> SelectImagesResponse:
    sections = doTextSegmentation("conservative", body.story, max_sections=5)
    results = []

    for section in sections[body.sections]:
        section_images = get_top_k_images_from_text(
            section,
            body.dataset.value,
            k=6,
        )
        results.append({"section": section, "images": section_images})

    return {"sections": results}


@router.post("/improve-text")
async def improve_text(
    body: ImproveTextRequestDTO,
) -> ImproveTextResponseDTO:
    prompt_template = load_vr_prompt()
    
    messages = [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": body.raw_text}
    ]
    
    response = client.chat.completions.create(
        model="sabiazinho-3",
        messages=messages,
        max_tokens=1024,
        temperature=0.3,
    )
    
    processed_text = response.choices[0].message.content.strip()
    
    return {"processed_text": processed_text}
