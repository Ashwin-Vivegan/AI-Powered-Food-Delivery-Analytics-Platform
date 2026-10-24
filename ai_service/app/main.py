
import logging
import os
from pathlib import Path

from app.schemas import TextToSQLResponse
from app.services.sql_generator import generate_safe_sql
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from app.schemas import AnalyticsQueryResponse
from app.services.sql_generator import generate_safe_sql
from app.services.snowflake_executor import execute_readonly_query

from app.schemas import AnalyticsPlan, QuestionRequest
from app.services.planner import plan_question

from app.services.knowledge_answer import answer_knowledge_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the .env file from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


app = FastAPI(
    title="AI Food Delivery Analytics API",
    description=(
        "LLM-powered question planning for food delivery analytics."
    ),
    version="0.2.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Food Delivery Analytics API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-food-delivery-analytics",
    }


@app.post(
    "/api/v1/analytics/plan",
    response_model=AnalyticsPlan,
)
def create_analytics_plan(request: QuestionRequest) -> AnalyticsPlan:
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI provider is not configured.",
        )

    try:
        return plan_question(request.question)

    except ValueError as exc:
        logger.warning("AI configuration error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="AI service configuration is incomplete.",
        ) from exc

    except Exception as exc:
        # Do not expose provider errors, prompts, or credentials
        # through the public API response.
        logger.exception("Analytics planning request failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate an analytics plan.",
        ) from exc


@app.post(
    "/api/v1/analytics/sql",
    response_model=TextToSQLResponse,
)
def create_sql_query(request: QuestionRequest) -> TextToSQLResponse:
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI provider is not configured.",
        )

    try:
        plan = plan_question(request.question)
    except Exception as exc:
        logger.exception("Question planning failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to plan this analytics question.",
        ) from exc

    if not plan.is_supported or plan.needs_clarification:
        return TextToSQLResponse(
            question=request.question,
            plan=plan,
            sql=None,
            validated=False,
            message=(
                plan.clarification_question
                or "This question is unsupported by the available data."
            ),
        )

    if len(plan.relevant_marts) != 1:
        return TextToSQLResponse(
            question=request.question,
            plan=plan,
            sql=None,
            validated=False,
            message=(
                "This version supports questions using one analytics "
                "mart. Cross-mart queries will be added later."
            ),
        )

    try:
        sql, explanation = generate_safe_sql(request.question, plan)
    except ValueError as exc:
        logger.warning("SQL generation rejected: %s", exc)
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("SQL generation or validation failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate a validated SQL query.",
        ) from exc

    return TextToSQLResponse(
        question=request.question,
        plan=plan,
        sql=sql,
        validated=True,
        message=explanation,
    )


@app.post(
    "/api/v1/analytics/query",
    response_model=AnalyticsQueryResponse,
)
def run_analytics_query(
    request: QuestionRequest,
) -> AnalyticsQueryResponse:
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI provider is not configured.",
        )

    # 1. Interpret the question.
    try:
        plan = plan_question(request.question)
    except Exception as exc:
        logger.exception("Analytics planning failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to plan the analytics question.",
        ) from exc

    # 2. Reject unsupported questions before generating SQL.
    if not plan.is_supported or plan.needs_clarification:
        return AnalyticsQueryResponse(
            question=request.question,
            plan=plan,
            sql=None,
            validated=False,
            executed=False,
            message=(
                plan.clarification_question
                or "The question is unsupported by the available data."
            ),
        )

    if len(plan.relevant_marts) != 1:
        return AnalyticsQueryResponse(
            question=request.question,
            plan=plan,
            sql=None,
            validated=False,
            executed=False,
            message=(
                "This version requires one relevant analytics mart "
                "per query."
            ),
        )

    # 3. Generate SQL and run the existing validator.
    target_mart = plan.relevant_marts[0]

    try:
        sql, explanation = generate_safe_sql(
            request.question,
            plan,
        )
    except ValueError as exc:
        logger.warning("SQL proposal rejected: %s", exc)
        raise HTTPException(
            status_code=422,
            detail="The proposed query did not pass validation.",
        ) from exc
    except Exception as exc:
        logger.exception("SQL generation failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate a safe SQL query.",
        ) from exc

    # 4. Execute only after validation, through the read-only role.
    try:
        result = execute_readonly_query(sql, target_mart)
    except (ValueError, PermissionError) as exc:
        logger.warning("Query execution rejected: %s", exc)
        raise HTTPException(
            status_code=403,
            detail="The query was rejected by the execution safeguards.",
        ) from exc
    except Exception as exc:
        logger.exception("Snowflake query execution failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to execute the analytics query.",
        ) from exc

    # 5. Return both the SQL and its actual results.
    return AnalyticsQueryResponse(
    question=request.question,
    plan=plan,
    sql=sql,
    validated=True,
    executed=True,
    columns=result["columns"],
    rows=result["rows"],
    row_count=result["row_count"],
    message=(
        f"Query returned {result['row_count']} rows. "
        "Results are limited to a maximum of 100 rows per query."
    ),
)

@app.post("/api/v1/analytics/ask")
def ask_analytics_knowledge(request: QuestionRequest):
    answer = answer_knowledge_question(request.question)

    return {
        "question": request.question,
        "answer": answer,
    }