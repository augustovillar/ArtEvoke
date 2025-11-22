from fastapi import APIRouter, Depends
from routes import get_db
from utils.text_processing import doTextSegmentation
from utils.embeddings import (
    get_top_k_images_from_text,
)
from api_types.common import (
    Dataset,
    SelectImagesResponse,
    SelectImagesRVRequestDTO,
    SectionVRResponseDTO,
    ImproveTextRequestDTO,
    ImproveTextResponseDTO,
)
from clients import get_maritaca_client
from utils.text_correction import parse_llm_json_response
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
) -> SectionVRResponseDTO:
    # Split the Story into Segments
    sections = doTextSegmentation("conservative", body.story, max_sections=5)

    section_images = get_top_k_images_from_text(
        sections[body.section_number],
        Dataset.wikiart,
        k=6,
    )

    return {"section": sections[body.section_number], "images": section_images, "sectionsQuantity": len(sections)}


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
    
    response_content = response.choices[0].message.content.strip()
    processed_text = parse_llm_json_response(response_content, json_key="improved_text", raise_on_error=True)
    return ImproveTextResponseDTO(processed_text=processed_text)
