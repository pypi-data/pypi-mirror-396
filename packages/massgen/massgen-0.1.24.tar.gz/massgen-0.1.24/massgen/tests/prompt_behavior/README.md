# Prompt Behavior Tests

This directory contains **isolated tests** for voting sensitivity and answer novelty prompts. Instead of running full multi-agent coordination, these tests send carefully crafted contexts directly to models to verify that our prompt modifications actually affect behavior.

## Purpose

Test whether our `voting_sensitivity` and `answer_novelty_requirement` parameters actually change model behavior:
- **Lenient** → Should vote YES more easily
- **Balanced** → Should apply detailed evaluation criteria
- **Strict** → Should require high standards before voting YES

## Directory Structure

```
prompt_behavior/
├── contexts/                          # Test scenarios
│   ├── scenario_1_good_answer.json
│   ├── scenario_2_mediocre_answer.json
│   ├── scenario_3_similar_answers.json
│   └── scenario_4_obvious_gaps.json
├── test_voting_sensitivity.py         # Main test runner
└── README.md                          # This file
```

## Context Scenario Format

Each scenario is a JSON file with:

```json
{
  "name": "Human-readable name",
  "description": "What this tests",
  "original_message": "The user's question",
  "existing_answers": {
    "agent_a": "First answer text...",
    "agent_b": "Second answer text..."
  },
  "expected_behavior": {
    "lenient": "vote or new_answer",
    "balanced": "new_answer (reason)",
    "strict": "new_answer (reason)"
  }
}
```

### Optional Fields

For testing answer novelty:
```json
{
  "novelty_test": {
    "proposed_answer": "A new answer to test similarity against",
    "similarity_to_agent_a": 0.75,
    "expected_rejection": {
      "lenient": false,
      "balanced": true,
      "strict": true
    }
  }
}
```

## Running Tests

### Test All Scenarios

```bash
# Use default model (gemini-2.5-flash)
uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py

# Use specific model
uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py --model gpt-4o
```

### Test Specific Scenario

```bash
uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py \
  --scenario scenario_1_good_answer
```

### Save Results

```bash
uv run python massgen/tests/prompt_behavior/test_voting_sensitivity.py \
  --output results.json
```

## Example Output

```
Testing Voting Sensitivity Prompts
Model: gemini-2.5-flash
Scenarios: 4

Testing: Good Comprehensive Answer
  Testing lenient sensitivity...
    System message: 616 chars
    User message: 1309 chars
    Tools: 2 provided
    Calling gemini-2.5-flash... ✓ vote
  Testing balanced sensitivity...
    System message: 772 chars
    User message: 1309 chars
    Tools: 2 provided
    Calling gemini-2.5-flash... ✓ vote
  Testing strict sensitivity...
    System message: 920 chars
    User message: 1309 chars
    Tools: 2 provided
    Calling gemini-2.5-flash... ✓ new_answer

Summary of Results

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Scenario           ┃      Lenient       ┃      Balanced      ┃       Strict       ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Good               │ vote               │ vote               │ new_answer         │
│ Comprehensive      │ (exp: vote)        │ (exp: vote or      │ (exp: new_answer)  │
│ Answer             │                    │  new_answer)       │                    │
└────────────────────┴────────────────────┴────────────────────┴────────────────────┘

Test Statistics:
  Total tests run: 12
  Successful: 12
  Failed/unclear: 0

✓ All tests completed successfully!
```

**Color Coding**:
- 🟢 Green: Actual matches expected behavior
- 🔴 Red: Actual doesn't match expected
- 🟡 Yellow: Unclear response or acceptable alternative

## Current Status

✅ **Fully Implemented and Ready to Use**

The test framework is complete:
- ✅ Load scenario contexts from JSON files
- ✅ Build full prompts with different sensitivity levels using `MessageTemplates`
- ✅ Call Gemini and OpenAI models via their backends
- ✅ Parse responses to detect vote vs new_answer tool choices
- ✅ Display results in color-coded tables
- ✅ Save detailed results to JSON for analysis

**Supported Models**: Any Gemini or OpenAI model (gemini-*, gpt-*, o1, o3, etc.)

## Environment Setup

Before running tests, ensure you have the required API keys:

```bash
# Add to your .env file or export directly
export GEMINI_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

The test runner will automatically detect the model type from the name and use the appropriate backend:
- Models starting with `gemini-*` use `GeminiBackend` with `GEMINI_API_KEY`
- Models starting with `gpt-*` or `o*` use `OpenAIBackend` with `OPENAI_API_KEY`

**Note**: You only need the API key for the model you're testing. For example, if testing `gemini-2.5-flash`, only `GEMINI_API_KEY` is required.

## Example Scenarios

### Scenario 1: Good Comprehensive Answer
- **Expected**: Lenient votes YES, Balanced might vote, Strict might request improvements
- **Tests**: Whether strict criteria actually make agents more critical

### Scenario 2: Mediocre Incomplete Answer
- **Expected**: Lenient might vote, Balanced/Strict should provide new answers
- **Tests**: Whether evaluation criteria detect incomplete answers

### Scenario 3: Two Similar Answers
- **Expected**: All should vote (can't add novel content)
- **Tests**: Answer novelty requirement prevents rephrasing

### Scenario 4: Answer with Obvious Gaps
- **Expected**: Balanced/Strict should provide new answers with missing info
- **Tests**: Whether prompts help agents identify gaps

## Adding New Scenarios

Create a new JSON file in `contexts/`:

```bash
cat > massgen/tests/prompt_behavior/contexts/scenario_5_custom.json << 'EOF'
{
  "name": "Your Test Case",
  "description": "What you're testing",
  "original_message": "The question",
  "existing_answers": {
    "agent_a": "An answer"
  },
  "expected_behavior": {
    "lenient": "vote",
    "balanced": "new_answer",
    "strict": "new_answer"
  }
}
EOF
```

## Interpreting Results

Look for these patterns:
- ✅ **Lenient votes more often** than balanced/strict → Working as intended
- ✅ **Strict provides more new answers** for mediocre content → Working as intended
- ❌ **No difference between levels** → Prompts may need adjustment
- ❌ **All levels behave the same** → Model may ignore criteria

## Future Enhancements

- [x] Integrate with actual model backends (Gemini + OpenAI)
- [ ] Add statistical analysis (run each scenario N times for consistency)
- [ ] Test answer novelty requirement separately
- [ ] Add more edge case scenarios
- [ ] Support testing with multiple models in parallel
- [ ] Generate benchmarking reports with charts
- [ ] Add adversarial scenarios (trick questions, ambiguous cases)
- [ ] Support Claude, Grok, and other providers
- [ ] Add confidence scoring for tool choice detection

## Related Files

- `massgen/message_templates.py` - Where prompts are defined
- `massgen/orchestrator.py` - Where prompts are used in coordination
- `massgen/tests/test_config_builder.py` - Unit tests for config builder
