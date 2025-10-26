from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, Patient, MemoryReconstruction, ArtExploration
from api_types.user import (
    User,
    UserInDB,
    UserLogin,
    LoginResponse,

    MessageResponse,
    RetrieveSearchesResponse,
)
from api_types.art import (
    SaveStoryRequest,
    SaveGenerationRequest,
)
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from datetime import datetime
from typing import Dict, List
import uuid

router = APIRouter()


@router.post("/signup")
async def signup(user: User, db: Session = Depends(get_db)) -> UserInDB:
    print(f"Attempting signup for email: {user.email}")
    existing_user = db.query(Patient).filter(Patient.email == user.email).first()
    print(f"Find one result: {existing_user}")
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)

    # Create new patient with required fields
    new_patient = Patient(
        id=str(uuid.uuid4()),
        email=user.email,
        password=hashed_password,
        name="",  # Use email as name for now
        date_of_birth=datetime(2000, 1, 1).date(),
        education_level="Not specified",
        occupation="Not specified",
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return UserInDB(
        _id=new_patient.id,
        email=new_patient.email,
        password=new_patient.password,
        savedArtSearches=[],
        savedStoryGenerations=[],
    )


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)) -> LoginResponse:
    db_user = db.query(Patient).filter(Patient.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"userId": db_user.id})
    user_return = UserInDB(
        _id=db_user.id,
        email=db_user.email,
        password=db_user.password,
        savedArtSearches=[],
        savedStoryGenerations=[],
    )

    return {"message": "Login successful", "token": access_token, "user": user_return}


@router.get("/profile")
async def get_profile(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    return current_user


@router.post("/save-story")
async def save_art_search(
    story_data: SaveStoryRequest,
    current_user: str = Depends(get_current_user),
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

        # Create ArtExploration entry
        art_exploration = ArtExploration(
            id=str(uuid.uuid4()),
            patient_id=current_user,
            story_generated=story_text,
            dataset="WikiArt",  # Default dataset - you may want to get this from request
            language="EN",  # Default language - you may want to get this from request
        )

        db.add(art_exploration)
        db.commit()
        db.refresh(art_exploration)

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
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        image_urls: List[str] = story_data.selectedImages
        story_text: str = story_data.generatedStory

        if not story_text:
            raise HTTPException(status_code=400, detail="Missing generatedStory")

        # Create MemoryReconstruction entry
        memory_reconstruction = MemoryReconstruction(
            id=str(uuid.uuid4()),
            patient_id=current_user,
            story=story_text,
            dataset="WikiArt",  # Default dataset - you may want to get this from request
            language="EN",  # Default language - you may want to get this from request
            segmentation_strategy="Conservative",  # Default strategy - you may want to get this from request
        )

        db.add(memory_reconstruction)
        db.commit()
        db.refresh(memory_reconstruction)

        # TODO: Map selectedImages to proper Sections with images relationship

        return {"message": "Generation saved successfully"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("/retrieve-searches")
async def retrieve_searches(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RetrieveSearchesResponse:
    # Get user's art explorations (saved searches)
    art_explorations = (
        db.query(ArtExploration).filter(ArtExploration.patient_id == current_user).all()
    )

    # Get user's memory reconstructions (saved generations)
    memory_reconstructions = (
        db.query(MemoryReconstruction)
        .filter(MemoryReconstruction.patient_id == current_user)
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
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        memory_reconstruction = (
            db.query(MemoryReconstruction)
            .filter(
                MemoryReconstruction.id == generation_id,
                MemoryReconstruction.patient_id == current_user,
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
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        art_exploration = (
            db.query(ArtExploration)
            .filter(
                ArtExploration.id == search_id,
                ArtExploration.patient_id == current_user,
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
