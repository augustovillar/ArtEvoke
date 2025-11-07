from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from orm import get_db, ArtExploration, Images
from orm.session_models import Session as SessionModel
from api_types.art_exploration import (
    SaveArtExplorationRequestDTO,
    ImagesItem,
    RetrieveArtExplorationResponseDTO,
    ArtExplorationResponse
)
from utils.auth import (
    get_current_user,
)
import uuid
from typing import List, Optional

router = APIRouter()


@router.post("/save")
async def create_art_exploration(
    request: SaveArtExplorationRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    art_exploration_id: Optional[str] = Query(None, description="Optional ID for session mode. If not provided, a new ID will be generated (free mode)"),
):
    """
    Create a new art exploration record.
    
    - **Free mode**: No ID provided, generates new UUID
    - **Session mode**: ID provided from session's art_exploration_id
    """
    # Generate or use provided ID
    record_id = art_exploration_id if art_exploration_id else str(uuid.uuid4())
    
    art_exploration = ArtExploration(
        id=record_id,
        patient_id=current_user["id"],
        story_generated=request.story_generated,
        dataset=request.dataset,  
        language=request.language
    )

    db.add(art_exploration)
    db.flush() 

    for i, image in enumerate(request.images_selected):
        image_record = Images(
            id=str(uuid.uuid4()),
            art_exploration_id=art_exploration.id,
            catalog_id=image.id,
            display_order=i + 1, 
        )
        
        db.add(image_record)

    # If this is session mode, update session status to 'in_evaluation'
    if art_exploration_id:
        session = db.query(SessionModel).filter(
            SessionModel.art_exploration_id == art_exploration_id
        ).first()
        
        if session:
            session.status = "in_evaluation"
            db.add(session)

    db.commit()
    db.refresh(art_exploration)

    return {"message": "Art exploration saved successfully", "id": art_exploration.id}


@router.get("/retrieve", response_model=RetrieveArtExplorationResponseDTO)
async def get_art_explorations(
    limit: int = 5,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get art explorations for the current user with pagination"""
    # Get total count
    total_count = db.query(ArtExploration).filter(
        ArtExploration.patient_id == current_user["id"]
    ).count()
    
    # Get art explorations with pagination
    art_exploration_query: List[ArtExploration] = db.query(ArtExploration).filter(
        ArtExploration.patient_id == current_user["id"]
    ).order_by(ArtExploration.created_at.desc()).offset(offset).limit(limit).all()

    art_explorations = []
    for ae in art_exploration_query:
        # Get images for the art exploration
        image_query = db.query(Images).filter(
            Images.art_exploration_id == ae.id
        ).order_by(Images.display_order).all()

        images = []
        for image in image_query:
            images.append(ImagesItem(
                id=image.catalog_id,
                display_order=image.display_order,
            ))

        art_explorations.append(ArtExplorationResponse(
            id=ae.id,
            story_generated=ae.story_generated,
            dataset=ae.dataset,
            language=ae.language,
            created_at=ae.created_at,
            images=images
        ))
        
    has_more = (offset + limit) < total_count

    return RetrieveArtExplorationResponseDTO(
        art_explorations=art_explorations,
        total_count=total_count,
        has_more=has_more,
    )


@router.delete("/delete/{art_exploration_id}")
async def delete_art_exploration(
    art_exploration_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an art exploration and its associated images"""
    # Find the art exploration
    art_exploration = db.query(ArtExploration).filter(
        ArtExploration.id == art_exploration_id,
        ArtExploration.patient_id == current_user["id"]
    ).first()

    if not art_exploration:
        raise HTTPException(status_code=404, detail="Art exploration not found")

    # Delete associated images first (cascade will handle this, but being explicit)
    db.query(Images).filter(
        Images.art_exploration_id == art_exploration_id
    ).delete()

    # Delete the art exploration
    db.delete(art_exploration)
    db.commit()

    return {"message": "Art exploration deleted successfully"}
