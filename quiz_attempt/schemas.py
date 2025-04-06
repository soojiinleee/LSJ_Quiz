from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse
from rest_framework import status
from question.serializers import QuestionDetailWithChoicesSerializer
from .serializers import QuizSubmissionSerializer

ATTEMPT_QUIZ_CREATE_SCHEMA = extend_schema(
    tags=['퀴즈 응시'],
    summary='퀴즈 응시',
    description="""
        - 퀴즈 응시 내역 저장
        - 퀴즈 응시 시점의 문제 배치 저장
    """,
)
ATTEMPT_QUESTION_SCHEMA = extend_schema(
    tags=['퀴즈 응시'],
    summary='퀴즈 문제 풀이',
    description="""
        1. 문제 조회
        2. 문제 연관 선택지 조회
            - 선택지 순서 저장 O -> 랜덤 정렬 (is_ordered=false)
            - 선택지 순서 저장 X -> 저장된 순서 정렬 (is_ordered=true)
    """,
    parameters=[
        OpenApiParameter(
            name='question_id',
            description='문제 id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
        OpenApiParameter(
            name='quiz_id',
            description='퀴즈 id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=True,
        ),
    ],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=QuestionDetailWithChoicesSerializer(),
            description="선택지 포함한 문제 상세 내용 반환",
        )
    },
)
SAVE_CHOICE_ORDER_SCHEMA = extend_schema(
    tags=['퀴즈 응시'],
    summary='선택지 순서 저장',
    description="""
        - 퀴즈 문제 풀이 response 중 is_ordered=false 이면 해당 API 호출
    """,
)
SELECTED_CHOICE_SCHEMA = extend_schema(
    tags=['퀴즈 응시'],
    summary='문제 풀이 중 유저가 선택한 정답',
)
ATTEMPT_CHOICE_SCHEMA_View = extend_schema_view(
    post=SAVE_CHOICE_ORDER_SCHEMA,
    put=SELECTED_CHOICE_SCHEMA,
    patch=extend_schema(exclude=True),
)
QUIZ_SUBMISSION_SCHEMA = extend_schema(
    tags=['퀴즈 응시'],
    summary='퀴즈 제출',
    description="제출 시 맞춘 문제 개수 반환",
    parameters=[
        OpenApiParameter(
            name='quiz_id',
            description='퀴즈 id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=QuizSubmissionSerializer(),
            description="퀴즈 제출 결과 반환",
        )
    },
)
QUIZ_SUBMISSION_SCHEMA_View = extend_schema_view(
    put=QUIZ_SUBMISSION_SCHEMA, patch=extend_schema(exclude=True)
)
