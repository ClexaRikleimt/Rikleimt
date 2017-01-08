# encoding=utf-8
from flask_assets import Environment, Bundle

assets = Environment()

scss = Bundle('styles/main.css', output='styles/main.css')
js = Bundle('scripts/main.js', output='scripts/main.js')

assets.register('scss_main', scss)
assets.register('js_main', js)
