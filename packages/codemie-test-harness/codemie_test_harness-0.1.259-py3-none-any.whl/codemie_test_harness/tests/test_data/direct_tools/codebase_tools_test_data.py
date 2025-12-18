import pytest

from codemie_test_harness.tests.enums.tools import Toolkit, CodeBaseTool

sonar_tools_test_data = [
    pytest.param(
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 80,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 80
              },
              "effortTotal" : 458,
              "issues" : [ {
                "key" : "8fd858da-e04c-4de3-b5a5-c14962c1c11e",
                "rule" : "python:S3776",
                "severity" : "CRITICAL",
                "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                "project" : "codemie",
                "line" : 114,
                "hash" : "6490d07b2b75b2b09264d73ebe73d9e0",
                "textRange" : {
                  "startLine" : 114,
                  "endLine" : 114,
                  "startOffset" : 8,
                  "endOffset" : 24
                },
                "flows" : [ {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 130,
                      "endLine" : 130,
                      "startOffset" : 8,
                      "endOffset" : 10
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 137,
                      "endLine" : 137,
                      "startOffset" : 12,
                      "endOffset" : 14
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 140,
                      "endLine" : 140,
                      "startOffset" : 12,
                      "endOffset" : 16
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 141,
                      "endLine" : 141,
                      "startOffset" : 16,
                      "endOffset" : 18
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 145,
                      "endLine" : 145,
                      "startOffset" : 12,
                      "endOffset" : 16
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 147,
                      "endLine" : 147,
                      "startOffset" : 16,
                      "endOffset" : 18
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 149,
                      "endLine" : 149,
                      "startOffset" : 16,
                      "endOffset" : 20
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 154,
                      "endLine" : 154,
                      "startOffset" : 12,
                      "endOffset" : 16
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 156,
                      "endLine" : 156,
                      "startOffset" : 16,
                      "endOffset" : 18
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 161,
                      "endLine" : 161,
                      "startOffset" : 12,
                      "endOffset" : 16
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 163,
                      "endLine" : 163,
                      "startOffset" : 16,
                      "endOffset" : 18
                    },
                    "msg" : "+2 (incl 1 for nesting)",
                    "msgFormattings" : [ ]
                  } ]
                }, {
                  "locations" : [ {
                    "component" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                    "textRange" : {
                      "startLine" : 167,
                      "endLine" : 167,
                      "startOffset" : 8,
                      "endOffset" : 14
                    },
                    "msg" : "+1",
                    "msgFormattings" : [ ]
                  } ]
                } ],
                "status" : "OPEN",
                "message" : "Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.",
                "effort" : "6min",
                "debt" : "6min",
                "author" : "",
                "tags" : [ "brain-overload" ],
                "creationDate" : "2025-10-24T08:38:35+0000",
                "updateDate" : "2025-10-24T08:38:35+0000",
                "type" : "CODE_SMELL",
                "scope" : "MAIN",
                "quickFixAvailable" : false,
                "messageFormattings" : [ ],
                "codeVariants" : [ ],
                "cleanCodeAttribute" : "FOCUSED",
                "cleanCodeAttributeCategory" : "ADAPTABLE",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "HIGH"
                } ],
                "issueStatus" : "OPEN",
                "prioritizedRule" : false
              } ],
              "components" : [ {
                "key" : "codemie:src/codemie/workflows/nodes/bedrock_flow_node.py",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "bedrock_flow_node.py",
                "longName" : "src/codemie/workflows/nodes/bedrock_flow_node.py",
                "path" : "src/codemie/workflows/nodes/bedrock_flow_node.py"
              }, {
                "key" : "codemie",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "codemie",
                "longName" : "codemie"
              } ],
              "facets" : [ ]
            }
        """,
        marks=pytest.mark.sonar,
        id=CodeBaseTool.SONAR,
    ),
    pytest.param(
        Toolkit.CODEBASE_TOOLS,
        CodeBaseTool.SONAR_CLOUD,
        {
            "relative_url": "/api/issues/search",
            "params": '{"types":"CODE_SMELL","ps":"1"}',
        },
        """
            {
              "total" : 15,
              "p" : 1,
              "ps" : 1,
              "paging" : {
                "pageIndex" : 1,
                "pageSize" : 1,
                "total" : 15
              },
              "effortTotal" : 127,
              "debtTotal" : 127,
              "issues" : [ {
                "key" : "AZTWg867SN_Wuz1X4Py2",
                "rule" : "kubernetes:S6892",
                "severity" : "MAJOR",
                "component" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "project" : "alezander86_python38g",
                "line" : 34,
                "hash" : "723c0daa435bdafaa7aa13d3ae06ca5e",
                "textRange" : {
                  "startLine" : 34,
                  "endLine" : 34,
                  "startOffset" : 19,
                  "endOffset" : 30
                },
                "flows" : [ ],
                "status" : "OPEN",
                "message" : "Specify a CPU request for this container.",
                "effort" : "5min",
                "debt" : "5min",
                "author" : "codebase@edp.local",
                "tags" : [ ],
                "creationDate" : "2024-11-07T13:14:43+0000",
                "updateDate" : "2025-02-05T14:28:27+0000",
                "type" : "CODE_SMELL",
                "organization" : "alezander86",
                "cleanCodeAttribute" : "COMPLETE",
                "cleanCodeAttributeCategory" : "INTENTIONAL",
                "impacts" : [ {
                  "softwareQuality" : "MAINTAINABILITY",
                  "severity" : "MEDIUM"
                }, {
                  "softwareQuality" : "RELIABILITY",
                  "severity" : "MEDIUM"
                } ],
                "issueStatus" : "OPEN",
                "projectName" : "python38g"
              } ],
              "components" : [ {
                "organization" : "alezander86",
                "key" : "alezander86_python38g:deploy-templates/templates/deployment.yaml",
                "uuid" : "AZTWg8uJSN_Wuz1X4Pye",
                "enabled" : true,
                "qualifier" : "FIL",
                "name" : "deployment.yaml",
                "longName" : "deploy-templates/templates/deployment.yaml",
                "path" : "deploy-templates/templates/deployment.yaml"
              }, {
                "organization" : "alezander86",
                "key" : "alezander86_python38g",
                "uuid" : "AZTWgJZiF0LopzvlIH8p",
                "enabled" : true,
                "qualifier" : "TRK",
                "name" : "python38g",
                "longName" : "python38g"
              } ],
              "organizations" : [ {
                "key" : "alezander86",
                "name" : "Taruraiev Oleksandr"
              } ],
              "facets" : [ ]
            }
        """,
        marks=pytest.mark.sonar,
        id=CodeBaseTool.SONAR_CLOUD,
    ),
]
