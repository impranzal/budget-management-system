from typing import Dict

# Define keyword-category mapping
KEYWORD_CATEGORY_MAP: Dict[str, str] = {
    'uber': 'Transport',
    'taxi': 'Transport',
    'bus': 'Transport',
    'train': 'Transport',
    'pizza': 'Food',
    'restaurant': 'Food',
    'grocery': 'Food',
    'salary': 'Salary',
    'freelance': 'Freelance',
    'rent': 'Rent',
    'movie': 'Entertainment',
    'netflix': 'Entertainment',
    'electricity': 'Utilities',
    'water': 'Utilities',
    'internet': 'Utilities',
    'shopping': 'Shopping',
    'clothes': 'Shopping',
    'gift': 'Gifts',
    'medical': 'Health',
    'doctor': 'Health',
    'pharmacy': 'Health',
    # Add more as needed
}

def auto_tag_category(description: str) -> str:
    """
    Suggest a category based on keywords in the description.
    Returns 'Other' if no keyword matches.
    """
    desc = description.lower()
    for keyword, category in KEYWORD_CATEGORY_MAP.items():
        if keyword in desc:
            return category
    return 'Other' 