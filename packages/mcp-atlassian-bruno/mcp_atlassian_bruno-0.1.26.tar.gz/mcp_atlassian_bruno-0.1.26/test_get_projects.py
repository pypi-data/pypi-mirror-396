#!/usr/bin/env python3
"""Test script to debug get_all_projects issue."""

import asyncio
import json
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_get_all_projects():
    """Test the get_all_projects function."""
    from mcp_atlassian.jira.config import JiraConfig
    from mcp_atlassian.jira import JiraFetcher
    from mcp_atlassian.servers.dependencies import get_context

    logger.info("=" * 70)
    logger.info("TESTING: get_all_projects()")
    logger.info("=" * 70)

    try:
        # Load Jira configuration
        logger.info("\n[1] Loading Jira configuration from environment...")
        jira_config = JiraConfig.from_env()
        logger.info(f"    URL: {jira_config.url}")
        logger.info(f"    Auth configured: {jira_config.is_auth_configured()}")
        logger.info(f"    Projects filter: {jira_config.projects_filter}")

        # Create Jira fetcher
        logger.info("\n[2] Creating JiraFetcher...")
        jira_fetcher = JiraFetcher(config=jira_config)
        logger.info("    JiraFetcher created successfully")

        # Call get_all_projects (no archive)
        logger.info("\n[3] Calling get_all_projects(include_archived=False)...")
        projects = jira_fetcher.get_all_projects(include_archived=False)
        logger.info(f"    Result type: {type(projects)}")
        logger.info(f"    Number of projects: {len(projects)}")

        if projects:
            logger.info(f"\n[4] Projects found ({len(projects)}):")
            for i, proj in enumerate(projects[:5], 1):  # Show first 5
                logger.info(f"    {i}. {proj.get('name')} ({proj.get('key')})")
            if len(projects) > 5:
                logger.info(f"    ... and {len(projects) - 5} more")

            logger.info(f"\n[5] Full result (first project):")
            logger.info(f"    {json.dumps(projects[0], indent=2, ensure_ascii=False)}")
        else:
            logger.warning("\n[4] NO PROJECTS FOUND!")
            logger.warning("    This might be due to:")
            logger.warning("    - Authentication failure")
            logger.warning("    - No projects accessible to the user")
            logger.warning("    - API parameter issue")

        # Call get_all_projects (with archive)
        logger.info("\n[6] Calling get_all_projects(include_archived=True)...")
        projects_with_archived = jira_fetcher.get_all_projects(include_archived=True)
        logger.info(f"    Number of projects (including archived): {len(projects_with_archived)}")

        # Compare
        logger.info(f"\n[7] Comparison:")
        logger.info(f"    Without archived: {len(projects)} projects")
        logger.info(f"    With archived: {len(projects_with_archived)} projects")
        logger.info(f"    Difference: {len(projects_with_archived) - len(projects)} archived projects")

    except Exception as e:
        logger.error(f"\n[ERROR] {e}", exc_info=True)

    logger.info("\n" + "=" * 70)


async def test_jira_client_direct():
    """Test the Jira client directly to see raw API response."""
    import os
    from atlassian import Jira

    logger.info("\n" + "=" * 70)
    logger.info("TESTING: Direct Jira Client API Call")
    logger.info("=" * 70)

    try:
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_api_token = os.getenv("JIRA_API_TOKEN")

        logger.info(f"\n[1] Creating Atlassian Jira client...")
        logger.info(f"    URL: {jira_url}")
        logger.info(f"    Username: {jira_username}")

        # Create Jira client
        jira_client = Jira(
            url=jira_url,
            username=jira_username,
            password=jira_api_token,
            verify_ssl=False,
        )

        # Test with included_archived=True
        logger.info(f"\n[2] Calling jira.projects(included_archived=True)...")
        projects_true = jira_client.projects(included_archived=True)
        logger.info(f"    Result type: {type(projects_true)}")
        logger.info(f"    Count: {len(projects_true) if isinstance(projects_true, list) else 'N/A'}")
        if isinstance(projects_true, list) and projects_true:
            logger.info(f"    First project: {projects_true[0].get('name')} ({projects_true[0].get('key')})")

        # Test with included_archived=False
        logger.info(f"\n[3] Calling jira.projects(included_archived=False)...")
        projects_false = jira_client.projects(included_archived=False)
        logger.info(f"    Result type: {type(projects_false)}")
        logger.info(f"    Count: {len(projects_false) if isinstance(projects_false, list) else 'N/A'}")
        if isinstance(projects_false, list) and projects_false:
            logger.info(f"    First project: {projects_false[0].get('name')} ({projects_false[0].get('key')})")

        # Test without parameter
        logger.info(f"\n[4] Calling jira.projects() (no parameters)...")
        projects_none = jira_client.projects()
        logger.info(f"    Result type: {type(projects_none)}")
        logger.info(f"    Count: {len(projects_none) if isinstance(projects_none, list) else 'N/A'}")
        if isinstance(projects_none, list) and projects_none:
            logger.info(f"    First project: {projects_none[0].get('name')} ({projects_none[0].get('key')})")

    except Exception as e:
        logger.error(f"\n[ERROR] {e}", exc_info=True)

    logger.info("\n" + "=" * 70)


async def main():
    """Run all tests."""
    await test_jira_client_direct()
    await test_get_all_projects()


if __name__ == "__main__":
    asyncio.run(main())
