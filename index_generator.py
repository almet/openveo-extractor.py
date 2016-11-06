 # -*- coding: utf-8 -*-
import json
import os
from codecs import open

from jinja2 import FileSystemLoader, Environment
from slugify import slugify

__HERE__ = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_FOLDER = os.path.join(__HERE__, 'templates')


def generate_html(json_file, html_dir):
    with open(json_file) as f:
        data = json.load(f)
    videos = data['rows']

    simple_loader = FileSystemLoader(TEMPLATES_FOLDER)
    env = Environment(loader=simple_loader)
    template = env.get_template('list.html')
    rendered = template.render(
        videos=videos,
        slugify=slugify)
    dest_file = os.path.join(html_dir, 'index.html')
    with open(dest_file, 'w+', encoding='utf-8') as f:
        f.write(rendered)


if __name__ == '__main__':
    generate_html('reponse.json', '.')
