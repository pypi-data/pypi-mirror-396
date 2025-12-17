# Anki Card Cleaner

A simple Python utility to clean Anki card text, removing cloze deletions, normalizing whitespace, and handling common Anki formatting quirks.

## Installation

```bash
pip install anki-card-cleaner
```

## Usage

```python
from anki_card_cleaner import clean_card_text

text = "The capital of France is {{c1::Paris::City}}."
cleaned = clean_card_text(text)
print(cleaned)
# Output: "the capital of france is paris (city)."
```

## Features

- Removes {{c1::...}} cloze deletions.
- Handles custom Answer::Hint format in clozes.
- Normalizes unicode non-breaking spaces.
- Fixes spacing after question marks.
- Lowercases everything.
