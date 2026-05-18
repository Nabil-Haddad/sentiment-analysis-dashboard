from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class AspectAnalysis(BaseModel):
    phrase: str = Field(...,min_length=1,max_length=512,description="The phrase extracted from the original comment")
    aspect: str = Field(...,min_length=1,max_length=64,description="The detected aspect in the phrase such as design, battery, or performance")
    label: str = Field(...,min_length=1,max_length=64,description="Predicted sentiment label for the detected aspect")
    score: float = Field(...,ge=0,le=1,description="Confidence score of the sentiment prediction between 0 and 1")

    class Config:
        from_attributes = True


class WithoutAspectAnalysis(BaseModel):
    phrase: str = Field(...,min_length=1,max_length=512,description="The phrase extracted from the original comment")
    label: str = Field(...,min_length=1,max_length=64,description="Predicted sentiment label for the phrase")
    score: float = Field(...,ge=0,le=1,description="Confidence score of the sentiment prediction between 0 and 1" )

    class Config:
        from_attributes = True


class AnalysisRespond(BaseModel):
    analysis_id: int = Field(..., description="Unique ID of the created analysis")
    ResultsAspect: List[AspectAnalysis] = Field(..., description="List of phrase-level sentiment results where an aspect was detected")
    ResultsWithoutAspect: List[WithoutAspectAnalysis] = Field(..., description="List of phrase-level sentiment results where no aspect was detected")


class AnalysisWithResults(BaseModel):
    analysis_id: int = Field(..., description="Unique ID of the analysis")
    created_at: datetime = Field(..., description="When the analysis was created")
    aspect_results: List[AspectAnalysis] = Field(..., description="Results where an aspect was detected")
    without_aspect_results: List[WithoutAspectAnalysis] = Field(..., description="Results where no aspect was detected")

    class Config:
        from_attributes = True