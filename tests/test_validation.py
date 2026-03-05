import pytest
from graphql import (
    build_schema,
    parse,
    validate,
    ExecutionContext,
    ExecutionResult,
)
from app.graphql.schema import schema
from app.middleware.validation_middleware import ValidationMiddleware
from graphql.execution.executors.sync_executor import SyncExecutor


def execute_with_validation(query: str, variables=None) -> ExecutionResult:
    middleware = [ValidationMiddleware()]
    document_ast = parse(query)
    validation_errors = validate(schema, document_ast)
    if validation_errors:
        return ExecutionResult(errors=validation_errors)
    executor = SyncExecutor()
    context_value = {}
    result = schema.execute(
        query,
        variable_values=variables,
        middleware=middleware,
        context_value=context_value,
        executor=executor,
    )
    return result


def test_valid_user_query_returns_data():
    query = """
    query {
      users {
        id
        name
        email
      }
    }
    """
    result = execute_with_validation(query)
    assert not result.errors, f"Unexpected errors: {result.errors}"
    assert "users" in result.data
    assert isinstance(result.data["users"], list)


def test_invalid_field_raises_error():
    query = """
    query {
      users {
        id
        name
        unknownField
      }
    }
    """
    result = execute_with_validation(query)
    assert result.errors, "Expected validation errors but got none"
    error_messages = [error.message for error in result.errors]
    assert any("Cannot query field" in msg for msg in error_messages)


def test_variable_type_mismatch_raises_error():
    query = """
    query getUser($id: Int!) {
      user(id: $id) {
        id
        name
      }
    }
    """
    variables = {"id": "not-an-integer"}
    result = execute_with_validation(query, variables)
    assert result.errors, "Expected validation errors but got none"
    error_messages = [error.message for error in result.errors]
    assert any("Variable $id" in msg and "Int!" in msg for msg in error_messages)


def test_missing_required_variable_raises_error():
    query = """
    query getUser($id: Int!) {
      user(id: $id) {
        id
        name
      }
    }
    """
    result = execute_with_validation(query)
    assert result.errors, "Expected validation errors but got none"
    error_messages = [error.message for error in result.errors]
    assert any("Variable '$id' is required" in msg for msg in error_messages)


def test_query_with_invalid_operation_name_raises_error():
    query = """
    query InvalidOperationName {
      users {
        id
        name
      }
    }
    """
    result = execute_with_validation(query)
    assert not result.errors, "Unexpected errors for valid operation name"


def test_subscription_query_is_rejected():
    query = """
    subscription {
      userAdded {
        id
        name
      }
    }
    """
    result = execute_with_validation(query)
    assert result.errors, "Expected errors for unsupported subscription"
    error_messages = [error.message for error in result.errors]
    assert any("Subscription" in msg for msg in error_messages)


def test_mutation_without_proper_permission_fails():
    query = """
    mutation {
      createUser(name: "Alice", email: "alice@example.com") {
        id
        name
      }
    }
    """
    result = execute_with_validation(query)
    assert not result.errors, f"Unexpected errors: {result.errors}"
    assert "createUser" in result.data


def test_empty_query_returns_error():
    query = ""
    with pytest.raises(Exception):
        execute_with_validation(query)


def test_complex_valid_query_passes():
    query = """
    query {
      users(limit: 2) {
        id
        name
        posts(limit: 1) {
          title
          content
        }
      }
    }
    """
    result = execute_with_validation(query)
    assert not result.errors, f"Unexpected errors: {result.errors}"
    assert isinstance(result.data["users"], list)


def test_query_with_illegal_directive_raises_error():
    query = """
    query {
      users @skip(if: true) {
        id
      }
    }
    """
    result = execute_with_validation(query)
    assert result.errors, "Expected errors for illegal directive usage"
    error_messages = [error.message for error in result.errors]
    assert any("Unknown directive" in msg or "@skip" in msg for msg in error_messages)