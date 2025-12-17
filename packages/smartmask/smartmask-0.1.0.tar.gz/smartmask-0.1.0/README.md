# smartmask

A simple utility to mask sensitive values automatically.

## Install

pip install smartmask

## Usage

'''python

from smartmask import mask

mask("example.gmail.com")
mask("1234567890")
mask("ABCD123DE")

## ouput

e******.gmail.com
12******90
AB*****E

