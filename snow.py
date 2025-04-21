import hvac
import os

class VaultManager:
    def __init__(self, vault_addr, token, vault_path):
        self.vault_addr = vault_addr
        self.token = token
        self.vault_path = vault_path
        self.client = hvac.Client(url=self.vault_addr, token=self.token)

    def write_secret(self, secret_name, secret_data):
        """Write secret to HashiCorp Vault."""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=f"{self.vault_path}/{secret_name}",
            secret=secret_data
        )
        print(f"Secret '{secret_name}' written to Vault.")

    def read_secret(self, secret_name):
        """Read a secret from HashiCorp Vault."""
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=f"{self.vault_path}/{secret_name}"
        )
        print(f"Secret '{secret_name}' retrieved from Vault.")
        return secret['data']['data']

class SnowflakeVaultApp:
    def __init__(self, vault_manager):
        self.vault_manager = vault_manager

    def store_snowflake_creds(self, secret_name, username, password, account):
        """Store Snowflake credentials in Vault."""
        secret_data = {
            'username': username,
            'password': password,
            'account': account
        }
        self.vault_manager.write_secret(secret_name, secret_data)

    def retrieve_snowflake_creds(self, secret_name):
        """Retrieve Snowflake credentials from Vault."""
        creds = self.vault_manager.read_secret(secret_name)
        return creds

if __name__ == "__main__":
    # Configuration
    VAULT_ADDR = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')
    VAULT_TOKEN = os.getenv('VAULT_TOKEN', 'your-root-token')
    VAULT_PATH = os.getenv('VAULT_PATH', 'snowflake/creds')

    vault_manager = VaultManager(VAULT_ADDR, VAULT_TOKEN, VAULT_PATH)
    app = SnowflakeVaultApp(vault_manager)

    # Store Snowflake credentials
    app.store_snowflake_creds(
        secret_name="prod-db",
        username="sf_user",
        password="sf_pass",
        account="sf_account"
    )

    # Retrieve Snowflake credentials
    credentials = app.retrieve_snowflake_creds("prod-db")
    print("Retrieved credentials:", credentials)
