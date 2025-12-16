# -*- coding: utf-8 -*-
"""
Unit tests for persona generator functionality.

Tests PersonaGeneratorConfig, GeneratedPersona, and PersonaGenerator classes.
"""

import json
from unittest.mock import MagicMock

import pytest

from massgen.persona_generator import (
    GeneratedPersona,
    PersonaGenerator,
    PersonaGeneratorConfig,
)


class TestPersonaGeneratorConfig:
    """Test PersonaGeneratorConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PersonaGeneratorConfig()

        assert config.enabled is False
        assert config.backend == {"type": "openai", "model": "gpt-4o-mini"}
        assert config.strategy == "complementary"
        assert config.persona_guidelines is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PersonaGeneratorConfig(
            enabled=True,
            backend={"type": "gemini", "model": "gemini-2.0-flash"},
            strategy="diverse",
            persona_guidelines="Focus on technical expertise",
        )

        assert config.enabled is True
        assert config.backend == {"type": "gemini", "model": "gemini-2.0-flash"}
        assert config.strategy == "diverse"
        assert config.persona_guidelines == "Focus on technical expertise"

    def test_backend_default_initialization(self):
        """Test that backend is properly initialized when None."""
        config = PersonaGeneratorConfig(enabled=True)
        assert config.backend is not None
        assert config.backend["type"] == "openai"


class TestGeneratedPersona:
    """Test GeneratedPersona dataclass."""

    def test_persona_creation(self):
        """Test basic persona creation."""
        persona = GeneratedPersona(
            agent_id="agent_a",
            persona_text="You are an analytical thinker.",
            attributes={"thinking_style": "analytical", "focus_area": "details"},
        )

        assert persona.agent_id == "agent_a"
        assert "analytical" in persona.persona_text
        assert persona.attributes["thinking_style"] == "analytical"
        assert persona.attributes["focus_area"] == "details"

    def test_persona_empty_attributes(self):
        """Test persona with empty attributes."""
        persona = GeneratedPersona(
            agent_id="agent_b",
            persona_text="A simple persona.",
            attributes={},
        )

        assert persona.agent_id == "agent_b"
        assert persona.attributes == {}


class TestPersonaGenerator:
    """Test PersonaGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(
            backend=mock_backend,
            strategy="complementary",
            guidelines="Custom guidelines",
        )

        assert generator.backend == mock_backend
        assert generator.strategy == "complementary"
        assert generator.guidelines == "Custom guidelines"

    def test_get_strategy_instructions_complementary(self):
        """Test complementary strategy instructions."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend, strategy="complementary")

        instructions = generator._get_strategy_instructions()
        assert "complement each other" in instructions
        assert "different aspects" in instructions.lower()

    def test_get_strategy_instructions_diverse(self):
        """Test diverse strategy instructions."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend, strategy="diverse")

        instructions = generator._get_strategy_instructions()
        assert "diversity" in instructions.lower()
        assert "different viewpoint" in instructions.lower()

    def test_get_strategy_instructions_specialized(self):
        """Test specialized strategy instructions."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend, strategy="specialized")

        instructions = generator._get_strategy_instructions()
        assert "specialized" in instructions.lower()
        assert "expertise" in instructions.lower()

    def test_get_strategy_instructions_adversarial(self):
        """Test adversarial strategy instructions."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend, strategy="adversarial")

        instructions = generator._get_strategy_instructions()
        assert "adversarial" in instructions.lower()
        assert "devil's advocate" in instructions.lower()

    def test_get_strategy_instructions_fallback(self):
        """Test fallback to complementary for unknown strategy."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend, strategy="unknown")

        instructions = generator._get_strategy_instructions()
        assert "complement each other" in instructions

    def test_build_generation_prompt(self):
        """Test prompt building."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(
            backend=mock_backend,
            strategy="complementary",
            guidelines="Test guidelines",
        )

        prompt = generator._build_generation_prompt(
            agent_ids=["agent_a", "agent_b"],
            task="Analyze code for bugs",
            existing_system_messages={"agent_a": "Existing message", "agent_b": None},
        )

        # Check prompt contains required elements
        assert "agent_a" in prompt
        assert "agent_b" in prompt
        assert "Analyze code for bugs" in prompt
        assert "Test guidelines" in prompt
        assert "complementary" in prompt.lower()
        assert "Has existing instruction" in prompt
        assert "Existing message" in prompt  # Full message included, not truncated
        assert "No existing instruction" in prompt

    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        response = json.dumps(
            {
                "personas": {
                    "agent_a": {
                        "persona_text": "You are analytical and detail-oriented.",
                        "attributes": {
                            "thinking_style": "analytical",
                            "focus_area": "details",
                            "communication": "concise",
                        },
                    },
                    "agent_b": {
                        "persona_text": "You are creative and big-picture focused.",
                        "attributes": {
                            "thinking_style": "creative",
                            "focus_area": "big-picture",
                            "communication": "thorough",
                        },
                    },
                },
            },
        )

        personas = generator._parse_response(response, ["agent_a", "agent_b"])

        assert len(personas) == 2
        assert personas["agent_a"].agent_id == "agent_a"
        assert "analytical" in personas["agent_a"].persona_text
        assert personas["agent_b"].attributes["thinking_style"] == "creative"

    def test_parse_response_with_markdown_code_block(self):
        """Test parsing response with markdown code block."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        response = """Here are the personas:
```json
{
    "personas": {
        "agent_a": {
            "persona_text": "Analytical thinker.",
            "attributes": {"thinking_style": "analytical"}
        }
    }
}
```
"""

        personas = generator._parse_response(response, ["agent_a"])

        assert len(personas) == 1
        assert "Analytical" in personas["agent_a"].persona_text

    def test_parse_response_missing_agent(self):
        """Test handling missing agent in response."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        response = json.dumps(
            {
                "personas": {
                    "agent_a": {
                        "persona_text": "Test persona.",
                        "attributes": {},
                    },
                },
            },
        )

        # Request personas for agent_a and agent_b, but only agent_a in response
        personas = generator._parse_response(response, ["agent_a", "agent_b"])

        assert len(personas) == 2
        assert personas["agent_a"].persona_text == "Test persona."
        # agent_b should get default
        assert "thoughtfully" in personas["agent_b"].persona_text.lower()

    def test_parse_response_invalid_json(self):
        """Test handling invalid JSON response."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        response = "This is not valid JSON"

        personas = generator._parse_response(response, ["agent_a", "agent_b"])

        # Should return fallback personas
        assert len(personas) == 2
        assert personas["agent_a"].agent_id == "agent_a"
        assert personas["agent_b"].agent_id == "agent_b"

    def test_generate_fallback_personas(self):
        """Test fallback persona generation."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        personas = generator._generate_fallback_personas(["agent_a", "agent_b", "agent_c"])

        assert len(personas) == 3
        # Check that different styles are assigned
        styles = [p.attributes.get("thinking_style") for p in personas.values()]
        assert "analytical" in styles
        assert "creative" in styles
        assert "systematic" in styles

    def test_generate_fallback_personas_cycling(self):
        """Test that fallback personas cycle through templates."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        # Create more agents than templates (5 templates)
        agent_ids = [f"agent_{i}" for i in range(7)]
        personas = generator._generate_fallback_personas(agent_ids)

        assert len(personas) == 7
        # First and sixth should have same style (cycling)
        assert personas["agent_0"].attributes["thinking_style"] == personas["agent_5"].attributes["thinking_style"]

    @pytest.mark.asyncio
    async def test_generate_personas_success(self):
        """Test successful persona generation."""
        mock_backend = MagicMock()
        mock_backend.config = {"model": "gpt-4o-mini"}

        # Mock the streaming response
        async def mock_stream(*args, **kwargs):
            response = json.dumps(
                {
                    "personas": {
                        "agent_a": {
                            "persona_text": "Analytical thinker.",
                            "attributes": {"thinking_style": "analytical"},
                        },
                        "agent_b": {
                            "persona_text": "Creative thinker.",
                            "attributes": {"thinking_style": "creative"},
                        },
                    },
                },
            )
            # Simulate streaming chunks
            chunk = MagicMock()
            chunk.content = response
            yield chunk

        mock_backend.stream_with_tools = mock_stream

        generator = PersonaGenerator(backend=mock_backend, strategy="complementary")

        personas = await generator.generate_personas(
            agent_ids=["agent_a", "agent_b"],
            task="Test task",
            existing_system_messages={},
        )

        assert len(personas) == 2
        assert personas["agent_a"].attributes["thinking_style"] == "analytical"
        assert personas["agent_b"].attributes["thinking_style"] == "creative"

    @pytest.mark.asyncio
    async def test_generate_personas_empty_agents(self):
        """Test generation with no agents."""
        mock_backend = MagicMock()
        generator = PersonaGenerator(backend=mock_backend)

        personas = await generator.generate_personas(
            agent_ids=[],
            task="Test task",
            existing_system_messages={},
        )

        assert personas == {}

    @pytest.mark.asyncio
    async def test_generate_personas_exception_handling(self):
        """Test that exceptions fall back to default personas."""
        mock_backend = MagicMock()
        mock_backend.config = {"model": "gpt-4o-mini"}

        # Mock an exception
        async def mock_stream(*args, **kwargs):
            raise Exception("API error")
            yield  # Make this a generator

        mock_backend.stream_with_tools = mock_stream

        generator = PersonaGenerator(backend=mock_backend)

        personas = await generator.generate_personas(
            agent_ids=["agent_a", "agent_b"],
            task="Test task",
            existing_system_messages={},
        )

        # Should return fallback personas
        assert len(personas) == 2
        assert personas["agent_a"].agent_id == "agent_a"
        assert personas["agent_b"].agent_id == "agent_b"


class TestPersonaGeneratorIntegration:
    """Integration tests for persona generator with CoordinationConfig."""

    def test_coordination_config_with_persona_generator(self):
        """Test that CoordinationConfig properly includes persona_generator."""
        from massgen.agent_config import CoordinationConfig

        pg_config = PersonaGeneratorConfig(
            enabled=True,
            backend={"type": "openai", "model": "gpt-4o"},
            strategy="diverse",
        )

        coord_config = CoordinationConfig(persona_generator=pg_config)

        assert coord_config.persona_generator.enabled is True
        assert coord_config.persona_generator.backend["model"] == "gpt-4o"
        assert coord_config.persona_generator.strategy == "diverse"

    def test_coordination_config_default_persona_generator(self):
        """Test that CoordinationConfig has default persona_generator."""
        from massgen.agent_config import CoordinationConfig

        coord_config = CoordinationConfig()

        assert coord_config.persona_generator is not None
        assert coord_config.persona_generator.enabled is False
