# TTS Unhoster
A simple script to quickly dump a Tabletop Simulator workshop mod to disk for archiving or to speed up loading

## Why?
There are two main scenarios this can be useful. The first is to allow mod creators or uploaders to create an archived package of their mod's contents, which they can host as a single file in multiple places, or a torrent, so that there is little issue if one or more of the mod's files becoming unreachable due to a host removing them or closing down.

Secondly, users can use it to prefetch the entirety of a mod so that they don't have to download anything ingame (additionally, to download everything ingame, users would have to spawn every last model -- this script garuntees that every model is fetched).


## Requirements
Python 3 and [Requests](http://docs.python-requests.org/en/latest/) (the latter can be easily installed on most platforms using `pip install requests`).

## Usage
There's multiple ways to use the script:

Drag and drop one or more workshop mod `.json` files onto the script -- it'll put the output folders (and the files they contain) into the same directory as the `.json` named after the first mod.

or

Drag and drop your `WorkshopFileInfos.json` file onto the script -- you'll see a list of the mods you have installed and will be prompted to specify which one to fetch, by name (Helpful as the mod `.json` files have fairly arbitary filenames!)

or

`python unhoster.py [PATH TO JSON FILE/S]` in a terminal (you can point it at `WorkshopFileInfos.json` as well)

Regardless of which above methods you use, you'll end up with a folder which contains two subfolders: `\Images\` and `\Models\`. If you wish to "install" these in your game, simply paste the two folders into the equivalent directory for your system:

    C:\Users\[USERNAME]\Documents\My Games\Tabletop Simulator\Mods\

You can decide whether to replace any conflcting files, though unless the files have been updated but still use the same URL, they'll likely be identical.

If you're packaging the resources for other users, I'd recommend adding a simple README.txt before compressing the folder into a `.zip` -- they don't need the script at all to benefit from the resources (as they simply need to be copied into the aforementioned TTS folder).

    This is an archive of all the custom models and textures featured in the mod.
    Using the files in this archive saves both having Tabletop Simulator download them for you, and garuntees you can use the models (even if the mod's hosting sites shut down!)

    TO INSTALL
    Copy the "\Models\" and "\Images\" folders into:
        "C:\Users\[USERNAME]\Documents\My Games\Tabletop Simulator\Mods\"
    So that they merge with the existing two folders there.

    And you're done! Go check out the models ingame.
You can stick something like the above into the archive, so that users have a reference. You could even link to this `README.md` if you want to show someone what it's all about.

## Arguments

- *Material* `-m --material MATERIAL` - Explicitly tell the script what `.mtl` file to use.
- *Output* `-o --output OUTPUT` - Explicitly tell the script where output to.
- *Add* `-a --add [ADD, ...]` - Additional images to be packed. (Probably useless)
- *No crop* `--no-crop` - Disable any cropping or tiling/unrolling.
- *No tile* `--no-tile` - Ignore any wrapped/tiling of textures (depends on cropping).


## Features
- If you point the script at your `WorkshopFileInfos.json` file (or drag and drop the file onto the script) within `\Mods\Workshop\`, you can run the script on any installed mod by typing in its name.
- You can specify any number of mod `.json` files, the script will combine all of their contents into the same two folders (just as Tabletop Simlator does).
- Multiple downloads are performed at the same time, so it is fairly quick

## How does it work?
When you subscribe to a mod on the workshop, you are sent a `.json` file found within *(on Windows)* your `\Documents\My Games\Tabletop Simulator\Mods\Workshop\` directory. This file tells the game everything it needs to know about a save (or mod), including the URLs it must use to retrieve content (custom model meshes and textures).

When you spawn a model from one of these Workshop mods, Tabletop Simulator first checks to see if you have previously downloaded it, and if so, loads the model from disk (at `\My Games\Tabletop Simulator\Mods\Models\` and `\Images\`). If this fails, it downloads from the URL and places the content into the aforementioned folders.

So, this script effectively does what Tabletop Simulator does ingame, but for an entire mod's (or multiple mod's) worth of content, and into a folder of the user's choosing. You pass it a workshop `.json` file, it nabs the URLs from it and downloads the content into local `\Models\` and `\Images\` folders.

This means you can copy-paste those folders into your `\My Games\Tabletop Simulator\Mods\` folder and have them merge with the folders already there, filling in any missing local files.

Have fun.
