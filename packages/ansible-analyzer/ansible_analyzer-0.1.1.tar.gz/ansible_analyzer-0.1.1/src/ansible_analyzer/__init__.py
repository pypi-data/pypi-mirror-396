# General idea
# Build a directed graph by starting from an entrypoint(task/playbook)
# and forming a node for each task/playbook and an edge for every time
# a different task file is called
# This would be useful to see which files are used the most and how complex
# a given role is

from .log import init_logger

logger = init_logger()
