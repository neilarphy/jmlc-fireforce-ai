from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

def test_user_permissions(**context):
    """Проверка прав пользователя wildfire_user"""
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем текущего пользователя и его права
    user_info = pg_hook.get_first("SELECT current_user, current_database(), current_schema();")
    print(f"Current user: {user_info[0]}, Database: {user_info[1]}, Schema: {user_info[2]}")
    
    # Проверяем права на схему fireforceai
    schema_permissions = pg_hook.get_records("""
        SELECT 
            nspname as schema_name,
            has_schema_privilege(current_user, nspname, 'USAGE') as has_usage,
            has_schema_privilege(current_user, nspname, 'CREATE') as has_create
        FROM pg_namespace 
        WHERE nspname = 'fireforceai'
    """)
    
    print("Schema permissions:")
    for row in schema_permissions:
        print(f"Schema: {row[0]}, Usage: {row[1]}, Create: {row[2]}")
    
    # Проверяем права на таблицы в схеме fireforceai
    table_permissions = pg_hook.get_records("""
        SELECT 
            schemaname,
            tablename,
            has_table_privilege(current_user, schemaname||'.'||tablename, 'SELECT') as has_select,
            has_table_privilege(current_user, schemaname||'.'||tablename, 'INSERT') as has_insert,
            has_table_privilege(current_user, schemaname||'.'||tablename, 'UPDATE') as has_update
        FROM pg_tables 
        WHERE schemaname = 'fireforceai'
    """)
    
    print("Table permissions:")
    for row in table_permissions:
        print(f"Table: {row[0]}.{row[1]}, Select: {row[2]}, Insert: {row[3]}, Update: {row[4]}")
    
    return "Permissions check completed"

with DAG(
    dag_id="test_permissions",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["debug", "permissions"]
) as dag:
    
    test_perms = PythonOperator(
        task_id="test_user_permissions",
        python_callable=test_user_permissions,
        dag=dag
    ) 