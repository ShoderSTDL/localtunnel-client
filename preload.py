from modules.paths import models_path
import os
def preload(parser):
    parser.add_argument("--localtunnel", action='store_true', help="alternative to gradio --share")
    parser.add_argument("--localtunnel-host", type=str, help="URL to the localtunnel server", default=None)
