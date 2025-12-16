# FoxDotLink - Sync mechanism for [Ableton Link](https://www.ableton.com)

## Instalation

``` shell
pip install FoxDotLink
# or
pip install git+https://codeberg.org/FoxDotExtensions/FoxDotLink
```

## Usage

Just import the library and this will connect Ableton Link and change
the bpm to be updated by Ableton Link

``` python
import FoxDotLink

Clock.bpm = var([80,120], 4)
```
