from fastapi import APIRouter, Depends, HTTPException, status, Request
from models import User, UserInDB, UserLogin
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from orm import Patient, ArtExploration, MemoryReconstruction, Sections, Images, get_db
import uuid


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = str(os.getenv("JWT_SECRET"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> str:
    token = (
        request.headers.get("Authorization").split(" ")[1]
        if request.headers.get("Authorization")
        else None
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("userId")
        user = db.query(Patient).filter(Patient.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user.id
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )


@router.post("/signup", response_model=UserInDB)
async def signup(user: User, db: Session = Depends(get_db)):
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


@router.post("/login", response_model=Dict)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(Patient).filter(Patient.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
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


@router.get("/profile", response_model=UserInDB)
async def get_profile(current_user: UserInDB = Depends(get_current_user)):
    return current_user


# TODO: FIX IT
@router.post("/save-story")
async def save_art_search(
    story_data: dict, current_user: str = Depends(get_current_user), db=Depends(get_db)
):
    try:
        story_text: str = story_data.get("storyText", "")
        selected_images_by_dataset: Dict[str, List[str]] = story_data.get(
            "selectedImagesByDataset", {}
        )

        if not story_text and not selected_images_by_dataset:
            raise HTTPException(
                status_code=400, detail="No story text or selected images to save."
            )

        # Create ArtExploration entry
        art_exploration = ArtExploration(
            id=str(uuid.uuid4()),
            patient_id=current_user,
            exploration_date=datetime.utcnow(),
            generated_story=story_text,
            # TODO: Map selectedImagesByDataset to proper images relationship
            # For now storing the structure as JSON in a field if needed
        )

        db.add(art_exploration)
        db.commit()

        return {"message": "Story saved successfully"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


# TODO: FIX IT
@router.post("/save-generation")
async def save_story_generation(
    story_data: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        story_text: str = story_data.get("generatedStory", "")

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


# TODO: FIX IT
@router.get("/retrieve-searches")
async def retrieve_searches(
    current_user: str = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dict[str, Optional[List[dict]]]:
    # Query ArtExploration entries
    art_searches = (
        db.query(ArtExploration).filter(ArtExploration.patient_id == current_user).all()
    )

    # Query MemoryReconstruction entries
    story_generations = (
        db.query(MemoryReconstruction)
        .filter(MemoryReconstruction.patient_id == current_user)
        .all()
    )

    # Convert to dict format similar to MongoDB structure
    saved_art_searches = [
        {
            "_id": art.id,
            "text": art.generated_story or "",
            "selectedImagesByDataset": {},  # TODO: Map from images relationship
            "dateAdded": art.exploration_date,
        }
        for art in art_searches
    ]

    saved_story_generations = [
        {
            "_id": story.id,
            "text": story.original_story or "",
            "images": [],  # TODO: Map from images relationship
            "dateAdded": story.reconstruction_date,
        }
        for story in story_generations
    ]

    return {
        "savedArtSearches": saved_art_searches,
        "savedStoryGenerations": saved_story_generations,
    }


# TODO: FIX IT
@router.delete("/delete-generation/{generation_id}")
async def delete_story_generation(
    generation_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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


# TODO: FIX IT
@router.delete("/delete-art-search/{search_id}")
async def delete_art_search(
    search_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
