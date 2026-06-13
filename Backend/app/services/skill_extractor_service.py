try:
    from Backend.data.skills import SKILLS, SKILL_NORMALIZATION_MAP
except ModuleNotFoundError:
    from data.skills import SKILLS, SKILL_NORMALIZATION_MAP

import re


def _build_skill_patterns() -> list[tuple[re.Pattern[str], str]]:
    terms_to_canonical = {
        skill: skill
        for skill in SKILLS
    }
    terms_to_canonical.update(SKILL_NORMALIZATION_MAP)

    patterns = []
    for term, canonical in terms_to_canonical.items():
        pattern = re.compile(
            rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        )
        patterns.append((pattern, canonical))

    # Match longer aliases before shorter ones to reduce partial overlaps.
    patterns.sort(key=lambda item: len(item[0].pattern), reverse=True)
    return patterns


SKILL_PATTERNS = _build_skill_patterns()


def extract_skills(text: str):
    text = text.lower()
    found_skills = set()

    for pattern, canonical_skill in SKILL_PATTERNS:
        if pattern.search(text):
            found_skills.add(canonical_skill)

    return sorted(found_skills)
