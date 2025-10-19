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
    existing_user = await db.users.find_one({"email": user.email})
    print(f"Find one result: {existing_user}")
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    result = await db.users.insert_one(user_dict)
    new_user = await db.users.find_one({"_id": result.inserted_id})
    return UserInDB(**new_user)


@router.post("/login")
async def login(user: UserLogin, db=Depends(get_db)) -> LoginResponse:
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    cleaned_user = convert_object_ids(db_user)
    access_token = create_access_token(data={"userId": cleaned_user["_id"]})
    user_return = UserInDB(**cleaned_user)

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

        db.users.update_one(
            {"_id": current_user},
            {
                "$push": {
                    "savedStoryGenerations": {
                        "_id": ObjectId(),
                        "text": story_text,
                        "images": image_urls,
                        "dateAdded": datetime.utcnow(),
                    }
                }
            },
        )
        return {"message": "Generation saved successfully"}
    except Exception as e:
        print(e)
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
        delete_result = await db.users.update_one(
            {"_id": current_user},
            {"$pull": {"savedStoryGenerations": {"_id": ObjectId(generation_id)}}},
        )
        if delete_result.modified_count == 1:
            return {"message": "Generation deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Generation not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.delete("/delete-art-search/{search_id}")
async def delete_art_search(
    search_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> MessageResponse:
    try:
        delete_result = await db.users.update_one(
            {"_id": current_user},
            {"$pull": {"savedArtSearches": {"_id": ObjectId(search_id)}}},
        )
        if delete_result.modified_count == 1:
            return {"message": "Art search deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Art search not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
