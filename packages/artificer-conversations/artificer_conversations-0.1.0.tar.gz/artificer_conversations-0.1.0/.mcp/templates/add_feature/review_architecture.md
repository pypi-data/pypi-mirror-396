Review the project architecture and determine how this feature should be integrated.

## Task
You must perform an architectural review before planning implementation. This is a critical step to prevent complexity creep and maintain system simplicity.

### Steps to Complete:

1. **Read the existing ARCHITECTURE.md** (if it exists in the project root)
   - Understand the current architectural principles
   - Identify the core components and their responsibilities
   - Note any intentional constraints or limitations

2. **Analyze where the feature fits**
   - How does this feature align with existing architectural principles?
   - Which components will be affected?
   - Are there existing patterns we should follow?

3. **Identify simplifications needed** (CRITICAL)
   - What can be simplified or removed before adding this feature?
   - Are there redundant components that can be eliminated?
   - Can we refactor to make the system simpler before extending it?

4. **Determine refactoring requirements**
   - What needs to be refactored to cleanly support this feature?
   - Are there architectural improvements we should make first?

5. **Update ARCHITECTURE.md**
   - Document how this feature changes the architecture
   - Update component descriptions
   - Add to the "Recent Changes" section
   - If ARCHITECTURE.md doesn't exist, create it using the template structure
   - Save changes to ARCHITECTURE.md

## Requirements from Previous Step
{% if result %}
{{ result.summary }}

**Requirements document**: {{ result.artifact.path }}
{% endif %}

{% if artifacts %}
## Available Artifacts
{% for artifact in artifacts %}
- **{{ artifact.name }}**: {{ artifact.description or 'No description' }}
  - Path: {{ artifact.path }}
{% endfor %}
{% endif %}

## Critical Questions to Answer

1. **What can be removed or simplified?**
   Think about: unused code, redundant abstractions, over-engineered solutions, unnecessary features

2. **How does this feature fit the current architecture?**
   Does it align with existing patterns? Does it require architectural changes?

3. **What are the architectural risks?**
   Could this feature introduce complexity? Does it violate any architectural principles?

4. **What refactorings should happen first?**
   Are there cleanups or improvements that should precede this implementation?

## Deliverables

Create or update ARCHITECTURE.md in the project root with:

1. **Architecture Overview** (if not present)
   - Core principles and design philosophy
   - Key components and responsibilities
   - Intentional constraints

2. **Impact Analysis** (new section for this feature)
   - Where the feature fits in the architecture
   - Components affected
   - Simplifications made to accommodate the feature

3. **Recent Changes** (append)
   - Date and feature name
   - What changed architecturally
   - What was removed or simplified
   - Rationale

## Philosophy

**Remember**: The goal is not just to add features, but to maintain architectural integrity.

Every feature should make the system better, not just bigger. If we can't identify something to simplify or remove, we may be adding unnecessary complexity.

Think like an architect pruning a garden, not just planting new seeds.
