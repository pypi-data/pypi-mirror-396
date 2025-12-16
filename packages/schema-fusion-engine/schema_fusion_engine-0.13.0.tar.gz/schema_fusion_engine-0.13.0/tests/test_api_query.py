"""Integration tests for query API endpoint."""

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient


class TestQueryEndpoint:
    """Test cases for POST /fusion/query endpoint."""

    def test_execute_query_success(self, client: TestClient, sample_query_result):
        """Test successful query execution."""
        columns, rows = sample_query_result

        with patch("src.api.query.trino_client") as mock_client:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [(col,) for col in columns]
            mock_cursor.fetchmany.return_value = rows
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_client.get_connection.return_value = mock_conn

            response = client.post(
                "/fusion/query",
                json={
                    "query": "SELECT * FROM postgres.public.users LIMIT 10",
                    "catalog": "postgres",
                    "schema": "public",
                    "max_rows": 100,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "SELECT * FROM postgres.public.users LIMIT 10"
            assert data["columns"] == columns
            assert data["row_count"] == len(rows)
            assert data["execution_time_ms"] is not None
            assert data["error"] is None

    def test_execute_query_with_max_rows(self, client: TestClient):
        """Test query execution respects max_rows limit."""
        columns = ["id", "name"]
        rows = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]

        with patch("src.api.query.trino_client") as mock_client:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [(col,) for col in columns]
            mock_cursor.fetchmany.return_value = rows[:2]  # Return only 2 rows
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_client.get_connection.return_value = mock_conn

            response = client.post(
                "/fusion/query",
                json={
                    "query": "SELECT * FROM test",
                    "max_rows": 2,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["row_count"] == 2
            mock_cursor.fetchmany.assert_called_once_with(2)

    def test_execute_query_error_handling(self, client: TestClient):
        """Test error handling in query execution."""
        with patch("src.api.query.trino_client") as mock_client:
            mock_conn = Mock()
            mock_conn.__enter__ = Mock(side_effect=Exception("Connection failed"))
            mock_conn.__exit__ = Mock(return_value=False)
            mock_client.get_connection.return_value = mock_conn

            response = client.post(
                "/fusion/query",
                json={
                    "query": "SELECT * FROM nonexistent",
                    "max_rows": 100,
                },
            )

            assert response.status_code == 200  # Returns 200 with error in body
            data = response.json()
            assert data["error"] is not None
            assert "Connection failed" in data["error"]
            assert data["columns"] is None
            assert data["rows"] is None
            assert data["execution_time_ms"] is not None

    def test_execute_query_without_catalog_schema(self, client: TestClient):
        """Test query execution without catalog and schema."""
        columns = ["id"]
        rows = [(1,)]

        with patch("src.api.query.trino_client") as mock_client:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [(col,) for col in columns]
            mock_cursor.fetchmany.return_value = rows
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_client.get_connection.return_value = mock_conn

            response = client.post(
                "/fusion/query",
                json={
                    "query": "SELECT 1",
                    "catalog": None,
                    "schema": None,
                    "max_rows": 100,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["error"] is None

    def test_execute_query_empty_result(self, client: TestClient):
        """Test query execution with empty result set."""
        with patch("src.api.query.trino_client") as mock_client:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [("id",)]
            mock_cursor.fetchmany.return_value = []
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_client.get_connection.return_value = mock_conn

            response = client.post(
                "/fusion/query",
                json={
                    "query": "SELECT * FROM empty_table",
                    "max_rows": 100,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["row_count"] == 0
            assert data["rows"] == []

    @patch("src.api.query.settings")
    def test_query_validation_rejects_non_select(self, mock_settings, client: TestClient):
        """Test that query validation rejects non-SELECT queries when enabled."""
        # Enable query validation
        mock_settings.query_validation_enabled = True
        mock_settings.query_require_select = True
        mock_settings.query_max_joins = None
        mock_settings.query_max_subqueries = None
        mock_settings.query_max_unions = None
        mock_settings.query_max_tables = None
        mock_settings.query_max_length = None
        mock_settings.query_timeout_enabled = False
        mock_settings.query_timeout_seconds = 300

        response = client.post(
            "/fusion/query",
            json={
                "query": "INSERT INTO users VALUES (1, 'test')",
                "max_rows": 100,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["error"] is not None
        assert "validation failed" in data["error"].lower()
        assert data["row_count"] == 0

    @patch("src.api.query.settings")
    def test_query_validation_rejects_too_many_joins(self, mock_settings, client: TestClient):
        """Test that query validation rejects queries with too many JOINs."""
        # Enable query validation with JOIN limit
        mock_settings.query_validation_enabled = True
        mock_settings.query_require_select = True
        mock_settings.query_max_joins = 2
        mock_settings.query_max_subqueries = None
        mock_settings.query_max_unions = None
        mock_settings.query_max_tables = None
        mock_settings.query_max_length = None

        # Query with 3 JOINs
        query = "SELECT * FROM a JOIN b ON a.id = b.id JOIN c ON b.id = c.id JOIN d ON c.id = d.id"

        response = client.post(
            "/fusion/query",
            json={
                "query": query,
                "max_rows": 100,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["error"] is not None
        assert "JOIN" in data["error"]
        assert data["row_count"] == 0

    @patch("src.api.query.settings")
    def test_query_validation_allows_valid_query(self, mock_settings, client: TestClient):
        """Test that query validation allows valid queries."""
        # Enable query validation
        mock_settings.query_validation_enabled = True
        mock_settings.query_require_select = True
        mock_settings.query_max_joins = 10
        mock_settings.query_max_subqueries = 5
        mock_settings.query_max_unions = 10
        mock_settings.query_max_tables = 20
        mock_settings.query_max_length = 100000
        # Disable query timeout for this test
        mock_settings.query_timeout_enabled = False
        mock_settings.query_timeout_seconds = 300

        columns = ["id"]
        rows = [(1,)]

        with patch("src.api.query.trino_client") as mock_client:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.description = [(col,) for col in columns]
            mock_cursor.fetchmany.return_value = rows
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_client.get_connection.return_value = mock_conn

            response = client.post(
                "/fusion/query",
                json={
                    "query": "SELECT * FROM users",
                    "max_rows": 100,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["error"] is None
            assert data["row_count"] == 1
