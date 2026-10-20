from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.data import DataCreate, DataUpdate, DataItem, DataSummaryResponse
from app.services.data_service import DataService

router = APIRouter()

@router.get(
    "/summary",
    response_model=DataSummaryResponse,
    summary="데이터 요약 정보 조회 (프롬프트 주입용)",
    description="기간, 총 개수, 주요 지표(합계/평균/최대/최소), 최근 트렌드를 계산하여 반환합니다."
)
def get_data_summary():
    return DataService.get_summary()

@router.get(
    "",
    response_model=List[DataItem],
    summary="데이터 목록 조회",
    description="저장된 시계열 데이터 목록을 날짜 오름차순으로 조회합니다."
)
def get_data_list(limit: Optional[int] = Query(None, description="가져올 최대 데이터 개수 (기본값: 전체)")):
    return DataService.get_all_data(limit=limit)

@router.post(
    "",
    response_model=DataItem,
    status_code=status.HTTP_201_CREATED,
    summary="새 데이터 추가",
    description="(date, value, memo) 형태의 시계열 데이터를 추가합니다."
)
def create_data(payload: DataCreate):
    return DataService.add_data(payload)

@router.put(
    "/{id}",
    response_model=DataItem,
    summary="데이터 수정",
    description="ID에 해당하는 시계열 데이터를 수정합니다."
)
def update_data(id: str, payload: DataUpdate):
    return DataService.update_data(id, payload)

@router.delete(
    "/{id}",
    summary="데이터 삭제",
    description="ID에 해당하는 시계열 데이터를 삭제합니다."
)
def delete_data(id: str):
    return DataService.delete_data(id)
