#!/usr/bin/env python

from __future__ import division, print_function
from os import path
from PIL import Image, ImageDraw
from itertools import product, chain
from collections import Counter
from subprocess import Popen, PIPE
from sys import stdout, stderr
import json

PARAMS = json.load(file(path.join(path.dirname(__file__), '..', 'params.json')))

BG = tuple(PARAMS['bgcolor'])
FG = tuple(PARAMS['fgcolor'])

def main():
    canvas = Image.new('RGB', (PARAMS['width'], PARAMS['height']), BG)
    for breeder in PARAMS['breeders']:
        ((sleft, stop), (sright, sbottom)), ((eleft, etop), (eright, ebottom)) = breeder['box']
        start, end = breeder['steps']
        fps = breeder['frame_per_step']
        srot, erot = breeder.get('rotate', [0, 0])
        for c, step in enumerate(xrange(start, end)):
            for i in xrange(1, fps + 1):
                inframe = Image.open(path.join(path.dirname(__file__), 'images', '{0:06}.png'.format(step)))
                w, h = inframe.size
                cif = (c + i / fps) / (end - start)
                rot = srot + (erot - srot) * cif
                print(c, i, rot, file=stderr)
                left = sleft + (eleft - sleft) * cif
                right = sright + (eright - sright) * cif
                top = stop + (etop - stop) * cif
                bottom = sbottom + (ebottom - sbottom) * cif
                mag = min(PARAMS['width'] / (right - left), PARAMS['height'] / (bottom - top))
                inframe = inframe.resize((int(w * mag), int(h * mag)))
                if rot:
                    center_x = int((right + left) / 2 * mag)
                    center_y = int((top + bottom) / 2 * mag)
                    size = int(max(right * mag - center_x, bottom * mag - center_y)) * 2
                    inframe.paste(
                            inframe.crop([center_x - size, center_y - size,
                                center_x + size, center_y + size]).rotate(
                                    rot, resample=Image.BICUBIC),
                            (center_x - size, center_y - size))
                canvas.paste(inframe, (int(-left * mag), int(-top * mag)))
                stdout.write(canvas.tobytes())


if __name__ == '__main__':
    main()
