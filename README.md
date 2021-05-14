# aax2m4b

aax2m4b bakes Audiobooks (m4b) from aax files.

## Download release

* build your own :-)

## Extra note

* I write this software as OpenSource and don't expect to be paid for it. I write this stuff for myself and that makes
  me happy.
* These are the consequences of writing free software:
    * I am not in the position to [sign](https://developer.apple.com/developer-id/) my code
      "The Apple Way" as I am not prepared to pay $99 a year to give away (less than) free software 😄. This means that
      you might have to perform some extra steps to be able to run a (possible future) distribution on your machine.
    * You can not expect support from me in any way. As long as I am happy with how it works I hope you like it to.
      Feature requests will only be honoured if I see a benefit in it. You are of course always free to create a Pull
      Request with your proposed feature.

# Donations / Appreciation

* If you like this software and think I deserve a nice cold beer, or a good cup of coffee you can consider giving me
  a [donation](http://ivo2u.nl/Zc).
* Just showing your appreciation on Twitter is almost just as nice!

# If you are a Developers

## Requirements

- Python 3.9 (brew install python)

To be placed in src/resources:

- ffmpeg (https://evermeet.cx/ffmpeg/)
- ffprobe (https://evermeet.cx/ffmpeg/)
- mp4art (brew install mp4v2)
- AtomicParsley (brew install AtomicParsley
  or [binary](https://github.com/wez/atomicparsley/releases/))
- rcrack (build from source: https://github.com/inAudible-NG/RainbowCrack-NG)


how...

```shell
cp -vf "$(which ffmpeg)" "./src/resources"
cp -vf "$(which ffprobe)" "./src/resources"
cp -vf "$(which mp4art)" "./src/resources"
cp -vf "$(which AtomicParsley)" "./src/resources"
```

## Create environment

To create and activate the environment

```shell
python3.9 -m venv venv
source venv/bin/activate
pip install poetry 
poetry install
```

## Usage

```shell
cd PROJECT
source venv/bin/activate
python src/aax2m4b.py

# or

DEBUG=True python src/aax2m4b.py # Will show extra debug logging in the log window
```

## Build Mac App

```shell
source venv/bin/activate
./build.sh [clean]
```

The clean option will first remove the build and dist folder before rendering all the images to the
ivonet/image/images.py file and building the application

See also the build.sh script

## Rendering the images

```shell
./images.sh
```

This script will convert all the ./images/*.{bmp,png} images to a format easily understood by wxPython.

## Collaboration

If you want to collaborate on this project to improve it or give in more functionality please drop
me a PM on twitter (@ivonet)

# See also

* [My Blog](https://www.ivonet.nl) 
