from PIL import Image, ImageDraw, ImageColor
from . import map_cfg
import math

# 1299 pixels wide, 999 pixels tall

def draw_hold(draw, order, color):
    location_todraw=order['new']
    (x,y)=map_cfg.unit_locations[location_todraw]
    draw.ellipse([(x-12,y-12),(x+12,y+12)], outline='black')
    return draw

def draw_move(draw, order, color):
    location_draw_to = order['new']
    location_draw_from = order['conflict']
    (x0, y0) = map_cfg.unit_locations[location_draw_from]
    (x1, y1) = map_cfg.unit_locations[location_draw_to]

    draw.line([(x0, y0),(x1, y1)], fill=color, width=2)

    xb = 0.9*(x1-x0)+x0
    yb = 0.9*(y1-y0)+y0

    # Work out the other two vertices of the triangle
    # Check if line is vertical
    if x0==x1:
       vtx0 = (xb-5, yb)
       vtx1 = (xb+5, yb)
    # Check if line is horizontal
    elif y0==y1:
       vtx0 = (xb, yb+5)
       vtx1 = (xb, yb-5)
    else:
       alpha = math.atan2(y1-y0,x1-x0)-90*math.pi/180
       a = 8*math.cos(alpha)
       b = 8*math.sin(alpha)
       vtx0 = (xb+a, yb+b)
       vtx1 = (xb-a, yb-b)
    draw.polygon([vtx0, vtx1, x1, y1], fill=color, outline='black')
    return draw

def draw_sup(draw, order, color):
    return draw

def draw_con(draw, order, color):
    return draw

def draw_orders(draw, game_doc):
    orders=game_doc['next_orders']
    print(orders)
    
    if (all(value == [] for value in orders.values())):
        return draw
    else:
        for country in orders.keys():
            all_orders = orders[country]
            color = map_cfg.color_countries[country]
            for order in all_orders:
                switcher={
                    'HOL':draw_hold,
                    'MOV':draw_move,
                    'SUP':draw_sup,
                    'CON':draw_con
                }
                draw=switcher[order['command']](draw, order, color)
    return draw

def draw_supply(draw, game_doc):
    
    for supply in map_cfg.supply_sites.keys():
        (x,y)=map_cfg.supply_sites[supply]
        drawn=False
        for country in map_cfg.color_countries.keys():
            if (supply in game_doc['state'][country]['controls']):
                drawn=True
                draw.rectangle([(x-5,y-5),(x+5,y+5)],fill=map_cfg.color_countries[country],outline='black')
        if (not drawn):
            draw.rectangle([(x-5,y-5),(x+5,y+5)],fill='white',outline='black')

    return draw

def draw_units(draw, game_doc):
    for country in map_cfg.color_countries.keys():
        color = map_cfg.color_countries[country]
        for unit in game_doc['state'][country]['armies']:
            (x,y)=map_cfg.unit_locations[unit]
            draw.ellipse([(x-8,y-8),(x+8,y+8)],fill=color,outline='black')
        for unit in game_doc['state'][country]['fleets']:
            (x,y)=map_cfg.unit_locations[unit]
            draw.polygon([(x-8,y-8),(x,y+8),(x+8,y-8)],fill=color,outline='black')
    return draw

def draw_map_from_state(game_doc):
    map_basic=Image.open('bin/maps/map_with_text.png').convert('RGBA')
    draw=ImageDraw.Draw(map_basic,'RGBA')
    draw=draw_supply(draw, game_doc)
    draw=draw_units(draw, game_doc)
    draw=draw_orders(draw, game_doc)
    return map_basic