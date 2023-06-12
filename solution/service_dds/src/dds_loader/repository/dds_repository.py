import os
import uuid
from lib.pg import PgConnect


pg_warehouse_host = str(os.getenv('PG_WAREHOUSE_HOST') or "")
pg_warehouse_port = int(str(os.getenv('PG_WAREHOUSE_PORT') or 0))
pg_warehouse_dbname = str(os.getenv('PG_WAREHOUSE_DBNAME') or "")
pg_warehouse_user = str(os.getenv('PG_WAREHOUSE_USER') or "")
pg_warehouse_password = str(os.getenv('PG_WAREHOUSE_PASSWORD') or "")


def get_uuid(v):
    uuid_ = uuid.uuid5(name=str(v), namespace=uuid.NAMESPACE_OID)
    return uuid_


def pg_warehouse_db():
    return PgConnect(
        pg_warehouse_host,
        pg_warehouse_port,
        pg_warehouse_dbname,
        pg_warehouse_user,
        pg_warehouse_password
    )


class DdsRepository:
    def __init__(self, db: PgConnect) -> None:
        self._db = db

    def insert_hub(hub_name: str,
                   names: list,
                   values: list,
                   ) -> None:
        with pg_warehouse_db().connection() as conn:
            uuid_name = f'h_{hub_name}_pk'
            names = [uuid_name] + names
            uuid_value = get_uuid(values[0])
            values = [uuid_value] + values
            values_ = []
            for v in values:
                v_ = f"'{str(v)}'"
                values_.append(v_)
            with conn.cursor() as cur:
                query = f"""
                        INSERT INTO dds.h_{hub_name}
                        ({','.join(names)})
                        VALUES({','.join(values_)})
                        ON CONFLICT ({names[0]})
                        DO NOTHING;
                    """
                print(query)
                cur.execute(query

                            )
                conn.commit()

    def insert_link(left_name: str,
                    left_value: str,
                    right_name: str,
                    right_value: str,
                    src: str,
                    ) -> None:
        with pg_warehouse_db().connection() as conn:
            pk_name = f'hk_{left_name}_{right_name}_pk'
            pk_value = get_uuid(f'{left_value}{right_value}')

            with conn.cursor() as cur:
                query = f"""
                    INSERT INTO dds.l_{left_name}_{right_name}
                    ({pk_name}, h_{left_name}_pk, h_{right_name}_pk, load_src)
                    VALUES('{pk_value}','{get_uuid(left_value)}','{get_uuid(right_value)}','{src}')
                        ON CONFLICT ({pk_name})
                        DO NOTHING;
                    """
                print(query)
                cur.execute(query

                            )
                conn.commit()

    def insert_satellit(hub_name: str,
                        satellit_name: str,
                        columns: list,
                        values: list,
                        ) -> None:
        with pg_warehouse_db().connection() as conn:
            uuid_name = f'hk_{hub_name}_{satellit_name}_pk'
            columns = [uuid_name] + columns
            uuid_value = get_uuid(f'{values[0]},{values[1]}')
            values[0] = get_uuid(values[0])
            values = [uuid_value] + values
            values_ = []
            for v in values:
                v_ = f"'{str(v)}'"
                values_.append(v_)
            columns_ = []
            for c in columns:
                q = f'''{c} = EXCLUDED."{c}"'''
                columns_.append(q)
            with conn.cursor() as cur:
                query = f"""
                        INSERT INTO dds.s_{hub_name}_{satellit_name}
                        ({','.join(columns)})
                        VALUES({','.join(values_)})
                        ON CONFLICT (h_{hub_name}_pk)
                        DO UPDATE 
                        SET {','.join(columns_)},load_dt = CURRENT_TIMESTAMP;

                    """
                print(query)
                cur.execute(query

                            )
                conn.commit()