# -*- coding: utf-8 -*-
import json
from flask import Response

from .database import Session
from .utils import Dimension, Schema, decimal_default, list_from_str
from .utils import GreyhoundReadSchema, GreyhoundInfoSchema
from .conf import Config

class GreyhoundInfo(object):

    def run(self):
        # a little faster than boundingbox()
        # box = Session.boundingbox()
        box = Session.boundingbox2()

        # approximate but far faster than Session.numpoints()
        # npoints = Session.numpoints()
        npoints = Session.approx_row_count() * Session.patch_size()

        srs = Session.srs()
        schema_json = GreyhoundInfoSchema().json()

        info = json.dumps( {
            "baseDepth" : 6,
            "bounds" : [box['xmin'], box['ymin'], box['zmin'],
                box['xmax'], box['ymax'], box['zmax']],
            "boundsConforming" : [box['xmin'], box['ymin'], box['zmin'],
                box['xmax'], box['ymax'], box['zmax']],
            "numPoints" : npoints,
            "schema" : schema_json,
            "srs" : srs,
            "type" : "octree"}, default = decimal_default )

        resp = Response(info)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'text/plain'
        return resp

class GreyhoundRead(object):

    def run(self, args):

        read = ""

        offset = list_from_str(args['offset'])
        box = list_from_str(args['bounds'])

        read = Session.get_points(box, GreyhoundReadSchema().dims, offset,
            args['scale'], args['depthEnd'] - Config.DEPTH + 1)

        resp = Response(read)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'application/octet-stream'
        return resp

class GreyhoundHierarchy(object):

    def run(self):
        resp = Response(json.dumps(self.fake_hierarchy(0, Config.DEPTH)))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = 'text/plain'
        return resp

    def fake_hierarchy(self, begin, end):
        p = {}
        begin = begin + 1

        if begin != end:
            p['n'] = 500*1000

            if begin != (end-1):
                p['nwu'] = self.fake_hierarchy(begin, end)
                p['nwd'] = self.fake_hierarchy(begin, end)
                p['neu'] = self.fake_hierarchy(begin, end)
                p['ned'] = self.fake_hierarchy(begin, end)
                p['swu'] = self.fake_hierarchy(begin, end)
                p['swd'] = self.fake_hierarchy(begin, end)
                p['seu'] = self.fake_hierarchy(begin, end)
                p['sed'] = self.fake_hierarchy(begin, end)

        return p