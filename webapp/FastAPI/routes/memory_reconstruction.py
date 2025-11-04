from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, MemoryReconstruction, Sections
from api_types.memory_reconstruction import (
    SaveMemoryReconstructionRequestDTO,
    RetrieveMemoryReconstructionsResponseDTO,
    MemoryReconstructionResponse,
    SectionResponse,
)
from utils.auth import (
    get_current_user,
)
import uuid

router = APIRouter()


@router.post("/save")
async def save_memory_reconstruction(
    request: SaveMemoryReconstructionRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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

    db.commit()
    db.refresh(memory_reconstruction)


    return {"message": "Memory reconstruction saved successfully"}


@router.get("/retrieve", response_model=RetrieveMemoryReconstructionsResponseDTO)
async def get_memory_reconstructions(
    limit: int = 5,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get total count (only items not in session - session_id is NULL)
    total_count = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.patient_id == current_user["id"],
        MemoryReconstruction.session_id.is_(None)
    ).count()

    # Get memory reconstructions with pagination (only items not in session)
    memory_reconstructions_query = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.patient_id == current_user["id"],
        MemoryReconstruction.session_id.is_(None)
    ).order_by(MemoryReconstruction.created_at.desc()).offset(offset).limit(limit).all()

    memory_reconstructions = []
    for mr in memory_reconstructions_query:
        # Get sections for this memory reconstruction
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


@router.delete("/delete/{memory_reconstruction_id}")
async def delete_memory_reconstruction(
    memory_reconstruction_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find the memory reconstruction
    memory_reconstruction = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.id == memory_reconstruction_id,
        MemoryReconstruction.patient_id == current_user["id"]
    ).first()

    if not memory_reconstruction:
        raise HTTPException(status_code=404, detail="Memory reconstruction not found")

    # Delete associated sections first
    db.query(Sections).filter(
        Sections.memory_reconstruction_id == memory_reconstruction_id
    ).delete()

    # Delete the memory reconstruction
    db.delete(memory_reconstruction)
    db.commit()

    return {"message": "Memory reconstruction deleted successfully"}
