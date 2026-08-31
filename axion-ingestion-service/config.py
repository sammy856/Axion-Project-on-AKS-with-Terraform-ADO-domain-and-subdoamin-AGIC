# """
# Axion Ingestion Service - Configuration
# Loads database connection string from environment variable.
# """

# import os
# from dataclasses import dataclass


# @dataclass
# class Settings:
#     # PostgreSQL connection string
#     # Format: postgresql://<user>:<password>@<host>:<port>/<database>
#     # Example: postgresql://postgres:postgres@localhost:5432/axiondb
#     DATABASE_URL: str = os.getenv(
#         "DATABASE_URL",
#         "postgresql://axion_user:P%40ssw01rd%40123@localhost:5432/axion_db",
#     )

# settings = Settings()


#####################################

#db credentails are now stored in Azure Key Vault and accessed via Kubernetes Secrets Store CSI Driver. The connection string is constructed from individual environment variables for better security and flexibility.

"""
Axion Ingestion Service - Configuration
Loads PostgreSQL credentials from Kubernetes environment variables.
"""

import os
from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass
class Settings:
    # PostgreSQL credentials
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")

    # PostgreSQL Kubernetes Service
    POSTGRES_HOST: str = os.getenv(
        "POSTGRES_HOST",
        "postgresql-service"
    )

    POSTGRES_PORT: str = os.getenv(
        "POSTGRES_PORT",
        "5432"
    )

    # PostgreSQL database
    POSTGRES_DB: str = os.getenv(
        "POSTGRES_DB",
        "postgresdb"
    )

    @property
    def DATABASE_URL(self) -> str:
        # Encode password so special characters are handled correctly
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)

        return (
            f"postgresql://"
            f"{self.POSTGRES_USER}:"
            f"{encoded_password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()