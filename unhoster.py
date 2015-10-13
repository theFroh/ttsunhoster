import os
from json import load
import pprint
from enum import Enum
import urllib.parse

import concurrent.futures
import urllib.request

class DataType(Enum):
    image = 1
    model = 2

# what do we want to fetch?
MESH_DATA = {
    "MeshURL": DataType.model,
    "NormalURL": DataType.image,
    "DiffuseURL": DataType.image,
    "ColliderURL": DataType.model
    }

def load_tts_url(tts_url, timeout):
    with urllib.request.urlopen(tts_url[0], timeout=timeout) as conn:
        return conn.read()

def url_to_tts(url):
    url_path = urllib.parse.urlparse(url).path
    url_ext = os.path.splitext(url_path)[1]

    return "".join([c for c in url if c.isalpha() or c.isdigit()]).rstrip() + url_ext

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Unhosts Tabletop Simulator workshop custom content.")
    parser.add_argument("json_input", help="path to the .json file")
    args = parser.parse_args()

    with open(args.json_input, "r") as fp:
        save = load(fp)
        objects = save["ObjectStates"]
        save_name = save["SaveName"]

    output_dir = os.path.join(os.path.dirname(os.path.abspath(args.json_input)),
        "".join([c for c in save_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip())
    print("Output directory:", output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_dir = os.path.join(output_dir, "Images")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    model_dir = os.path.join(output_dir, "Models")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)


    image_urls = {}
    model_urls = {}

    for obj in objects:
        # grab a usable name
        name = obj["GUID"] # default to what always exists
        if "Nickname" in obj:
            name = obj["Nickname"]
        print("Object", name)

        if "CustomMesh" in obj:
            custom_mesh = obj["CustomMesh"]
            for key,dtype in MESH_DATA.items():
                if key in custom_mesh:
                    url = custom_mesh[key]
                    if url: # make sure not empty
                        if dtype == DataType.image:
                            print("\tIMAGE", key, url)
                            image_urls[(url, dtype)] = url_to_tts(url)
                        elif dtype == DataType.model:
                            print("\tMODEL", key, url)
                            model_urls[(url, dtype)] = url_to_tts(url)

    print("\nURL's to nab:")

    # get a list of all urls
    all_urls = list(model_urls)
    all_urls.extend(list(image_urls))

    pprint.pprint(all_urls)

    print("\nGrabbing files")
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        future_to_url = {executor.submit(load_tts_url, url, 60): url for url in all_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%r is %d bytes' % (url[0], len(data)), end="")

                if url[1] == DataType.image and url in image_urls:
                    with open(os.path.join(image_dir, image_urls[url]), "wb") as fp:
                        fp.write(data)
                elif url[1] == DataType.model and url in model_urls:
                    with open(os.path.join(model_dir, model_urls[url]), "wb") as fp:
                        fp.write(data)

                print("... Saved.")
