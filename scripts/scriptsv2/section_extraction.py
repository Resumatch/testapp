import re

def extract_sections(text, clues):
    sections = []
    for clue in clues:
        pattern = re.compile(rf"{clue}", re.IGNORECASE)
        matches = pattern.split(text)
        for match in matches[1:]:  # Skip the text before the first match
            sections.append(match)
    return sections

# Example usage
clues = [
    "Death benefits", "Death benefit", "Lump sum",
    "Interest rate", "Rate of interest", "Lump sum payment interest",
    "Lump sum interest rate", "Death benefit interest", "Interest accrued",
    "Interest on death benefit"
]