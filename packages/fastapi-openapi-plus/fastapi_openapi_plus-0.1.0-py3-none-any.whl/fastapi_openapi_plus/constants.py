"""Pre-built константы для стандартных параметров.

TODO: Реализовать константы:
- Path параметры: PLAYER_ID, TEAM_ID, TOURNAMENT_ID, SEASON_ID_PATH
- Query параметры (обязательные): SEASON_ID, TOURNAMENT_ID_QUERY, ROLE_ID
- Query параметры (опциональные): SEASON_ID_OPTIONAL, TOURNAMENT_ID_OPTIONAL
- Boolean параметры: INCLUDE_STATS, BY_STATISTIC
- Pagination: PAGE, PAGE_SIZE

ВАЖНО: Константы для Path должны использоваться только с тем же именем в маршруте.
Например, PLAYER_ID можно использовать только в @router.get("/{playerId}/...")

См. fastapi-openapi-plus-concept.md для детального описания.
"""

