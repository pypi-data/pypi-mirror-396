from __future__ import annotations

from enum import StrEnum
from typing import Literal

import pydantic

__all__ = (
    "Character",
    "DiscMainStatSection",
    "DiscSection",
    "DiscSetSection",
    "MindscapeSection",
    "OriginalGuide",
    "Section",
    "Skill",
    "SkillPrioritySection",
    "SkillType",
    "StatSection",
    "Team",
    "TeamMember",
    "TeamSection",
    "WeaponSection",
)


class Section(pydantic.BaseModel):
    """A section, anything can be written, like additional explanations."""

    title: str = pydantic.Field(description="Title of the section")
    description: str = pydantic.Field(description="Description of the section")


class Character(pydantic.BaseModel):
    name: str = pydantic.Field(description="Name of the character")
    rarity: Literal[4, 5] = pydantic.Field(
        description="Rarity of the character, either 4 (A-rank) or 5 (S-rank) stars."
    )

    banner: str | None = pydantic.Field(None, description="Banner image for the character")
    """A custom banner can be provided, otherwise defaults to M6 art."""


class WeaponSection(pydantic.BaseModel):
    name: str = pydantic.Field(description="Name of the weapon")
    description: str = pydantic.Field(description="Description of the weapon")

    title: str | None = pydantic.Field(
        None,
        description="Title of the section. "
        "A custom title for the section can be provided, "
        "otherwise shows the ranking of the weapon, e.g. '2nd Best W-Engine.'",
    )
    icon: str | None = pydantic.Field(
        None,
        description="Icon of the weapon. A custom icon can be provided, "
        "otherwise an icon will be fetched based on the name.",
    )


class DiscSetSection(pydantic.BaseModel):
    name: str = pydantic.Field(description="Name of the drive disc set")
    description: str = pydantic.Field(description="Description for this section")

    icon: str | None = pydantic.Field(
        None,
        description="Icon of the drive disc set. "
        "A custom icon can be provided, otherwise an icon "
        "will be fetched based on the name.",
    )


class DiscSection(pydantic.BaseModel):
    four_pieces: list[DiscSetSection] = pydantic.Field(description="List of four-piece disc sets.")
    two_pieces: list[DiscSetSection] = pydantic.Field(description="List of two-piece disc sets.")

    extra_sections: list[Section] = pydantic.Field(
        default_factory=list,
        description="Additional sections that can be added to the disc section.",
    )


class DiscMainStatSection(pydantic.BaseModel):
    stat_priority: str = pydantic.Field(
        description="Priority of the main stat for this position's disc, e.g. 'ATK > CRIT DMG > CRIT RATE'."
    )
    pos: Literal[4, 5, 6] = pydantic.Field(description="Position of the disc, either 4, 5, or 6.")


class StatSection(pydantic.BaseModel):
    main_stats: list[DiscMainStatSection] = pydantic.Field(
        description="List of main stats for each disc position (4, 5, 6)."
    )
    sub_stats: str = pydantic.Field(
        description="Priority of sub stats for the character, e.g. 'ATK > CRIT DMG > CRIT RATE > SPD'."
    )
    baseline_stats: str = pydantic.Field(
        description="Baseline stats for the character, e.g. 'ATK: 1000, DEF: 500, HP: 2000'."
    )

    extra_sections: list[Section] = pydantic.Field(
        default_factory=list,
        description="Additional sections that can be added to the stat section.",
    )


class MindscapeSection(pydantic.BaseModel):
    num: Literal[1, 2, 3, 4, 5, 6] = pydantic.Field(
        description="Number of the mindscape, from 1 to 6."
    )
    description: str = pydantic.Field(
        description="Description of the mindscape, explaining its effects and importance."
    )


class SkillType(StrEnum):
    CORE = "core"
    BASIC = "basic"
    DODGE = "dodge"
    SPECIAL = "special"
    CHAIN = "chain"
    ASSIST = "assist"


class SkillPrioritySection(pydantic.BaseModel):
    priorities: list[list[SkillType]] = pydantic.Field(
        description="List of skill priorities, where each sublist represents a priority level. "
        "For example, [[core, basic], [special, dodge]] means the first priority is core and basic skills, "
        "and the second priority is special and dodge skills."
    )
    description: str = pydantic.Field(description="Description of the skill priority section")


class TeamMember(pydantic.BaseModel):
    name: str = pydantic.Field(description="Name of the team member")


class Team(pydantic.BaseModel):
    name: str = pydantic.Field(description="Name of the team")
    characters: list[TeamMember] = pydantic.Field(description="List of characters in the team")

    description: str | None = pydantic.Field(None, description="Description of the team")


class TeamSection(pydantic.BaseModel):
    teams: list[Team] = pydantic.Field(
        default_factory=list, description="List of teams that the character can be part of."
    )
    extra_sections: list[Section] = pydantic.Field(
        default_factory=list, description="Additional sections for the team section."
    )


class Skill(pydantic.BaseModel):
    title: str = pydantic.Field(description="Title of the skill")
    description: str = pydantic.Field(description="Description of the skill")
    explanation: str = pydantic.Field(description="Explanation of the skill mechanics")

    demo: str | None = pydantic.Field(None, description="Demo GIF of the skill")


class OriginalGuide(pydantic.BaseModel):
    character: Character = pydantic.Field(description="Character information")
    description: str = pydantic.Field(
        description="Description of the guide, explaining its purpose and content."
    )

    weapons: list[WeaponSection] = pydantic.Field(
        default_factory=list, description="List of weapon sections for the character."
    )
    discs: DiscSection | None = pydantic.Field(None, description="Disc section for the character.")
    stat: StatSection | None = pydantic.Field(None, description="Stat section for the character.")
    skill_priority: SkillPrioritySection | None = pydantic.Field(
        None, description="Skill priority section for the character."
    )
    skills: list[Skill] = pydantic.Field(
        default_factory=list, description="List of skills for the character."
    )
    mindscapes: list[MindscapeSection] = pydantic.Field(
        default_factory=list, description="List of mindscapes for the character."
    )
    team: TeamSection | None = pydantic.Field(None, description="Team section for the character.")
    rotation: Section | None = pydantic.Field(
        None,
        description="Rotation section for the character, explaining how to use skills effectively.",
    )
