from enum import Enum

from sqlalchemy.dialects import postgresql


class DepartmentType(str, Enum):
    committee = "committee"
    initiative = "initiative"
    advisor = "advisor"


class EventType(str, Enum):
    internal = "internal"
    acm = "ACM"
    talk = "talk"
    hackathon = "hackathon"
    sdd = "SDD"
    launch = "launch"
    other = "other"


class WorkPermission(str, Enum):
    YES = "yes"
    NO = "no"
    REQUIRE_VISA = "require visa sponsorship"


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-binary"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class Tags(str, Enum):
    # placeholder to keep enum constructor from failing
    # can't find any tags in the API reference or on live events
    Investors = "Investors"


# New enums requested
class OutreachChannel(str, Enum):
    # Placeholder
    EMAIL = "email"
    LUMA = "luma"
    INSTAGRAM = "Instagram"
    LINKEDIN = "LinkedIn"
    WEBSITE = "website"
    OTHER = "other"


class DietaryPreference(str, Enum):
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    OTHER = "other"


class OrganisationEventRole(str, Enum):
    ATTENDEE = "attendee"
    SPONSOR = "sponsor"
    PARTNER = "partner"
    ECOSYSTEM_PARTNER = "ecosystem partner"
    NETWORK_PARTNER = "network partner"
    MEDIA_PARTNER = "media partner"
    TECH_PARTNER = "tech partner"
    LEGAL_PARTNER = "legal partner"


class SponsorshipType(str, Enum):
    CLUB_SPONSOR = "club sponsor"
    EVENT_SPONSOR = "event sponsor"
    IN_KIND = "in-kind sponsor"


# Helpers for Alembic migrations: a pre-configured postgresql.ENUM instance
# Use create_type=True only when creating the DB enum (initial migration).
def pg_department_enum(create_type: bool = False) -> postgresql.ENUM:
    return postgresql.ENUM(
        *(e.value for e in DepartmentType),
        name="departmenttype",
        create_type=create_type,
    )


def pg_event_enum(create_type: bool = False) -> postgresql.ENUM:
    return postgresql.ENUM(
        *(e.value for e in EventType), name="eventtype", create_type=create_type
    )


# helpers for new enums (use create_type=True in initial migrations)
def pg_outreach_channel_enum(create_type: bool = False) -> postgresql.ENUM:
    return postgresql.ENUM(
        *(e.value for e in OutreachChannel),
        name="outreachchannel",
        create_type=create_type,
    )


def pg_dietary_preference_enum(create_type: bool = False) -> postgresql.ENUM:
    return postgresql.ENUM(
        *(e.value for e in DietaryPreference),
        name="dietarypreference",
        create_type=create_type,
    )


def pg_organisation_event_role_enum(create_type: bool = False) -> postgresql.ENUM:
    return postgresql.ENUM(
        *(e.value for e in OrganisationEventRole),
        name="organisationeventrole",
        create_type=create_type,
    )


def pg_sponsorship_type_enum(create_type: bool = False) -> postgresql.ENUM:
    return postgresql.ENUM(
        *(e.value for e in SponsorshipType),
        name="sponsorshiptype",
        create_type=create_type,
    )
