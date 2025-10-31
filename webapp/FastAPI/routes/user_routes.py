from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, Patient, MemoryReconstruction, ArtExploration
from orm import Session as SessionModel
from api_types.user import (
    MessageResponse,
    RetrieveSearchesResponse,
)
from api_types.art import (
    SaveStoryRequest,
    SaveGenerationRequest,
)
from utils.auth import (
    get_current_user,
)
from typing import Dict, List
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/save-story")
async def save_art_search(
    story_data: SaveStoryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        story_text: str = story_data.storyText
        selected_images_by_dataset: Dict[str, List[str]] = (
            story_data.selectedImagesByDataset
        )

        if not story_text and not selected_images_by_dataset:
            raise HTTPException(
                status_code=400, detail="No story text or selected images to save."
            )

        # If evaluationId provided, update existing record (session mode)
        if story_data.evaluationId:
            art_exploration = (
                db.query(ArtExploration)
                .filter(
                    ArtExploration.id == story_data.evaluationId,
                    ArtExploration.patient_id == current_user["id"],
                )
                .first()
            )

            if not art_exploration:
                raise HTTPException(
                    status_code=404, detail="Evaluation instance not found"
                )

            # Update existing record
            art_exploration.story_generated = story_text
            # Keep in_session='true' as it was created by session

        else:
            # Create new ArtExploration entry (practice mode)
            art_exploration = ArtExploration(
                id=str(uuid.uuid4()),
                patient_id=current_user["id"],
                story_generated=story_text,
                dataset="WikiArt",  # Default dataset
                language="EN",  # Default language
                in_session="false",  # Practice mode
            )
            db.add(art_exploration)

        db.commit()
        db.refresh(art_exploration)

        # If sessionId provided, mark session as completed
        if story_data.sessionId:
            session = db.query(SessionModel).filter(
                SessionModel.id == story_data.sessionId,
                SessionModel.patient_id == current_user["id"]
            ).first()
            
            if session:
                session.status = "completed"
                session.ended_at = datetime.utcnow().date()
                db.commit()

        # TODO: Add Images records for selected_images_by_dataset
        # This would require mapping image IDs to catalog_item IDs

        return {"message": "Story saved successfully"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.post("/save-generation")
async def save_story_generation(
    story_data: SaveGenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        image_urls: List[str] = story_data.selectedImages
        story_text: str = story_data.generatedStory

        if not story_text:
            raise HTTPException(status_code=400, detail="Missing generatedStory")

        # If evaluationId provided, update existing record (session mode)
        if story_data.evaluationId:
            memory_reconstruction = (
                db.query(MemoryReconstruction)
                .filter(
                    MemoryReconstruction.id == story_data.evaluationId,
                    MemoryReconstruction.patient_id == current_user["id"],
                )
                .first()
            )

            if not memory_reconstruction:
                raise HTTPException(
                    status_code=404, detail="Evaluation instance not found"
                )

            # Update existing record
            memory_reconstruction.story = story_text
            # Keep in_session='true' as it was created by session

        else:
            # Create new MemoryReconstruction entry (practice mode)
            memory_reconstruction = MemoryReconstruction(
                id=str(uuid.uuid4()),
                patient_id=current_user["id"],
                story=story_text,
                dataset="WikiArt",  # Default dataset
                language="EN",  # Default language
                segmentation_strategy="Conservative",  # Default strategy
                in_session="false",  # Practice mode
            )
            db.add(memory_reconstruction)

        db.commit()
        db.refresh(memory_reconstruction)

        # If sessionId provided, mark session as completed
        if story_data.sessionId:
            session = db.query(SessionModel).filter(
                SessionModel.id == story_data.sessionId,
                SessionModel.patient_id == current_user["id"]
            ).first()
            
            if session:
                session.status = "completed"
                session.ended_at = datetime.utcnow().date()
                db.commit()

        # TODO: Map selectedImages to proper Sections with images relationship

        return {"message": "Generation saved successfully"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("/retrieve-searches")
async def retrieve_searches(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RetrieveSearchesResponse:
    # Get user's art explorations (saved searches)
    art_explorations = (
        db.query(ArtExploration).filter(ArtExploration.patient_id == current_user["id"]).all()
    )

    # Get user's memory reconstructions (saved generations)
    memory_reconstructions = (
        db.query(MemoryReconstruction)
        .filter(MemoryReconstruction.patient_id == current_user["id"])
        .all()
    )

    # Convert to expected format
    saved_art_searches = [
        {
            "_id": art_exp.id,
            "text": art_exp.story_generated,
            "selectedImagesByDataset": {},  # TODO: populate from Images relationship
            "dateAdded": art_exp.created_at,
        }
        for art_exp in art_explorations
    ]

    saved_story_generations = [
        {
            "_id": memory_rec.id,
            "generatedStory": memory_rec.story,
            "selectedImages": [],  # TODO: populate from Sections relationship
            "dateAdded": memory_rec.created_at,
        }
        for memory_rec in memory_reconstructions
    ]

    return {
        "savedArtSearches": saved_art_searches,
        "savedStoryGenerations": saved_story_generations,
    }


@router.delete("/delete-generation/{generation_id}")
async def delete_story_generation(
    generation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        memory_reconstruction = (
            db.query(MemoryReconstruction)
            .filter(
                MemoryReconstruction.id == generation_id,
                MemoryReconstruction.patient_id == current_user["id"],
            )
            .first()
        )

        if not memory_reconstruction:
            raise HTTPException(status_code=404, detail="Generation not found")

        db.delete(memory_reconstruction)
        db.commit()
        return {"message": "Generation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.delete("/delete-art-search/{search_id}")
async def delete_art_search(
    search_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        art_exploration = (
            db.query(ArtExploration)
            .filter(
                ArtExploration.id == search_id,
                ArtExploration.patient_id == current_user["id"],
            )
            .first()
        )

        if not art_exploration:
            raise HTTPException(status_code=404, detail="Art search not found")

        db.delete(art_exploration)
        db.commit()
        return {"message": "Art search deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
