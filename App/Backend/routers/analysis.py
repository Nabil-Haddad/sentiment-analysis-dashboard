from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from sqlalchemy.orm import Session

from db.deps import get_db
from schemas.analysis import AnalysisRespond, AnalysisWithResults
from services.analysis_service import (
    analyse_and_save_comments,
    list_analyses,
    get_single_analysis,
    delete_single_analysis,
    get_summary,
    get_all_analysis,
    get_single_result
)


router = APIRouter(
    prefix="/sentiment-analysis",
    tags=["Sentiment Analysis"]
)


@router.post("/", response_model=AnalysisRespond)
def make_analysis(comments: List[str], db: Session = Depends(get_db)):
    if not comments:
        raise HTTPException(
            status_code=400,
            detail="Comments list cannot be empty"
        )

    cleaned_comments = [comment.strip() for comment in comments if comment.strip()]

    if not cleaned_comments:
        raise HTTPException(
            status_code=400,
            detail="Comments must contain at least one non-empty text"
        )

    return analyse_and_save_comments(
        comments=cleaned_comments,
        db=db
    )


@router.get("/", )
def get_analyses(db: Session = Depends(get_db)):
    analyses = list_analyses(db)

    if not analyses:
        raise HTTPException(
            status_code=404,
            detail="No analyses found"
        )

    return analyses


@router.get("/stats/summary")
def get_stats_summary(db: Session = Depends(get_db)):
    summary = get_summary(db)

    if summary["total_analyses"] == 0:
        raise HTTPException(
            status_code=404,
            detail="No analyses found to summarize"
        )

    return summary


@router.get("/all", response_model=List[AnalysisWithResults])
def get_analysis_with_results(db: Session = Depends(get_db)):
    all_results = get_all_analysis(db)

    if not all_results:
        raise HTTPException(
            status_code=404,
            detail="No analyses found"
        )

    return all_results


# add an endpoint where we get the summary of stats of a single analysis

@router.get("/results/{analysis_id}", response_model=AnalysisWithResults)
def get_analysis_result(
    analysis_id: int = Path(gt=0, description="ID of the analysis to retrieve the results"),
    db: Session = Depends(get_db)
):
    return get_single_result(analysis_id, db)


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: int = Path(gt=0, description="ID of the analysis to retrieve"),
    db: Session = Depends(get_db)
):
    return get_single_analysis(analysis_id, db)


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int = Path(gt=0, description="ID of the analysis to delete"),
    db: Session = Depends(get_db)
):
    return delete_single_analysis(analysis_id, db)
