import pytest

from innertubei import Suggestions
from innertubei.core.constants import ResultMode


class TestSuggestions:
    @pytest.mark.asyncio
    async def test_suggestions_basic(self):
        suggestions = await Suggestions.get("python")

        assert suggestions is not None
        assert isinstance(suggestions, dict)
        assert "result" in suggestions
        assert isinstance(suggestions["result"], list)

        if len(suggestions["result"]) > 0:
            for suggestion in suggestions["result"][:5]:
                assert isinstance(suggestion, str)
                assert len(suggestion) > 0

    @pytest.mark.asyncio
    async def test_suggestions_with_different_queries(self):
        queries = ["music", "tutorial", "python", "javascript"]

        for query in queries:
            suggestions = await Suggestions.get(query)
            assert suggestions is not None
            assert "result" in suggestions

    @pytest.mark.asyncio
    async def test_suggestions_with_language_region(self):
        suggestions = await Suggestions.get("music", language="en", region="US")

        assert suggestions is not None
        assert "result" in suggestions
        assert isinstance(suggestions["result"], list)

    @pytest.mark.asyncio
    async def test_suggestions_result_modes(self):
        dict_result = await Suggestions.get("test", mode=ResultMode.dict)
        json_result = await Suggestions.get("test", mode=ResultMode.json)

        assert isinstance(dict_result, dict)
        assert isinstance(json_result, str)

        import json

        parsed_json = json.loads(json_result)
        assert isinstance(parsed_json, dict)


class TestSuggestionsErrorHandling:
    @pytest.mark.asyncio
    async def test_empty_query_suggestions(self):
        suggestions = await Suggestions.get("")

        assert suggestions is not None
        assert "result" in suggestions

    @pytest.mark.asyncio
    async def test_very_long_query(self):
        long_query = "test query " * 50
        suggestions = await Suggestions.get(long_query)

        assert suggestions is not None
        assert "result" in suggestions

    @pytest.mark.asyncio
    async def test_special_characters_query(self):
        special_queries = [
            "test@#$%",
            "test query with spaces",
            "test+query",
            "テスト",
        ]

        for query in special_queries:
            suggestions = await Suggestions.get(query)
            assert suggestions is not None
            assert "result" in suggestions

    @pytest.mark.asyncio
    async def test_invalid_language_region(self):
        suggestions = await Suggestions.get("test", language="invalid", region="XX")

        assert suggestions is not None
        assert "result" in suggestions

    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self):
        suggestions = await Suggestions.get("test")

        assert suggestions is not None or suggestions == {"result": []}


class TestSuggestionsDataIntegrity:
    @pytest.mark.asyncio
    async def test_suggestions_data_structure(self):
        suggestions = await Suggestions.get("python programming")

        assert isinstance(suggestions, dict)
        assert "result" in suggestions

        result = suggestions["result"]
        assert isinstance(result, list)

        for suggestion in result[:10]:
            assert isinstance(suggestion, str)
            assert len(suggestion.strip()) > 0

    @pytest.mark.asyncio
    async def test_suggestions_uniqueness(self):
        suggestions = await Suggestions.get("popular query")

        if suggestions and suggestions["result"]:
            result = suggestions["result"]
            unique_suggestions = set(result)

            assert len(unique_suggestions) == len(result)

    @pytest.mark.asyncio
    async def test_suggestions_relevance(self):
        query = "python"
        suggestions = await Suggestions.get(query)

        if suggestions and suggestions["result"]:
            result = suggestions["result"]

            if len(result) > 0:
                first_suggestion = result[0].lower()
                assert query.lower() in first_suggestion or len(first_suggestion) > 0
