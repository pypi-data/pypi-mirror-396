from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from typing import Literal

import hakushin  # noqa: TC002
import pydantic

from .original import Character, OriginalGuide, Team, TeamMember, TeamSection, WeaponSection

__all__ = (
    "ParsedCharacter",
    "ParsedGuide",
    "ParsedTeam",
    "ParsedTeamMember",
    "ParsedTeamSection",
    "ParsedWeaponSection",
)


class ParsedCharacter(Character):
    id: int
    element: hakushin.ZZZElement | None
    specialty: hakushin.ZZZSpecialty


class ParsedWeaponSection(WeaponSection):
    id: int
    rarity: Literal["S", "A", "B"]
    specialty: hakushin.ZZZSpecialty
    icon: str


class ParsedTeamMember(TeamMember):
    ids: list[int]
    icons: list[str]


class ParsedTeam(Team):
    characters: list[ParsedTeamMember]


class ParsedTeamSection(TeamSection):
    teams: list[ParsedTeam] = pydantic.Field(default_factory=list)


class ParsedGuide(OriginalGuide):
    character: ParsedCharacter
    weapons: Sequence[ParsedWeaponSection | WeaponSection] = pydantic.Field(default_factory=list)
    team: ParsedTeamSection | None = None
