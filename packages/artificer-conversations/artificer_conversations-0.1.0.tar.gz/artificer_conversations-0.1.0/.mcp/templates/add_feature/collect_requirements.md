Gather requirements for the feature from the user.

Ask clarifying questions if needed, then document the requirements clearly.

Write a requirements.md file to: {{ step_dir }}/requirements.md

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}

{% endif %}
