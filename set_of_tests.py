import os
import test_playwright_1, test_playwright_2

scenarios = [
    test_playwright_1
]

code_template = """
def test_{}(page):
    {}.test(page) 
"""

# Execute scenarios

for scenario in scenarios:
    if scenario:
        module_name = os.path.basename(scenario.__file__).replace(".py", "")
        code = code_template.format(module_name, module_name)
        exec(code)



