import os
import pytest
import httpx
from dotenv import load_dotenv


SERVICE = {
    "api": "merge/",
    "clickhouse": "ping"
}

load_dotenv(".env.test")


def is_responsive(docker_ip: str, port: int, service: str) -> bool:
    try:
        print(f"http://{docker_ip}:{port}/{SERVICE[service]}")
        client = httpx.get(f"http://{docker_ip}:{port}/{SERVICE[service]}")
        if client.status_code == 200:
            return True
        return False
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")


@pytest.fixture(scope="session")
def test_env_vars():
    return {
        "tesseract_backend": os.getenv("TESSERACT_BACKEND", "clickhouse://readonly:test@localhost:9000/default"),
        "tesseract_schema": os.getenv("TESSERACT_SCHEMA", "./tests/fixtures/schema"),
        "clickhouse_user": os.getenv("CLICKHOUSE_USER", "readonly"),
        "clickhouse_password": os.getenv("CLICKHOUSE_PASSWORD", "test")
    }


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.test.yaml")


@pytest.fixture(scope="session")
def clickhouse_service(docker_ip, docker_services):
    service = "clickhouse"
    port = docker_services.port_for(service, 8123)

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.5,
        check=lambda: is_responsive(docker_ip, port, service)
    )

    return docker_ip, port

@pytest.fixture(scope="session")
def api_service(docker_ip, docker_services):
    service = "api"
    port = docker_services.port_for(service, 8000)

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.5,
        check=lambda: is_responsive(docker_ip, port, service)
    )

    return docker_ip, port