Implement the feature according to the plan.

Read the requirements.md and plan.md files from previous steps (see Available Artifacts below).

Write the code, making commits as appropriate.

Write an implementation.md file to: {{ step_dir }}/implementation.md documenting what was implemented.

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}

{% endif %}
