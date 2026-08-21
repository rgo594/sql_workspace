import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization


def get_connection():
    private_key = serialization.load_pem_private_key(
        os.environ["DBT_PROFILES_PRIVATE_KEY"].encode(),
        password=os.environ["DBT_PROFILES_PRIVATE_KEY_PASSPHRASE"].encode(),
    )

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user="SERV_DEV_DBT_USER",
        role="SERV_DEV_DBT_ROLE",
        private_key=private_key,
        warehouse="DBT_DEV_WH",
        database="DATA_MART_DEV",
        schema="dbt_rogara",
    )


def execute_to_csv(query, output_file):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)

            first = True

            for df in cur.fetch_pandas_batches():
                df.to_csv(
                    output_file,
                    mode="w" if first else "a",
                    header=first,
                    index=False,
                )
                first = False