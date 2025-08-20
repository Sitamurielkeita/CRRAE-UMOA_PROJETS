
import psycopg2
import os

# Connexion PostgreSQL
DATABASE_URL = "A recupérer dans le TP"

def get_connection():
    """Établit la connexion à la base de données."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    """Crée la table 'accounts' si elle n'existe pas."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        balance NUMERIC DEFAULT 0
                    )
                """)
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la DB : {e}")


def load_accounts_db():
    """Charge tous les comptes depuis la base de données."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, balance FROM accounts ORDER BY id")
            return cur.fetchall()

def add_account_db(name, email, balance):
    """Ajoute un nouveau compte à la base de données."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO accounts (name, email, balance) VALUES (%s, %s, %s)",
                (name, email, balance or 0)
            )

def update_account_db(account_id, name, email, balance):
    """Met à jour un compte existant."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE accounts SET name = %s, email = %s, balance = %s WHERE id = %s",
                (name, email, balance or 0, account_id)
            )

def delete_account_db(account_id):
    """Supprime un compte de la base de données."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM accounts WHERE id = %s", (account_id,))