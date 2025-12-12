Create an implementation plan for the feature.

Read the requirements.md file from previous steps to understand what needs to be implemented.

Break down the work into clear, actionable steps.

Write a plan.md file to: {{ step_dir }}/plan.md

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}

{% endif %}
