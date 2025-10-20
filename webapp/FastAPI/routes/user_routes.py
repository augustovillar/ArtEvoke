from fastapi import APIRouter, Depends, HTTPException, status
from routes import get_db
from utils.types import (
    User,
    UserInDB,
    UserLogin,
    LoginResponse,
    SaveStoryRequest,
    SaveGenerationRequest,
    MessageResponse,
    RetrieveSearchesResponse,
)
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    convert_object_ids,
)
from datetime import datetime
from bson.objectid import ObjectId
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


@router.post("/signup")
async def signup(user: User, db=Depends(get_db)) -> UserInDB:
    print(f"Attempting signup for email: {user.email}")
    existing_user = db.query(Patient).filter(Patient.email == user.email).first()
    print(f"Find one result: {existing_user}")
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)

    # Create new patient with required fields
    new_patient = Patient(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        password=hashed_password,
        name=user.username,
        date_of_birth=datetime(2000, 1, 1).date(),
        education_level="Not specified",
        occupation="Not specified",
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return UserInDB(
        _id=new_patient.id,
        username=new_patient.username,
        email=new_patient.email,
        password=new_patient.password,
        savedArtSearches=[],
        savedStoryGenerations=[],
    )


@router.post("/login")
async def login(user: UserLogin, db=Depends(get_db)) -> LoginResponse:
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(data={"userId": db_user.id})
    user_return = UserInDB(
        _id=db_user.id,
        username=db_user.username,
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
    db=Depends(get_db),
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

        db.users.update_one(
            {"_id": current_user},
            {
                "$push": {
                    "savedArtSearches": {
                        "_id": ObjectId(),
                        "text": story_text,
                        "selectedImagesByDataset": selected_images_by_dataset,
                        "dateAdded": datetime.utcnow(),
                    }
                }
            },
        )
        return {"message": "Story saved successfully"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.post("/save-generation")
async def save_story_generation(
    story_data: SaveGenerationRequest,
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
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
            reconstruction_date=datetime.utcnow(),
            original_story=story_text,
            # TODO: Map selectedImages to proper images relationship and create Sections
        )

        db.add(memory_reconstruction)
        db.commit()

        return {"message": "Generation saved successfully"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("/retrieve-searches")
async def retrieve_searches(
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> RetrieveSearchesResponse:
    user = await db.users.find_one(
        {"_id": ObjectId(current_user)},
        {"savedArtSearches": 1, "savedStoryGenerations": 1, "_id": 1},
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    cleaned_user = convert_object_ids(user)

    return {
        "savedArtSearches": cleaned_user.get("savedArtSearches", []),
        "savedStoryGenerations": cleaned_user.get("savedStoryGenerations", []),
    }


@router.delete("/delete-generation/{generation_id}")
async def delete_story_generation(
    generation_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
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
    db: AsyncIOMotorDatabase = Depends(get_db),
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
