
from app.services.retriever import retrieve_context


def test_food_popularity_retrieval():
    results = retrieve_context(
        "How is total recorded revenue calculated for food items?",
        top_k=3,
    )

    assert results
    combined = " ".join(item["content"] for item in results).lower()

    assert "mart_food_popularity" in combined
    assert "total_recorded_revenue" in combined


def test_delivery_time_limitation_retrieval():
    results = retrieve_context(
        "Which restaurants have the fastest delivery times?",
        top_k=4,
    )

    assert results
    combined = " ".join(item["content"] for item in results).lower()

    assert "delivery" in combined
    assert "unavailable" in combined or "not available" in combined


def test_retrieval_scores_are_descending():
    results = retrieve_context(
        "What does average review rating mean?",
        top_k=4,
    )

    scores = [item["score"] for item in results]
    assert scores == sorted(scores, reverse=True)


def test_empty_query_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        retrieve_context("   ")


def test_invalid_top_k_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        retrieve_context("food popularity", top_k=0)
