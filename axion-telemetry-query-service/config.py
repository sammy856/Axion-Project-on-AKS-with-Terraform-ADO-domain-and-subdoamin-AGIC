# """
# Axion Telemetry Query Service - Configuration
# """

# import os
# from dataclasses import dataclass

# @dataclass
# class Settings:
#     # PostgreSQL connection string
#     # Format: postgresql://<user>:<password>@<host>:<port>/<database>
#     DATABASE_URL: str = os.getenv(
#         "DATABASE_URL",
#         "postgresql://axion_user:P%40ssw01rd%40123@localhost:5432/axion_db",
#     )
#     # Allows configuring a different port, e.g., if we run multiple services
#     PORT: int = int(os.getenv("PORT", "8000"))

# settings = Settings()


###################################

#db credentails are now stored in Azure Key Vault and accessed via Kubernetes Secrets Store CSI Driver. The connection string is constructed from individual environment variables for better security and flexibility.

"""
Axion Telemetry Query Service - Configuration
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    # PostgreSQL connection details
    POSTGRES_HOST: str = os.getenv(
        "POSTGRES_HOST",
        "postgresql-service"
    )

    POSTGRES_PORT: int = int(os.getenv(
        "POSTGRES_PORT",
        "5432"
    ))

    POSTGRES_DB: str = os.getenv(
        "POSTGRES_DB",
        "postgresdb"
    )

    # These will be injected from Azure Key Vault
    POSTGRES_USER: str = os.getenv(
        "POSTGRES_USER",
        ""
    )

    POSTGRES_PASSWORD: str = os.getenv(
        "POSTGRES_PASSWORD",
        ""
    )

    # Application port
    PORT: int = int(os.getenv(
        "PORT",
        "8000"
    ))


settings = Settings()
