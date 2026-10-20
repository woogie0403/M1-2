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
        데이터 요약 정보(summary)를 시스템 프롬프트에 주입(Context Injection)하여 생성합니다.
        """
        summary = DataService.get_summary()
        metrics = summary.get("metrics", {})

        total_fmt = f"{metrics.get('total', 0):,.0f}"
        avg_fmt = f"{metrics.get('average', 0):,.0f}"
        max_fmt = f"{metrics.get('max', 0):,.0f}"
        min_fmt = f"{metrics.get('min', 0):,.0f}"

        prompt = f"""당신은 2024~2025 대한민국 박스오피스 데이터를 전문적으로 분석하는 AI 비서 'K-BoxOffice AI'입니다.

[사용자 데이터 요약]
- 데이터 기간: {summary.get('period', '기간 미상')}
- 총 레코드: {summary.get('count', 0)}개 (일별 관객 및 1위 영화 데이터)
- 주요 지표:
  * 총 누적 관객수: {total_fmt}명
  * 일일 평균 관객수: {avg_fmt}명
  * 일일 최다 관객수: {max_fmt}명
  * 일일 최소 관객수: {min_fmt}명
- 최근 트렌드: {summary.get('trend', '분석 불가')}

[답변 지침]
1. 사용자의 질문에 친절하고 분석적인 어조로 답변하세요.
2. 관객 실적, 성수기/비수기, 흥행 추세에 대해 물어보면 반드시 위의 데이터 요약 수치를 구체적으로 인용하여 신뢰도 높은 답변을 제공하세요.
3. 한국어로 자연스럽고 가독성 좋게 답변하세요.
"""
        return prompt

    @staticmethod
    def chat(user_message: str, conv_id: Optional[str] = None) -> Dict[str, Any]:
        """
        1. 시스템 프롬프트(데이터 요약 주입) 구성
        2. 이전 대화 기록 로드 (멀티턴)
        3. LLM API (Gemini/OpenAI) 호출
        4. 대화 기록 자동 저장
        """
        system_prompt = AIService.generate_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 이전 대화 기록 불러오기 (최근 6개 메시지 반영)
        if conv_id:
            try:
                prev_conv = ConversationService.get_conversation_by_id(conv_id)
                hist = prev_conv.get("messages", [])
                for msg in hist[-6:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            except Exception as e:
                logger.warning(f"이전 대화 로드 실패 ({conv_id}): {e}")

        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})

        ai_response_text = ""
        try:
            client = OpenAI(
                api_key=settings.ACTIVE_AI_KEY,
                base_url=settings.ACTIVE_BASE_URL
            )

            response = client.chat.completions.create(
                model=settings.ACTIVE_MODEL,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            ai_response_text = response.choices[0].message.content or "답변을 생성하지 못했습니다."
        except Exception as e:
            logger.error(f"AI 호출 에러: {e}")
            ai_response_text = f"죄송합니다. AI 모델 호출 중 오류가 발생했습니다: {str(e)}"

        # 대화 자동 저장 (conversations 컬렉션)
        saved_conv = ConversationService.save_chat_turn(conv_id, user_message, ai_response_text)
        actual_conv_id = saved_conv.get("id", conv_id or "default")

        return {
            "response": ai_response_text,
            "conversation_id": actual_conv_id,
            "summary_applied": True
        }
