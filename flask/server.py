#!/usr/bin/env python

import flask
from flask_cors import cross_origin 

import logging
logging.basicConfig(level=logging.DEBUG)

app = flask.Flask(__name__)

import roygbiv
import webcolors
import json
import cgi
import Image
import logging
logging.basicConfig(level=logging.DEBUG)

def closest_colour(requested_colour):
    min_colours = {}
    
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_closest(hex):

    rgb = webcolors.hex_to_rgb(hex)
    
    try:
        closest_name = actual_name = webcolors.rgb_to_name(rgb)
    except ValueError:
        closest_name = closest_colour(rgb)
        actual_name = None
        
    if actual_name:
        actual = webcolors.name_to_hex(actual_name)
    else:
        actual = None
            
    closest = webcolors.name_to_hex(closest_name)

    return actual, closest

def prep(hex):

    web_actual, web_closest = get_closest(hex)
    
    return {
        'colour': hex,
        'closest': web_closest,
    }

@app.route('/ping', methods=['GET'])
@cross_origin(methods=['GET'])
def ping():
    rsp = {'stat': 'ok'}
    return flask.jsonify(**rsp)

@app.route('/extract', methods=['GET'])
@cross_origin(methods=['GET'])
def get_palette(path):

    roy = roygbiv.Roygbiv(path)
    average = roy.get_average_hex()
    palette = roy.get_palette_hex()
    
    average = prep(average)
    palette = map(prep, palette)
    
    rsp = { 'reference-closest': 'css3', 'average': average, 'palette': palette }

    status = '200 OK'
    rsp = {}

    path = flask.request.args.get('path')

    if not path:
        flask.abort(400)

    try:
        rsp = get_palette(path)
        rsp['stat']  = 'ok'
    except Exception, e:
        flask.abort(500)
        
    if rsp['stat'] != 'ok':
        flask.abort(500)

    logging.debug("%s : %s" % (path, status))

    return flask.jsonify(**rsp)


if __name__ == '__main__':
    debug = True	# sudo make me a CLI option
    app.run(debug=debug)