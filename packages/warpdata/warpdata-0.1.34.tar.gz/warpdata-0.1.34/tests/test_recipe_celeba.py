"""
Tests for CelebA recipe.
"""
import pytest
from pathlib import Path
import warpdata as wd


def test_celeba_recipe_basic():
    """Test basic CelebA recipe execution with query-time filtering."""
    # Run with small limit for quick test
    result = wd.run_recipe(
        "celeba",
        "warpdata://vision/celeba-test",
        limit=50,
        add_embeddings=False,
        with_materialize=True
    )

    # Load dataset
    df = wd.load("warpdata://vision/celeba-test", as_format="pandas")

    # Verify structure
    assert len(df) == 50
    assert 'image_id' in df.columns
    assert 'image_path' in df.columns
    assert 'Male' in df.columns
    assert 'Smiling' in df.columns
    assert 'Young' in df.columns

    # Verify boolean conversion
    assert df['Male'].dtype == bool
    assert df['Smiling'].dtype == bool

    # Test query-time filtering (no physical subdatasets needed)
    males = df[df['Male']]
    assert len(males) > 0
    assert all(males['Male'])

    smiling = df[df['Smiling']]
    young_females = df[(~df['Male']) & df['Young']]


def test_celeba_recipe_query_filtering():
    """Test CelebA recipe with query-time filtering instead of subdatasets."""
    result = wd.run_recipe(
        "celeba",
        "warpdata://vision/celeba-filter",
        limit=100,
        add_embeddings=False,
        with_materialize=True
    )

    # Load main dataset
    df = wd.load("warpdata://vision/celeba-filter", as_format="pandas")
    assert len(df) == 100

    # Test query-time filtering (more efficient than physical subdatasets)
    males = df[df['Male']]
    females = df[~df['Male']]
    smiling = df[df['Smiling']]
    young_smiling_females = df[(~df['Male']) & df['Smiling'] & df['Young']]

    # Verify filtering works correctly
    assert len(males) + len(females) == len(df)
    assert all(males['Male'])
    assert all(~females['Male'])
    assert all(smiling['Smiling'])
    assert all((~young_smiling_females['Male']) & young_smiling_females['Smiling'] & young_smiling_females['Young'])


def test_celeba_attributes():
    """Test that all expected attributes are present."""
    result = wd.run_recipe(
        "celeba",
        "warpdata://vision/celeba-attrs",
        limit=20,
        create_subdatasets=False,
        add_embeddings=False,
        with_materialize=True
    )

    df = wd.load("warpdata://vision/celeba-attrs", as_format="pandas")

    # Expected attributes (subset)
    expected_attrs = [
        'Male', 'Smiling', 'Young', 'Attractive',
        'Eyeglasses', 'Wearing_Hat', 'Bald',
        'Black_Hair', 'Blond_Hair', 'Brown_Hair',
    ]

    for attr in expected_attrs:
        assert attr in df.columns, f"Missing attribute: {attr}"

    # Verify all are boolean
    for attr in expected_attrs:
        assert df[attr].dtype == bool, f"{attr} should be boolean"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
