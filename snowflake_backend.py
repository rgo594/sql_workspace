import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from pathlib import Path
from datetime import datetime
#from sql_shell import query_history_fp, log_query
from time import perf_counter

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

def execute_to_csv(query, workspace_id, output_file, conn):
    with conn.cursor() as cur:
        status = "success"
        start = perf_counter()

        try:
            print(f"Executing query: {query}")
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

        except KeyboardInterrupt:
            status = "cancelled"
            raise

        except Exception:
            status = "failed"
            raise

        finally:
            execution_time = perf_counter() - start

            metadata = {
                "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "workspace_id": workspace_id,
                "status": status,
                "query_id": cur.sfqid,
                "row_count": cur.rowcount,
                "execution_time_seconds": round(execution_time, 3)
            }
            print(f"LOGGING: {metadata}", flush=True)
            return metadata