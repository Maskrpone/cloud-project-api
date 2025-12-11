def valid_category(category: str, keyword: str) -> bool:
    """
    Utility to filter out some useless categories
    """
    forbidden_keywords = ["boissons", "sucreries", "bonbons"]

    for word in forbidden_keywords:
        if word in category.lower():
            return False

    if keyword == "Fruits" and "fruits de mer" in category.lower():
        return False

    return True


def get_category_mapping(
    categories_keyword: list[str], all_categories: list[str]
) -> dict[str, list[str]]:
    """
    Utility to map category keywords to its complete names (e.g: 'viande' -> 'Viande et abats')
    @param categories_keyword: list of category keywords
    @param all_categories: complete category names queried
    """
    category_mapping = {}
    for keyword in categories_keyword:
        category_mapping[keyword] = [
            category
            for category in all_categories
            if keyword.lower() in category.lower() and valid_category(category, keyword)
        ]

    return category_mapping
