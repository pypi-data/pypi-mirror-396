---
name: case-study-writer
description: Use when creating case studies to document MassGen features. MassGen follows case-driven development - each version has an associated case study. Covers preparation (config creation, recording guide) and writing phases. Case studies should demonstrate self-evolution capabilities.
---

# Case Study Writer

MassGen follows **case-driven development**. Each version is documented with a case study.

## Primary Focus: Self-Evolution

Case studies should showcase how new features enable MassGen self-evolution:
- Bug fixing / SWEbench-style tasks
- New feature implementation
- Case study creation (meta-documentation)
- Market analysis
- PR submission and self-review

## Location

- Case studies: `docs/source/examples/case_studies/`
- Configs: `massgen/configs/tools/{category}/`
- Resources: `massgen/configs/resources/`

## Two-Phase Workflow

### Phase 1: Preparation (Before User Recording)

1. **Internalize template**: Read `docs/source/examples/case_studies/case-study-template.md` and existing case studies
2. **Analyze design doc**: Extract key capabilities and improvements
3. **Propose examples**: 2-3 concrete, runnable examples centered on new feature + self-evolution aspect
4. **Create config files**: See config creation rules below
5. **Create RECORDING_GUIDE.md** with:
   - Complete setup commands
   - Exact CLI commands
   - Expected results checklist (✅ succeed vs ❌ fail)
   - Outputs/logs to capture
   - Warnings (e.g., "DO NOT rm -rf .massgen/")
6. Confirm user is ready to record

### Phase 2: Case Study Writing (After User Recording)

7. Review outputs, logs, artifacts from user
8. Verify features are demonstrated properly
9. If not properly demonstrated, iterate with new examples
10. Write case study using REAL recorded outputs
11. Save to `docs/source/examples/case_studies/`

## Config Creation Rules

**CRITICAL: Read existing configs first, never hallucinate properties!**

1. **Read first**: Check 2-3 existing configs in `massgen/configs/tools/{category}/` and `massgen/configs/basic/multi/`
2. **Never invent**: Only use properties found in existing examples
3. **Verify placement**:
   - `context_paths` → orchestrator level (NOT per-agent)
   - `filesystem.cwd` → per-agent
   - `enable_image_generation` → backend level

**File naming**: `{agent1}_{agent2}_{feature}.yaml`

**Model preferences**: GPT-5 variants (gpt-5-nano, gpt-5-mini) over GPT-4o for cost

**Config structure**:
```yaml
agents:
  - id: "agent_a"
    backend:
      type: "openai"
      model: "gpt-5-mini"
    filesystem:
      cwd: "workspace1"
    system_message: "..."  # Both agents should have identical system_message

  - id: "agent_b"
    backend:
      type: "openai"
      model: "gpt-5-nano"
    filesystem:
      cwd: "workspace2"
    system_message: "..."  # Same as agent_a

orchestrator:
  snapshot_storage: "snapshots"
  agent_temporary_workspace: "agent_temp"

filesystem:
  context_paths:
    - path: "massgen/configs/resources/v{X.Y.Z}-example/{subdir}"
      permission: "read"

ui:
  display_type: "rich_terminal"
  logging_enabled: true
```

**Key rules**:
- Unique workspace per agent
- Copy COMPLETE files to resource directories (not partials)
- Include `session_storage` ONLY for multiturn
- Resource pattern: `massgen/configs/resources/v{X.Y.Z}-example/{subdirectory}/`

## Templates and Examples

**Template**: `docs/source/examples/case_studies/case-study-template.md`

**Example**: `docs/source/examples/case_studies/multimodal-case-study-video-analysis.md`

## Quality Standards

- **Accuracy**: Every command and output must be real and verified
- **Clarity**: Write for first-time users
- **Completeness**: Include all setup, commands, explanations
- **Consistency**: Match existing case study style
- **Practicality**: Focus on realistic scenarios

## File Creation Policy

**Create only**:
- Config files for examples
- RECORDING_GUIDE.md
- Final case study markdown

**Do NOT create**:
- README files
- Unnecessary documentation

## Important Guidelines

- Don't write case study until you have REAL validated output
- Use Write tool to create actual config files
- Never suggest cleanup commands that delete logs
- Ask clarifying questions when design doc is ambiguous
- Ensure case study tells coherent problem→solution story
