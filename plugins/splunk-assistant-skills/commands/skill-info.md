---
name: skill-info
description: Show detailed information about a specific Splunk skill
arguments:
  - name: skill
    description: "The skill name (e.g., splunk-search, splunk-job)"
    required: true
---

# Skill Information: {{ skill }}

Display detailed documentation for the specified Splunk Assistant skill.

## Instructions

Read the SKILL.md file for the requested skill and present:

1. **Purpose**: What the skill does
2. **Triggers**: Keywords that activate this skill
3. **CLI Commands**: Available `splunk-as` commands with examples
4. **API Endpoints**: Underlying Splunk REST API endpoints
5. **Best Practices**: Tips for effective usage
6. **Related Skills**: Other skills that work together

## Skill Location

The skill documentation is at:
`${CLAUDE_PLUGIN_ROOT}/skills/{{ skill }}/SKILL.md`

## Available Skills

- splunk-assistant
- splunk-search
- splunk-job
- splunk-export
- splunk-metadata
- splunk-lookup
- splunk-kvstore
- splunk-savedsearch
- splunk-alert
- splunk-app
- splunk-security
- splunk-rest-admin
- splunk-tag
- splunk-metrics

If the skill name is not found, suggest similar skills from the list above.
