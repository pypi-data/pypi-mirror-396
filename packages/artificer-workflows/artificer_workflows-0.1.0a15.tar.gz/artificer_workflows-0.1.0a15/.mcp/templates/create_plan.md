{% extends "base.md" %}

{% block agent %}
If available, use a sub-agent specialized for planning or architecture. Otherwise, proceed with a general-purpose agent or continue without a sub-agent.
{% endblock %}

{% block goal %}
Create an implementation plan for the feature.
{% endblock %}

{% block content %}
* Read the requirements.md file from previous steps to understand what needs to be implemented.
* Break down the work into clear, actionable steps.
* Estimate the time and resources needed for each step.
* Organize the steps in a logical order to ensure efficient implementation.
* Discuss the plan with the user to ensure it meets their expectations and adjust as necessary.
* Write a plan.md file to: {{ step_dir }}/plan.md
{% endblock %}
