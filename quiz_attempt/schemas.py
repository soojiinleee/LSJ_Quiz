from drf_spectacular.utils import extend_schema, extend_schema_view

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
)
QUIZ_SUBMISSION_SCHEMA_View = extend_schema_view(
    put=QUIZ_SUBMISSION_SCHEMA, patch=extend_schema(exclude=True)
)
