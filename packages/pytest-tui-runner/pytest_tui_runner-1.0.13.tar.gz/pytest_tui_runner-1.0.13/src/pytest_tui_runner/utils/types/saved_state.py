ArgumentName = str
ArgumentValue = str

TestState = bool | dict[ArgumentName, ArgumentValue]
TestValue = list[TestState]
SavedSubcat = dict[str, TestValue]
SavedCat = dict[str, SavedSubcat]

SavedState = dict[str, SavedCat]
