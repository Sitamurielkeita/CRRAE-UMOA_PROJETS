import pytest
from unittest.mock import MagicMock, patch

from database_logic import add_account_db, delete_account_db, load_accounts_db


# Le 'mocker' est une "fixture" fournie par pytest-mock.
# Il simplifie la création de mocks.

def test_add_account_db(mocker):
    """
    Vérifie que la fonction add_account_db appelle bien la bonne commande SQL
    avec les bons paramètres, sans toucher à une vraie base de données.
    """
    # 1. Préparation du Mock : On simule psycopg2.connect
    mock_connect = mocker.patch('database_logic.psycopg2.connect')

    # 2. Appel de la fonction à tester
    add_account_db("John Doe", "john.doe@email.com", 100)

    # 3. Assertions : On vérifie ce qui s'est passé
    # A-t-on bien tenté de se connecter ?
    mock_connect.assert_called_once()

    # Récupérons le curseur simulé
    mock_cursor = mock_connect().__enter__().cursor().__enter__()

    # A-t-on exécuté la bonne commande SQL ?
    expected_sql = "INSERT INTO accounts (name, email, balance) VALUES (%s, %s, %s)"
    expected_params = ("John Doe", "john.doe@email.com", 100)
    mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)


def test_delete_account_db(mocker):
    """Vérifie que la fonction delete_account_db exécute la bonne requête DELETE."""
    # 1. Préparation
    mock_connect = mocker.patch('database_logic.psycopg2.connect')

    # 2. Appel
    account_id_to_delete = 42
    delete_account_db(account_id_to_delete)

    # 3. Assertions
    mock_cursor = mock_connect().__enter__().cursor().__enter__()
    expected_sql = "DELETE FROM accounts WHERE id = %s"
    expected_params = (account_id_to_delete,)
    mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)


