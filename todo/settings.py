"""
Settings alias module.
The primary Django settings module for this project is 'Task.settings'.
This module re-exports Task.settings to support references to 'todo.settings'.
"""
from Task.settings import *  # noqa: F401, F403
