{% block agent %}{% endblock %}

# Goal
{% block goal %}{% endblock %}

{% block content %}{% endblock %}

# Common
* Create a plan to achieve the goal of this step.
* Write a TODO.md file to: {{ step_dir }}/TODO.md to track the tasks needed to complete this step.
* Update the TODO.md file as tasks are completed.

{% if artifacts %}
## Available Artifacts
Previous steps have created the following artifacts:
{% for artifact in artifacts %}
- {{ artifact.name }}{% if artifact.description %}: {{ artifact.description }}{% endif %}
  Path: {{ artifact.path }}
{% endfor %}
{% endif %}
