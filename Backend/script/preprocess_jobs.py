import json
import unicodedata
from pathlib import Path

import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent

RAW_DATA_CANDIDATES = [
    BACKEND_DIR / "data" / "raw" / "postings.csv",
    PROJECT_DIR / "data" / "raw" / "postings.csv",
]

OUTPUT_PATH = BACKEND_DIR / "data" / "jobs" / "jobs.json"
TEXT_COLUMNS = ["title", "company", "location", "description"]
REQUIRED_TEXT_COLUMNS = ["title", "description"]
MOJIBAKE_REPLACEMENTS = {
    "Ã¢â‚¬â„¢": "'",
    "Ã¢â‚¬Ëœ": "'",
    "Ã¢â‚¬Å“": '"',
    "Ã¢â‚¬Â": '"',
    "Ã¢â‚¬â€œ": "-",
    "Ã¢â‚¬â€": "-",
    "Ã¢â‚¬Â¢": "-",
    "Ã¢â‚¬Â¦": "...",
    "Ã‚ ": " ",
    "Ã‚": "",
    "“": '"',
    "”": '"',
    "’": "'",
    "‘": "'",
    "–": "-",
    "—": "-",
    "•": "-",
    "…": "...",
    "®": "",
}
BROKEN_TEXT_TOKENS = ("Ã", "�")


def resolve_raw_data_path() -> Path:
    for candidate in RAW_DATA_CANDIDATES:
        if candidate.exists():
            return candidate

    searched_paths = "\n".join(str(path) for path in RAW_DATA_CANDIDATES)
    raise FileNotFoundError(
        "postings.csv not found. Checked:\n"
        f"{searched_paths}"
    )


def fix_mojibake(text: str) -> str:
    suspicious_tokens = ("Ã¢", "Ã‚")
    if not any(token in text for token in suspicious_tokens):
        return text

    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def clean_text(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""

    text = fix_mojibake(text)
    for source, target in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(source, target)

    text = unicodedata.normalize("NFKC", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = " ".join(text.split())

    return text.strip()


def contains_broken_text(row: pd.Series) -> bool:
    values = (
        row["title"],
        row["company"],
        row["location"],
        row["description"],
    )
    return any(
        token in value
        for token in BROKEN_TEXT_TOKENS
        for value in values
    )


RAW_DATA_PATH = resolve_raw_data_path()

print("Loading dataset...")
df = pd.read_csv(RAW_DATA_PATH)
print(f"Original rows: {len(df)}")

print("\nColumns in dataset:")
print(df.columns.tolist())

df = df.rename(columns={"company_name": "company"})

missing_columns = [
    column for column in TEXT_COLUMNS
    if column not in df.columns
]
if missing_columns:
    raise KeyError(
        "Missing required columns after normalization: "
        f"{missing_columns}"
    )

df = df[TEXT_COLUMNS].copy()

for column in TEXT_COLUMNS:
    df[column] = df[column].apply(clean_text)

df["location"] = df["location"].replace("", "Unknown Location")

for column in REQUIRED_TEXT_COLUMNS:
    df = df[df[column] != ""]

df = df[df["company"] != ""]
df = df[~df.apply(contains_broken_text, axis=1)]
df = df.drop_duplicates(subset=["title", "company", "description"])
df = df[df["description"].str.len() > 100]

MAX_ROWS = 1000
df = df.head(MAX_ROWS)

jobs = []
for job_id, row in enumerate(df.itertuples(index=False), start=0):
    jobs.append(
        {
            "id": job_id,
            "title": row.title,
            "company": row.company,
            "location": row.location,
            "description": row.description,
        }
    )

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(jobs, file, indent=4, ensure_ascii=False)

print("\nDataset preprocessing completed.")
print(f"Clean jobs saved: {len(jobs)}")
print(f"Output path: {OUTPUT_PATH}")
