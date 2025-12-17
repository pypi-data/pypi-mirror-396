import os
from types import SimpleNamespace

# Get the absolute path to THIS directory
_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))



Bessica_D_v1_1_skeleton = SimpleNamespace()
Bessica_D_v1_1_skeleton.xml = os.path.join(_MODULE_PATH, "Bessica_D_v1_1_skeleton.xml")