{% extends "base.md" %}

{% block agent %}
If available, use a sub-agent specialized for requirements gathering or user interviews. Otherwise, proceed with a general-purpose agent or continue without a sub-agent.
{% endblock %}

{% block goal %}
Collect requirements for a new feature to be added to the project.
{% endblock %}

{% block content %}
* Prompt the user for details about the feature they want to add.
* Ask clarifying questions if needed, then document the requirements clearly.
* Write a requirements.md file to: {{ step_dir }}/requirements.md
* Before completing the step, ask the user to review the requirements and confirm they are correct.
{% endblock %}
