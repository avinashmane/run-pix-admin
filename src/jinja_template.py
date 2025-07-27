import os
from jinja2 import Undefined, Environment, FileSystemLoader, select_autoescape

from dotenv import load_dotenv
load_dotenv() 
APP_ROOT=os.environ.get('APP_ROOT', ".") # root for templates and config

jinja = Environment(
    loader=FileSystemLoader(f"{APP_ROOT}/templates"),
    autoescape=select_autoescape()
)

class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''
    