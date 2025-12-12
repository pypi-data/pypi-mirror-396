Review the implementation for correctness, style, and best practices.

Read the requirements.md file from previous steps (see Available Artifacts below) to verify they are met.

Based on your review, determine if the feature needs revision or is complete:
- If there are issues, bugs, or improvements needed → set needs_revision: true (workflow will return to planning)
- If the implementation is satisfactory and meets requirements → set needs_revision: false (workflow will proceed to summary)

Write a review.md file to: {{ step_dir }}/review.md with your findings.

IMPORTANT: Your output must include a "needs_revision" boolean field indicating whether changes are needed.

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}

{% endif %}
