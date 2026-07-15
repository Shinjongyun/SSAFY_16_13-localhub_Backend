import json
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI
from openai import OpenAIError

from app.repositories.chat_repository import (
    chat_repository
)

from app.schemas.chat_schema import (
    ChatAnalysis,
    ChatData,
    ChatIntent,
    ChatPlaceItem,
    ChatResponse,
)


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")


class ChatService:

    def __init__(self):

        self.client = (
            OpenAI(
                api_key=OPENAI_API_KEY
            )
            if OPENAI_API_KEY
            else None
        )

    def chat(
        self,
        message: str,
        previous_response_id: str | None,
    ) -> ChatResponse:

        message = message.strip()

        # 클라이언트가 빈 문자열("")로 "이전 대화 없음"을 표현하는 경우가 있어
        # 여기서 한 번에 None으로 정규화한다.
        previous_response_id = previous_response_id or None

        if not message:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "질문을 입력해주세요.",
                    "data": None,
                },
            )

        analysis, analysis_response_id = self._analyze_question(
            message=message,
            previous_response_id=previous_response_id,
        )

        print(
            f"[DEBUG] intent={analysis.intent}, category={analysis.category}, "
            f"district={analysis.district}, keywords={analysis.keywords}"
        )

        # -----------------------------------
        # REGIONAL_INFO / UNKNOWN은 모델이 "JSON으로 못 푼다"고
        # 명시적으로 판단한 경우이므로 최우선으로 처리한다.
        # category가 우연히 채워져 있더라도 이 판단을 뒤집지 않는다.
        # (예: "음식점 추천해줘"는 지원 카테고리가 없어 REGIONAL_INFO여야
        #  하는데, category 우선 라우팅이 이걸 덮어써서 억지로
        #  JSON 검색으로 보내던 문제가 있었다.)
        # -----------------------------------

        if analysis.intent == ChatIntent.REGIONAL_INFO:
            return self._handle_regional_info(
                message=message,
                previous_response_id=previous_response_id,
            )

        if analysis.intent == ChatIntent.UNKNOWN:
            return self._handle_unknown()

        # -----------------------------------
        # 여기부터는 intent가 PLACE_RECOMMEND 또는 FOLLOW_UP인 경우만
        # 남는다. 이 둘 사이에서는 category 유무를 타이브레이커로 쓴다.
        #
        # 이유: 대화가 이어질수록 분류기가 새로운 카테고리 등장을
        # 놓치고 intent를 FOLLOW_UP으로 잘못 판단하는 경우가 있다
        # (예: 쇼핑 얘기하다 "관광지도 추천해줘"라고 하면 새 카테고리인데도
        #  FOLLOW_UP으로 오분류되어 JSON 재검색 없이 이전 답변을 재탕).
        # category가 채워져 있다는 것 자체를 "새로 검색이 필요한 질문"의
        # 신호로 삼아 코드 레벨에서 방어한다.
        #
        # 단, REGIONAL_INFO/UNKNOWN은 위에서 이미 걸러졌기 때문에
        # 이 분기가 "지원하지 않는 카테고리(예: 음식점)"까지
        # 억지로 PLACE_RECOMMEND로 끌고 가는 일은 없다.
        # -----------------------------------

        if analysis.category is not None:
            return self._handle_place_recommend(
                message=message,
                analysis=analysis,
                previous_response_id=previous_response_id,
            )

        return self._handle_follow_up(
            message=message,
            previous_response_id=previous_response_id,
        )

    def _get_client(self) -> OpenAI:

        if self.client is None:

            raise HTTPException(
                status_code=500,
                detail={
                    "message": "OPENAI_API_KEY가 없습니다.",
                    "data": None,
                },
            )

        return self.client

    def _analyze_question(
        self,
        message: str,
        previous_response_id: str | None,
    ) -> tuple[ChatAnalysis, str]:

        client = self._get_client()

        system_prompt = """
너는 서울 지역 정보 챗봇의 질문 분류기다.

질문을 아래 네 가지 중 하나로 분류한다.

1. PLACE_RECOMMEND

서울 지역 장소 추천 질문이며,
아래 지원 카테고리 중 하나에 해당하는 경우다.

지원 카테고리

ATTRACTION (관광지)
CULTURE (문화시설)
LEISURE (레포츠)
SHOPPING (쇼핑)
ACCOMMODATION (숙박)
FESTIVAL (축제/공연/행사)

이 경우 category는 반드시 위 카테고리 중 하나로 채운다.
카테고리를 특정할 수 있는 질문이면
이전 대화의 흐름과 무관하게 PLACE_RECOMMEND로 분류하고
category를 채운다.

2. FOLLOW_UP

이전 대화를 이어가는 질문이며,
새로운 장소 카테고리를 특정할 수 없는 경우다.

예시

그중에서
거기는?
첫 번째는?
방금 추천한 곳은?
그 장소 주소 알려줘

단, 새로운 지역이나 새로운 카테고리가 등장하면
FOLLOW_UP이 아니라 PLACE_RECOMMEND다.

3. REGIONAL_INFO

서울 지역 관련 질문이지만
JSON 검색만으로 답할 수 없는 질문이다.

지원 카테고리(ATTRACTION, CULTURE, LEISURE, SHOPPING,
ACCOMMODATION, FESTIVAL)에 해당하지 않는 장소 유형은
전부 REGIONAL_INFO로 분류하고, category는 반드시 null로 둔다.
지원 카테고리에 억지로 끼워맞추지 않는다.

예시

음식점
맛집
카페
운영시간
입장료
오늘 축제
실시간 정보

4. UNKNOWN

서울 지역과 무관한 질문이다.

예시

파이썬 코드 작성

부산 여행

미국 주식

district에는 서울 구 이름만 넣는다.

keywords 규칙:
- 사용자가 메시지에서 직접 언급한 장소명, 지명, 상호명만 넣는다.
- 사용자가 특정 장소를 언급하지 않았다면 keywords는 빈 배열로 둔다.
- 카테고리를 나타내는 일반 단어
  (관광지, 맛집, 명소, 쇼핑, 서울, 서울특별시 등)는 keywords에 넣지 않는다.
- 실제 존재 여부를 모르는 장소 이름을 추측해서 넣지 않는다.
""".strip()

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        try:

            kwargs = {
                "model": OPENAI_MODEL,
                "input": messages,
                "text_format": ChatAnalysis,
            }

            if previous_response_id:
                kwargs["previous_response_id"] = previous_response_id

            response = client.responses.parse(
                **kwargs
            )

            analysis = response.output_parsed

            if analysis is None:
                raise ValueError(
                    "분석 실패"
                )

            return analysis, response.id

        except (
            OpenAIError,
            ValueError,
        ) as error:

            raise HTTPException(
                status_code=502,
                detail={
                    "message": "질문 분석 실패",
                    "data": {
                        "reason": str(error)
                    },
                },
            ) from error

    def _handle_place_recommend(
        self,
        message: str,
        analysis: ChatAnalysis,
        previous_response_id: str | None,
    ) -> ChatResponse:

        if analysis.category is None:

            return self._handle_regional_info(
                message=message,
                previous_response_id=previous_response_id,
            )

        places = chat_repository.search_places(
            category=analysis.category,
            district=analysis.district,
            keywords=analysis.keywords,
            limit=5,
        )

        if not places:

            return self._handle_regional_info(
                message=message,
                previous_response_id=previous_response_id,
            )

        answer, response_id = self._generate_place_answer(
            user_message=message,
            places=places,
            previous_response_id=previous_response_id,
        )

        return ChatResponse(
            success=True,
            status=200,
            message="요청에 성공하였습니다.",
            data=ChatData(
                answer=answer,
                places=places,
                responseId=response_id,
            ),
        )

    def _handle_follow_up(
        self,
        message: str,
        previous_response_id: str | None,
    ) -> ChatResponse:
        client = self._get_client()

        kwargs = {
            "model": OPENAI_MODEL,
            "instructions": (
                "이전 대화를 참고하여 사용자의 후속 질문에 "
                "한국어로 간단히 답변하세요. "
                "이전 대화에 없는 정보는 추측하지 마세요."
            ),
            "input": message,
            "store": True,
        }

        if previous_response_id:
            kwargs["previous_response_id"] = previous_response_id

        try:
            response = client.responses.create(
                **kwargs
            )

            answer = response.output_text.strip()

            if not answer:
                answer = (
                    "이전 대화만으로는 해당 질문에 "
                    "답변하기 어려워요."
                )

            return ChatResponse(
                success=True,
                status=200,
                message="요청에 성공하였습니다.",
                data=ChatData(
                    answer=answer,
                    places=[],
                    responseId=response.id,
                ),
            )

        except OpenAIError as error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "후속 질문 답변 생성에 실패했습니다.",
                    "data": {
                        "reason": str(error),
                    },
                },
            ) from error

    def _handle_regional_info(
        self,
        message: str,
        previous_response_id: str | None,
    ) -> ChatResponse:
        client = self._get_client()

        input_messages = [
            {
                "role": "system",
                "content": """
너는 서울 지역 정보 챗봇이다.

웹 검색 결과를 근거로 사용자의 질문에 답변한다.

규칙:
- 서울 지역과 직접 관련된 내용만 답변한다.
- 최신 정보가 필요한 경우 웹 검색 결과를 우선한다.
- 확인되지 않은 정보는 추측하지 않는다.
- 음식점, 운영시간, 가격, 일정 등의 정보는
검색 결과에 근거하여 답변한다.
- 한국어로 간결하게 답변한다.
""".strip(),
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        kwargs = {
            "model": OPENAI_MODEL,
            "tools": [
                {
                    "type": "web_search",
                    "search_context_size": "low",
                }
            ],
            "input": input_messages,
            "store": True,
        }

        if previous_response_id:
            kwargs["previous_response_id"] = (
                previous_response_id
            )

        try:
            response = client.responses.create(
                **kwargs
            )

            answer = response.output_text.strip()

            if not answer:
                answer = (
                    "웹 검색에서 관련 정보를 "
                    "찾지 못했습니다."
                )

            return ChatResponse(
                success=True,
                status=200,
                message="요청에 성공하였습니다.",
                data=ChatData(
                    answer=answer,
                    places=[],
                    responseId=response.id,
                ),
            )

        except OpenAIError as error:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": (
                        "웹 검색 답변 생성 중 "
                        "오류가 발생했습니다."
                    ),
                    "data": {
                        "reason": str(error)
                    },
                },
            ) from error

    def _handle_unknown(
        self,
    ) -> ChatResponse:
        return ChatResponse(
            success=True,
            status=200,
            message="요청에 성공하였습니다.",
            data=ChatData(
                answer=(
                    "해당 질문에는 답변할 수 없어요. "
                    "서울 지역 장소나 관광 정보를 질문해 주세요."
                ),
                places=[],
                responseId=None,
            ),
        )

    def _generate_place_answer(
        self,
        user_message: str,
        places: list[ChatPlaceItem],
        previous_response_id: str | None,
    ) -> tuple[str, str | None]:
        client = self._get_client()

        place_data = [
            place.model_dump(mode="json")
            for place in places
        ]

        input_messages = [
            {
                "role": "system",
                "content": """
너는 서울 지역 장소 추천 챗봇이다.

제공된 JSON 검색 결과만 사용하여 답변한다.
검색 결과에 없는 내용은 추측하지 않는다.
장소 이름과 주소를 목록으로 안내한다.
""".strip(),
            },
            {
                "role": "user",
                "content": (
                    f"사용자 질문:\n{user_message}\n\n"
                    "JSON 검색 결과:\n"
                    f"{json.dumps(place_data, ensure_ascii=False)}"
                ),
            },
        ]

        kwargs = {
            "model": OPENAI_MODEL,
            "input": input_messages,
            "store": True,
        }

        if previous_response_id:
            kwargs["previous_response_id"] = (
                previous_response_id
            )

        try:
            response = client.responses.create(
                **kwargs
            )

            answer = response.output_text.strip()

            if not answer:
                answer = self._make_fallback_answer(
                    places=places
                )

            return answer, response.id

        except OpenAIError:
            return (
                self._make_fallback_answer(
                    places=places
                ),
                previous_response_id,
            )

    @staticmethod
    def _make_fallback_answer(
        places: list[ChatPlaceItem],
    ) -> str:
        lines = [
            "조건에 맞는 장소를 추천해드릴게요."
        ]

        for place in places:
            address = " ".join(
                value
                for value in [
                    place.addr1,
                    place.addr2,
                ]
                if value
            )

            if address:
                lines.append(
                    f"- {place.title}: {address}"
                )
            else:
                lines.append(
                    f"- {place.title}"
                )

        return "\n".join(lines)


chat_service = ChatService()