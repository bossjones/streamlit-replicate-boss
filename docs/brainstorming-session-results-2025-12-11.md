# Brainstorming Session Results

**Session Date:** 2025-12-11
**Facilitator:** Business Analyst Mary
**Participant:** bossjones

## Executive Summary

**Topic:** Specific features or improvements

**Session Goals:** Explore limitations and generate feature ideas to address the core problem of being limited to one model/endpoint in the Streamlit image generation app.

**Techniques Used:** Five Whys Deep Dive, Lessons Learned Extraction

**Total Ideas Generated:** 36

### Key Themes Identified:

- **Flexibility over specialization:** The app should be a flexible creative tool, not a single-purpose generator
- **Workflow continuity:** Eliminate context switching to maintain creative flow
- **Configuration management:** Tools to handle complexity of multiple models and settings
- **Discovery and inspiration:** Features that help users understand and explore model capabilities
- **Investment leverage:** Features that maximize value from custom-trained models

## Technique Sessions

### Five Whys Deep Dive

**Starting Point:** Limitation - "Limited to one model/endpoint"

**The Chain of Reasoning:**
1. **Why is being limited to one model/endpoint a limitation?** → Can't switch between different model endpoints (e.g., helldiver tactical armor, starship trooper uniform, firebeardjones)
2. **Why do you need to switch between different model endpoints?** → Each model generates different styles, allowing flexibility for different needs
3. **Why do you need that flexibility?** → Currently requires visiting different Replicate pages, need unified interface for efficiency
4. **Why is creating images more efficiently important?** → You've invested time training custom models and want to leverage that investment
5. **Why is it important to use your custom retrained models?** → Without flexibility, the app becomes a "one-shot pony" instead of a flexible tool for creative expression

**Root Cause Discovered:** The app is too rigid, limiting creative expression and flexibility. The core need is for a flexible creative platform that supports multiple models efficiently.

**Ideas Generated During Session:**
- Model selector dropdown with custom models
- Quick-switch between models without leaving the app
- Preset configurations per model (trigger words, settings)
- Save all settings (full parameter configurations)
- Example images (pull from Replicate)
- Auto-load examples
- Default model selection
- Custom model management interface (UI + config)
- Model favorites and search/filter
- Parameter presets with tags/categories
- Share presets (file export)
- Model preview cards
- Auto-suggest trigger words
- Model comparison mode
- And 22 more related ideas...

## Idea Categorization

### Immediate Opportunities

_Ideas ready to implement now_

1. **Model selector dropdown with custom models** - Core functionality to enable model switching
2. **Quick-switch between models without leaving the app** - Maintains workflow continuity
3. **Preset configurations per model (trigger words, settings)** - Essential for proper model usage
4. **Save all settings (full parameter configurations)** - Configuration persistence
5. **Example images (pull from Replicate model pages)** - Discovery and inspiration
6. **Auto-load examples** - Discovery automation when selecting models
7. **Default model selection** - Better user experience with model memory

### Future Innovations

_Ideas requiring development/research_

- Custom model management interface (UI form + config file)
- Model favorites (star frequently used models)
- Model search/filter (find by tags like "tactical", "uniform", "character")
- Model grouping (organize into categories)
- Custom model import (add new models via UI, not just code)
- Model history (track which models used and when)
- Parameter presets (save named configurations like "High Quality", "Fast Generation")
- Share presets (export/import preset files)
- Model preview cards (show example image, trigger words, key settings)
- Auto-suggest trigger words (auto-fill or suggest when selecting model)
- Model comparison mode (generate same prompt with multiple models side-by-side)
- Preset inheritance (base presets that others can extend)
- Version control for presets (track changes to saved configurations)
- Preset tags/categories (organize presets)
- Quick preset switcher (keyboard shortcuts or buttons)
- Preset preview (see settings before applying)
- Model + Preset combos (save which preset works best with which model)
- Batch preset application (apply preset to multiple models)
- Preset templates (start from templates)
- Settings diff view (compare current vs saved preset)
- Example gallery per model (display examples when selecting)
- "Try this prompt" button (click example to use its prompt)
- Model metadata display (show model info: runs, cost, examples)

### Moonshots

_Ambitious, transformative concepts_

- Preset marketplace (community-shared parameter configurations)
- Batch generation across models (generate one prompt with multiple selected models)
- Model + Preset combos with AI recommendations
- Import/Export workflow for entire model libraries
- Model comparison view (side-by-side example images from different models)
- Model presets library (save favorite prompt + model combinations)

### Insights and Learnings

_Key realizations from the session_

**Key Themes Identified:**
- **Flexibility over specialization:** The app should be a flexible creative tool, not a single-purpose generator
- **Workflow continuity:** Eliminate context switching to maintain creative flow
- **Configuration management:** Tools to handle complexity of multiple models and settings
- **Discovery and inspiration:** Features that help users understand and explore model capabilities
- **Investment leverage:** Features that maximize value from custom-trained models

**Surprising Connections:**
- The technical limitation (one model) connects to a deeper need for creative expression
- Model management and preset management are interdependent—solving one requires solving the other
- Example images serve both discovery (what can this model do?) and inspiration (try this prompt)

**Key Realizations:**
- The problem isn't just "add more models"—it's "create a flexible creative platform"
- Configuration management is as important as model selection
- User experience matters as much as technical capability
- Root cause: The app is too rigid, limiting creative expression and flexibility
- Core need: A flexible creative platform that supports multiple models efficiently
- Pain point: Context switching between multiple Replicate pages breaks creative flow
- Investment: You've trained custom models and want to leverage that investment

## Action Planning

### Top 3 Priority Ideas

#### #1 Priority: Model selector dropdown with custom models

- **Rationale:** It directly addresses the core problem—enabling model selection so users can switch between custom models
- **Next steps:**
  1. Design the model data structure (model ID, name, trigger words, endpoint)
  2. Create a configuration file/format to store custom models
  3. Add a Streamlit selectbox/dropdown in the sidebar
  4. Update the API call to use the selected model endpoint
  5. Test with your existing models (helldiver, starship-trooper, firebeardjones)
- **Resources needed:**
  - Streamlit selectbox component
  - Configuration storage (YAML/JSON file or secrets.toml)
  - Replicate API integration (already exists)
  - Your custom model endpoints and trigger words
- **Timeline:** Estimate 2-4 hours for initial implementation and testing

#### #2 Priority: Quick-switch between models without leaving the app

- **Rationale:** Maintains creative flow by avoiding context switching, keeping users in the creative zone
- **Next steps:**
  1. Ensure model selector updates immediately without page reload
  2. Preserve current prompt and settings when switching models
  3. Update UI to reflect the selected model (show trigger words, model info)
  4. Handle model-specific parameter differences gracefully
  5. Test rapid switching between multiple models
- **Resources needed:**
  - Streamlit session state management
  - Model metadata storage (trigger words, default settings)
  - UI update logic (reactive components)
  - Error handling for model switching edge cases
- **Timeline:** Estimate 3-5 hours (builds on Priority #1)

#### #3 Priority: Preset configurations per model (trigger words, settings)

- **Rationale:** Knowing how to trigger the model correctly is important. Presets handle trigger words and settings automatically so users can focus on creating
- **Next steps:**
  1. Design preset data structure (trigger words, default settings per model)
  2. Create preset storage (YAML/JSON file or database)
  3. Add preset selector/manager UI in sidebar
  4. Auto-apply preset when model is selected
  5. Allow manual override of preset values
  6. Test with your models' trigger words (HELLDIVERB01TACTICALARMOR, STARSHIPTROOPERUNIFORMWITHHELMET)
- **Resources needed:**
  - Preset storage system (file-based or config)
  - UI components for preset selection
  - Model-to-preset mapping logic
  - Trigger word injection into prompts
  - Settings override mechanism
- **Timeline:** Estimate 4-6 hours (builds on Priorities #1 and #2)

**Total estimated timeline:** 9-15 hours of development work

**Implementation order:** Sequential (each builds on the previous)

## Reflection and Follow-up

### What Worked Well

- The Five Whys technique effectively uncovered the root cause (flexibility and creative expression)
- Systematic idea generation built naturally on the root cause discovery
- Categorization helped prioritize actionable features
- Lessons Learned extraction provided strategic insights

### Areas for Further Exploration

- Technical architecture for model management system
- UI/UX design patterns for model selector and preset management
- Data storage and configuration management approaches
- Integration patterns with Replicate API for multiple models
- Error handling and edge cases for model switching

### Recommended Follow-up Techniques

- **SCAMPER Method** - For systematic product improvement of the existing app
- **What If Scenarios** - To explore edge cases and future possibilities
- **Analogical Thinking** - To learn from similar multi-model applications
- **First Principles Analysis** - To design the model management architecture from fundamentals

### Questions That Emerged

- How to handle model-specific parameter differences gracefully?
- What's the best way to store and manage model configurations (file-based vs database)?
- How to handle errors when switching between models?
- What's the optimal user experience flow for preset management?
- How to balance simplicity with flexibility in the UI?

### Next Session Planning

- **Suggested topics:** Technical architecture design, UI/UX mockups, implementation planning
- **Recommended timeframe:** After initial implementation of Priority #1
- **Preparation needed:** Review current codebase structure, identify integration points

---

_Session facilitated using the BMAD CIS brainstorming framework_

