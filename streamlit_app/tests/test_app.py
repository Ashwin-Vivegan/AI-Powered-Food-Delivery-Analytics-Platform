
from pathlib import Path

import pytest
import requests
from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).resolve().parents[1] / "app.py"


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def run_app_question(
    monkeypatch,
    *,
    endpoint,
    question,
    payload,
    input_label,
    button_label,
):
    """Run the Streamlit app with a mocked FastAPI response."""
    monkeypatch.setenv("API_BASE_URL", "http://testserver")

    def fake_post(url, json, timeout):
        assert url.endswith(endpoint)
        assert json["question"] == question
        return FakeResponse(payload)

    monkeypatch.setattr(requests, "post", fake_post)

    app = AppTest.from_file(
        str(APP_FILE),
        default_timeout=20,
    ).run()

    assert not app.exception

    question_input = next(
        widget
        for widget in app.text_area
        if widget.label == input_label
    )
    question_input.set_value(question)

    submit_button = next(
        widget
        for widget in app.button
        if widget.label == button_label
    )
    submit_button.click()

    app.run()
    assert not app.exception

    return app


def test_streamlit_app_renders():
    app = AppTest.from_file(
        str(APP_FILE),
        default_timeout=20,
    ).run()

    assert not app.exception


def test_knowledge_question_returns_grounded_answer(monkeypatch):
    question = "How is total recorded revenue calculated?"

    payload = {
        "question": question,
        "answer": (
            "total_recorded_revenue is the sum of recorded "
            "line_amount values. It is available in "
            "mart_food_popularity and mart_restaurant_performance."
        ),
    }

    app = run_app_question(
        monkeypatch,
        endpoint="/api/v1/analytics/ask",
        question=question,
        payload=payload,
        input_label="Your question",
        button_label="Ask AI",
    )

    rendered_text = "\n".join(
        str(item.value) for item in app.markdown
    )

    assert "line_amount" in rendered_text
    assert "mart_food_popularity" in rendered_text


def test_supported_analytics_query_displays_results(monkeypatch):
    question = (
        "Which 10 food items have the highest recorded revenue?"
    )

    rows = [
        {
            "FOOD_ID": f"fd{i}",
            "FOOD_NAME": f"Food {i}",
            "TOTAL_RECORDED_REVENUE": str(10000 - i * 100),
        }
        for i in range(10)
    ]

    payload = {
        "question": question,
        "plan": {
            "intent": "food_popularity",
            "relevant_marts": ["mart_food_popularity"],
            "is_supported": True,
            "needs_clarification": False,
            "clarification_question": None,
            "summary": "Rank food items by recorded revenue.",
        },
        "sql": (
            "SELECT food_id, food_name, total_recorded_revenue "
            "FROM mart_food_popularity "
            "ORDER BY total_recorded_revenue DESC LIMIT 10"
        ),
        "validated": True,
        "executed": True,
        "columns": [
            "FOOD_ID",
            "FOOD_NAME",
            "TOTAL_RECORDED_REVENUE",
        ],
        "rows": rows,
        "row_count": 10,
        "message": (
            "Query returned 10 rows. Results are limited "
            "to a maximum of 100 rows per query."
        ),
    }

    app = run_app_question(
        monkeypatch,
        endpoint="/api/v1/analytics/query",
        question=question,
        payload=payload,
        input_label="Analytics question",
        button_label="Run analytics",
    )

    assert any(
        "Query validated and executed" in str(item.value)
        for item in app.success
    )

    assert any(
        "SELECT food_id" in str(item.value)
        for item in app.code
    )

    assert any(
        "maximum of 100 rows" in str(item.value)
        for item in app.caption
    )


def test_unsupported_question_displays_warning(monkeypatch):
    question = "Which restaurants have the fastest delivery times?"

    payload = {
        "question": question,
        "plan": {
            "intent": "unsupported",
            "relevant_marts": [],
            "is_supported": False,
            "needs_clarification": False,
            "clarification_question": None,
            "summary": (
                "Delivery-time data is unavailable in the marts."
            ),
        },
        "sql": None,
        "validated": False,
        "executed": False,
        "columns": [],
        "rows": [],
        "row_count": 0,
        "message": (
            "The question is unsupported by the available data."
        ),
    }

    app = run_app_question(
        monkeypatch,
        endpoint="/api/v1/analytics/query",
        question=question,
        payload=payload,
        input_label="Analytics question",
        button_label="Run analytics",
    )

    assert any(
        "not supported" in str(item.value).lower()
        for item in app.warning
    )

    assert not any(
        "Query validated and executed" in str(item.value)
        for item in app.success
    )


def test_city_rating_query_shows_result_limit(monkeypatch):
    question = (
        "Show the average review rating for restaurants in each city."
    )

    rows = [
        {
            "CITY": f"City {i:03d}",
            "AVG_REVIEW_RATING": "3.75",
        }
        for i in range(100)
    ]

    payload = {
        "question": question,
        "plan": {
            "intent": "review_analytics",
            "relevant_marts": ["mart_review_analytics"],
            "is_supported": True,
            "needs_clarification": False,
            "clarification_question": None,
            "summary": "Average review rating per city.",
        },
        "sql": (
            "SELECT city, AVG(average_review_rating) "
            "AS avg_review_rating "
            "FROM mart_review_analytics "
            "GROUP BY city ORDER BY city ASC LIMIT 100"
        ),
        "validated": True,
        "executed": True,
        "columns": ["CITY", "AVG_REVIEW_RATING"],
        "rows": rows,
        "row_count": 100,
        "message": (
            "Query returned 100 rows. Results are limited "
            "to a maximum of 100 rows per query."
        ),
    }

    app = run_app_question(
        monkeypatch,
        endpoint="/api/v1/analytics/query",
        question=question,
        payload=payload,
        input_label="Analytics question",
        button_label="Run analytics",
    )

    assert any(
        "maximum of 100 rows" in str(item.value)
        for item in app.caption
    )

    assert any(
        "GROUP BY city" in str(item.value)
        for item in app.code
    )
