import pytest

from codemie_test_harness.tests.enums.tools import (
    CodeExplorationTools,
    CodeAnalysisTools,
)

code_analysis_toolkit_toolkit_test_data = [
    pytest.param(
        "Show me the hierarchical representation of the file system structure starting from the ./",
        CodeAnalysisTools.GET_FILES_TREE,
        id="file_tree_structure",
    ),
    pytest.param(
        "Show me external dependencies for the build.gradle file",
        CodeAnalysisTools.GET_OUTGOING_DEPENDENCIES,
        id="external_dependencies",
    ),
    pytest.param(
        "Show me datasource information",
        CodeAnalysisTools.GET_DATASOURCE,
        id="datasource_info",
    ),
    pytest.param(
        "List all files under the src directory",
        CodeAnalysisTools.GET_FILES_LIST,
        id="files_list_in_src",
    ),
    pytest.param(
        "Show me metadata for the build.gradle file",
        CodeAnalysisTools.GET_METADATA,
        id="file_metadata",
    ),
    pytest.param(
        "Show me code members (functions, classes, etc.) in Test.java file",
        CodeAnalysisTools.GET_CODE_MEMBERS,
        id="code_members",
    ),
    pytest.param(
        "Show me the content of Test.java file",
        CodeAnalysisTools.GET_CODE,
        id="file_content",
    ),
]

code_exploration_toolkit_test_data = [
    pytest.param(
        "show info about node d865ccff-bb1d-4d1a-a34e-87b679308034",
        CodeExplorationTools.GET_NODES_BY_IDS,
        id="get_node_by_id",
    ),
    pytest.param(
        "show all nodes",
        CodeExplorationTools.GRAPH_SEARCH,
        id="graph_search_all_nodes",
    ),
    pytest.param(
        "show datasource info",
        CodeExplorationTools.GET_DATASOURCE,
        id="get_datasource_info",
    ),
    pytest.param(
        "show node with name NODE_NAME",
        CodeExplorationTools.FIND_NODES_BY_NAME,
        id="find_node_by_name",
    ),
    pytest.param(
        "show the directory tree structure starting from root",
        CodeExplorationTools.WORKSPACE_TREE_EXPLORATION,
        id="workspace_tree_exploration",
    ),
    pytest.param(
        "show the graph database structure",
        CodeExplorationTools.GET_GRAPH_DATA_MODEL,
        id="get_graph_data_model",
    ),
    pytest.param(
        'show nodes with summary: "code execution"',
        CodeExplorationTools.SUMMARIES_SEARCH,
        id="summaries_search",
    ),
]
