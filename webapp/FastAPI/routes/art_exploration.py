from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from orm import get_db, ArtExploration, Images, CatalogItem
from api_types.art_exploration import (
    SaveArtExplorationRequestDTO,
    ImagesItem,
    RetrieveArtExplorationResponseDTO,
    ArtExplorationResponse
)
from api_types.common import (
    GenerateStoryRequestDTO,
    GenerateStoryResponse,
    Dataset,
    Language,
)
from utils.auth import get_current_user
from clients import get_maritaca_client
import uuid
import os
import json
import re
from typing import List

router = APIRouter()

client = get_maritaca_client()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")


def load_prompt(language: Language) -> str:
    filename = f"story_prompt_{language.value}.md"
    filepath = os.path.join(PROMPTS_DIR, filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


@router.post("/save")
async def save_art_exploration(
    request: SaveArtExplorationRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    art_exploration = ArtExploration(
        id=str(uuid.uuid4()),
        patient_id=current_user["id"],
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_count = db.query(ArtExploration).filter(
        ArtExploration.patient_id == current_user["id"],
        ArtExploration.session_id.is_(None)
    ).count()

    art_exploration_query: List[ArtExploration] = db.query(ArtExploration).filter(
        ArtExploration.patient_id == current_user["id"],
        ArtExploration.session_id.is_(None)
    ).order_by(ArtExploration.created_at.desc()).offset(offset).limit(limit).all()

    art_explorations = []
    for ae in art_exploration_query:
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
    memory_reconstruction = db.query(ArtExploration).filter(
        ArtExploration.id == art_exploration_id,
        ArtExploration.patient_id == current_user["id"]
    ).first()

    if not memory_reconstruction:
        raise HTTPException(status_code=404, detail="Art exploration not found")

    db.query(Images).filter(
        Images.art_exploration_id == art_exploration_id
    ).delete()

    db.delete(memory_reconstruction)
    db.commit()

    return {"message": "Art exploration deleted successfully"}


@router.post("/generate-story")
async def generate_story(
    body: GenerateStoryRequestDTO, 
    db: Session = Depends(get_db)
) -> GenerateStoryResponse:
    catalog_item_ids = body.selectedImageIds
    
    catalog_items = (
        db.query(CatalogItem)
        .options(
            joinedload(CatalogItem.ipiranga),
            joinedload(CatalogItem.wikiart),
            joinedload(CatalogItem.semart),
        )
        .filter(CatalogItem.id.in_(catalog_item_ids))
        .all()
    )
    
    items_by_id = {item.id: item for item in catalog_items}
    
    art_descriptions = []
    for catalog_item_id in catalog_item_ids:
        catalog_item = items_by_id.get(catalog_item_id)
        if not catalog_item:
            print(f"[Warning] No catalog item found for ID: {catalog_item_id}")
            continue
        
        description = None
        if catalog_item.source == Dataset.semart and catalog_item.semart:
            description = catalog_item.semart.description
        elif catalog_item.source == Dataset.wikiart and catalog_item.wikiart:
            description = catalog_item.wikiart.description
        elif catalog_item.source == Dataset.ipiranga and catalog_item.ipiranga:
            description = catalog_item.ipiranga.description
        
        if description:
            art_descriptions.append(description)
        else:
            print(f"[Warning] No description found for catalog item: {catalog_item_id}")

    if not art_descriptions:
        raise HTTPException(
            status_code=400,
            detail="No descriptions found for the selected images. Cannot generate story."
        )

    messages = [
        {"role": "system", "content": load_prompt(body.language)},
        {"role": "user", "content": "\n".join(f"- {desc}" for desc in art_descriptions)}
    ]

    response = client.chat.completions.create(
        model="sabiazinho-3",
        messages=messages,
        max_tokens=1024,
        temperature=0.9,
    )

    content = response.choices[0].message.content.strip()
    
    json_str = None
    code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if code_block_match:
        json_str = code_block_match.group(1)
    else:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
    
    if not json_str:
        raise HTTPException(
            status_code=500,
            detail="The AI response does not contain valid JSON format"
        )
    
    try:
        parsed = json.loads(json_str)
        
        if 'story' in parsed and 'text' not in parsed:
            parsed['text'] = parsed.pop('story')
        
        response_data = GenerateStoryResponse(**parsed)
        
        if len(response_data.events) != 4:
            raise HTTPException(
                status_code=500,
                detail=f"Expected 4 events in the story, but got {len(response_data.events)}"
            )
        
        return response_data.model_dump()
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse the AI response as JSON"
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to validate the AI response structure"
        )
