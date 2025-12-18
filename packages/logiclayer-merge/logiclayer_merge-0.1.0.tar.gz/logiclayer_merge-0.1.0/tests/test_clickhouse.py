import json
import httpx

class TestClickhouseClient:
    def test_ping_clickhouse_successful(self, clickhouse_service):
        docker_ip, port = clickhouse_service
        client = httpx.get(f"http://{docker_ip}:{port}/ping")

        assert client.status_code == 200

    def test_table_orders(self, clickhouse_service, test_env_vars):
        clickhouse_user = test_env_vars.get("clickhouse_user")
        clickhouse_password = test_env_vars.get("clickhouse_password")
        docker_ip, port = clickhouse_service
        payload = 'select * from orders;'
        client = httpx.post(f'http://{docker_ip}:{port}/?add_http_cors_header=1&user={clickhouse_user}&password={clickhouse_password}&default_format=JSON&enable_http_compression=1&extremes=1',
                            content=payload)

        assert len(json.loads(client.content.decode('utf-8'))["data"]) == 9

    def test_table_customers(self, clickhouse_service, test_env_vars):
        clickhouse_user = test_env_vars.get("clickhouse_user")
        clickhouse_password = test_env_vars.get("clickhouse_password")
        docker_ip, port = clickhouse_service
        payload = 'select * from customers;'
        client = httpx.post(f'http://{docker_ip}:{port}/?add_http_cors_header=1&user={clickhouse_user}&password={clickhouse_password}&default_format=JSON&enable_http_compression=1&extremes=1',
                            content=payload)

        assert len(json.loads(client.content.decode('utf-8'))["data"]) == 6
    
    def test_table_join(self, clickhouse_service, test_env_vars):
        clickhouse_user = test_env_vars.get("clickhouse_user")
        clickhouse_password = test_env_vars.get("clickhouse_password")
        docker_ip, port = clickhouse_service
        payload = 'select * from customers left outer join orders on customers.customer_id = orders.customer_id;'
        client = httpx.post(f'http://{docker_ip}:{port}/?add_http_cors_header=1&user={clickhouse_user}&password={clickhouse_password}&default_format=JSON&enable_http_compression=1&extremes=1',
                            content=payload)

        assert len(json.loads(client.content.decode('utf-8'))["data"]) == 10
