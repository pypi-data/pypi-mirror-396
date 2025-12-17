#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIgMAG CLI wrapper for app.py and app_lite.py
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIgMAG CLI wrapper for app.py
"""

import runpy
import os

def run_app():
    """Run the full BIgMAG app without modifying app.py"""
    script_path = os.path.join(os.path.dirname(__file__), "app.py")
    script_path = os.path.abspath(script_path)
    runpy.run_path(script_path, run_name="__main__")

def run_app_lite():
    """Run the lite BIgMAG app without modifying app_lite.py"""
    script_path = os.path.join(os.path.dirname(__file__), "app_lite.py")
    script_path = os.path.abspath(script_path)
    runpy.run_path(script_path, run_name="__main__")