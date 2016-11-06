import argparse
import copy
import json
import os
import requests
import shutil
import urlparse

from jinja2 import FileSystemLoader, Environment

__HERE__ = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_FOLDER = os.path.join(__HERE__, 'templates')


class VideoDownloader(object):

    def __init__(self, metadata_dir, html_dir='.', verbose=True,
                 dry_run=False):
        self.metadata_dir = metadata_dir
        self.html_dir = html_dir
        self.verbose = verbose
        self.dry_run = dry_run

    def log(self, message):
        if self.verbose:
            print(message)

    def transform_metadata(self, url):
        resp = requests.get(url)
        resp.raise_for_status()

        origin = resp.json()['entity']
        dest = copy.deepcopy(origin)

        timecodes = origin['timecodes']
        video_id = origin['id']

        local_folder = os.path.join(self.metadata_dir, video_id)
        if not (self.dry_run and os.path.exists(local_folder)):
            os.makedirs(local_folder)

        def transform_timecodes(timecode):
            small_url = urlparse.urljoin(url, timecode['image']['small'])
            large_url = urlparse.urljoin(url, timecode['image']['large'])
            filename = urlparse.urlparse(small_url).path.split('/')[-1]
            name, ext = os.path.splitext(filename)
            small_fn = os.path.join(local_folder, '%s-small%s' % (name, ext))
            large_fn = os.path.join(local_folder, '%s-large%s' % (name, ext))
            image = timecode['image']
            image['small'] = self.download_image(small_url, small_fn)
            image['large'] = self.download_image(large_url, large_fn)
            return timecode

        dest['timecodes'] = map(transform_timecodes, timecodes)
        thumbnail_url = urlparse.urljoin(url, origin['thumbnail'])
        thumbnail_fn = os.path.join(local_folder, 'thumbnail.jpg')
        dest['thumbnail'] = self.download_image(thumbnail_url, thumbnail_fn)

        return dest

    def download_image(self, image_url, destination_path):
        self.log('Downloading %s at %s' % (image_url, destination_path))
        if not self.dry_run:
            resp = requests.get(image_url, stream=True)
            if resp.status_code == 200:
                with open(destination_path, 'wb') as f:
                    resp.raw_decode_content = True
                    shutil.copyfileobj(resp.raw, f)
        return destination_path

    def download_slides(self, url):
        metadata = self.transform_metadata(url)
        filename = '%s.json' % metadata['id']
        if not self.dry_run:
            with open(os.path.join(self.metadata_dir, filename), 'w+') as f:
                json.dump(metadata, f)
        return filename, metadata

    def copy_templates(self, filename, metadata):
        simple_loader = FileSystemLoader(TEMPLATES_FOLDER)
        env = Environment(loader=simple_loader)
        template = env.get_template('index.html')
        rendered = template.render(metadata=metadata, filename=filename)
        dest_file = os.path.join(self.html_dir, metadata['id'] + '.html')
        if not self.dry_run:
            with open(dest_file, 'w+') as f:
                f.write(rendered)

    def get_metadata_url_from_video_url(self, video_url):
        _id = urlparse.urlparse(video_url).path.split('/')[-1]
        metadata_url = 'http://www.demo.openveo.com/publish/getVideo/%s' % _id
        return metadata_url

    def generate_video_html(self, video_url):
        try:
            metadata_url = self.get_metadata_url_from_video_url(video_url)
            filename, metadata = self.download_slides(metadata_url)
            self.copy_templates(filename, metadata)
        except Exception as e:
            self.log(str(e))


def get_list_of_urls(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return ['http://www.demo.openveo.com' + r['link']
            for r in data['rows']]


def main(json_file, metadata_dir, html_dir, verbose=None, dry_run=None):
    downloader = VideoDownloader(metadata_dir, html_dir, verbose, dry_run)
    urls = get_list_of_urls(json_file)
    downloader.log('Downloading %s videos' % len(urls))
    for url in urls:
        downloader.generate_video_html(url)


if __name__ == '__main__':
    description = 'Download and host openveo videos on a static website.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'json_file',
        help='JSON file containing the list of videos')
    parser.add_argument(
        'metadata_dir',
        help='Path to the dir where metadata files will be written')
    parser.add_argument('--html-dir', default='.')
    parser.add_argument('--quiet', action='store_true', default=False)
    parser.add_argument('--dry-run', action='store_true', default=False)
    args = parser.parse_args()
    main(args.json_file, args.metadata_dir, args.html_dir, not args.quiet,
         args.dry_run)
