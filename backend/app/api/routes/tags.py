from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import SessionDep
from app.models import GamesPublic, GameStatus, TagsPublic
from app.serializers.game import games_public

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagsPublic)
def read_tags(session: SessionDep) -> Any:
    tags = crud.list_distinct_tags(session)
    return TagsPublic(data=tags, count=len(tags))


@router.get("/{slug}/games", response_model=GamesPublic)
def read_games_by_tag(
    session: SessionDep,
    slug: str,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
) -> Any:
    if not crud.tag_exists(session, slug):
        raise HTTPException(status_code=404, detail="Tag not found")

    games, count = crud.search_games_query(
        session=session,
        status=GameStatus.approved,
        tag_slugs=[slug],
        search=search,
        skip=skip,
        limit=limit,
    )
    return games_public(session, games, count)
