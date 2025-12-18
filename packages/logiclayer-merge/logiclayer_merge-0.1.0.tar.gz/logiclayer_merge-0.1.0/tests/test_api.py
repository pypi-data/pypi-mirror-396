import httpx

class TestAPIClient:
    def test_ping_api_successful(self, api_service):
        docker_ip, port = api_service
        client = httpx.get(f"http://{docker_ip}:{port}/merge/")

        assert client.status_code == 200

    def test_endpoint_cubes_fastapi_successful(self, api_service):
        docker_ip, port = api_service
        client = httpx.get(f"http://{docker_ip}:{port}/merge/cubes")

        assert client.status_code == 200

    def test_endpoint_structures_fastapi_successful(self, api_service):
        docker_ip, port = api_service
        client = httpx.get(f"http://{docker_ip}:{port}/merge/structures")

        assert client.status_code == 200

    def test_endpoint_dimensions_measures_fastapi_successful(self, api_service):
        docker_ip, port = api_service
        data = '{"cube_name":["customers","orders"],"locale": "en"}'
        client = httpx.post(f"http://{docker_ip}:{port}/merge/cubes/dimensions_measures", content=data)

        assert client.status_code == 200

    def test_endpoint_merge_fastapi_error(self, api_service):
        docker_ip, port = api_service
        data = """{
            "query_left": {
                "url": "https://api-v2.oec.world/tesseract/data.csv?locale=en&cube=trade_i_baci_a_96&measures=Trade+Value&drilldowns=Year&time=Year.latest.10"
            },
            "query_right": {
                "url": "https://api-v2.oec.world/tesseract/data.jsonrecords?locale=en&cube=trade_i_baci_a_22&measures=Trade+Value&drilldowns=Year&time=Year.latest.10"
            },
            "pagination": {
                "limit": 0,
                "offset": 0
            },
            "join": {
                "on": "Year",
                "how": "left",
                "suffix": " (right)"
            }
        }"""
        client = httpx.post(f"http://{docker_ip}:{port}/merge/cubes/merge.jsonrecords", content=data)

        assert client.status_code == 500
