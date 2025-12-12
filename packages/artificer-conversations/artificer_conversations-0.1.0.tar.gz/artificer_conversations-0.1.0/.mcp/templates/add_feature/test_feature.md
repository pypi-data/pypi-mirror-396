Test the implementation.

Run existing tests and add new tests as needed. If any tests fail, attempt to fix them.

Only use status=ERROR if you cannot resolve the failures.

Optionally, if there are test results to document, save them to: {{ step_dir }}/test_results.txt

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}

{% endif %}
