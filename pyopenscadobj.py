#!/usr/bin/env python
# Copyright (C) 2016 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
# License: GPLv3+


import time
import math
import os
import itertools

import openscad

from pyopenscad import *
from polysurface import spline_double_divide, Offset, SurfaceFromCurves
from polysurface import vtrans, vmult, vsub
from copy import deepcopy
from pyscadutil import B0, B45, pin
from pyscadutil import curvebox, shearedcube, hollowbox, touch_arc
from pyscadutil import L, R, T, D, F, B

BOM_3D = 0x1
BOM_PART = 0x2
BOM_ASSY = 0x4
BOM_3D_COMPOSITE = 0x8
BOM_NOSCAD = 0x10
BOM_PARTSONLY = (BOM_3D|BOM_PART|BOM_ASSY)
BOM_ALL = 0xfffffffff

def cmpfn(f1, f2):
    return cmp(f1[1][1] & BOM_PARTSONLY, f2[1][1] & BOM_PARTSONLY) or \
           cmp(f1[0], f2[0])

BOM_STR = {BOM_3D: '3D', BOM_PART: 'PART', BOM_ASSY: 'ASSY',
           BOM_3D_COMPOSITE: '3D'}

pth_postfix = ""

class Object:
    def __init__(self, o=None, bomtype=0, description=None, url=None):
        self.description = description
        self.url = url
        self.o = o
        self.parent = None
        self.parent_offset = [0.0]*3
        self.children = []
        self._size = [0]*3
        self._prot = [0]*3
        self._rot = []
        self._ptrans = [0]*3
        self._trans = [0]*3
        self._colour = None
        self._pcolour = None
        self._visible = True
        self._bomtype = bomtype
    
    def name(self):
        return self.__class__.__name__

    def get_description(self):
        if self.description:
            return self.description
        if self._bomtype == BOM_ASSY:
            l = []
            for c in self.children:
                l.append(repr(c))
            return ', '.join(l)
        return ''

    def get_bom_info(self):
        return [self.get_description(), self.url or '']

    def __repr__(self):
        return self.__class__.__name__

    def _get_bom_list(self, bomtype=BOM_ALL):
        if self._bomtype & bomtype:
            bominfo = self.get_bom_info()
            l = [[self.name(), self._bomtype] + bominfo]
        else:
            l = []
        for c in self.children:
            l += c._get_bom_list()
        return l

    def add_support(self):
        return False

    def creaate_support(self):
        return None

    def get_bom(self):
        l = self._get_bom_list()
        d = {}
        for (item, bomtype, desc, url) in l:
            if not d.has_key(item):
                d[item] = [0, bomtype, desc, url]
            d[item][0] += 1
        l = []
        items = d.items()
        items.sort(cmpfn)
        for (k, (count, bomtype, desc, url)) in items:
            bomtype &= ~BOM_NOSCAD
            l.append("%s\t%d\t%s\t%s\t%s" % (BOM_STR[bomtype], count, k, desc, url))
        return '\n'.join(l) + '\n'


    def set_visible(self, visible):
        self._visible = visible

    def set_parent(self, parent, parent_offset=None):
        self.parent = parent
        self.parent_offset = parent_offset
        self.parent.children.append(self)

    def set_colour(self, rgba):
        self._colour = rgba

    def set_postcolour(self, rgba):
        self._pcolour = rgba

    def size(self, r):
        self._size = r

    def rotate(self, r):
        if not isinstance(r[0], list):
            r = [r]
        self._rot += r # keep on adding rotations

    def postrotate(self, t):
        self._prot = t

    def posttranslate(self, t):
        self._ptrans = t

    def translate(self, t):
        self._trans = t

    def get_stl_orientation(self):
        # for generate_stls, use to orientate for printing
        return None

    def get_parent_offset(self):
        return self.parent_offset
        #if self.parent is None:
        #return vtrans(self.parent.get_parent_offset(), self.parent_offset)

    def openscad_to_stl(self):
        name = self.name()
        scadpth = os.path.join(".", "scad", pth_postfix)
        stlpth = os.path.join(".", "scad", "stl", pth_postfix)
        try:
            os.makedirs(scadpth)
        except OSError:
            pass
        try:
            os.makedirs(stlpth)
        except OSError:
            pass

        scad_name = os.path.join(scadpth, name + ".scad")
        stl_name = os.path.join(stlpth, name + ".stl")

        include_children = self._bomtype == BOM_3D_COMPOSITE
        print "generating scad for ", name, include_children
        o = self.obj(include_children, True)
        r = self.get_stl_orientation()
        if r:
            o = rotate(r).add(o)
            
        scad_render_to_file(o, scad_name)
        print "generating stl for ", name
        openscad.run("-o", stl_name, scad_name)

    def generate_stls(self):
        if self._bomtype == BOM_3D or self._bomtype == BOM_3D_COMPOSITE:
            self.openscad_to_stl()
        for c in self.children:
            c.generate_stls()

    def obj(self, add_children=True, scad_check=False):
        u = union()
        d = self.o or union()
        if self.add_support():
            s = self.create_support()
            if s:
                u += s

        if self._colour:
            c = color(self._colour)
            c.add(d)
            d = c
        if self._visible:
            u += d
        if add_children:
            for c in self.children:
                if scad_check and c._bomtype & BOM_NOSCAD:
                    continue
                o = c.obj(add_children, scad_check)
                u += translate(c.get_parent_offset()).add(o)

        # ok resize and rotate... but first, move everything back to the origin
        if self._size != [0]*3:
            u = resize(self._size, False).add(u)
        if self._trans != [0]*3:
            u = translate(self._trans).add(u)
        for r in self._rot:
            u = rotate(r).add(u)
        if self._ptrans != [0]*3:
            u = translate(self._ptrans).add(u)
        if self._prot != [0]*3:
            u = rotate(self._prot).add(u)
        if self._pcolour:
            c = color(self._pcolour)
            c.add(u)
            u = c
        return u


class STLObject(Object):
    def __init__(self, stlfile, bomtype=BOM_3D, description=None, url=None):
        Object.__init__(self, import_stl(filename = stlfile),
                              bomtype, description, url)
    

