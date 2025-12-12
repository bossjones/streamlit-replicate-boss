# Product Brief: streamlit-replicate-boss

**Date:** 2025-12-11
**Author:** bossjones
**Status:** Draft for PM Review

---

## Executive Summary

**streamlit-replicate-boss** is a personal creative tool that transforms a single-model AI image generation application into a flexible, multi-model creative platform. The product enables creators to use multiple AI models (including custom-trained models) within a unified Streamlit interface, eliminating the need to context-switch between different Replicate pages. The core value proposition is **workflow continuity** and **time efficiency**—reducing the friction of managing multiple model endpoints while maximizing the value of custom-trained model investments.

**Primary Problem:** Current implementation is locked to a single model endpoint, forcing users to visit multiple Replicate pages to access different models, breaking creative flow and wasting time.

**Target Market:** Personal creative tool for the author (bossjones) exclusively.

**Key Value Proposition:** Unified interface for multiple AI image generation models with preset management, eliminating context switching and enabling seamless creative workflows.

---

## Problem Statement

### Current State Frustrations

1. **Single Model Limitation**: The application is hardcoded to use one Replicate model endpoint (`REPLICATE_MODEL_ENDPOINTSTABILITY`), preventing access to multiple models without code changes.

2. **Context Switching Overhead**: To use different models (e.g., helldiver tactical armor, starship trooper uniform, firebeardjones), users must:
   - Navigate to different Replicate model pages
   - Copy/paste prompts and settings between interfaces
   - Lose workflow continuity and creative momentum

3. **Underutilized Investment**: Custom-trained models (helldiver, starship-trooper, firebeardjones) cannot be easily leveraged within the existing application, reducing ROI on model training investments.

4. **Configuration Fragmentation**: Model-specific settings (trigger words, optimal parameters) are not preserved or easily accessible, requiring manual re-entry each time.

### Quantifiable Impact

- **Time Loss**: Estimated 2-5 minutes per model switch (navigation, re-entry of settings, context re-establishment)
- **Creative Flow Disruption**: Breaking focus to switch contexts reduces creative output quality and quantity
- **Investment Waste**: Custom models remain underutilized due to access friction

### Why Existing Solutions Fall Short

- **Replicate's Native Interface**: Requires separate page navigation for each model, no unified workflow
- **Current Application**: Single-model architecture doesn't support the flexibility needed for multi-model creative work
- **Manual Workarounds**: Copy-paste between interfaces is error-prone and time-consuming

### Urgency

The problem is **actively blocking creative productivity** and preventing full utilization of custom-trained model investments. Each creative session involves multiple model switches, compounding the time loss and frustration.

---

## Proposed Solution

### Core Approach

Transform the single-model Streamlit application into a **flexible multi-model creative platform** that:

1. **Unifies Model Access**: Single interface supporting multiple Replicate model endpoints (including custom-trained models)
2. **Preserves Workflow Continuity**: Enable model switching without leaving the application or losing context
3. **Manages Configuration Complexity**: Automate model-specific settings (trigger words, optimal parameters) through preset management
4. **Maximizes Investment Value**: Make custom-trained models as accessible as standard models

### Key Differentiators

| Feature | Current State | Proposed Solution |
|---------|--------------|-------------------|
| Model Access | Single hardcoded endpoint | Dynamic model selector with custom model support |
| Workflow | Context switching required | Seamless in-app model switching |
| Configuration | Manual re-entry | Preset-based automation per model |
| Custom Models | Not accessible | First-class support with trigger word management |

### Why This Will Succeed

1. **Addresses Root Cause**: Solves the flexibility and creative expression limitation identified in brainstorming
2. **Leverages Existing Investment**: Makes custom-trained models immediately usable
3. **Builds on Solid Foundation**: Extends proven Streamlit architecture with minimal disruption
4. **Personal Use Case**: Designed for specific, known user needs with clear success metrics

### Ideal User Experience

1. User opens application → sees model selector with all available models (standard + custom)
2. Selects model → preset automatically loads (trigger words, optimal settings)
3. Adjusts prompt and generates → seamless workflow maintained
4. Switches to different model → instant switch, preset loads, creative flow continues
5. Saves favorite configurations → reusable presets for future sessions

---

## Target Users

### Primary User Segment

**Profile**: bossjones (the author)
- **Role**: Creative professional / developer using AI image generation for personal projects
- **Technical Skill**: Intermediate to advanced (capable of training custom models, managing API integrations)
- **Current Problem-Solving Method**: Manual navigation between Replicate pages, copy-paste workflows
- **Specific Pain Points**:
  - Context switching breaks creative flow
  - Time wasted on repetitive configuration entry
  - Custom models underutilized due to access friction
- **Goals**: 
  - Maximize creative output efficiency
  - Leverage custom-trained model investments
  - Maintain creative momentum without interruption
- **Usage Pattern**: Regular use for creative projects, multiple model switches per session

### Secondary User Segment

**N/A - Personal Use Only**

*This is a personal creative tool designed exclusively for the author's use. No secondary user segment is planned or required.*

---

## Goals and Success Metrics

### Business Objectives

**N/A - Personal Project**

*Note: As a personal project, traditional business objectives (revenue, market share) do not apply. Success is measured through personal productivity and creative output improvements.*

### User Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Time Saved per Model Switch** | 2-5 minutes → <30 seconds | Manual timing of workflow before/after |
| **Context Switching Reduction** | Eliminate external navigation | Track in-app model switches vs. external page visits |
| **Custom Model Utilization** | 3+ custom models actively used | Count of unique models used per session |
| **Workflow Continuity** | Zero external navigation during creative session | User self-reporting of flow state |
| **Configuration Reuse** | 80%+ of sessions use saved presets | Track preset usage vs. manual configuration |

### Key Performance Indicators (KPIs)

1. **Efficiency Gain**: Time per model switch reduced by 80%+ (from 2-5 min to <30 sec)
2. **Adoption Rate**: All 3 custom models (helldiver, starship-trooper, firebeardjones) actively used within first week
3. **Preset Utilization**: At least 2 presets created and reused per model within first month
4. **Session Quality**: User reports improved creative flow and reduced frustration in usage logs

---

## Strategic Alignment and Financial Impact

### Financial Impact

**Personal Project Context**: No direct revenue or cost implications. Investment is time-based development effort.

**Value Quantification**:
- **Time Investment**: Estimated 9-15 hours development (from brainstorming priorities)
- **Time Savings**: 2-5 minutes per model switch × multiple switches per session × regular usage = significant cumulative time savings
- **ROI**: Improved creative productivity and better utilization of custom model training investments

**Cost Considerations**:
- Replicate API usage costs remain the same (no change in API calls)
- No additional infrastructure costs (Streamlit app architecture unchanged)
- Development time is the primary investment

### Company Objectives Alignment

**N/A - Personal Project**

*Note: As a personal project, company alignment is not applicable. The project aligns with personal productivity and creative goals.*

### Strategic Initiatives

**Personal Strategic Goals**:
1. **Productivity Enhancement**: Reduce time waste in creative workflows
2. **Investment Maximization**: Fully utilize custom-trained model investments
3. **Tool Refinement**: Build a flexible creative platform that grows with needs
4. **Skill Development**: Enhance Streamlit and API integration expertise

---

## MVP Scope

### Core Features (Must Have)

**Priority 1: Model Selector with Custom Models**
- Dropdown/selectbox in sidebar for model selection
- Support for multiple Replicate model endpoints
- Configuration file (YAML/JSON) for custom model definitions
- Model data structure: `{id, name, endpoint, trigger_words, default_settings}`
- **Estimated Effort**: 2-4 hours

**Priority 2: Quick-Switch Between Models**
- Instant model switching without page reload
- Preserve current prompt and settings when switching
- Update UI to reflect selected model (show trigger words, model info)
- Handle model-specific parameter differences gracefully
- **Estimated Effort**: 3-5 hours (builds on Priority 1)

**Priority 3: Preset Configurations per Model**
- Preset data structure (trigger words, default settings per model)
- Preset storage system (file-based: YAML/JSON)
- Preset selector/manager UI in sidebar
- Auto-apply preset when model is selected
- Allow manual override of preset values
- **Estimated Effort**: 4-6 hours (builds on Priorities 1 & 2)

**Total MVP Effort**: 9-15 hours

### Out of Scope for MVP

**Explicitly Excluded** (from brainstorming "Future Innovations"):
- Custom model management UI (add models via code/config file for MVP)
- Model favorites/starring system
- Model search/filter by tags
- Model grouping/categories
- Model history tracking
- Preset sharing/export functionality
- Preset marketplace
- Model comparison mode (side-by-side generation)
- Batch generation across multiple models
- Example gallery per model (pull from Replicate)
- Model metadata display (runs, cost, examples)

**Rationale**: MVP focuses on core functionality (model switching + presets). Advanced features can be added post-MVP based on usage patterns.

### MVP Success Criteria

1. **Functional Requirements**:
   - ✅ User can select from 3+ models (including custom models) via dropdown
   - ✅ Model switching happens instantly without page reload
   - ✅ Presets auto-load when model is selected
   - ✅ Trigger words are automatically injected into prompts
   - ✅ Settings persist when switching models

2. **Performance Requirements**:
   - Model switch completes in <1 second
   - No data loss when switching models (prompt/settings preserved)

3. **Usability Requirements**:
   - Zero external navigation required during creative session
   - All 3 custom models (helldiver, starship-trooper, firebeardjones) accessible
   - At least 1 preset per model configured and working

4. **Success Validation**:
   - User completes a creative session using 3+ different models without leaving the app
   - Time per model switch reduced to <30 seconds
   - User reports improved workflow continuity

---

## Post-MVP Vision

### Phase 2 Features

**Model Management Enhancements**:
- Custom model management UI (add/edit models via form, not just config file)
- Model favorites/starring for frequently used models
- Model search/filter by tags (e.g., "tactical", "uniform", "character")
- Model grouping/categories for organization
- Model history tracking (which models used, when)

**Preset System Enhancements**:
- Preset sharing/export (save presets as files, import from others)
- Preset tags/categories for organization
- Preset templates (starter presets for common use cases)
- Settings diff view (compare current vs. saved preset)
- Version control for presets (track changes)

**Discovery and Inspiration**:
- Example gallery per model (pull example images from Replicate model pages)
- "Try this prompt" button (click example to use its prompt)
- Model preview cards (show example image, trigger words, key settings)
- Model metadata display (runs, cost, examples from Replicate)

### Long-term Vision (1-2 Years)

**Advanced Workflow Features**:
- Model comparison mode (generate same prompt with multiple models side-by-side)
- Batch generation across models (one prompt → multiple model outputs)
- AI-powered preset recommendations (suggest optimal presets based on prompt content)
- Workflow templates (save entire creative workflows: model sequence, prompts, settings)

**Personal Workflow Enhancements**:
- Export/import model configurations for backup/restore
- Personal preset library organization and management
- Personal examples gallery for inspiration

**Platform Expansion**:
- Support for other AI platforms beyond Replicate (if needed)
- Mobile/tablet interface for on-the-go creation (personal use)
- API access for programmatic image generation (personal automation)

### Expansion Opportunities

**Personal Project Focus** - All expansion opportunities are for personal use only:

1. **Enhanced Personal Workflows**: Advanced automation and workflow templates for personal creative projects
2. **Integration with Personal Tools**: Connect with other personal creative tools (image editors, workflow managers)
3. **Personal Documentation**: Document personal workflows and preset libraries for future reference
4. **Extended Platform Support**: Add support for additional AI platforms if personal needs expand

---

## Technical Considerations

### Platform Requirements

- **Platform**: Web application (Streamlit)
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge) - latest 2 versions
- **OS Support**: Any OS that runs Python 3.13+ and modern browsers
- **Performance Needs**: 
  - Fast model switching (<1 second)
  - Responsive UI during API calls
  - Efficient state management for multiple models
- **Accessibility Standards**: Not required (personal use only)

### Technology Preferences

**Current Stack** (to be maintained):
- **Runtime**: Python 3.13+
- **Web Framework**: Streamlit ≥1.50.0
- **Package Manager**: uv
- **API Client**: replicate ≥1.0.7
- **HTTP Client**: requests ≥2.32.5
- **UI Component**: streamlit-image-select ≥0.6.0

**New Components Needed**:
- **Configuration Management**: YAML or JSON for model/preset storage
- **State Management**: Streamlit session state (already in use, extend for multi-model)
- **File I/O**: Standard library for reading/writing config files

**Technology Constraints**:
- Must maintain compatibility with existing Streamlit architecture
- No database required (file-based configuration for MVP)
- No additional external services (Replicate API only)

### Architecture Considerations

**Current Architecture**:
- Single-page application with sidebar controls
- Two main functions: `configure_sidebar()` and `main_page()`
- Session state for generated images
- Direct Replicate API integration

**Proposed Architecture Changes**:
1. **Model Configuration Layer**:
   - YAML/JSON config file: `models.yaml` or `models.json`
   - Structure: `{models: [{id, name, endpoint, trigger_words, default_settings}]}`
   - Load at app startup, cache in session state

2. **Preset Management Layer**:
   - YAML/JSON config file: `presets.yaml` or `presets.json`
   - Structure: `{presets: [{id, name, model_id, trigger_words, settings}]}`
   - Link presets to models via `model_id`

3. **State Management Extensions**:
   - `st.session_state.selected_model` - Current model
   - `st.session_state.model_configs` - Loaded model configurations
   - `st.session_state.presets` - Loaded preset configurations
   - `st.session_state.current_preset` - Active preset

4. **UI Component Updates**:
   - Add model selector to `configure_sidebar()`
   - Add preset selector to `configure_sidebar()`
   - Update `main_page()` to use selected model endpoint
   - Display model info (trigger words, description) in sidebar

**Integration Points**:
- Model selector → updates `st.session_state.selected_model`
- Preset selector → applies preset settings to form
- Model change → triggers preset auto-load
- Form submission → uses selected model endpoint from config

**Error Handling**:
- Validate model endpoints before API calls
- Handle missing/invalid config files gracefully
- Provide user feedback for API errors
- Fallback to default model if selected model fails

---

## Constraints and Assumptions

### Constraints

1. **Development Time**: Personal project with limited time availability (9-15 hours estimated)
2. **Resource Limits**: Single developer (bossjones), no team support
3. **Technical Constraints**: 
   - Must work within Streamlit framework limitations
   - Replicate API rate limits and costs (unchanged, but awareness needed)
   - File-based configuration (no database for MVP)
4. **Scope Constraints**: MVP must be achievable in estimated timeframe
5. **Maintenance Constraints**: Personal project means ongoing maintenance is personal responsibility

### Key Assumptions

1. **User Behavior**:
   - User will actively use 3+ models regularly
   - Presets will be created and reused (not just one-time setup)
   - Model switching frequency: multiple times per creative session

2. **Technical Assumptions**:
   - Replicate API supports all custom model endpoints as expected
   - Model endpoints remain stable (no frequent changes)
   - Streamlit session state is sufficient for state management
   - File-based config is acceptable (no concurrent access issues)

3. **Market/Usage Assumptions**:
   - Personal use case remains primary (not planning for multi-user initially)
   - Custom models will continue to be trained/added over time
   - Workflow patterns will remain similar (text-to-image generation)

4. **Validation Assumptions**:
   - Time savings can be measured through user self-reporting
   - Success criteria are achievable with MVP scope
   - No major technical blockers will emerge during implementation

**Assumptions Needing Validation**:
- [ ] Replicate API behavior with custom model endpoints
- [ ] Optimal preset data structure (may need iteration)
- [ ] User's actual model switching frequency and patterns
- [ ] Whether file-based config scales or needs database later

---

## Risks and Open Questions

### Key Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Replicate API Changes** | High - Could break model endpoints | Low | Monitor Replicate updates, version pinning if possible |
| **Config File Complexity** | Medium - May become unwieldy with many models | Medium | Start simple (YAML), refactor to database if needed |
| **State Management Issues** | Medium - Streamlit state may not handle rapid switches | Low | Test thoroughly, use session state best practices |
| **Scope Creep** | High - Temptation to add Phase 2 features | Medium | Strictly adhere to MVP scope, document Phase 2 separately |
| **Time Overrun** | Medium - 9-15 hours may be optimistic | Medium | Prioritize core features, defer nice-to-haves |
| **Custom Model Compatibility** | Medium - Custom models may have different parameter requirements | Medium | Test with all 3 custom models early, handle edge cases |

### Open Questions

1. **Technical**:
   - How to handle model-specific parameter differences? (Some models may not support all parameters)
   - Best format for config files? (YAML vs JSON - YAML more readable, JSON more standard)
   - Should presets be model-specific or cross-model? (Starting model-specific, may expand later)
   - How to handle model endpoint errors gracefully? (Retry logic, fallback model?)

2. **User Experience**:
   - Should model switching clear the current prompt or preserve it? (Proposed: preserve)
   - How to display trigger words? (Auto-inject into prompt vs. show separately?)
   - Should presets be editable in-app or config-file only for MVP? (Config-file for MVP)
   - How to handle preset conflicts? (User override always wins)

3. **Future Planning**:
   - When to migrate from file-based to database? (If >10 models, though unlikely for personal use)
   - Personal tool only - no open-source or distribution plans
   - Integration with other tools? (Not in scope, but consider architecture)

### Areas Needing Further Research

1. **Replicate API Deep Dive**:
   - Confirm custom model endpoint format and requirements
   - Verify parameter compatibility across different model types
   - Research rate limits and best practices for multiple model calls

2. **Streamlit State Management**:
   - Best practices for complex state (multiple models, presets)
   - Performance implications of frequent state updates
   - Session persistence across page reloads

3. **Configuration Management Patterns**:
   - YAML vs JSON for readability vs. tooling support
   - Validation strategies for config files
   - Versioning and migration strategies for config changes

4. **User Workflow Analysis**:
   - Actual model switching patterns (frequency, sequence)
   - Most common preset configurations
   - Pain points in current workflow (beyond what's documented)

---

## Appendices

### A. Research Summary

**Brainstorming Session (2025-12-11)**:
- **Root Cause Identified**: App is too rigid, limiting creative expression and flexibility
- **Core Need**: Flexible creative platform supporting multiple models efficiently
- **Key Themes**: Flexibility over specialization, workflow continuity, configuration management, discovery/inspiration, investment leverage
- **Priority Features**: Model selector (Priority 1), Quick-switch (Priority 2), Presets (Priority 3)
- **Total Ideas Generated**: 36 ideas across immediate opportunities, future innovations, and moonshots

**Project Overview Analysis**:
- Current architecture: Single-model Streamlit app with basic image generation
- Technology stack: Python 3.13, Streamlit, Replicate API, standard libraries
- Key limitation: Hardcoded single model endpoint prevents multi-model usage

**Codebase Review**:
- Main entry: `streamlit_app.py` with `configure_sidebar()` and `main_page()` functions
- Current model: `REPLICATE_MODEL_ENDPOINTSTABILITY` from secrets
- State management: Uses `st.session_state` for generated images
- Extension points: Sidebar configuration, API call location, state management

### B. Stakeholder Input

**Primary Stakeholder: bossjones (Author/User)**
- **Vision**: Enable creators to use multiple AI models in one interface, reduce context switching
- **Success Metric**: Time saved vs. using multiple Replicate pages
- **Context**: Personal creative tool, personal project
- **Custom Models**: helldiver tactical armor, starship trooper uniform, firebeardjones
- **Priority**: Model selector → Quick-switch → Presets (sequential implementation)

**No Additional Stakeholders** (Personal Project)

### C. References

**Documentation**:
- Project Overview: `docs/project-overview.md`
- Brainstorming Results: `docs/brainstorming-session-results-2025-12-11.md`
- Workflow Status: `docs/bmm-workflow-status.yaml`

**Technical References**:
- Streamlit Documentation: https://docs.streamlit.io/
- Replicate API Documentation: https://replicate.com/docs
- Stability AI SDXL Model: https://replicate.com/stability-ai/sdxl

**Code References**:
- Main Application: `streamlit_app.py`
- Configuration: `.streamlit/config.toml`, `.streamlit/secrets.toml`
- Project Config: `bmad/bmm/config.yaml`

---

_This Product Brief serves as the foundational input for Product Requirements Document (PRD) creation._

_Next Steps: Handoff to Product Manager for PRD development using the `workflow prd` command._
