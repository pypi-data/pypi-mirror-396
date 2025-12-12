Create a comprehensive summary of the completed feature implementation.

Review all artifacts and work completed during this workflow execution.

Write a summary.md file to: {{ step_dir }}/summary.md that includes:
- Overview of what was implemented
- Key implementation decisions made
- Test results and quality checks
- Any notable challenges or considerations
- Final status of the feature

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}

{% endif %}
