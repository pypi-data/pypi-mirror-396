from textual.widget import Widget

TestArguments = list[Widget]

TestWidgets = list[Widget] | list[TestArguments]
SubCategoryDict = dict[str, TestWidgets]
CategoryDict = dict[str, SubCategoryDict]

WidgetsDict = dict[str, CategoryDict]
