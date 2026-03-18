"""코드 리뷰 역할(Role) 정의.

9개의 리뷰 도메인을 정의합니다.
역할은 캐릭터와 독립적이며, 어떤 캐릭터든 어떤 역할이든 수행할 수 있습니다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewRole:
    """A single code review role / domain."""

    id: str  # unique key (e.g. "security")
    name: str  # display name
    icon: str  # emoji for the role
    goal: str  # what to look for
    focus_areas: list[str]  # specific areas to review
    primary_character: str  # default Hashira ID
    secondary_character: str  # alternative Hashira ID


# ──────────────────────────────────────────────
#  9 리뷰 역할 정의
# ──────────────────────────────────────────────

SECURITY = ReviewRole(
    id="security",
    name="Security Review",
    icon="🔒",
    goal=(
        "코드 변경에서 보안 취약점, 위험한 패턴, 잠재적 공격 벡터를 찾아냅니다. "
        "OWASP Top 10, 인젝션, 인증/인가, 민감 데이터 노출, XSS, CSRF 등을 점검합니다."
    ),
    focus_areas=[
        "SQL Injection / NoSQL Injection",
        "XSS (Cross-Site Scripting)",
        "인증/인가 취약점",
        "민감 데이터 하드코딩 (API key, password)",
        "CSRF, SSRF 취약점",
        "안전하지 않은 의존성",
        "입력 검증 누락",
    ],
    primary_character="shinobu",
    secondary_character="obanai",
)

PERFORMANCE = ReviewRole(
    id="performance",
    name="Performance Review",
    icon="⚡",
    goal=(
        "코드 변경의 성능 이슈, 병목, 비효율적인 패턴을 찾아냅니다. "
        "시간/공간 복잡도, N+1 쿼리, 불필요한 연산, 메모리 누수 등을 분석합니다."
    ),
    focus_areas=[
        "시간 복잡도 (Big-O 분석)",
        "공간 복잡도 / 메모리 사용량",
        "N+1 쿼리 문제",
        "불필요한 루프 / 반복 연산",
        "캐싱 기회",
        "비동기 처리 최적화",
        "데이터베이스 인덱스 활용",
    ],
    primary_character="muichiro",
    secondary_character="giyu",
)

CODE_QUALITY = ReviewRole(
    id="code_quality",
    name="Code Quality Review",
    icon="✨",
    goal=(
        "코드의 품질, 가독성, 유지보수성을 평가합니다. "
        "SOLID 원칙, 코드 스멜, 중복 코드, 적절한 에러 핸들링 등을 점검합니다."
    ),
    focus_areas=[
        "SOLID 원칙 준수",
        "코드 중복 (DRY 원칙)",
        "함수/클래스 크기 및 책임",
        "적절한 에러 핸들링",
        "매직 넘버 / 하드코딩된 값",
        "사용하지 않는 코드 (dead code)",
        "테스트 커버리지 갭",
    ],
    primary_character="obanai",
    secondary_character="shinobu",
)

ARCHITECTURE = ReviewRole(
    id="architecture",
    name="Architecture Review",
    icon="🏛️",
    goal=(
        "아키텍처 결정, 설계 패턴, 모듈 구조, 의존성 방향을 평가합니다. "
        "변경이 전체 시스템 설계에 미치는 영향을 분석합니다."
    ),
    focus_areas=[
        "디자인 패턴 적절성",
        "모듈 간 결합도/응집도",
        "의존성 방향 (Dependency Inversion)",
        "레이어 경계 위반",
        "확장성 고려",
        "인터페이스/추상화 수준",
        "순환 참조",
    ],
    primary_character="gyomei",
    secondary_character="tengen",
)

BUG_DETECTION = ReviewRole(
    id="bug_detection",
    name="Bug Detection",
    icon="🐛",
    goal=(
        "코드 변경에서 잠재적 버그, 논리 오류, 런타임 에러 가능성을 찾아냅니다. "
        "null 참조, 오프바이원, 레이스 컨디션, 타입 에러 등을 탐지합니다."
    ),
    focus_areas=[
        "Null / undefined 참조",
        "Off-by-one 에러",
        "레이스 컨디션",
        "타입 불일치",
        "리소스 누수 (파일, 커넥션)",
        "무한 루프 가능성",
        "잘못된 조건 분기",
    ],
    primary_character="rengoku",
    secondary_character="sanemi",
)

LOGIC_FLOW = ReviewRole(
    id="logic_flow",
    name="Logic & Flow Review",
    icon="🌊",
    goal=(
        "코드의 논리적 흐름, 제어 구조, 상태 관리를 분석합니다. "
        "복잡한 조건 분기, 상태 전이, 데이터 흐름의 정확성을 검증합니다."
    ),
    focus_areas=[
        "제어 흐름 명확성",
        "조건 분기 완전성",
        "상태 관리 / 상태 전이",
        "데이터 흐름 추적",
        "Early return 패턴",
        "Guard clause 활용",
        "복잡도 감소 (Cyclomatic complexity)",
    ],
    primary_character="giyu",
    secondary_character="muichiro",
)

EDGE_CASES = ReviewRole(
    id="edge_cases",
    name="Edge Case Review",
    icon="⚔️",
    goal=(
        "경계값, 극단적 입력, 예외 상황에서 코드가 어떻게 동작하는지 분석합니다. "
        "누락된 에러 핸들링, 타임아웃, 빈 입력 처리 등을 공격적으로 탐색합니다."
    ),
    focus_areas=[
        "빈 입력 / null 입력",
        "경계값 (0, -1, MAX_INT)",
        "타임아웃 처리",
        "네트워크 실패 시나리오",
        "동시성 / 병렬 처리",
        "대용량 데이터 처리",
        "비정상 종료 시 원복",
    ],
    primary_character="sanemi",
    secondary_character="rengoku",
)

READABILITY = ReviewRole(
    id="readability",
    name="Readability & Documentation Review",
    icon="📖",
    goal=(
        "코드의 가독성, 문서화, 네이밍을 평가합니다. "
        "새로운 팀원이 이 코드를 이해할 수 있는지 관점에서 검토합니다."
    ),
    focus_areas=[
        "변수/함수/클래스 네이밍",
        "주석 적절성",
        "JSDoc / docstring",
        "README / 문서 업데이트",
        "복잡한 로직 설명",
        "코드 자체 문서화 (self-documenting code)",
        "API 문서",
    ],
    primary_character="mitsuri",
    secondary_character="gyomei",
)

STYLE_CONVENTION = ReviewRole(
    id="style",
    name="Style & Convention Review",
    icon="🎨",
    goal=(
        "코드 스타일, 포맷, 프로젝트 컨벤션 준수 여부를 평가합니다. "
        "일관성, 네이밍 규칙, 파일 구조, import 정리 등을 점검합니다."
    ),
    focus_areas=[
        "코드 포맷팅 일관성",
        "네이밍 컨벤션 (camelCase, snake_case 등)",
        "import 정렬 / 구조",
        "파일/디렉토리 구조",
        "린터 규칙 준수",
        "일관된 에러 메시지 형식",
        "일관된 API 응답 형식",
    ],
    primary_character="tengen",
    secondary_character="mitsuri",
)


# ── Role registry ──
ALL_ROLES: dict[str, ReviewRole] = {
    r.id: r
    for r in [
        SECURITY,
        PERFORMANCE,
        CODE_QUALITY,
        ARCHITECTURE,
        BUG_DETECTION,
        LOGIC_FLOW,
        EDGE_CASES,
        READABILITY,
        STYLE_CONVENTION,
    ]
}

# Default roles when no config is provided
DEFAULT_ROLE_IDS = ["security", "performance", "code_quality", "architecture", "bug_detection"]


def get_role(role_id: str) -> ReviewRole:
    """Get a review role by ID.

    Raises:
        KeyError: If the role ID is not found.
    """
    if role_id not in ALL_ROLES:
        valid = ", ".join(ALL_ROLES.keys())
        raise KeyError(f"Unknown role '{role_id}'. Valid: {valid}")
    return ALL_ROLES[role_id]
