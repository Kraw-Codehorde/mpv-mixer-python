# **README File**

## **MPV Random Segmented Playlist Generator**

Generates a playlist from files in directory, randomly picking segments to play in each file.

## **Introduction**

Simple program that does something i couldn't get to do with LUA scripting in MPV, thus decided to write my own on Python.

As said in the description, it chooses segments/chunks of video files and add them to a playlist.

## **Installation**

A portable version (.exe for windows systems) is available on releases section.

If you want to download the source code the only dependencies needed to use this script are pymediainfo and more_iteritools. Use a tool like PIP to install them with your python interpreter.

`pip install more-itertools`
`pip install pymediainfo`

## **Usage**

There are two ways to use this program.

If downloaded the executable:

1. Place the executable in the folder with all your media files and just run it.
2. On the shell window it will prompt you for a a duration. This duration refers to the length of each segment/chunk that you want to play. By default its 15 seconds, caution against lowering it too much, mpv might bug and not work as expected.
3. (optional) Make a .bat shortcut to point at this file location so you dont need to copy/paste it on each different location. A simple .bat like this will work out just fine.

```
@echo off
start "" "C:\Users\Santi\projects\mpv-mixer-python\dist\main.exe" "%~dp0"
```

If downloaded just main.py:

1. Like explained in previous section, make sure dependencies are installed, and you also have a working python installation in your system.
2. Place the file in your folder containing your video files.
3. Simply run the script: **`python main.py`**

## **License**

Project Title is released under the MIT License. See the **[LICENSE](https://www.blackbox.ai/share/LICENSE)** file for details.

## **FAQ**

**Q:** What is this for?

**A:** It just makes a playlist in mpv with random sections from different videos. I didn't see one like this one on the internet, so i had to make it.

**Q:** How do I use it?

**A:** If you are on Windows and don't know how to use the script directly, then there's an .exe file in Release section. Place this file on the folder with all your videos and run it.

**Q:** Why use Python instead of native LUA for MPV?

**A:** I tried to at first, but it would always bug out and never work as intended. So i decided to try my hand at writing this in a Python wrapper.

**Q:** There's a bug, or it stops working after some time, what do i do?

**A:** Open a ticket and will see what i can do. Reminder this was make on a rush, and this was my first time working with subprocesses in Python. There's A LOT to improve (and will do so with time), and even more to learn about handling pipes. But so far it works for my purposes, thus i released it as it is.

## **Changelog**

- **0.1.0:** Initial release

## **Contact**

If you have any questions or comments about Project Title, please contact **[Nico](kraw.hq@gmail.com)**.
