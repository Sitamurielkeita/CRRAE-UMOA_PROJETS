# Importation des libraries
import psycopg2
import os

# Connexion PostgreSQL
DATABASE_URL = "postgresql://crrae:crrae_umoa@postgresql-34636-0.cloudclusters.net:34636/crrae_umoa?sslmode=require"

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
                "UPDATE accounts SET email = %s, balance = %s WHERE id = %s", # Il enlève 'name'
                 (email, balance or 0, account_id)

            )

def delete_account_db(account_id):
    """Supprime un compte de la base de données."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM accounts WHERE id = %s", (account_id,))

def get_account_balance(conn, account_id):

"""Récupère le solde d'un compte spécifique."""
    with conn.cursor() as cur:
        cur.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
        result = cur.fetchone()
        if result is None:
            raise ValueError(f"Le compte avec l'ID {account_id} n'existe pas.")
            return result[0]

def transfer_funds_db(source_id, destination_id, amount):

    """Transfère un montant d'un compte source vers un compte destinationen utilisant une transaction pour garantir l'intégrité"""
    if source_id == destination_id:
        raise ValueError("Le compte source et destination ne peuvent pas être identiques.")
        if amount <= 0:
            raise ValueError("Le montant du transfert doit être positif.")
            conn = get_connection()
            try:
                with conn: # Utiliser 'with conn' gère automatiquement commit/rollback
                with conn.cursor() as cur:
# 1. Vérifier le solde du compte source (avec verrouillage pour la sécurité)
                    cur.execute("SELECT balance FROM accounts WHERE id = %s FOR UPDATE", (source_id,) 
                    source_balance = cur.fetchone()[0]
                    if source_balance < amount:
                        raise ValueError("Solde insuffisant pour effectuer le transfert.") 
# 2. Débiter le compte source
                        cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s",(amount, source_id))
# 3. Créditer le compte destination
                        cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s",(amount, destination_id))

# Le 'with conn' exécute conn.commit() ici si tout s'est bien passé.
            except (Exception, psycopg2.Error) as error:
                print(f"Erreur de transaction, rollback effectué : {error}")
                raise error
            finally:
                if conn:
                    conn.close()

