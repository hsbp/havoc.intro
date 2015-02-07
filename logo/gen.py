#!/usr/bin/env python

from __future__ import division, print_function
from os import path
from PIL import Image, ImageDraw
from itertools import product, chain
from collections import Counter
from sys import stdout, stderr
import json

HEIGHT_RATIO = 0.8

PARAMS = json.load(file(path.join(path.dirname(__file__), '..', 'params.json')))

BG = tuple(PARAMS['bgcolor'])
FG = tuple(PARAMS['fgcolor'])

LOGO = Image.open(PARAMS['logo']).convert('RGB')
LOGO_OLD_W, LOGO_OLD_H = LOGO.size
LOGO_PIXELS = LOGO.load()

LOGO_H = int(PARAMS['height'] * HEIGHT_RATIO)
LOGO_W = LOGO_OLD_W * LOGO_H // LOGO_OLD_H
LOGO_X = (PARAMS['width'] - LOGO_W) // 2
LOGO_Y = int((1 - HEIGHT_RATIO) / 2 * PARAMS['height'])

"""
  x a   b   a
  <---><-><--->         x goes from (x0 - grow_delta) to x0
  |   |   |   |         y goes from (y0 - grow_delta) to y0
     ._____.    ___ y   a goes from 0 to (x1 - x0) / 2
   ,'       ',  _|_ c   b goes from (x1 - x0 + 2 * grow_delta) to 0
   |  color  |   |      c goes from 0 to (y1 - y0) / 2
   |         |  _|_ d   d goes from (y1 - y0 + 2 * grow_delta) to 0
   ',       ,'   |  c  
     '-----'    -'-     color goes from FG to tone
"""

def main():
    white_lines = calc_white_lines()
    white_cols = calc_white_cols(white_lines)
    corners = calc_corners(white_lines, white_cols)
    grow_delta = calc_grow_delta(white_lines, white_cols)

    print(white_lines, white_cols, corners, grow_delta, sep='\n', file=stderr)

    canvas = Image.new('RGB', (PARAMS['width'], PARAMS['height']), BG)

    for frame in xrange(PARAMS['frames']['logo'] + 1 + PARAMS['frames']['logo_still']):
        print(frame, file=stderr)
        logo_copy = LOGO.copy()
        draw = ImageDraw.Draw(logo_copy)
        if frame <= PARAMS['frames']['logo']:
            draw.rectangle([0, white_lines[-2][1], LOGO.size[0] - 1, LOGO.size[1]], BG)
            state = (1.0 / PARAMS['frames']['logo']) * frame
            state_inv = 1 - state
            for ((x0, x1), (y0, y1)) in product(*corners):
                c_line = (y0 + y1) // 2
                colors = Counter(LOGO_PIXELS[i, c_line] for i in xrange(x0, x1))
                if len(colors) < 2:
                    continue
                del colors[BG]

                ((tone, _),) = colors.most_common(1)
                fr, fg, fb = FG
                tr, tg, tb = tone
                color = (int(tr * state + fr * state_inv),
                        int(tg * state + fg * state_inv),
                        int(tb * state + fb *  state_inv))
                gds = int(grow_delta * state_inv)
                gd2 = grow_delta * 2
                w = x1 - x0
                h = y1 - y0

                x = x0 - gds
                y = y0 - gds
                a = int(w / 2.0 * state)
                b = int((w + gd2) * state_inv)
                c = int(h / 2.0 * state)
                d = int((h + gd2) * state_inv)

                draw.pieslice([x, y, x + 2 * a, y + 2 * c], 180, 270, color)
                draw.pieslice([x + b, y, x + 2 * a + b, y + 2 * c], 270, 360, color)
                draw.pieslice([x + b, y + d, x + 2 * a + b, y + 2 * c + d], 0, 90, color)
                draw.pieslice([x, y + d, x + 2 * a, y + 2 * c + d], 90, 180, color)

                draw.rectangle([x + a, y, x + a + b, y + 2 * c + d], color)
                draw.rectangle([x, y + c, x + 2 * a + b, y + c + d], color)

        canvas.paste(logo_copy.resize((LOGO_W, LOGO_H), Image.ANTIALIAS), (LOGO_X, LOGO_Y))
        stdout.write(canvas.tobytes())

def calc_grow_delta(white_lines, white_cols):
    centers = chain.from_iterable(zip(white_lines, white_cols)[1:-1])
    return int(min(b - a for a, b in centers) / 2)

def calc_corners(white_lines, white_cols):
    wl_iter = iter(white_lines)
    wc_iter = iter(white_cols)
    pwl = next(wl_iter)
    pwc = next(wc_iter)
    y_corners = []
    x_corners = []
    try:
        while True:
            nwl = next(wl_iter)
            nwc = next(wc_iter)
            y_corners.append((pwl[1], nwl[0]))
            x_corners.append((pwc[1], nwc[0]))
            pwl = nwl
            pwc = nwc
    except StopIteration:
        pass
    
    return x_corners, y_corners


def calc_white_lines():
    white_lines = None
    for line in xrange(LOGO_OLD_H):
        if all(LOGO_PIXELS[i, line] == BG for i in xrange(LOGO_OLD_W)):
            if white_lines is not None:
                last = white_lines.pop()
                if last[1] == line - 1:
                    white_lines.append((last[0], line))
                else:
                    white_lines.extend([last, (line, line)])
            else:
                white_lines = [(line, line)]
    return white_lines


def calc_white_cols(white_lines):
    white_cols = None
    for col in xrange(LOGO_OLD_W):
        if all(LOGO_PIXELS[col, i] == BG for i in xrange(white_lines[-2][0])):
            if white_cols is not None:
                last = white_cols.pop()
                if last[1] == col - 1:
                    white_cols.append((last[0], col))
                else:
                    white_cols.extend([last, (col, col)])
            else:
                white_cols = [(col, col)]
    return white_cols


if __name__ == '__main__':
    main()
