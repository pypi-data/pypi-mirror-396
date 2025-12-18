import pytest

from codemie_test_harness.tests.enums.tools import VcsTool
from codemie_test_harness.tests.utils.credentials_manager import CredentialsManager

GITHUB_TOOL_TASK = (
    f"Using github tool get info about issue №5 for the repo {CredentialsManager.get_parameter('GITHUB_PROJECT')}. "
    f"Do not wrap tool parameters in additional query object"
)

RESPONSE_FOR_GITHUB = """
            Issue #5 Details for Repository wild47/final_task
            Title: Test
            State: Open
            Created At: January 15, 2025
            Updated At: January 15, 2025
            Author: wild47
            Body: This is a test issue.
            Comments: 0
            Labels: None
            URL: View Issue on GitHub
            Additional Information
            Assignees: None
            Milestone: None
            Reactions:
            👍: 0
            👎: 0
            😄: 0
            🎉: 0
            😕: 0
            ❤️: 0
            🚀: 0
            👀: 0
"""

GITLAB_PROJECT_ID = CredentialsManager.get_parameter("GITLAB_PROJECT_ID")

GITLAB_TOOL_TASK = (
    f"Using gitlab tool get info about MR №7014 for repo with id '{GITLAB_PROJECT_ID}'"
)

AZURE_DEVOPS_PROJECT = CredentialsManager.get_parameter("AZURE_DEVOPS_PROJECT_NAME")

AZURE_DEVOPS_GIT_TOOL_TASK = f"Using azuredevops tool get info about pull request №1 for project '{AZURE_DEVOPS_PROJECT} and repository '{AZURE_DEVOPS_PROJECT}'"

RESPONSE_FOR_GITLAB = f"""
        Here is the information about Merge Request (MR) №7014 for the repository with id '{GITLAB_PROJECT_ID}':

        - **Title:** sdk_juhigsaqwkedvdy
        - **Description:** Merge the changes in branch `sdk_cgkbdhekvjiolpi` to the main branch, including the creation of `SdkYmsodrhepphxpyl.java` with 'Hello World'.
        - **State:** Closed
        - **Created At:** August 8, 2025, 08:23:05 UTC
        - **Updated At:** August 8, 2025, 08:23:22 UTC
        - **Closed At:** August 8, 2025, 08:23:22 UTC
        - **Target Branch:** main
        - **Source Branch:** sdk_cgkbdhekvjiolpi
        - **Merge Status:** can be merged
        - **User Notes Count:** 0
        - **Upvotes:** 0
        - **Downvotes:** 0
        - **Author:** [Anton Yeromin](https://gitbud.epam.com/anton_yeromin)
        - **Labels:** created-by-agent
        - **Web URL:** [Link to MR](https://gitbud.epam.com/epm-cdme/autotests/codemie-test-project/-/merge_requests/7014)

        This MR does not have any assignees or reviewers and was closed by Anton Yeromin. There are no merge conflicts, and it's the author's first contribution to this project.
"""

RESPONSE_FOR_AZURE_DEVOPS_GIT = """
        Here is the information about Pull Request #1 for the repository 'CodemieAnton':
       
       - **Title:** Add random value to README
       - **Description:** This PR adds a random value section to the README file. Please update the README manually on the develop branch before merging.
       - **Status:** Active
       - **Created By:** Anton Yeromin
         - **Display Name:** Anton Yeromin
         - **Email:** Anton_Yeromin@epam.com
         - **Profile URL:** [Profile](https://spsprodneu1.vssps.visualstudio.com/Add1f60ac-c7d4-4a5f-b497-bdb733dc5847/_apis/Identities/7bfb0794-d7d6-6d0b-be18-a8c9cbedead2)
         - **Avatar:** ![Avatar](https://dev.azure.com/AntonYeromin/_apis/GraphProfile/MemberAvatars/aad.N2JmYjA3OTQtZDdkNi03ZDBiLWJlMTgtYThjOWNiZWRlYWQy)
       - **Creation Date:** 2025-10-20
       - **Source Branch:** `refs/heads/develop`
       - **Target Branch:** `refs/heads/main`
       - **Merge Status:** Succeeded
       - **Is Draft:** No
       - **Comments:** Added README.md
       - **Pull Request URL:** [Pull Request](https://dev.azure.com/AntonYeromin/9d40cdc1-5404-4d40-8025-e5267d69dc89/_apis/git/repositories/fb1015be-4aed-46f2-a41f-8b121a9568d1/pullRequests/1)
       
       If you need more information, let me know!
"""

vcs_tools_test_data = [
    pytest.param(
        VcsTool.GITHUB,
        GITHUB_TOOL_TASK,
        RESPONSE_FOR_GITHUB,
        marks=pytest.mark.github,
        id=VcsTool.GITHUB,
    ),
    pytest.param(
        VcsTool.GITLAB,
        GITLAB_TOOL_TASK,
        RESPONSE_FOR_GITLAB,
        marks=pytest.mark.gitlab,
        id=VcsTool.GITLAB,
    ),
    pytest.param(
        VcsTool.AZURE_DEVOPS_GIT,
        AZURE_DEVOPS_GIT_TOOL_TASK,
        RESPONSE_FOR_AZURE_DEVOPS_GIT,
        marks=pytest.mark.azure_devops_git,
        id=VcsTool.AZURE_DEVOPS_GIT,
    ),
]
