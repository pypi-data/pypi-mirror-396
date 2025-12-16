"""Model package exports.

Explicitly export model symbols to make imports and static analysis clearer.
"""

from .models import (
    Alumni,
    Department,
    Event,
    HelperShift,
    JobInfo,
    Member,
    MemberSemesterInfo,
    Organisation,
    OrganisationEvent,
    Person,
    PersonEvent,
    PersonOrganisationAssociation,
    Sponsorship,
    StudentInfo,
)

__all__ = [
    "Person",
    "StudentInfo",
    "JobInfo",
    "Member",
    "Alumni",
    "MemberSemesterInfo",
    "Department",
    "Event",
    "PersonEvent",
    "HelperShift",
    "Organisation",
    "OrganisationEvent",
    "Sponsorship",
    "PersonOrganisationAssociation",
]
"""Expose models for the package."""

# Explicit imports above provide clear public API and satisfy linters.
