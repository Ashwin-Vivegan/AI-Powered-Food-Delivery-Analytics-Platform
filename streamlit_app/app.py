import os

import pandas as pd
import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = 90


st.set_page_config(
    page_title="Food Delivery AI Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Styling ----------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            padding: 16px;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- API helpers ----------

def post_to_api(endpoint: str, question: str) -> dict:
    """Send a question to the FastAPI backend."""
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json={"question": question},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def show_request_error(exc: Exception) -> None:
    """Display an API error without exposing sensitive details."""
    if isinstance(exc, requests.exceptions.Timeout):
        st.error(
            "The request timed out. The AI service or database "
            "may be taking too long to respond."
        )
    elif isinstance(exc, requests.exceptions.ConnectionError):
        st.error(
            "Cannot connect to FastAPI. Start the backend and "
            "verify the API URL in the sidebar."
        )
    elif isinstance(exc, requests.exceptions.HTTPError):
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else "unknown"
        )
        st.error(
            f"The API returned HTTP {status_code}. "
            "Check the backend logs for details."
        )
    else:
        st.error(
            "The request could not be completed. "
            "Check the backend logs."
        )


def check_api_health() -> bool:
    """Check whether the FastAPI service is responding."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


# ---------- Sidebar ----------

with st.sidebar:
    st.title("🍽️ Food Analytics")
    st.caption("AI-powered food delivery intelligence")

    st.divider()

    st.subheader("Backend")

    st.code(API_BASE_URL, language=None)

    if st.button("Check API connection", use_container_width=True):
        with st.spinner("Checking FastAPI..."):
            healthy = check_api_health()

        if healthy:
            st.success("FastAPI is responding.")
        else:
            st.error("FastAPI is unreachable.")

    st.divider()

    st.markdown("### Available capabilities")
    st.markdown(
        """
        - Documentation-grounded AI answers
        - Natural-language analytics queries
        - Validated SQL generation
        - Snowflake query execution
        """
    )

    st.caption("Powered by FastAPI, Groq, RAG and Snowflake.")


# ---------- Main header ----------

st.title("Food Delivery AI Analytics")
st.write(
    "Explore food popularity, restaurant performance, menu "
    "pricing and review analytics using natural language."
)

st.info(
    "Ask questions about documented metrics, or run an analytics "
    "query against the available data. Unsupported questions "
    "will be identified rather than answered with invented data."
)


# ---------- Application tabs ----------

ask_tab, query_tab = st.tabs(
    ["💬 Ask AI", "📊 Analytics Query"]
)


# ---------- Knowledge Q&A ----------

with ask_tab:
    st.subheader("Ask the analytics knowledge base")

    st.write(
        "Understand metric definitions, data availability "
        "and the platform's analytical capabilities."
    )

    with st.form("knowledge_question_form"):
        knowledge_question = st.text_area(
            "Your question",
            placeholder=(
                "Example: How is total recorded revenue calculated?"
            ),
            height=110,
            max_chars=2000,
        )

        ask_submitted = st.form_submit_button(
            "Ask AI",
            type="primary",
            use_container_width=True,
        )

    if ask_submitted:
        if not knowledge_question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner(
                    "Retrieving documentation and generating an answer..."
                ):
                    answer_response = post_to_api(
                        "/api/v1/analytics/ask",
                        knowledge_question.strip(),
                    )

                answer = answer_response.get("answer")

                if not answer:
                    st.warning("The API returned no answer.")
                else:
                    st.subheader("Answer")
                    st.markdown(answer)

            except requests.exceptions.RequestException as exc:
                show_request_error(exc)
            except (ValueError, KeyError):
                st.error("The API returned an invalid response.")


# ---------- Analytics query ----------

with query_tab:
    st.subheader("Run an analytics query")

    st.write(
        "Ask a business question. The backend plans the analysis, "
        "generates SQL, validates it and executes supported queries."
    )

    with st.form("analytics_query_form"):
        analytics_question = st.text_area(
            "Analytics question",
            placeholder=(
                "Example: Which 10 food items have the highest "
                "recorded revenue?"
            ),
            height=110,
            max_chars=2000,
        )

        query_submitted = st.form_submit_button(
            "Run analytics",
            type="primary",
            use_container_width=True,
        )

    if query_submitted:
        if not analytics_question.strip():
            st.warning("Enter an analytics question first.")
        else:
            try:
                with st.spinner(
                    "Planning, validating and running your query..."
                ):
                    result = post_to_api(
                        "/api/v1/analytics/query",
                        analytics_question.strip(),
                    )

                plan = result.get("plan") or {}
                is_supported = plan.get("is_supported", False)
                executed = result.get("executed", False)

                st.divider()
                st.subheader("Analysis result")

                if not is_supported:
                    st.warning(
                        "This question is not supported by the "
                        "currently available analytics data."
                    )

                    summary = plan.get("summary")
                    if summary:
                        st.write(summary)

                    clarification = plan.get("clarification_question")
                    if clarification:
                        st.info(clarification)

                elif not executed:
                    st.error(
                        result.get(
                            "message",
                            "The query was not executed successfully.",
                        )
                    )

                else:
                    st.success("Query validated and executed.")

                    metric1, metric2, metric3 = st.columns(3)

                    metric1.metric(
                        "Rows returned",
                        result.get("row_count", 0),
                    )

                    metric2.metric(
                        "SQL validated",
                        "Yes" if result.get("validated") else "No",
                    )

                    metric3.metric(
                        "Executed",
                        "Yes" if executed else "No",
                    )

                    rows = result.get("rows") or []
                    columns = result.get("columns") or []

                    if rows:
                        st.subheader("Results")

                        dataframe = pd.DataFrame(
                            rows,
                            columns=columns if not isinstance(rows[0], dict)
                            else None,
                        )

                        st.dataframe(
                            dataframe,
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.info("The query returned no rows.")

                    message = result.get("message")
                    if message:
                        st.caption(message)

                    sql = result.get("sql")
                    if sql:
                        with st.expander("View generated SQL"):
                            st.code(sql, language="sql")

                    with st.expander("View analytics plan"):
                        st.json(plan)

            except requests.exceptions.RequestException as exc:
                show_request_error(exc)
            except (ValueError, KeyError, TypeError):
                st.error(
                    "The API returned an unexpected response format."
                )


# ---------- Footer ----------

st.divider()

st.caption(
    "Food Delivery Analytics Platform · "
    "Streamlit frontend · FastAPI backend"
)