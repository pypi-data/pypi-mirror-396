from datetime import UTC, date, datetime
from typing import ClassVar, Optional

from sqlalchemy import JSON, ForeignKey, ForeignKeyConstraint, Index, UniqueConstraint
from sqlmodel import Column, DateTime, Field, Integer, Relationship, SQLModel, String
from sqlmodel import Enum as SQLEnum

from .enums import (
    DepartmentType,
    DietaryPreference,
    EventType,
    Gender,
    OrganisationEventRole,
    OutreachChannel,
    SponsorshipType,
    Tags,
    WorkPermission,
)


class Person(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, nullable=False))
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    birthdate: date | None = None
    github: str | None = None
    linkedin: str | None = None
    personal_website: str | None = None
    work_permission_ch: WorkPermission | None = Field(
        default=None, sa_column=Column(SQLEnum(WorkPermission))
    )
    work_permission_eu: WorkPermission | None = Field(
        default=None, sa_column=Column(SQLEnum(WorkPermission))
    )
    gender: Gender | None = Field(
        default=None, sa_column=Column(SQLEnum(Gender, name="gender_enum"))
    )
    # TODO: CV attribute

    # relationships
    # Use Optional[] instead of | None for forward references in relationships
    # SQLModel extracts the class name from the type annotation
    member: Optional["Member"] = Relationship(
        back_populates="person",
        sa_relationship_kwargs={
            "uselist": False,
            "passive_deletes": True,
        },
    )
    person_events: list["PersonEvent"] = Relationship(
        back_populates="person",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    helper_shifts: list["HelperShift"] = Relationship(
        back_populates="person",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    org_associations: list["PersonOrganisationAssociation"] = Relationship(
        back_populates="person",
        sa_relationship_kwargs={"passive_deletes": True},
    )

    __table_args__ = (
        UniqueConstraint("email", name="uq_person_email"),
        Index("ix_person_email", "email"),
    )


class StudentInfo(SQLModel, table=True):
    __tablename__: ClassVar[str] = "student_info"
    id: int | None = Field(default=None, primary_key=True)
    poa_oid: int = Field(sa_column=Column(Integer, nullable=False))
    poa_pid: int = Field(sa_column=Column(Integer, nullable=False))
    role: str | None = None
    field_of_study: str | None = None
    gpa: float | None = None
    start_date: date | None = None
    end_date: date | None = None

    person_organisation_association: "PersonOrganisationAssociation" = Relationship(
        back_populates="student_infos",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["poa_oid", "poa_pid"],
            [
                "person_organisation_association.oid",
                "person_organisation_association.pid",
            ],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        Index("ix_student_info_poa", "poa_oid", "poa_pid"),
    )


class JobInfo(SQLModel, table=True):
    __tablename__: ClassVar[str] = "job_info"
    id: int | None = Field(default=None, primary_key=True)
    poa_oid: int = Field(sa_column=Column(Integer, nullable=False))
    poa_pid: int = Field(sa_column=Column(Integer, nullable=False))
    role: str = Field(default=None)

    person_organisation_association: "PersonOrganisationAssociation" = Relationship(
        back_populates="job_infos",
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["poa_oid", "poa_pid"],
            [
                "person_organisation_association.oid",
                "person_organisation_association.pid",
            ],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        Index("ix_job_info_poa", "poa_oid", "poa_pid"),
    )


class Member(SQLModel, table=True):
    __tablename__: ClassVar[str] = "member"
    # one-to-one: Member.id references Person.id (same PK)
    # primary key must be declared on the Column when sa_column is used
    id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("person.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    ec_email: str = Field(sa_column=Column(String, nullable=False))
    google_id: str | None = None
    # add fields for permission managements / which google groups the member is in

    person: Optional["Person"] = Relationship(
        back_populates="member",
        sa_relationship_kwargs={
            "uselist": False,
            "passive_deletes": True,
        },
    )
    alumni: Optional["Alumni"] = Relationship(
        back_populates="member",
        sa_relationship_kwargs={
            "uselist": False,
        },
    )
    member_semester_infos: list["MemberSemesterInfo"] = Relationship(
        back_populates="member",
    )


class Alumni(SQLModel, table=True):
    __tablename__: ClassVar[str] = "alumni"
    id: int | None = Field(foreign_key="member.id", primary_key=True)

    member: "Member" = Relationship(
        back_populates="alumni",
    )


class MemberSemesterInfo(SQLModel, table=True):
    __tablename__: ClassVar[str] = "member_semester_info"
    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("member.id", ondelete="CASCADE", onupdate="CASCADE")
        )
    )
    role: str | None = None
    semester: str | None = None

    member: Optional["Member"] = Relationship(
        back_populates="member_semester_infos",
    )
    # The DBML had Ref: member_semester_info.id > department.id which is odd;
    # provide optional department_id
    department_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("department.id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        ),
    )
    department: Optional["Department"] = Relationship(
        back_populates="member_semester_infos",
    )


class Department(SQLModel, table=True):
    __tablename__: ClassVar[str] = "department"
    id: int | None = Field(sa_column=Column(Integer, primary_key=True))
    name: str = Field(sa_column=Column(String, nullable=False))
    type: DepartmentType = Field(
        sa_column=Column(SQLEnum(DepartmentType), nullable=False)
    )

    member_semester_infos: list["MemberSemesterInfo"] = Relationship(
        back_populates="department",
    )


class Event(SQLModel, table=True):
    __tablename__: ClassVar[str] = "event"
    id: int | None = Field(sa_column=Column(Integer, primary_key=True))
    type: EventType = Field(sa_column=Column(SQLEnum(EventType), nullable=False))
    start: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    end: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    parent_event: int | None = Field(
        default=None,
        sa_column=Column(
            ForeignKey("event.id", ondelete="SET NULL", onupdate="CASCADE")
        ),
    )
    # use JSON for portability across DB backends (SQLite in-memory tests etc.)
    # stored as a list of tag values (strings). Application can map them to Tags enum.
    tags: list[Tags] | None = Field(default=None, sa_column=Column(JSON, nullable=True))

    parent: Optional["Event"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "remote_side": "Event.id",
            "passive_deletes": True,
        },
    )
    children: list["Event"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    person_events: list["PersonEvent"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    helper_shifts: list["HelperShift"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    organisation_events: list["OrganisationEvent"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    sponsorships: list["Sponsorship"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )


class PersonOrganisationAssociation(SQLModel, table=True):
    __tablename__: ClassVar[str] = "person_organisation_association"
    oid: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("organisation.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    pid: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("person.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )

    organisation: Optional["Organisation"] = Relationship(
        back_populates="person_associations",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    person: Optional["Person"] = Relationship(
        back_populates="org_associations",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    job_infos: list["JobInfo"] = Relationship(
        back_populates="person_organisation_association",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    person_events: list["PersonEvent"] = Relationship(
        back_populates="person_organisation_association",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    student_infos: list["StudentInfo"] = Relationship(
        back_populates="person_organisation_association",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )


class PersonEvent(SQLModel, table=True):
    __tablename__: ClassVar[str] = "person_event"
    pid: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("person.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    eid: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("event.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    role: str = Field(nullable=False)
    # optional reference columns; composite FK in __table_args__ enforces relation
    poa_oid: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))
    poa_pid: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))
    outreach_channel: OutreachChannel | None = Field(
        default=None,
        sa_column=Column(SQLEnum(OutreachChannel, name="outreachchannel_enum")),
    )
    attended: bool = Field(default=True)
    has_been_at_event_before: bool | None = None
    dietary_preference: DietaryPreference | None = Field(
        default=None,
        sa_column=Column(SQLEnum(DietaryPreference, name="dietarypreference_enum")),
    )

    # Add fields for person feedback; lu.ma API currently does not provide
    # their star ratings and comments from feedback forms
    # We could create another table or unstructured documents
    # for more extensive feedback

    person: Optional["Person"] = Relationship(
        back_populates="person_events",
    )
    event: Optional["Event"] = Relationship(
        back_populates="person_events",
    )
    person_organisation_association: Optional["PersonOrganisationAssociation"] = (
        Relationship(
            back_populates="person_events",
        )
    )

    __table_args__ = (
        Index("ix_person_event_pid_eid", "pid", "eid"),
        ForeignKeyConstraint(
            ["poa_oid", "poa_pid"],
            [
                "person_organisation_association.oid",
                "person_organisation_association.pid",
            ],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )


class HelperShift(SQLModel, table=True):
    __tablename__: ClassVar[str] = "helper_shift"
    id: int | None = Field(sa_column=Column(Integer, primary_key=True))
    pid: int = Field(
        sa_column=Column(
            Integer, ForeignKey("person.id", ondelete="CASCADE", onupdate="CASCADE")
        )
    )
    eid: int = Field(
        sa_column=Column(
            Integer, ForeignKey("event.id", ondelete="CASCADE", onupdate="CASCADE")
        )
    )
    role: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    person: Optional["Person"] = Relationship(
        back_populates="helper_shifts",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    event: Optional["Event"] = Relationship(
        back_populates="helper_shifts",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )


class Organisation(SQLModel, table=True):
    __tablename__: ClassVar[str] = "organisation"
    id: int | None = Field(sa_column=Column(Integer, primary_key=True))
    name: str = Field(nullable=False)

    org_events: list["OrganisationEvent"] = Relationship(
        back_populates="organisation",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    person_associations: list["PersonOrganisationAssociation"] = Relationship(
        back_populates="organisation",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    sponsorships: list["Sponsorship"] = Relationship(
        back_populates="organisation",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )


class OrganisationEvent(SQLModel, table=True):
    __tablename__: ClassVar[str] = "organisation_event"
    oid: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("organisation.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    eid: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("event.id", ondelete="CASCADE", onupdate="CASCADE"),
            primary_key=True,
        )
    )
    role: OrganisationEventRole | None = Field(
        default=None,
        sa_column=Column(
            SQLEnum(OrganisationEventRole, name="organisationeventrole_enum")
        ),
    )

    organisation: Optional["Organisation"] = Relationship(
        back_populates="org_events",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    event: Optional["Event"] = Relationship(
        back_populates="organisation_events",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    __table_args__ = (Index("ix_organisation_event_oid_eid", "oid", "eid"),)


class Sponsorship(SQLModel, table=True):
    __tablename__: ClassVar[str] = "sponsorship"
    id: int | None = Field(sa_column=Column(Integer, primary_key=True))
    type: SponsorshipType = Field(
        sa_column=Column(
            SQLEnum(SponsorshipType, name="sponsorshiptype_enum"), nullable=False
        )
    )
    eid: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("event.id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        ),
    )
    organisation_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("organisation.id", ondelete="SET NULL", onupdate="CASCADE"),
            nullable=True,
        ),
    )

    event: Optional["Event"] = Relationship(
        back_populates="sponsorships",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    organisation: Optional["Organisation"] = Relationship(
        back_populates="sponsorships",
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
