mock_jobs = [
  {
    "server": {
      "id": 1,
      "user_id": 1,
      "hostname": "HPC16",
      "base_directory": "Documents/mydocs",
      "description": None,
      "created_at": "2024-09-30T12:39:32.000000Z",
      "updated_at": "2024-09-30T12:39:32.000000Z"
    },
    "project": {
      "id": 1,
      "project_title": "newproject6"
    },
    "project_job": {
      "job_title": "Job title for our understanding",
      "job_directory": "test_run_1",
      "job_description": None,
      "status": "pending"
    },
    "environment_variable_management": [
      {
        "variable": "input_file_name",
        "type": "text",
        "value": "1AKI"
      },
      {
        "variable": "input_file",
        "type": "input",
        "value": "input/1AKI.pdb"
      }
    ],
    "nodes": [
      {
        "id": "17277008189886114",
        "type": "terminal",
        "position": {
          "x": 305.85679626464844,
          "y": 152.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "py test.py"
            },
            {
              "command": "python3 test2.py",
              "response": None
            }
          ],
          "software": "python-3.9"
        }
      },
      {
        "id": "17277008378542058",
        "type": "terminal",
        "position": {
          "x": 318.85679626464844,
          "y": 249.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": None
            }
          ]
        }
      },
      {
        "id": "17277008418535338",
        "type": "splitterParent",
        "position": {
          "x": 373.35679626464844,
          "y": 345.7735252380371
        },
        "data": {
          "label": "Results",
          "multiSelect": True
        }
      },
      {
        "id": "17277008470471567",
        "type": "splitter-child",
        "position": {
          "x": 223.35679626464844,
          "y": 425.7735252380371
        },
        "data": {
          "label": "Analysis 1",
          "active": False
        }
      },
      {
        "id": "17277008470499571",
        "type": "splitter-child",
        "position": {
          "x": 403.35679626464844,
          "y": 425.7735252380371
        },
        "data": {
          "label": "Analysis 2",
          "active": True
        }
      },
      {
        "id": "17277008470505095",
        "type": "splitter-child",
        "position": {
          "x": 583.3567962646484,
          "y": 425.7735252380371
        },
        "data": {
          "label": "Analysis 3",
          "active": True
        }
      },
      {
        "id": "17277008772915259",
        "type": "terminal",
        "position": {
          "x": 209.85679626464844,
          "y": 524.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "python3 test.py"
            }
          ],
          "software": "python-3.9"
        }
      },
      {
        "id": "17277008789144515",
        "type": "terminal",
        "position": {
          "x": 409.85679626464844,
          "y": 523.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "python3 test.py"
            }
          ],
          "software": "python-3.9"
        }
      },
      {
        "id": "17277008806423193",
        "type": "terminal",
        "position": {
          "x": 597.8567962646484,
          "y": 521.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "python3 test.py"
            }
          ],
          "software": "python-3.9"
        }
      }
    ],
    "edges": [
      {
        "id": "e17277008189886114-17277008378542058",
        "type": "smoothstep",
        "source": "17277008189886114",
        "target": "17277008378542058"
      },
      {
        "id": "e17277008418535338-17277008470471567",
        "type": "default",
        "source": "17277008418535338",
        "target": "17277008470471567"
      },
      {
        "id": "e17277008418535338-17277008470499571",
        "type": "default",
        "source": "17277008418535338",
        "target": "17277008470499571"
      },
      {
        "id": "e17277008418535338-17277008470505095",
        "type": "default",
        "source": "17277008418535338",
        "target": "17277008470505095"
      },
      {
        "id": "e17277008378542058-17277008418535338",
        "type": "smoothstep",
        "source": "17277008378542058",
        "target": "17277008418535338"
      },
      {
        "id": "e17277008470471567-17277008772915259",
        "type": "smoothstep",
        "source": "17277008470471567",
        "target": "17277008772915259"
      },
      {
        "id": "e17277008470499571-17277008789144515",
        "type": "smoothstep",
        "source": "17277008470499571",
        "target": "17277008789144515"
      },
      {
        "id": "e17277008470505095-17277008806423193",
        "type": "smoothstep",
        "source": "17277008470505095",
        "target": "17277008806423193"
      }
    ],
    "new_job": 1
  },
  {
    "server": {
      "id": 1,
      "user_id": 1,
      "hostname": "HPC16",
      "base_directory": "Documents/mydocs2",
      "description": None,
      "created_at": "2024-09-30T12:39:32.000000Z",
      "updated_at": "2024-09-30T12:39:32.000000Z"
    },
    "project": {
      "id": 1,
      "project_title": "newproject6"
    },
    "project_job": {
      "job_title": "Job title for our understanding",
      "job_directory": "test_run_new_job",
      "job_description": None,
      "status": "pending"
    },
    "environment_variable_management": [
      {
        "variable": "input_file_name",
        "type": "text",
        "value": "1AKI"
      },
      {
        "variable": "input_file",
        "type": "input",
        "value": "input/1AKI.pdb"
      }
    ],
    "nodes": [
      {
        "id": "17277008189886114",
        "type": "terminal",
        "position": {
          "x": 305.85679626464844,
          "y": 152.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "py test.py"
            },
            {
              "command": "python3 test2.py",
              "response": None
            }
          ],
          "software": "python-3.9"
        }
      },
      {
        "id": "17277008378542058",
        "type": "terminal",
        "position": {
          "x": 318.85679626464844,
          "y": 249.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": None
            }
          ]
        }
      },
      {
        "id": "17277008418535338",
        "type": "splitterParent",
        "position": {
          "x": 373.35679626464844,
          "y": 345.7735252380371
        },
        "data": {
          "label": "Results",
          "multiSelect": True
        }
      },
      {
        "id": "17277008470471567",
        "type": "splitter-child",
        "position": {
          "x": 223.35679626464844,
          "y": 425.7735252380371
        },
        "data": {
          "label": "Analysis 1",
          "active": False
        }
      },
      {
        "id": "17277008470499571",
        "type": "splitter-child",
        "position": {
          "x": 403.35679626464844,
          "y": 425.7735252380371
        },
        "data": {
          "label": "Analysis 2",
          "active": True
        }
      },
      {
        "id": "17277008470505095",
        "type": "splitter-child",
        "position": {
          "x": 583.3567962646484,
          "y": 425.7735252380371
        },
        "data": {
          "label": "Analysis 3",
          "active": True
        }
      },
      {
        "id": "17277008772915259",
        "type": "terminal",
        "position": {
          "x": 209.85679626464844,
          "y": 524.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "python3 test.py"
            }
          ],
          "software": "python-3.9"
        }
      },
      {
        "id": "17277008789144515",
        "type": "terminal",
        "position": {
          "x": 409.85679626464844,
          "y": 523.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "python3 test.py"
            }
          ],
          "software": "python-3.9"
        }
      },
      {
        "id": "17277008806423193",
        "type": "terminal",
        "position": {
          "x": 597.8567962646484,
          "y": 521.7735252380371
        },
        "data": {
          "label": "Terminal Widget",
          "commands": [
            {
              "command": "python3 test.py"
            }
          ],
          "software": "python-3.9"
        }
      }
    ],
    "edges": [
      {
        "id": "e17277008189886114-17277008378542058",
        "type": "smoothstep",
        "source": "17277008189886114",
        "target": "17277008378542058"
      },
      {
        "id": "e17277008418535338-17277008470471567",
        "type": "default",
        "source": "17277008418535338",
        "target": "17277008470471567"
      },
      {
        "id": "e17277008418535338-17277008470499571",
        "type": "default",
        "source": "17277008418535338",
        "target": "17277008470499571"
      },
      {
        "id": "e17277008418535338-17277008470505095",
        "type": "default",
        "source": "17277008418535338",
        "target": "17277008470505095"
      },
      {
        "id": "e17277008378542058-17277008418535338",
        "type": "smoothstep",
        "source": "17277008378542058",
        "target": "17277008418535338"
      },
      {
        "id": "e17277008470471567-17277008772915259",
        "type": "smoothstep",
        "source": "17277008470471567",
        "target": "17277008772915259"
      },
      {
        "id": "e17277008470499571-17277008789144515",
        "type": "smoothstep",
        "source": "17277008470499571",
        "target": "17277008789144515"
      },
      {
        "id": "e17277008470505095-17277008806423193",
        "type": "smoothstep",
        "source": "17277008470505095",
        "target": "17277008806423193"
      }
    ],
    "new_job": 1
  }
]


mock_container_info = {
  "current_pipeline_containers": [
    "python-3.9",
    "gromacs-3.9"
  ],
  "user_all_unique_containers": [
    "python-3.9",
    "gromacs-3.9"
  ],
  "container_image_details": [
    {
      "name": "python",
      "version": "3.9",
      "image_name": "python-3.9",
      "sylabs_uri": "library://david.schmidt/car-flow/python3"
    },
    {
      "name": "Gromacs",
      "version": "3.9",
      "image_name": "gromacs-3.9",
      "sylabs_uri": "docker://gromacs/gromacs:latest"
    }
  ]
}