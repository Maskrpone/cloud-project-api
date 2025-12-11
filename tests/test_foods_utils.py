import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock

from app.utils import (
    valid_category,
    validate_params,
    map_categories,
    get_top_foods_by_category,
)


class MockFood:
    nom = "nom"
    categorie = "categorie"

    proteine = 1
    phosphore = 1


@pytest.mark.parametrize(
    "category, keyword, expected",
    [
        # Catégories à exclure
        ("Lait et Boissons au lait", "Lait", False),
        ("Desserts et sucreries", "Desserts", False),
        ("Bonbons à la menthe", "Bonbons", False),
        # Exclure "Fruits de mer" de la catégories "Fruits"
        ("Fruits de mer", "Fruits", False),
        # Ne pas exclure "Frutis de mer" si la catégorie est "Poisson"
        (
            "Fruits de mer et poissons",
            "Poisson",
            True,
        ),
        # Catégories valides
        ("Légumes frais", "Légumes", True),
        ("Fruits", "Fruits", True),
    ],
)
def test_valid_category(category, keyword, expected):
    assert valid_category(category, keyword) == expected


@patch("app.utils.Food", MockFood)
def test_validate_params_success():
    try:
        validate_params("proteine", 0.5)
    except HTTPException:
        pytest.fail("validate_params raised HTTPException on a valid input")


@pytest.mark.parametrize("percentage", [0.0, 1.1, -0.1])
@patch("app.utils.Food", MockFood)
def test_validate_params_percentage_fail(percentage):
    with pytest.raises(HTTPException) as exc_info:
        validate_params("proteine", percentage)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Percentage must be between 0.0 and 1.0."


@patch("app.utils.Food", MockFood)
def test_validate_params_nutrient_fail():
    with pytest.raises(HTTPException) as exc_info:
        validate_params("foo", 0.5)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Nutrient foo not found."


@pytest.fixture
def mock_session_map():
    session = MagicMock()

    db_categories = [
        "Fruits frais",
        "Fruits de mer",
        "Légumes cuits",
        "Boissons sucrées",
    ]

    session.exec().all.return_value = db_categories
    return session


def test_map_categories(mock_session_map):
    keyword = ["Fruits", "Légumes"]

    expected_mapping = {"Fruits": ["Fruits frais"], "Légumes": ["Légumes cuits"]}

    mapping = map_categories(mock_session_map, keyword)
    assert mapping == expected_mapping


@pytest.fixture
def mock_session_query():
    session = MagicMock()
    session.exec.return_value.one.return_value = 10
    session.exec.return_value.all.return_value = ["Steak", "Poulet"]


@patch("app.utils.Food", MockFood)
@patch("app.utils.select", MagicMock)
@patch("app.utils.func", MagicMock)
def test_get_top_foods_by_category(mock_session_query):
    category = ["Viande"]
    percentage = 0.2
    nutrient = "proteine"

    results = get_top_foods_by_category(
        mock_session_query, category, percentage, nutrient
    )
    assert results == ["Steak", "Poulet"]

    count_call_count = mock_session_query.exec.call_count
    assert count_call_count >= 1
    assert mock_session_query.exec.call_count >= 2
