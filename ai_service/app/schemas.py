from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


MartName = Literal[
    "mart_food_popularity",
    "mart_restaurant_performance",
    "mart_menu_pricing",
    "mart_review_analytics",
]

ColumnName = Literal[
    "food_id",
    "food_name",
    "food_category",
    "order_item_count",
    "distinct_order_count",
    "total_quantity_sold",
    "total_recorded_revenue",
    "average_unit_price",
    "restaurant_id",
    "restaurant_name",
    "city",
    "cuisine",
    "restaurant_listed_rating",
    "review_count",
    "rated_review_count",
    "average_review_rating",
    "positive_review_count",
    "low_rating_review_count",
    "neutral_rating_review_count",
    "first_review_date",
    "latest_review_date",
    "menu_price",
    "average_food_price_across_menus",
    "minimum_food_price",
    "maximum_food_price",
]


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=3, max_length=2000)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Question must contain at least 3 characters.")
        return value


class AnalyticsPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Literal[
        "food_popularity",
        "restaurant_performance",
        "menu_pricing",
        "review_analytics",
        "cross_domain",
        "unsupported",
    ]

    relevant_marts: list[MartName]
    metrics: list[ColumnName]
    dimensions: list[ColumnName]
    filters: list[str]

    is_supported: bool
    needs_clarification: bool
    clarification_question: str | None
    summary: str


class SQLProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_mart: MartName
    sql: str = Field(min_length=1, max_length=8000)
    explanation: str = Field(min_length=1, max_length=500)


class TextToSQLResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    plan: AnalyticsPlan
    sql: str | None
    validated: bool
    message: str


class AnalyticsQueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    plan: AnalyticsPlan
    sql: str | None
    validated: bool
    executed: bool
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    message: str
