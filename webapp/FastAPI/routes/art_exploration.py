from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, ArtExploration, Images
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
from typing import List

router = APIRouter()


@router.post("/save")
async def save_art_exploration(
    request: SaveArtExplorationRequestDTO,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    art_exploration = ArtExploration(
        id=str(uuid.uuid4()),
        patient_id=current_user,
        story_generated=request.story_generated,
        dataset=request.dataset,  
        language=request.language,
    )

    db.add(art_exploration)
    db.flush() 

    for i, image in enumerate(request.images_selected):
        section = Images(
            id=str(uuid.uuid4()),
            art_exploration_id=art_exploration.id,
            catalog_id=image.id,
            display_order=i + 1, 
        )
        
        db.add(section)

    db.commit()
    db.refresh(art_exploration)


    return {"message": "Art exploration saved successfully"}


@router.get("/retrieve", response_model=RetrieveArtExplorationResponseDTO)
async def get_art_explorations(
    limit: int = 5,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get total count
    total_count = db.query(ArtExploration).filter(
        ArtExploration.patient_id == current_user
    ).count()
    # Get memory reconstructions with pagination
    art_exploration_query: List[ArtExploration] = db.query(ArtExploration).filter(
        ArtExploration.patient_id == current_user
    ).order_by(ArtExploration.created_at.desc()).offset(offset).limit(limit).all()

    art_explorations = []
    for ae in art_exploration_query:
        # Get images for the
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
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find the memory reconstruction
    memory_reconstruction = db.query(ArtExploration).filter(
        ArtExploration.id == art_exploration_id,
        ArtExploration.patient_id == current_user
    ).first()

    if not memory_reconstruction:
        raise HTTPException(status_code=404, detail="Art exploration not found")

    # Delete associated sections first
    db.query(Images).filter(
        Images.art_exploration_id == art_exploration_id
    ).delete()

    # Delete the memory reconstruction
    db.delete(memory_reconstruction)
    db.commit()

    return {"message": "Art exploration deleted successfully"}
