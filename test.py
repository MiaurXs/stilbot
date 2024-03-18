import re

line = "привет 12345, как дела 67890?"
numbers = re.findall(r'\b\d+\b', line)
print(numbers)