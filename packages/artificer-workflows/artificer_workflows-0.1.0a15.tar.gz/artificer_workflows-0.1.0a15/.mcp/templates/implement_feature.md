{% extends "base.md" %}

{% block agent %}
If available, use a sub-agent specialized for code implementation. Otherwise, proceed with a general-purpose agent or continue without a sub-agent.
{% endblock %}

{% block goal %}
Implement the feature according to the plan.
{% endblock %}

{% block content %}
* Read the requirements.md and plan.md files from previous steps (see Available Artifacts below).
* Make the necessary code changes to implement the feature as per the plan.
* Ensure to follow coding standards and best practices.
* Test the implementation to verify it meets the requirements.
* Write an implementation.md file to: {{ step_dir }}/implementation.md documenting what was implemented.
{% endblock %}
