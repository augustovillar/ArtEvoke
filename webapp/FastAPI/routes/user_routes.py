from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, MemoryReconstruction, ArtExploration
from api_types.user import (
    MessageResponse,
    RetrieveSearchesResponse,
)
from utils.auth import (
    get_current_user,
)
router = APIRouter()


# @router.post("/save-story")
# async def save_art_search(
#     story_data: SaveStoryRequest,
#     current_user: str = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ) -> MessageResponse:
#     try:
#         story_text: str = story_data.storyText
#         selected_images_by_dataset: Dict[str, List[str]] = (
#             story_data.selectedImagesByDataset
#         )

#         if not story_text and not selected_images_by_dataset:
#             raise HTTPException(
#                 status_code=400, detail="No story text or selected images to save."
#             )

#         # Create ArtExploration entry
#         art_exploration = ArtExploration(
#             id=str(uuid.uuid4()),
#             patient_id=current_user,
#             story_generated=story_text,
#             dataset="WikiArt",  # Default dataset - you may want to get this from request
#             language="EN",  # Default language - you may want to get this from request
#         )

#         db.add(art_exploration)
#         db.commit()
#         db.refresh(art_exploration)

#         # TODO: Add Images records for selected_images_by_dataset
#         # This would require mapping image IDs to catalog_item IDs

#         return {"message": "Story saved successfully"}
#     except Exception as e:
#         print(e)
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Server error: {e}")


# @router.get("/retrieve-searches")
# async def retrieve_searches(
#     current_user: str = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ) -> RetrieveSearchesResponse:
#     # Get user's art explorations (saved searches)
#     art_explorations = (
#         db.query(ArtExploration).filter(ArtExploration.patient_id == current_user).all()
#     )

#     # Get user's memory reconstructions (saved generations)
#     memory_reconstructions = (
#         db.query(MemoryReconstruction)
#         .filter(MemoryReconstruction.patient_id == current_user)
#         .all()
#     )

#     # Convert to expected format
#     saved_art_searches = [
#         {
#             "_id": art_exp.id,
#             "text": art_exp.story_generated,
#             "selectedImagesByDataset": {},  # TODO: populate from Images relationship
#             "dateAdded": art_exp.created_at,
#         }
#         for art_exp in art_explorations
#     ]

#     saved_story_generations = [
#         {
#             "_id": memory_rec.id,
#             "text": memory_rec.story,
#             "images": [],  # TODO: populate from Sections relationship
#             "dateAdded": memory_rec.created_at,
#         }
#         for memory_rec in memory_reconstructions
#     ]

#     return {
#         "savedArtSearches": saved_art_searches,
#         "savedStoryGenerations": saved_story_generations,
#     }


# @router.delete("/delete-generation/{generation_id}")
# async def delete_story_generation(
#     generation_id: str,
#     current_user: str = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ) -> MessageResponse:
#     try:
#         memory_reconstruction = (
#             db.query(MemoryReconstruction)
#             .filter(
#                 MemoryReconstruction.id == generation_id,
#                 MemoryReconstruction.patient_id == current_user,
#             )
#             .first()
#         )

#         if not memory_reconstruction:
#             raise HTTPException(status_code=404, detail="Generation not found")

#         db.delete(memory_reconstruction)
#         db.commit()
#         return {"message": "Generation deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(e)
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Server error: {e}")


# @router.delete("/delete-art-search/{search_id}")
# async def delete_art_search(
#     search_id: str,
#     current_user: str = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ) -> MessageResponse:
#     try:
#         art_exploration = (
#             db.query(ArtExploration)
#             .filter(
#                 ArtExploration.id == search_id,
#                 ArtExploration.patient_id == current_user,
#             )
#             .first()
#         )

#         if not art_exploration:
#             raise HTTPException(status_code=404, detail="Art search not found")

#         db.delete(art_exploration)
#         db.commit()
#         return {"message": "Art search deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(e)
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Server error: {e}")
