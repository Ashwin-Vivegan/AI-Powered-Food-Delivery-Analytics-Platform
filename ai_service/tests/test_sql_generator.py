
import pytest

from app.services.sql_generator import validate_sql


MART = "mart_food_popularity"


def test_valid_query_is_accepted():
    sql = """
        SELECT food_name, total_recorded_revenue
        FROM mart_food_popularity
        ORDER BY total_recorded_revenue DESC
        LIMIT 10
    """

    result = validate_sql(sql, MART)

    assert "MART_FOOD_POPULARITY" in result.upper()
    assert "LIMIT 10" in result.upper()


def test_missing_limit_is_capped():
    sql = """
        SELECT food_name
        FROM mart_food_popularity
    """

    result = validate_sql(sql, MART)

    assert "LIMIT 100" in result.upper()


def test_wildcard_select_is_rejected():
    sql = "SELECT * FROM mart_food_popularity LIMIT 10"

    with pytest.raises(ValueError):
        validate_sql(sql, MART)


def test_unknown_column_is_rejected():
    sql = """
        SELECT password
        FROM mart_food_popularity
        LIMIT 10
    """

    with pytest.raises(ValueError):
        validate_sql(sql, MART)


def test_unapproved_table_is_rejected():
    sql = "SELECT food_name FROM raw_users LIMIT 10"

    with pytest.raises(ValueError):
        validate_sql(sql, MART)


def test_delete_statement_is_rejected():
    sql = "DELETE FROM mart_food_popularity"

    with pytest.raises(ValueError):
        validate_sql(sql, MART)


def test_multiple_statements_are_rejected():
    sql = """
        SELECT food_name FROM mart_food_popularity LIMIT 10;
        DELETE FROM mart_food_popularity
    """

    with pytest.raises(ValueError):
        validate_sql(sql, MART)


def test_join_is_rejected():
    sql = """
        SELECT f.food_name
        FROM mart_food_popularity AS f
        JOIN mart_menu_pricing AS m ON f.food_id = m.food_id
        LIMIT 10
    """

    with pytest.raises(ValueError):
        validate_sql(sql, MART)


def test_unapproved_schema_is_rejected():
    sql = """
        SELECT food_name
        FROM OTHER_SCHEMA.mart_food_popularity
        LIMIT 10
    """

    with pytest.raises(ValueError):
        validate_sql(sql, MART)
