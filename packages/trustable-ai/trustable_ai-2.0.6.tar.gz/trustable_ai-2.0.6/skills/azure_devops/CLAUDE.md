---
context:
  purpose: "Battle-tested Azure DevOps REST API operations with markdown support and verification, preventing work item operation errors"
  problem_solved: "Raw Azure CLI commands lack markdown format support and are error-prone - wrong parameters, auth failures, malformed responses. This skill uses Azure DevOps REST API v7.1 with automatic markdown formatting, proper error handling, field mapping, and verification patterns."
  keywords: [azure-devops, skill, work-items, verification, ado]
  task_types: [implementation, integration, work-tracking]
  priority: medium
  max_tokens: 600
  children: []
  dependencies: [core, adapters/azure_devops]
---
# Azure DevOps Skill

## Purpose

Solves **markdown format support**, **Azure CLI limitations**, and **missing verification** by providing battle-tested Azure DevOps REST API operations with built-in error handling and verification.

Azure CLI commands have critical limitations:
- No markdown format support → descriptions render as code blocks
- Wrong field names → data loss (field ignored)
- Authentication expired → operation fails, unclear why
- Malformed WIQL → cryptic parse errors
- No verification → claim success but operation failed

This skill uses **Azure DevOps REST API v7.1** with **automatic markdown formatting, validation, error handling, field mapping, and verification**, making Azure DevOps operations reliable and properly formatted.

## Features

- **Markdown Format Support**: Automatically sets markdown format for description fields (System.Description, Microsoft.VSTS.Common.AcceptanceCriteria, Microsoft.VSTS.TCM.ReproSteps)
- **Work Item CRUD**: Create, read, update, delete with verification via REST API
- **Single-Step Creation**: Sets all fields including iteration in one request (no two-step pattern)
- **Sprint Operations**: List sprints, assign work items (correct iteration path format)
- **Queries**: WIQL queries with batch fetching for large result sets
- **Field Mapping**: Generic fields → Azure DevOps-specific fields
- **Verification**: All operations verify results against external source of truth
- **REST API v7.1**: Uses Azure DevOps REST API for full feature support

## Usage

```python
from skills.azure_devops import AzureDevOpsSkill

skill = AzureDevOpsSkill()

# Create and verify
result = skill.create_work_item(title="Task", type="Task")
if result.success:
    work_item = skill.get_work_item(result.id)
    assert work_item.exists  # Verification passed
```

## Related

- **adapters/azure_devops/CLAUDE.md**: Low-level Azure DevOps adapter
- **workflows/CLAUDE.md**: Workflows using this skill
- **skills/azure_devops/README.md**: Iteration path guidance
