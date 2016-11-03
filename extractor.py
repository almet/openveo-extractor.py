import copy
import json
import os
import requests
import shutil
import sys
import urlparse


def transform_metadata(url, dest_path):
    resp = requests.get(url)

    origin = resp.json()['entity']
    dest = copy.deepcopy(origin)

    timecodes = origin['timecodes']
    video_id = origin['id']
    
    local_folder = os.path.join(dest_path, video_id)
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # origin['thumbnail']
    # origin['link']
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
                                    
    return dest


def download_image(url, path):
    print("Downloading %s at %s" % (url, path))
    resp  = requests.get(url, stream=True)
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit('Please specify the URL of the openveo JSON file to extract')
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) == 3 else '.'
    download_slides(url, output_dir)
