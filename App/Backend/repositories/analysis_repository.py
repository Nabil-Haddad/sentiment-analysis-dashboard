from sqlalchemy.orm import Session

from models.analysis import AnalysisDB, AspectAnalysisDB, WithoutAspectAnalysisDB


def save_analysis_results(db: Session, results: dict, user_id: int) -> int:
    new_analysis = AnalysisDB(user_id=user_id)

    db.add(new_analysis)
    db.flush()

    for result in results["aspect_analysis"]:
        db_result = AspectAnalysisDB(
            phrase=result["phrase"],
            aspect=result["aspect"],
            label=result["label"],
            score=result["score"],
            analysis_id=new_analysis.analysis_id,
        )
        db.add(db_result)

    for result in results["without_aspect_analysis"]:
        db_result = WithoutAspectAnalysisDB(
            phrase=result["phrase"],
            label=result["label"],
            score=result["score"],
            analysis_id=new_analysis.analysis_id,
        )
        db.add(db_result)

    db.commit()
    db.refresh(new_analysis)

    return new_analysis.analysis_id


def get_all_analyses(db: Session, user_id: int):
    return db.query(AnalysisDB).filter(
        AnalysisDB.user_id == user_id
    ).order_by(AnalysisDB.created_at.desc()).all()


def get_all_analyses_with_results(db: Session, user_id: int):
    return db.query(AnalysisDB).filter(
        AnalysisDB.user_id == user_id
    ).order_by(AnalysisDB.created_at.desc()).all()



def get_analysis_single_result(analysis_id: int, db: Session, user_id: int):
    return db.query(AnalysisDB).filter(
        AnalysisDB.user_id == user_id,
        AnalysisDB.analysis_id == analysis_id
    ).first()


def get_analysis_by_id(db: Session, analysis_id: int, user_id: int):
    return db.query(AnalysisDB).filter(
        AnalysisDB.analysis_id == analysis_id,
        AnalysisDB.user_id == user_id
    ).first()


def delete_analysis_by_id(db: Session, analysis_id: int, user_id: int) -> bool:
    analysis = get_analysis_by_id(db, analysis_id, user_id)

    if not analysis:
        return False

    db.delete(analysis)
    db.commit()

    return True


def get_analysis_summary(db: Session, user_id: int) -> dict:
    total_analyses = db.query(AnalysisDB).filter(
        AnalysisDB.user_id == user_id
    ).count()

    total_aspect_results = db.query(AspectAnalysisDB).join(
        AnalysisDB, AspectAnalysisDB.analysis_id == AnalysisDB.analysis_id
    ).filter(AnalysisDB.user_id == user_id).count()

    total_without_aspect_results = db.query(WithoutAspectAnalysisDB).join(
        AnalysisDB, WithoutAspectAnalysisDB.analysis_id == AnalysisDB.analysis_id
    ).filter(AnalysisDB.user_id == user_id).count()

    positive_count = db.query(AspectAnalysisDB).join(
        AnalysisDB, AspectAnalysisDB.analysis_id == AnalysisDB.analysis_id
    ).filter(AnalysisDB.user_id == user_id, AspectAnalysisDB.label == "positive").count()

    negative_count = db.query(AspectAnalysisDB).join(
        AnalysisDB, AspectAnalysisDB.analysis_id == AnalysisDB.analysis_id
    ).filter(AnalysisDB.user_id == user_id, AspectAnalysisDB.label == "negative").count()

    neutral_count = db.query(AspectAnalysisDB).join(
        AnalysisDB, AspectAnalysisDB.analysis_id == AnalysisDB.analysis_id
    ).filter(AnalysisDB.user_id == user_id, AspectAnalysisDB.label == "neutral").count()

    return {
        "total_analyses": total_analyses,
        "total_aspect_results": total_aspect_results,
        "total_without_aspect_results": total_without_aspect_results,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
    }
