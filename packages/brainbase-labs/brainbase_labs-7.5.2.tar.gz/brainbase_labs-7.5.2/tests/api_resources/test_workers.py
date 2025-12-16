# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from brainbase_labs import BrainbaseLabs, AsyncBrainbaseLabs
from brainbase_labs.types import WorkerListResponse
from brainbase_labs.types.shared import Worker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: BrainbaseLabs) -> None:
        worker = client.workers.create(
            description="description",
            name="name",
            status="status",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: BrainbaseLabs) -> None:
        response = client.workers.with_raw_response.create(
            description="description",
            name="name",
            status="status",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = response.parse()
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: BrainbaseLabs) -> None:
        with client.workers.with_streaming_response.create(
            description="description",
            name="name",
            status="status",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = response.parse()
            assert_matches_type(Worker, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: BrainbaseLabs) -> None:
        worker = client.workers.retrieve(
            "id",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: BrainbaseLabs) -> None:
        response = client.workers.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = response.parse()
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: BrainbaseLabs) -> None:
        with client.workers.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = response.parse()
            assert_matches_type(Worker, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: BrainbaseLabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.workers.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: BrainbaseLabs) -> None:
        worker = client.workers.update(
            id="id",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: BrainbaseLabs) -> None:
        worker = client.workers.update(
            id="id",
            description="description",
            name="name",
            status="status",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: BrainbaseLabs) -> None:
        response = client.workers.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = response.parse()
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: BrainbaseLabs) -> None:
        with client.workers.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = response.parse()
            assert_matches_type(Worker, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: BrainbaseLabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.workers.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: BrainbaseLabs) -> None:
        worker = client.workers.list()
        assert_matches_type(WorkerListResponse, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: BrainbaseLabs) -> None:
        response = client.workers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = response.parse()
        assert_matches_type(WorkerListResponse, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: BrainbaseLabs) -> None:
        with client.workers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = response.parse()
            assert_matches_type(WorkerListResponse, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: BrainbaseLabs) -> None:
        worker = client.workers.delete(
            "id",
        )
        assert worker is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: BrainbaseLabs) -> None:
        response = client.workers.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = response.parse()
        assert worker is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: BrainbaseLabs) -> None:
        with client.workers.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = response.parse()
            assert worker is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: BrainbaseLabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.workers.with_raw_response.delete(
                "",
            )


class TestAsyncWorkers:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncBrainbaseLabs) -> None:
        worker = await async_client.workers.create(
            description="description",
            name="name",
            status="status",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBrainbaseLabs) -> None:
        response = await async_client.workers.with_raw_response.create(
            description="description",
            name="name",
            status="status",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = await response.parse()
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBrainbaseLabs) -> None:
        async with async_client.workers.with_streaming_response.create(
            description="description",
            name="name",
            status="status",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = await response.parse()
            assert_matches_type(Worker, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncBrainbaseLabs) -> None:
        worker = await async_client.workers.retrieve(
            "id",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncBrainbaseLabs) -> None:
        response = await async_client.workers.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = await response.parse()
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncBrainbaseLabs) -> None:
        async with async_client.workers.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = await response.parse()
            assert_matches_type(Worker, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncBrainbaseLabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.workers.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncBrainbaseLabs) -> None:
        worker = await async_client.workers.update(
            id="id",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncBrainbaseLabs) -> None:
        worker = await async_client.workers.update(
            id="id",
            description="description",
            name="name",
            status="status",
        )
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncBrainbaseLabs) -> None:
        response = await async_client.workers.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = await response.parse()
        assert_matches_type(Worker, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncBrainbaseLabs) -> None:
        async with async_client.workers.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = await response.parse()
            assert_matches_type(Worker, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncBrainbaseLabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.workers.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncBrainbaseLabs) -> None:
        worker = await async_client.workers.list()
        assert_matches_type(WorkerListResponse, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBrainbaseLabs) -> None:
        response = await async_client.workers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = await response.parse()
        assert_matches_type(WorkerListResponse, worker, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBrainbaseLabs) -> None:
        async with async_client.workers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = await response.parse()
            assert_matches_type(WorkerListResponse, worker, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncBrainbaseLabs) -> None:
        worker = await async_client.workers.delete(
            "id",
        )
        assert worker is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBrainbaseLabs) -> None:
        response = await async_client.workers.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        worker = await response.parse()
        assert worker is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBrainbaseLabs) -> None:
        async with async_client.workers.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            worker = await response.parse()
            assert worker is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBrainbaseLabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.workers.with_raw_response.delete(
                "",
            )
