#!/usr/bin/env python3
import os
from json import load
import pprint
from enum import Enum

import requests
import urllib.parse

import concurrent.futures
import urllib.request

MAX_WORKERS = 15

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

def load_tts_url(tts_url):
    r = requests.get(tts_url[0])

    if r.status_code == requests.codes.ok:
        return r.content
    else:
        print("Error", tts_url[0], r.status_code)

def url_to_tts(url):
    url_path = urllib.parse.urlparse(url).path
    url_ext = os.path.splitext(url_path)[1]

    return "".join([c for c in url if c.isalpha() or c.isdigit()]).rstrip() + url_ext

def parse_tts_custom_object(workshop_json):
    with open(workshop_json, "r", encoding="utf-8") as fp:
        save = load(fp)
        objects = save["ObjectStates"]

    image_urls = {}
    model_urls = {}

    for obj in objects:
        if "CustomMesh" in obj:
            custom_mesh = obj["CustomMesh"]
            for key,dtype in MESH_DATA.items():
                if key in custom_mesh:
                    url = custom_mesh[key]
                    if url: # make sure not empty
                        if url[:4] != "http":
                            url = "http://" + url # partly handles these
                        if dtype == DataType.image:
                            image_urls[(url, dtype)] = url_to_tts(url)
                        elif dtype == DataType.model:
                            model_urls[(url, dtype)] = url_to_tts(url)

    return image_urls, model_urls

if __name__ == '__main__':
    download = False
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Unhosts Tabletop Simulator workshop custom content.")
    parser.add_argument("json_input", help="path to either a WorkshopFileInfos file, or one or more Workshop mod .json files", nargs="+")
    parser.add_argument("--output", "-o", help="where to store the Models and Images subdirectories")
    parser.add_argument("--replace", "-r", help="replace files already in the output directory")
    args = parser.parse_args()

    all_image_urls = {}
    all_model_urls = {}

    if len(args.json_input) == 1 and os.path.basename(args.json_input[0]) == "WorkshopFileInfos.json": # this wont ever break, ever! please
        print("Loaded WorkshopFileInfos.json; listing json names")

        with open(args.json_input[0], "r", encoding="utf-8") as fp:
            file_infos = load(fp)

        name_map = {}
        for info in file_infos:
            directory = info["Directory"]
            # print(info, directory[-4:])

            if directory[-4:] == "json": # I mean, we are only looking for json.
                name_map[info["Name"]] = directory

        pprint.pprint(name_map)

        print("\nType the name, or start of the name of the workshop mod you wish to dump.")

        name = None
        while True:
            query = input("> ").lower()
            matches = list(n for n in list(name_map) if n.lower().startswith(query))

            if query == "q" or query == "quit":
                sys.exit()

            if matches and len(matches) == 1: # try to be specific.
                name = matches[0]
                break
            elif len(matches) > 1:
                print("Multiple matches, be more specific;",matches)
            else:
                print("No matches found.")

        print(name)
        image_urls, model_urls = parse_tts_custom_object(name_map[name])

        all_image_urls.update(image_urls)
        all_model_urls.update(model_urls)

    else:
        for json in args.json_input:
            print(json)
            image_urls, model_urls = parse_tts_custom_object(json)

            all_image_urls.update(image_urls)
            all_model_urls.update(model_urls)

    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(args.json_input[0])),
            "Retrieved")

    print("Output directory:", output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_dir = os.path.join(output_dir, "Images")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    model_dir = os.path.join(output_dir, "Models")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    print("\nURL's to nab:")

    # get a list of all urls
    all_urls = list(all_model_urls)
    all_urls.extend(list(all_image_urls))

    pprint.pprint(all_urls)

    print("\nGrabbing {} files".format(len(all_urls)))
    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(load_tts_url, url): url for url in all_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            data = future.result()

            print("(%d/%d) %s" % (n, len(all_urls), url[0]))

            if data:
                if url[1] == DataType.image:
                    path = os.path.join(image_dir, all_image_urls[url])
                    if not os.path.isfile(path) or args.replace:
                        with open(path, "wb") as fp:
                            fp.write(data)
                    else:
                        print("\tAlready exists, skipping.")

                elif url[1] == DataType.model:
                    path = os.path.join(model_dir, all_model_urls[url])
                    if not os.path.isfile(path) or args.replace:
                        with open(path, "wb") as fp:
                            fp.write(data)
                    else:
                        print("\tAlready exists, skipping.")

                sys.stdout.flush()
            n += 1

    print("Done!")
