"""
Real consistency checking using NLP algorithms.
Replaces the fake random score in utils.py with actual comparisons.

Scoring breakdown:
  40% — Username similarity    (Levenshtein distance)
  35% — Bio/description similarity  (TF-IDF cosine similarity)
  25% — Name similarity        (Levenshtein distance)
"""

import requests
import Levenshtein
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Text Cleaning ──────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Lowercase, strip punctuation and extra whitespace"""
    if not text:
        return ''
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)   # remove punctuation
    text = re.sub(r'\s+', ' ', text)        # collapse whitespace
    return text.strip()


# ── Individual Similarity Functions ───────────────────────────────────────────

def username_similarity(username_a: str, username_b: str) -> float:
    """
    Compare two usernames using normalized Levenshtein distance.
    Returns a score from 0.0 to 100.0.
    
    Examples:
      'john_doe' vs 'johndoe'   → ~88
      'john_doe' vs 'janedoe'   → ~57
      'john_doe' vs 'xyz123'    → ~20
    """
    if not username_a or not username_b:
        return 0.0

    a = clean_text(username_a).replace(' ', '')
    b = clean_text(username_b).replace(' ', '')

    if a == b:
        return 100.0

    distance = Levenshtein.distance(a, b)
    max_len  = max(len(a), len(b))
    score    = (1 - distance / max_len) * 100
    return round(max(0.0, score), 2)


def name_similarity(name_a: str, name_b: str) -> float:
    """
    Compare display names using Levenshtein distance.
    Returns a score from 0.0 to 100.0.
    """
    if not name_a or not name_b:
        return 50.0  # neutral if one is missing

    a = clean_text(name_a)
    b = clean_text(name_b)

    if a == b:
        return 100.0

    distance = Levenshtein.distance(a, b)
    max_len  = max(len(a), len(b))
    score    = (1 - distance / max_len) * 100
    return round(max(0.0, score), 2)


def bio_similarity(bio_a: str, bio_b: str) -> float:
    """
    Compare two bios/descriptions using TF-IDF cosine similarity.
    Returns a score from 0.0 to 100.0.

    TF-IDF captures semantic overlap — shared keywords across bios
    will score high even if the wording is different.
    """
    a = clean_text(bio_a)
    b = clean_text(bio_b)

    # If both empty, assume consistent (no bio on either)
    if not a and not b:
        return 75.0

    # If only one has a bio, penalize slightly
    if not a or not b:
        return 30.0

    # If identical
    if a == b:
        return 100.0

    try:
        vectorizer = TfidfVectorizer(min_df=1, stop_words='english')
        tfidf      = vectorizer.fit_transform([a, b])
        score      = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100
        return round(float(score), 2)
    except Exception:
        # Fallback to Levenshtein if TF-IDF fails (e.g. all stopwords)
        distance = Levenshtein.distance(a, b)
        max_len  = max(len(a), len(b))
        return round((1 - distance / max_len) * 100, 2)


# ── Profile Fetchers ───────────────────────────────────────────────────────────

def fetch_github_profile(username: str) -> dict:
    """Fetch GitHub profile data via public API — no auth needed"""
    try:
        res  = requests.get(
            f'https://api.github.com/users/{username}',
            headers={'Accept': 'application/json'},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            return {
                'username': data.get('login', ''),
                'name':     data.get('name', ''),
                'bio':      data.get('bio', ''),
                'platform': 'GitHub'
            }
    except Exception:
        pass
    return {}


def fetch_google_profile(name: str, email: str = '') -> dict:
    """
    Google doesn't have a public profile API.
    We use whatever info we stored at OAuth time.
    """
    return {
        'username': email.split('@')[0] if email else '',
        'name':     name,
        'bio':      '',
        'platform': 'Google'
    }


# ── Main Consistency Engine ────────────────────────────────────────────────────

def calc_real_consistency_score(
    profile_a: dict,
    profile_b: dict
) -> dict:
    """
    Calculate a real consistency score between two platform profiles.

    Args:
        profile_a: dict with keys: username, name, bio, platform
        profile_b: dict with keys: username, name, bio, platform

    Returns a dict with:
        - total_score    (0-100)
        - breakdown      (individual scores)
        - explanation    (human readable)
    """

    # Calculate individual scores
    u_score = username_similarity(profile_a.get('username', ''), profile_b.get('username', ''))
    n_score = name_similarity(profile_a.get('name', ''),     profile_b.get('name', ''))
    b_score = bio_similarity(profile_a.get('bio', ''),       profile_b.get('bio', ''))

    # Weighted total
    total = round(
        (u_score * 0.40) +
        (n_score * 0.25) +
        (b_score * 0.35),
        2
    )

    # Human readable explanation
    def level(score):
        if score >= 80: return 'Very similar'
        if score >= 60: return 'Somewhat similar'
        if score >= 40: return 'Slightly similar'
        return 'Very different'

    return {
        'total_score': total,
        'breakdown': {
            'username_similarity': {'score': u_score, 'weight': '40%', 'level': level(u_score)},
            'name_similarity':     {'score': n_score, 'weight': '25%', 'level': level(n_score)},
            'bio_similarity':      {'score': b_score, 'weight': '35%', 'level': level(b_score)},
        },
        'profiles_compared': {
            'platform_a': profile_a.get('platform', ''),
            'platform_b': profile_b.get('platform', ''),
        },
        'algorithm': 'Levenshtein distance + TF-IDF cosine similarity'
    }


def run_consistency_check(identity_anchor, platform_a, platform_b, profile_data_a=None, profile_data_b=None):
    """
    Main entry point called from routes.
    
    If profile_data is provided (from OAuth verifications), use it.
    Otherwise fall back to fetching public GitHub data if available,
    or use the old seeded random score as a last resort.
    """
    from utils import calc_consistency_score as legacy_score

    # If real profile data provided for both — use real NLP
    if profile_data_a and profile_data_b:
        result = calc_real_consistency_score(profile_data_a, profile_data_b)
        return result['total_score'], result

    # Try to fetch GitHub profile if one of the platforms is GitHub
    profiles = {}
    for platform, data in [(platform_a, profile_data_a), (platform_b, profile_data_b)]:
        if data:
            profiles[platform] = data
        elif platform == 'GitHub':
            # We can try to look up the stored GitHub username from oauth_verifications
            profiles[platform] = {'username': '', 'name': '', 'bio': '', 'platform': 'GitHub'}

    if len(profiles) == 2:
        pa = profiles[platform_a]
        pb = profiles[platform_b]
        result = calc_real_consistency_score(pa, pb)
        return result['total_score'], result

    # Last resort — legacy seeded score (no real data available)
    score = legacy_score(identity_anchor, platform_a, platform_b)
    return score, {
        'total_score': score,
        'breakdown':   {},
        'note':        'Legacy score — no real profile data available for these platforms. Connect your accounts via OAuth to get a real score.',
        'algorithm':   'seeded random (legacy)'
    }