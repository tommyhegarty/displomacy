from PIL import Image, ImageDraw, ImageColor
from . import map_cfg

# 1299 pixels wide, 999 pixels tall

def draw_supply(draw, game_doc):
    
    for supply in map_cfg.supply_sites.keys():
        (x,y)=map_cfg.supply_sites[supply]
        drawn=False
        for country in map_cfg.color_countries.keys():
            if (supply in game_doc['state'][country]['controls']):
                drawn=True
                draw.rectangle([(x-8,y-8),(x+8,y+8)],fill=map_cfg.color_countries[country],outline='black')
        if (not drawn):
            draw.rectangle([(x-8,y-8),(x+8,y+8)],fill='white',outline='black')

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
    map_basic=Image.open('bin/maps/map_with_text.png').convert('RGB')
    draw=ImageDraw.Draw(map_basic)
    draw=draw_supply(draw, game_doc)
    draw=draw_units(draw, game_doc)
    return map_basic