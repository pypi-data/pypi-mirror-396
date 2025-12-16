from typing import Literal

ArgumentName = str
ArgumentType = Literal["select", "text_input"]
AdditionalInfo = list[str] | str | None

Argument = dict[
    str,
    ArgumentName | ArgumentType | AdditionalInfo,
]

TestLabel = str
TestName = str
Markers = list[str]
TestIdentifier = TestName | Markers
TestType = Literal["normal", "special"]
Arguments = list[Argument] | None

Test = dict[
    str,
    TestLabel | TestIdentifier | Arguments,
]

CategoryName = str
SubcategoryName = str

Subcategory = dict[str, SubcategoryName | list[Test]]
Category = dict[str, CategoryName | list[Subcategory]]

TestConfig = dict[str, list[Category]]
