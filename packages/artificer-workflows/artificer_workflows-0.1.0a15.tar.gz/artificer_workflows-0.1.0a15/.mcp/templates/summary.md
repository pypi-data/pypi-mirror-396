{% extends "base.md" %}

{% block agent %}
If available, use a sub-agent specialized for documentation or summarization. Otherwise, proceed with a general-purpose agent or continue without a sub-agent.
{% endblock %}

{% block goal %}
Create a comprehensive summary of the completed feature implementation.
{% endblock %}

{% block content %}
* Review all artifacts and work completed during this workflow execution.
*Write a summary.md file to: {{ step_dir }}/summary.md that includes:
** Overview of what was implemented
** Key implementation decisions made
** Test results and quality checks
** Any notable challenges or considerations
** Final status of the feature
{% endblock %}
