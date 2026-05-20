from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from services.inference import predict_comments
from services.aspect_service import get_user_aspects
from repositories.analysis_repository import(
     save_analysis_results, get_all_analyses,
     get_all_analyses_with_results,
     get_analysis_by_id,
     delete_analysis_by_id,
     get_analysis_summary ,
     get_analysis_single_result
)
import db.seed as seed


def analyse_and_save_comments(comments: list[str], db: Session) -> dict:
    try:
        active_aspects = get_user_aspects(db)
        results = predict_comments(comments, active_aspects)

        analysis_id = save_analysis_results(
            db=db,
            results=results,
            user_id=seed.temp_user_id
        )

        return {
            "analysis_id": analysis_id,
            "ResultsAspect": results["aspect_analysis"],
            "ResultsWithoutAspect": results["without_aspect_analysis"]
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while saving analysis results"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while processing analysis: {str(e)}"
        )


def list_analyses(db: Session):
    return get_all_analyses(db, seed.temp_user_id)


def get_single_analysis(analysis_id: int, db: Session):
    analysis = get_analysis_by_id(db, analysis_id, seed.temp_user_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis


def delete_single_analysis(analysis_id: int, db: Session):
    deleted = delete_analysis_by_id(db, analysis_id, seed.temp_user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {"message": "Analysis deleted successfully"}


def get_summary(db: Session):
    return get_analysis_summary(db, seed.temp_user_id)


def get_all_analysis(db: Session):
    return get_all_analyses_with_results(db, seed.temp_user_id)


def get_single_result(analysis_id: int, db: Session):
    result = get_analysis_single_result(analysis_id, db, seed.temp_user_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return result
