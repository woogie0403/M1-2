from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class DataCreate(BaseModel):
    date: str = Field(..., description="날짜 (YYYY-MM-DD)", example="2024-01-01")
    value: float = Field(..., description="시계열 수치 (일일 관객수/매출)", example=730970)
    memo: Optional[str] = Field(default="", description="비고/1위 영화 정보", example="1위: 노량: 죽음의 바다")

class DataUpdate(BaseModel):
    date: Optional[str] = Field(None, description="날짜 (YYYY-MM-DD)")
    value: Optional[float] = Field(None, description="시계열 수치")
    memo: Optional[str] = Field(None, description="비고/메모")

class DataItem(BaseModel):
    id: str = Field(..., description="문서 고유 ID")
    date: str
    value: float
    memo: str = ""

class SummaryMetrics(BaseModel):
    total: float
    average: float
    max: float
    min: float

class DataSummaryResponse(BaseModel):
    period: str
    count: int
    metrics: SummaryMetrics
    trend: str
