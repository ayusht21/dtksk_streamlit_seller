"""
Unit tests for LLM Provider abstraction and Mock provider fallback.
"""

import unittest
from services.llm_provider import MockOfflineProvider, ProviderResponse
from agent.prompts.system_prompt import get_system_prompt


class TestLLMProvider(unittest.TestCase):

    def setUp(self):
        self.mock_provider = MockOfflineProvider()
        self.system_prompt = get_system_prompt()

    def test_mock_cotton_bollworm(self):
        messages = [{"role": "user", "content": "माझ्या कापसावर बोंडअळी आहे, कोणते औषध फवारावे?"}]
        response: ProviderResponse = self.mock_provider.chat(
            messages=messages,
            system_prompt=self.system_prompt,
        )
        self.assertIsInstance(response, ProviderResponse)
        self.assertIn("Coragen", response.text)
        self.assertGreater(len(response.recommended_product_ids), 0)
        self.assertEqual(response.provider_used, "mock")

    def test_mock_image_fallback(self):
        messages = [{"role": "user", "content": "हे झाडाचे पान पहा."}]
        dummy_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        response = self.mock_provider.chat(
            messages=messages,
            system_prompt=self.system_prompt,
            image_bytes=dummy_image,
        )
    def test_agent_config_hybrid_models(self):
        from agent.agent_config import AGENT_CONFIG
        self.assertEqual(AGENT_CONFIG["openai"]["default_model"], "gpt-4o-mini")
        self.assertEqual(AGENT_CONFIG["openai"]["vision_model"], "gpt-4o")

    def test_config_openai_getters(self):
        import config
        self.assertEqual(config.get_openai_model(), "gpt-4o-mini")
        self.assertEqual(config.get_openai_vision_model(), "gpt-4o")


if __name__ == "__main__":
    unittest.main()
