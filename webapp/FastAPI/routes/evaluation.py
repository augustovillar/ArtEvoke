from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, time
import uuid

from orm import get_db, Evaluation, StoryOpenQuestion, ArtExploration, ChronologicalOrderQuestion
from orm.session_models import Session as SessionModel
from api_types.evaluation import (
    CreateEvaluationResponseDTO,
    SaveStoryOpenQuestionRequestDTO,
    SaveStoryOpenQuestionResponseDTO,
    GetChronologyEventsResponseDTO,
    SaveChronologicalOrderQuestionRequestDTO,
    SaveChronologicalOrderQuestionResponseDTO,
)
from utils.auth import get_current_user

router = APIRouter()


def parse_time(time_str: str) -> time:
    try:
        hours, minutes, seconds = map(int, time_str.split(":"))
        return time(hour=hours, minute=minutes, second=seconds)
    except (ValueError, AttributeError):
        return None


@router.post("/create", response_model=CreateEvaluationResponseDTO)
async def create_evaluation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.patient_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.art_exploration_id:
        mode = "art_exploration"
    elif session.memory_reconstruction_id:
        mode = "memory_reconstruction"
    else:
        raise HTTPException(
            status_code=400,
            detail="Session must have either art_exploration or memory_reconstruction linked"
        )
    
    existing_eval = db.query(Evaluation).filter(
        Evaluation.session_id == session_id
    ).first()
    
    if existing_eval:
        return CreateEvaluationResponseDTO(id=existing_eval.id)
    
    evaluation = Evaluation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        mode=mode,
        created_at=datetime.utcnow(),
    )
    
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    return CreateEvaluationResponseDTO(id=evaluation.id)


@router.post("/story-open-question", response_model=SaveStoryOpenQuestionResponseDTO)
async def save_story_open_question(
    request: SaveStoryOpenQuestionRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == request.eval_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    session = db.query(SessionModel).filter(
        SessionModel.id == evaluation.session_id
    ).first()
    
    if not session or session.patient_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to submit answers for this evaluation"
        )
    
    elapsed_time_obj = None
    if request.elapsed_time:
        elapsed_time_obj = parse_time(request.elapsed_time)
    
    question = StoryOpenQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        text=request.text,
        elapsed_time=elapsed_time_obj,
        created_at=datetime.utcnow(),
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return SaveStoryOpenQuestionResponseDTO(
        question_id=question.id
    )


@router.get("/chronology-events/{eval_id}", response_model=GetChronologyEventsResponseDTO)
async def get_chronology_events(
    eval_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == eval_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    session = db.query(SessionModel).filter(
        SessionModel.id == evaluation.session_id
    ).first()
    
    if not session or session.patient_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this evaluation"
        )
    
    if not session.art_exploration_id:
        raise HTTPException(
            status_code=400,
            detail="Session does not have an art exploration associated"
        )
    
    art_exploration = db.query(ArtExploration).filter(
        ArtExploration.id == session.art_exploration_id
    ).first()
    
    if not art_exploration:
        raise HTTPException(status_code=404, detail="Art exploration not found")
    
    events = []
    if art_exploration.correct_option_0:
        events.append(art_exploration.correct_option_0)
    if art_exploration.correct_option_1:
        events.append(art_exploration.correct_option_1)
    if art_exploration.correct_option_2:
        events.append(art_exploration.correct_option_2)
    if art_exploration.correct_option_3:
        events.append(art_exploration.correct_option_3)
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail="No chronology events found for this art exploration"
        )
    
    return GetChronologyEventsResponseDTO(events=events)


@router.post("/chronological-order-question", response_model=SaveChronologicalOrderQuestionResponseDTO)
async def save_chronological_order_question(
    request: SaveChronologicalOrderQuestionRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save chronological order question answer."""
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == request.eval_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    session = db.query(SessionModel).filter(
        SessionModel.id == evaluation.session_id
    ).first()
    
    if not session or session.patient_id != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to submit answers for this evaluation"
        )
    
    elapsed_time_obj = None
    if request.elapsed_time:
        elapsed_time_obj = parse_time(request.elapsed_time)
    
    question = ChronologicalOrderQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        selected_option_0=request.selected_option_0,
        selected_option_1=request.selected_option_1,
        selected_option_2=request.selected_option_2,
        selected_option_3=request.selected_option_3,
        elapsed_time=elapsed_time_obj,
        created_at=datetime.utcnow(),
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return SaveChronologicalOrderQuestionResponseDTO(
        question_id=question.id
    )

