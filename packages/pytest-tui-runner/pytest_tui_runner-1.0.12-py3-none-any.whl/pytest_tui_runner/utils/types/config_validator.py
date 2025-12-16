from typing import Literal

from pydantic import BaseModel, model_validator
from typing_extensions import Self


class Argument(BaseModel):
    """An argument for a test, which can be either a select or a text input."""

    arg_name: str
    arg_type: Literal["select", "text_input"]
    options: list[str] | None = None
    placeholder: str | None = None

    @model_validator(mode="after")
    def check_arg_type(self) -> Self:
        """Validate that the fields are consistent with the arg_type."""
        if self.arg_type == "select":
            if not self.options:
                raise ValueError("Argument with arg_type='select' must have 'options'")
            if self.placeholder is not None:
                raise ValueError("Argument with arg_type='select' must NOT have 'placeholder'")

        if self.arg_type == "text_input":
            if not self.placeholder:
                raise ValueError("Argument with arg_type='text_input' must have 'placeholder'")
            if self.options is not None:
                raise ValueError("Argument with arg_type='text_input' must NOT have 'options'")

        return self


class Test(BaseModel):
    """A test, which can be identified either by its name or by markers."""

    label: str
    test_name: str | None = None
    markers: list[str] | None = None
    arguments: list[Argument] | None = None

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> Self:
        """Validate that exactly one of test_name or markers is provided."""
        has_test_name = self.test_name is not None
        has_markers = self.markers is not None

        if has_test_name == has_markers:  # If both are there, or neither is
            raise ValueError(
                f"Test '{self.label}' must have exactly one of 'test_name' or 'markers'",
            )
        return self


class Subcategory(BaseModel):
    """A subcategory containing multiple tests."""

    label: str
    tests: list[Test]


class Category(BaseModel):
    """A category containing multiple subcategories."""

    label: str
    subcategories: list[Subcategory]


class Config(BaseModel):
    """The root configuration model containing all categories."""

    categories: list[Category]
