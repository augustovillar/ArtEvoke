from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from orm import get_db, MemoryReconstruction, Sections
from orm.session_models import Session as SessionModel
from api_types.memory_reconstruction import (
    SaveMemoryReconstructionRequestDTO,
    SaveMemoryReconstructionResponseDTO,
    RetrieveMemoryReconstructionsResponseDTO,
    DeleteMemoryReconstructionResponseDTO,
    MemoryReconstructionResponse,
    SectionResponse,
    AnalyzeStoryRequestDTO,
    AnalyzeStoryResponseDTO,
)
from api_types.common import (
    ImproveTextRequestDTO,
    ImproveTextResponseDTO,
)
from utils.auth import (
    get_current_user,
)
from typing import Optional
import uuid
import os
from clients import get_maritaca_client
from utils.text_correction import parse_llm_json_response

router = APIRouter()

client = get_maritaca_client()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")


def load_speech_correct_prompt(language: str = "pt") -> str:
    """Load the speech text correction prompt based on language."""
    if language == "en":
        filename = "speech_correct_text_en.md"
    else:
        filename = "speech_correct_text_pt.md"
    
    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_mr_prompt(language: str = "pt") -> str:
    """Load the memory reconstruction analysis prompt based on language."""
    if language == "en":
        filename = "mr_prompt_en.md"
    else:
        filename = "mr_prompt_pt.md"
    
    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


@router.post("/save", response_model=SaveMemoryReconstructionResponseDTO)
async def save_memory_reconstruction(
    request: SaveMemoryReconstructionRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    session_id: Optional[str] = Query(None, description="Optional session ID for session mode. If provided, links memory reconstruction to this session."),
):
    """
    Create a new memory reconstruction record.
    
    - **Free mode**: No session_id provided, generates new UUID
    - **Session mode**: session_id provided, generates UUID and links to session
    """
    
    memory_reconstruction = MemoryReconstruction(
        id=str(uuid.uuid4()),
        patient_id=current_user["id"],
        story=request.story,
        dataset=request.dataset,  
        language=request.language,
        segmentation_strategy=request.segmentation_strategy
    )

    db.add(memory_reconstruction)
    db.flush() 

    section_ids = []
    for i, section_item in enumerate(request.sections):
        section = Sections(
            id=str(uuid.uuid4()),
            memory_reconstruction_id=memory_reconstruction.id,
            section_content=section_item.section_content,
            display_order=i + 1, 
            image1_id=str(section_item.image1_id),
            image2_id=str(section_item.image2_id),
            image3_id=str(section_item.image3_id),
            image4_id=str(section_item.image4_id),
            image5_id=str(section_item.image5_id),
            image6_id=str(section_item.image6_id),
            fav_image_id=str(section_item.fav_image_id),
        )
        
        db.add(section)
        section_ids.append(section.id)

    # If this is session mode, update session with memory_reconstruction_id and change status
    if session_id:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.memory_reconstruction_id = memory_reconstruction.id
            session.status = "in_evaluation"

    db.commit()
    db.refresh(memory_reconstruction)


    return SaveMemoryReconstructionResponseDTO(
        message="Memory reconstruction saved successfully",
        id=memory_reconstruction.id,
        section_ids=section_ids
    )


@router.get("/retrieve", response_model=RetrieveMemoryReconstructionsResponseDTO)
async def get_memory_reconstructions(
    limit: int = 5,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_mr_ids = select(SessionModel.memory_reconstruction_id).where(
        SessionModel.memory_reconstruction_id.isnot(None)
    )
    
    total_count = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.patient_id == current_user["id"],
        ~MemoryReconstruction.id.in_(session_mr_ids)
    ).count()

    memory_reconstructions_query = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.patient_id == current_user["id"],
        ~MemoryReconstruction.id.in_(session_mr_ids)
    ).order_by(MemoryReconstruction.created_at.desc()).offset(offset).limit(limit).all()

    memory_reconstructions = []
    for mr in memory_reconstructions_query:
        sections_query = db.query(Sections).filter(
            Sections.memory_reconstruction_id == mr.id
        ).order_by(Sections.display_order).all()

        sections = []
        for section in sections_query:
            sections.append(SectionResponse(
                id=section.id,
                section_content=section.section_content,
                display_order=section.display_order,
                image1_id=str(section.image1_id),
                image2_id=str(section.image2_id),
                image3_id=str(section.image3_id),
                image4_id=str(section.image4_id),
                image5_id=str(section.image5_id),
                image6_id=str(section.image6_id),
                fav_image_id=str(section.fav_image_id) if section.fav_image_id else None,
            ))

        memory_reconstructions.append(MemoryReconstructionResponse(
            id=mr.id,
            story=mr.story,
            dataset=mr.dataset,
            language=mr.language,
            environment=mr.environment,
            time_of_day=mr.time_of_day,
            emotion=mr.emotion,
            segmentation_strategy=mr.segmentation_strategy,
            created_at=mr.created_at,
            sections=sections,
        ))

    has_more = (offset + limit) < total_count

    return RetrieveMemoryReconstructionsResponseDTO(
        memory_reconstructions=memory_reconstructions,
        total_count=total_count,
        has_more=has_more,
    )


@router.delete("/delete/{memory_reconstruction_id}", response_model=DeleteMemoryReconstructionResponseDTO)
async def delete_memory_reconstruction(
    memory_reconstruction_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memory_reconstruction = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.id == memory_reconstruction_id,
        MemoryReconstruction.patient_id == current_user["id"]
    ).first()

    if not memory_reconstruction:
        raise HTTPException(status_code=404, detail="Memory reconstruction not found")

    db.query(Sections).filter(
        Sections.memory_reconstruction_id == memory_reconstruction_id
    ).delete()

    db.delete(memory_reconstruction)
    db.commit()
    
    return DeleteMemoryReconstructionResponseDTO(
        message="Memory reconstruction deleted successfully",
        id=memory_reconstruction_id
    )


@router.post("/improve-text", response_model=ImproveTextResponseDTO)
async def improve_text(
    body: ImproveTextRequestDTO,
    current_user: dict = Depends(get_current_user),
) -> ImproveTextResponseDTO:
    """
    Improve and correct text from speech-to-text transcription.
    
    - **raw_text**: Text to be corrected (max 900 characters)
    - **language**: Language code ('pt' or 'en')
    
    Requires authentication (patient or doctor).
    """
    if len(body.raw_text) > 900:
        raise HTTPException(
            status_code=400,
            detail="Text is too long. Maximum length is 900 characters."
        )
    
    if not body.raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )
    
    language = body.language.value
    prompt_template = load_speech_correct_prompt(language)
    
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


@router.post("/{memory_reconstruction_id}/analyze-story", response_model=AnalyzeStoryResponseDTO)
async def analyze_story(
    memory_reconstruction_id: str, 
    body: AnalyzeStoryRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalyzeStoryResponseDTO:
    """
    Analyze a story to extract environment, time of day, and emotion.
    
    - **story**: The story text to analyze (max 900 characters)
    - **language**: Language code ('pt' or 'en')
    
    Returns:
    - **environment**: Environment type (Open/Aberto, Urban/Urbano, Closed/Fechado, Rural)
    - **time_of_day**: Time of day (Morning/Manhã, Afternoon/Tarde, Night/Noite)
    - **emotion**: Predominant emotion (Happiness/Felicidade, Sadness/Tristeza, Anger/Raiva, Surprise/Supresa, Disgust/Nojo)
    
    Requires authentication (patient or doctor).
    """
    if len(body.story) > 900:
        raise HTTPException(
            status_code=400,
            detail="Story is too long. Maximum length is 900 characters."
        )
    
    if not body.story.strip():
        raise HTTPException(
            status_code=400,
            detail="Story cannot be empty."
        )
    
    language = body.language.value
    prompt_template = load_mr_prompt(language)
    
    messages = [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": body.story}
    ]
    
    response = client.chat.completions.create(
        model="sabiazinho-3",
        messages=messages,
        max_tokens=512,
        temperature=0.3,
    )
    
    response_content = response.choices[0].message.content.strip()
    
    # Parse the response using the existing helper function
    parsed_data = parse_llm_json_response(response_content, raise_on_error=True)
    
    environment = parsed_data.get("environment", "")
    time_of_day = parsed_data.get("timeOfDay", "")
    emotion = parsed_data.get("emotion", "")
    
    if not environment or not time_of_day or not emotion:
        raise HTTPException(
            status_code=500,
            detail="LLM response is missing required fields"
        )
    
    # If memory_reconstruction_id is provided, update the record
    memory_reconstruction = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.id == memory_reconstruction_id,
        MemoryReconstruction.patient_id == current_user["id"]
    ).first()
    
    if not memory_reconstruction:
        raise HTTPException(status_code=404, detail="Memory reconstruction not found")
    
    memory_reconstruction.environment = environment
    memory_reconstruction.time_of_day = time_of_day
    memory_reconstruction.emotion = emotion
    
    db.commit()
    
    return AnalyzeStoryResponseDTO(
        environment=environment,
        time_of_day=time_of_day,
        emotion=emotion
    )
