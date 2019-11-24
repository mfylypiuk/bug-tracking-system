"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import bug_tracking_system.views
