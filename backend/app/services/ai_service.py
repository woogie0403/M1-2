import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.services.data_service import DataService
from app.services.conversation_service import ConversationService

logger = logging.getLogger("uvicorn.error")

class AIService:
    @staticmethod
    def generate_system_prompt() -> str:
        """
        데이터 요약 정보(summary)와 주요 극장가 이벤트를 시스템 프롬프트에 주입(Context Injection)합니다.
        """
        summary = DataService.get_summary()
        metrics = summary.get("metrics", {})
        all_data = DataService.get_all_data()

        total_fmt = f"{metrics.get('total', 0):,.0f}"
        avg_fmt = f"{metrics.get('average', 0):,.0f}"
        max_fmt = f"{metrics.get('max', 0):,.0f}"
        min_fmt = f"{metrics.get('min', 0):,.0f}"

        # 2024 및 2025 주요 지표 추출
        items_2024 = [x for x in all_data if str(x.get("date", "")).startswith("2024")]
        items_2025 = [x for x in all_data if str(x.get("date", "")).startswith("2025")]

        max_2024 = max(items_2024, key=lambda x: x["value"]) if items_2024 else None
        min_2024 = min(items_2024, key=lambda x: x["value"]) if items_2024 else None
        max_2025 = max(items_2025, key=lambda x: x["value"]) if items_2025 else None
        min_2025 = min(items_2025, key=lambda x: x["value"]) if items_2025 else None

        info_2024_max = f"{max_2024['date']} ({max_2024['value']:,}명, {max_2024['memo']})" if max_2024 else "-"
        info_2024_min = f"{min_2024['date']} ({min_2024['value']:,}명, {min_2024['memo']})" if min_2024 else "-"
        info_2025_max = f"{max_2025['date']} ({max_2025['value']:,}명, {max_2025['memo']})" if max_2025 else "-"
        info_2025_min = f"{min_2025['date']} ({min_2025['value']:,}명, {min_2025['memo']})" if min_2025 else "-"

        prompt = f"""당신은 2024~2025 대한민국 영화 박스오피스 시계열 데이터를 분석하는 전문 AI 비서 'K-BoxOffice AI'입니다.

[사용자 데이터 요약 (전체 731일치)]
- 데이터 기간: {summary.get('period', '2024-01-01 ~ 2025-12-31')} (총 {summary.get('count', 731)}일)
- 전체 누적 관객수: {total_fmt}명
- 일일 평균 관객수: {avg_fmt}명
- 최근 2개년 트렌드: {summary.get('trend', '분석 중')}

[연도별 주요 극장가 기록]
- 2024년 최다 관객일: {info_2024_max}
- 2024년 최저 관객일: {info_2024_min}
- 2025년 최다 관객일: {info_2025_max}
- 2025년 최저 관객일: {info_2025_min}
- 대표 흥행작: 파묘(48일 1위), 베테랑2(31일 1위), 하얼빈(29일 1위), 범죄도시4(28일 1위), 인사이드 아웃 2(27일 1위)

[답변 원칙]
1. 위 데이터의 날짜, 관객수, 영화명을 정확히 인용하여 한국어로 친절하고 명쾌하게 답변하세요.
2. 불필요하게 긴 서론을 피하고 핵심 요점 위주로 간결하고 시원하게 답변하세요.
"""
        return prompt

    @staticmethod
    def chat(user_message: str, conv_id: Optional[str] = None) -> Dict[str, Any]:
        system_prompt = AIService.generate_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if conv_id:
            try:
                prev_conv = ConversationService.get_conversation_by_id(conv_id)
                for msg in prev_conv.get("messages", [])[-4:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            except Exception as e:
                logger.warning(f"이전 대화 로드 실패 ({conv_id}): {e}")

        messages.append({"role": "user", "content": user_message})

        ai_response_text = ""
        try:
            client = OpenAI(
                api_key=settings.ACTIVE_AI_KEY,
                base_url=settings.ACTIVE_BASE_URL,
                timeout=25.0
            )

            response = client.chat.completions.create(
                model=settings.ACTIVE_MODEL,
                messages=messages,
                max_tokens=400,
                temperature=0.5
            )
            ai_response_text = response.choices[0].message.content or "답변을 생성하지 못했습니다."
        except Exception as e:
            logger.error(f"AI 호출 에러: {e}")
            ai_response_text = f"죄송합니다. AI 모델 호출 중 오류가 발생했습니다: {str(e)}"

        saved_conv = ConversationService.save_chat_turn(conv_id, user_message, ai_response_text)
        actual_conv_id = saved_conv.get("id", conv_id or "default")

        return {
            "response": ai_response_text,
            "conversation_id": actual_conv_id,
            "summary_applied": True
        }
