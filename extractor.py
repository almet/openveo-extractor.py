import copy
import json
import os
import requests
import shutil
import sys
import urlparse

from jinja2 import FileSystemLoader, Environment

__HERE__ = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_FOLDER = os.path.join(__HERE__, "templates")


def transform_metadata(url, dest_path):
    resp = requests.get(url)

    origin = resp.json()['entity']
    dest = copy.deepcopy(origin)

    timecodes = origin['timecodes']
    video_id = origin['id']

    local_folder = os.path.join(dest_path, video_id)
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    def transform_timecodes(timecode):
        small_url = urlparse.urljoin(url, timecode['image']['small'])
        large_url = urlparse.urljoin(url, timecode['image']['large'])
        filename = urlparse.urlparse(small_url).path.split('/')[-1]
        name, ext = os.path.splitext(filename)
        small_filename = os.path.join(local_folder, '%s-small%s' % (name, ext))
        large_filename = os.path.join(local_folder, '%s-large%s' % (name, ext))
        timecode['image']['small'] = download_image(small_url, small_filename)
        timecode['image']['large'] = download_image(large_url, large_filename)
        return timecode

    dest['timecodes'] = map(transform_timecodes, timecodes)
    thumbnail_url = urlparse.urljoin(url, origin["thumbnail"])
    thumbnail_filename = os.path.join(local_folder, 'thumbnail.jpg')
    dest['thumbnail'] = download_image(thumbnail_url, thumbnail_filename)

    # origin['link'] should be deleted?

    return dest


def download_image(url, path):
    print("Downloading %s at %s" % (url, path))
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(path, 'wb') as f:
            resp.raw_decode_content = True
            shutil.copyfileobj(resp.raw, f)
    return path


def download_slides(url, output_dir):
    metadata = transform_metadata(url, output_dir)
    filename = '%s.json' % metadata['id']
    with open(os.path.join(output_dir, filename), 'w+') as f:
        json.dump(metadata, f)

    return filename, metadata


def copy_templates(output_dir, filename, metadata):
    simple_loader = FileSystemLoader(TEMPLATES_FOLDER)
    env = Environment(loader=simple_loader)
    template = env.get_template("index.html")
    rendered = template.render(metadata=metadata, filename=filename)
    destination_file = os.path.join(output_dir, metadata['id'] + '.html')
    with open(destination_file, "w+") as f:
        f.write(rendered)


def get_metadata_url_from_video_url(video_url):
    _id = urlparse.urlparse(video_url).path.split('/')[-1]
    metadata_url = 'http://www.demo.openveo.com/publish/getVideo/%s' % _id
    return metadata_url


def main(video_url, metadata_dir, html_dir="."):
    metadata_url = get_metadata_url_from_video_url(video_url)
    filename, metadata = download_slides(metadata_url, metadata_dir)
    copy_templates(html_dir, filename, metadata)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit('Please specify the URL of the openveo JSON file to extract')
    url = sys.argv[1]
    metadata_dir = sys.argv[2] if len(sys.argv) >= 3 else '.'
    html_dir = sys.argv[3] if len(sys.argv) >= 4 else '.'
    main(url, metadata_dir, html_dir)
