"""
Pre-built Prompts for Domo MCP Server

Provides prompt templates for common Domo operations that can be
used to guide AI agents through complex workflows.
"""

from mcp.server.fastmcp.prompts import base

from domo_mcp.server import mcp


@mcp.prompt(name="audit_user_access", title="Audit User Access")
def audit_user_access(user_id: str) -> list[base.Message]:
    """Create a prompt to audit all access for a specific user.

    This prompt guides the AI to comprehensively audit a user's access
    including their group memberships, role permissions, and data access.

    Args:
        user_id: The ID of the user to audit
    """
    return [
        base.UserMessage(
            f"""Please audit all access for user ID {user_id} by performing the following steps:

1. **Get User Details**: Retrieve the user's profile information including their role
2. **Check Group Memberships**: List all groups the user belongs to
3. **Review Role Permissions**: Get the grants/permissions associated with their role
4. **Identify Data Access**: Based on their groups and role, summarize what data they can access

Please provide a comprehensive report of this user's access rights."""
        ),
    ]


@mcp.prompt(name="troubleshoot_dataflow", title="Troubleshoot Dataflow")
def troubleshoot_dataflow(dataflow_id: str) -> list[base.Message]:
    """Create a prompt to troubleshoot a failing dataflow.

    This prompt guides the AI to diagnose issues with a dataflow
    by examining its configuration and execution history.

    Args:
        dataflow_id: The ID of the dataflow to troubleshoot
    """
    return [
        base.UserMessage(
            f"""Please troubleshoot dataflow ID {dataflow_id} by performing the following steps:

1. **Get Dataflow Details**: Retrieve the dataflow's configuration and current state
2. **Review Execution History**: Check the recent execution history for failures
3. **Identify Errors**: Look for error messages in failed executions
4. **Analyze Patterns**: Identify if there are patterns in when failures occur
5. **Suggest Fixes**: Based on the errors found, suggest potential fixes

Please provide a detailed analysis and recommendations."""
        ),
    ]


@mcp.prompt(name="onboard_new_user", title="Onboard New User")
def onboard_new_user(
    email: str, display_name: str, department: str
) -> list[base.Message]:
    """Create a prompt to onboard a new user to Domo.

    This prompt guides the AI through the user onboarding process
    including account creation and group assignments.

    Args:
        email: Email address for the new user
        display_name: Display name for the new user
        department: Department the user belongs to
    """
    return [
        base.UserMessage(
            f"""Please help onboard a new user to Domo with the following details:
- Email: {email}
- Display Name: {display_name}
- Department: {department}

Please perform the following steps:

1. **Check Existing Users**: Verify this email doesn't already exist in the system
2. **Identify Appropriate Role**: Based on the department, suggest an appropriate role
3. **Find Relevant Groups**: Search for groups related to the department
4. **Create User Account**: Create the user with the suggested role
5. **Add to Groups**: Add the user to relevant department groups
6. **Send Invitation**: Ensure an invitation email is sent

Please report on each step and confirm successful onboarding."""
        ),
    ]


@mcp.prompt(name="data_governance_review", title="Data Governance Review")
def data_governance_review(dataset_id: str) -> list[base.Message]:
    """Create a prompt to review data governance for a dataset.

    This prompt guides the AI to audit data governance settings
    including access controls and PDP policies.

    Args:
        dataset_id: The ID of the dataset to review
    """
    return [
        base.UserMessage(
            f"""Please review the data governance settings for dataset ID {dataset_id}:

1. **Get Dataset Details**: Retrieve the dataset metadata including owner
2. **Review Access Permissions**: Check who has access to this dataset
3. **Check PDP Policies**: If PDP is enabled, list the policies in place
4. **Identify Sharing**: Check if the dataset is shared with groups or individual users
5. **Assess Risk**: Based on the data and access, identify any governance concerns
6. **Recommend Improvements**: Suggest any improvements to the governance settings

Please provide a comprehensive governance report."""
        ),
    ]


@mcp.prompt(name="instance_health_check", title="Instance Health Check")
def instance_health_check() -> list[base.Message]:
    """Create a prompt to perform a health check on the Domo instance.

    This prompt guides the AI to check various aspects of the Domo
    instance including users, datasets, and dataflows.
    """
    return [
        base.UserMessage(
            """Please perform a health check on this Domo instance:

1. **User Overview**: Get a count of total users and summarize by role
2. **Group Summary**: List the total number of groups
3. **Role Review**: List all roles and their user counts
4. **Dataflow Status**: Check for any recently failed dataflows
5. **Summary Report**: Provide an overall health summary

Please identify any potential issues or areas needing attention."""
        ),
    ]
