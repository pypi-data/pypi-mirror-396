"""Digital employee identity classes.

This module provides identity classes for digital employees with support for
different levels of identity (base, HR, and specific implementations).

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)

References:
    NONE
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints


class LangId(StrEnum):
    """The language id.

    Attributes:
        EN: Id for English language.
        ID: Id for Indonesian language.
    """

    EN = "en"
    ID = "id"


class DigitalEmployeeJob(BaseModel):
    """Digital employee Job definition.

    Encapsulates job-specific information for a digital employee,
    including title, description, and instructions.

    Attributes:
        title (str): The job title or role name (e.g., "HR Assistant", "Payroll Specialist").
        description (str): Detailed description of the job and responsibilities.
        instruction (str): Specific instructions or guidelines for performing the job.
    """

    title: str
    description: str
    instruction: str


class DigitalEmployeeSupervisor(BaseModel):
    """Digital employee Supervisor information.

    Represents the supervisor or manager overseeing the digital employee.

    Attributes:
        name (str): The supervisor's full name.
        email (EmailStr): The supervisor's email address. Must be a valid email format.
    """

    name: str
    email: EmailStr


class DigitalEmployeeIdentity(BaseModel):
    """Base digital employee Identity.

    This is the base identity class that provides comprehensive information
    for a digital employee, including personal details, job role, and supervisor.

    Attributes:
        name (Annotated[str, StringConstraints(max_length=100)]): The name of the digital employee.
            Maximum length is 100 characters.
        email (EmailStr): The digital employee's email address. Must be a valid email format.
        job (DigitalEmployeeJob): The job information (title, description, instruction).
        supervisor (DigitalEmployeeSupervisor | None, optional): The supervisor information (name and email).
            Defaults to None.
        languages (list[LangId]): The list of supported languages for the digital employee.
            Defaults to [LangId.EN].
    """

    name: Annotated[str, StringConstraints(max_length=100)]
    email: EmailStr
    job: DigitalEmployeeJob
    supervisor: DigitalEmployeeSupervisor | None = None
    languages: list[LangId] = Field(default_factory=lambda: [LangId.EN])
