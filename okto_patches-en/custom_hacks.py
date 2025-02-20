import pathlib
from dataclasses import dataclass


@dataclass
class ReplaceTilesHack:
    msg:        str
    image_path: pathlib.Path
    addr_range: range

@dataclass
class ReplaceTilesAndMapHack:
    msg:                str
    image_path:         pathlib.Path
    tiles_addr_range:   range
    tilemap_addr_range: range

@dataclass
class ReplaceBytesHack:
    msg:        str
    new_bytes:  bytes
    addr_range: range

@dataclass
class ReplaceSingleBytesHack:
    msg:        str
    new_bytes:  dict[int, int]  # key is the address in the ROM, value is the new byte value

@dataclass
class ReplaceTblTextHack:
    msg:        str
    text:       str
    addr_range: range

custom_hacks = [

    ## -------------------------------------------------------------------
    ## 1st title screen
    ## -------------------------------------------------------------------

    # Replace the Game-Tek logo with the vegimals
    ReplaceTilesHack(
        'Replace the Game-Tek logo with the vegimals',
        pathlib.Path('images/patches/tiles_Game_Tek_Logo_-_Vegimals.png'),
        range(0x94a1, 0x9601)
    ),

    # Fix the order of the tiles, since the empy tiles are in different
    # places in the vegimals image.
    ReplaceBytesHack(
        'Fix the order of the vegimals tiles',
        bytes([0x20, 0x0c, 0x00, 0x00, 0xa5, 0xa6, 0xa7, 0xa8, 0x00, 0xa9,
               0x20, 0x2c, 0x00, 0x00, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf,
               0x20, 0x4c, 0x00, 0x00, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5,
               0x20, 0x6c, 0x00, 0x00, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0x00]),
        range(0xc5d, 0xc85)
    ),

    # Replace the palettes with others matching our image.
    ReplaceBytesHack(
        'Replace palettes with others matching the vegimals tiles',
        bytes([0x0f, 0x2a, 0x20, 0x38,
               0x0f, 0x2c, 0x20, 0x38,
               0x0f, 0x1b, 0x20, 0x26,
               0x20, 0x1b, 0x20, 0x23]),
        range(0x861, 0x871)
    ),

    # Replace the used palettes in the title screen.
    ReplaceBytesHack(
        'Replace the used palettes in the title screen',
        bytes([0x55, 0x55, 0x55, 0x88, 0xdc, 0x55, 0x55, 0x55]),
        range(0x918, 0x920)
    ),

    ## -------------------------------------------------------------------
    ## 2nd (animated) title screen
    ## -------------------------------------------------------------------

    # Fix the palette entries of the logo to be consistent
    ReplaceBytesHack(
        'Fix the palette entries of the logo to be consistent',
        bytes([0xff] * 11),
        range(0x8fd, 0x908)
    ),

    ## -------------------------------------------------------------------
    ## Actual game screen
    ## -------------------------------------------------------------------

    # Replace the upper part of the letter wall (the decoration around the
    # letter tiles) with an underwater theme.
    ReplaceTilesHack(
        'Replace the letterwall deco tiles',
        pathlib.Path('images/patches/tiles_letterwall_deco.png'),
        range(0xa471, 0xaac1)
    ),

    # Change the palette for the letter wall decoration.
    ReplaceBytesHack(
        'Change the letterwall deco palette colors',
        bytes([0x00, 0x0a, 0x1c]),  # dark grey, dark green, darker blue
        range(0x822, 0x825)
    ),

    # Replace the lower part of the letter wall (the floor in front of the
    # letter wall)  with tiles similar to pebbles.
    ReplaceTilesHack(
        'Replace the letterwall floor tiles',
        pathlib.Path('images/patches/tiles_letterwall_floor.png'),
        range(0xaac1, 0xac91)
    ),

    # Change the palette for the letter wall floor
    ReplaceBytesHack(
        'Change the letterwall floor palette colors',
        bytes([0x07, 0x17, 0x37]),  # different shades of brown
        range(0x826, 0x829)
    ),

    # Change the palette for empty letter tiles
    ReplaceBytesHack(
        'Change the palette colors for empty letter tiles',
        bytes([0x03, 0x13, 0x23]),  # dark purple, purple, light purple
        range(0x82a, 0x82d)
    ),

    # Replace the backdrop color of the game screen (with the letter wall)
    # with a color indicating underwater.
    ReplaceBytesHack(
        'Change the backdrop color of the game screen (with the letter wall)',
        bytes([0x21]),
        range(0x871, 0x872)
    ),

    # Due to the change of the backdrop color the bevel borders look a bit
    # strange. Therefore we replace the invisible parts (that let the
    # backdrop color shine through) by a solid color. This gives a line
    # border experience. Not really beautiful, but better than the
    # transparent parts of the border.
    ReplaceTilesHack(
        'Replace bevel border tiles with non-transparent ones',
        pathlib.Path('images/patches/tiles_Bevel_Borders.png'),
        range(0x9a61, 0x9d41)
    ),

    # Fix a few glitches in the letter tiles where the color of some pixels
    # is odd. The affected letters are B, M, N, F.
    ReplaceSingleBytesHack(
        'Fix odd pixel colors in letter tiles',
        { 0x9dd5: 0xe3,
          0x9dd6: 0xe3,
          0x9ff3: 0xfb,
          0xa02c: 0x71,
          0xa1aa: 0x5e }
    ),

    ## -------------------------------------------------------------------
    ## Bonus round prizes (replace images, palette and texts)
    ## -------------------------------------------------------------------

    # INFO: The tilemaps are located somewhere around $4781 - $xxxx.

    ## --- Emerald Necklace → Smart Sisters Dinner ---

    # Replace the image of the bonus prize “Emerald Necklace” with
    # ???.
    ReplaceTilesHack(
        'Replace the bonus prize “Emerald Necklace” tiles with the “Smart Sisters Dinner”',
        pathlib.Path('images/patches/tiles_Emerald_Necklace_-_Smart_Sisters.png'),
        range(0x6ed2, 0x71c2)
    ),

    # Adjust tilemap to set the empty tiles to different places.
    ReplaceBytesHack(
        'Adjust the tilemap of the bonus prize “Emerald Necklace” to move the empty tiles.',
        bytes([0x00, 0x00]),
        range(0x4799, 0x479b)
    ),

    # Replace the /sprite/ image of the bonus prize “Emerald Necklace” with
    # the “Smart Sisters Dinner”. The sprite is used to get 3 additional
    # colors into the image. In that case to display the table and dishes
    # and detail on the characters.
    ReplaceTilesHack(
        'Replace the bonus prize “Emerald Necklace” sprites with the “Smart Sisters Dinner”',
        pathlib.Path('images/patches/tiles_Emerald_Necklace_-_Smart_Sisters_-_Sprites.png'),
        range(0x15b7f, 0x15cef)
    ),

    # Move the position of the sprites of the “Smart Sisters Dinner” around
    # to match the new image.
    ### FIXME: If we relocate /all/ of the sprite tiles, it breaks other
    ###        pictures. Therfore we use 3 sprite tiles less.
    ReplaceBytesHack(
        'Move the sprites of the “Smart Sisters Dinner” around',
        bytes([0x44, 0xff,
               0x1c, 0x07, 0x24, 0x07, 0x44, 0x07,
               0x0c, 0x0f, 0x1c, 0x0f, 0x24, 0x0f, 0x2c, 0x0f, 0x34, 0x0f, #0x3c, 0x0f,
               0x44, 0x0f,
               0x0c, 0x17, 0x1c, 0x17, 0x24, 0x17, 0x2c, 0x17, 0x34, 0x17, #0x3c, 0x17,
               0x44, 0x17,
               0x1c, 0x1f, 0x24, 0x1f, 0x2c, 0x1f, 0x34, 0x1f, #0x3c, 0x1f,
               0x00]),
        range(0x4b23, 0x4b4c)
    ),

    # Change the palette for the Smart Sisters Dinner.
    ReplaceBytesHack(
        'Replace the palette colors for the “Smart Sisters Dinner”',
        bytes([0x17, 0x27, 0x37]),  # brown, orange, beige
        range(0x41f1, 0x41f4)
    ),

    # Change the palette for the sprites in the bonus prize “Smart Sisters Dinner”.
    ReplaceBytesHack(
        'Replace the palette colors for the “Smart Sisters Dinner” sprite tiles',
        bytes([0x2a, 0x11, 0x20]),  # green, blue, white
        range(0x41df, 0x41e2)
    ),

    # Change the prize name for the “Smart Sisters Dinner”.
    ReplaceTblTextHack(
        'Replace the prize name for the “Smart Sisters Dinner”',
        '  Mystery Dinner  ',
        range(0x4651, 0x4663)
    ),


    ## --- Carribean Beach → Wracktauchen ---

    # Replace the image of the bonus prize “Carribean Beach” with
    # the Sunken Ship Tour.
    ReplaceTilesHack(
        'Replace the bonus prize “Carribean Beach” tiles with the “Sunken Ship Dive”',
        pathlib.Path('images/patches/tiles_Carribbean_Cruise_-_Sunken_Ship.png'),
        range(0x67d2, 0x6b02)
    ),

    # Change the palette for the Sunken Ship Dive.
    ReplaceBytesHack(
        'Replace the palette colors for the “Sunken Ship Dive”',
        bytes([0x1b, 0x0a, 0x08]),  # lighter green, darker green, brown
        range(0x41f4, 0x41f7)
    ),

    # Change the prize name for the Sunken Ship Tour.
    ReplaceTblTextHack(
        'Replace the prize name for the “Sunken Ship Dive”',
        ' Sunken Ship Dive ',
        range(0x4663, 0x4675)
    ),

    ## --- Beach House → Treasure Map ---

    # Replace the image of the bonus prize “Beach House” with
    # Treasure Map.
    ReplaceTilesHack(
        'Replace the bonus prize “Beach House” tiles with the “Treasure Map”',
        pathlib.Path('images/patches/tiles_Beach_House_-_Treasure_Map.png'),
        range(0x6b12, 0x6ec2)
    ),

    # Change the palette for the Treasure Map
    ReplaceBytesHack(
        'Replace the palette colors for the “Treasure Map”',
        bytes([0x07, 0x17, 0x37]),  # brown, orange, ocker
        range(0x41f7, 0x41fa)
    ),

    # Replace the /sprite/ image of the bonus prize “Beach House” with
    # Treasure Map. The sprite is used to get an additional color into the image.
    # In that case to mark the cross with a red color.
    ReplaceTilesHack(
        'Replace the bonus prize “Beach House” sprites with the “Treasure Map”',
        pathlib.Path('images/patches/tiles_Beach_House_-_Treasure_Map_-_Sprite.png'),
        range(0x15b1f, 0x15b7f)
    ),

    # Change the palette for the target cross in the treasure map.
    ReplaceBytesHack(
        'Replace the palette colors for the “Treasure Map” sprite tiles',
        bytes([0x16, 0x29, 0x2c]),  # red, irrelevant, irrelevant
        range(0x41e5, 0x41e8)
    ),

    # Change the prize name for the Treasure Map.
    ReplaceTblTextHack(
        'Replace the prize name for the “Treasure Map”',
        '   Treasure Map   ',
        range(0x4675, 0x4687)
    ),

    ## --- April in Paris → Deep Sea Exploration ---

    # Replace the image of the bonus prize “April in Paris” with
    # Deep Sea Exploration.
    ReplaceTilesAndMapHack(
        'Replace the bonus prize “April in Paris” tiles with the “Deep Sea Exploration”',
        pathlib.Path('images/patches/April_in_Paris_-_Octolab.png'),
        range(0x6182, 0x64c2),
        range(0x483e, 0x487a)
    ),

    # Change the palette for the Deep Sea Exploration
    ReplaceBytesHack(
        'Replace the palette colors for the “Deep Sea Exploration',
        bytes([0x2a, 0x21, 0x2d]),  # green, blue, grey
        range(0x41fa, 0x41fd)
    ),

    # Change the prize name for the Deap Sea Exploration
    ReplaceTblTextHack(
        'Replace the prize name for the “Deep Sea Exploration',
        'Deep Sea Exploring',
        range(0x4687, 0x4699)
    ),

    ## --- Concorde to London → Oktopod ---

    # Replace the image of the bonus prize “Concorde to London” with
    # the Octopod.
    ReplaceTilesHack(
        'Replace the bonus prize “Concorde to London” tiles with the “Octopod Visit”',
        pathlib.Path('images/patches/tiles_Concorde_to_London_-_Oktopod.png'),
        range(0x71d2, 0x7542)
    ),

    # Change the palette for the Oktopod.
    ReplaceBytesHack(
        'Replace the palette colors for the “Octopod Visit”',
        bytes([0x17, 0x1b, 0x10]),  # orange, grey, green
        range(0x41fd, 0x4200)
    ),

    # Change the prize name for the Oktopod.
    ReplaceTblTextHack(
        'Replace the prize name for the “Octopod Visit”',
        'Visit the Octopod ',
        range(0x4699, 0x46ab)
    ),

    ## --- Bentley → Gup B ---

    # Replace the upper part of the letter wall (the decoration around the
    # letter tiles) with an underwater theme.
    ReplaceTilesHack(
        'Replace the bonus prize “Bentley” tiles with the “Gup B Race”',
        pathlib.Path('images/patches/tiles_Bentley_-_Gup_B.png'),
        range(0x64c2, 0x67d3)
    ),

    # Change the palette for the Gup B.
    ReplaceBytesHack(
        'Replace the palette colors for the “Gup B Race”',
        #bytes([0x26, 0x0a, 0x10]),  # orange, grey, green
        bytes([0x17, 0x1b, 0x10]),  # orange, grey, green
        range(0x4200, 0x4203)
    ),

    # Change the prize name for the Gup B.
    # Attention! Contrary to all the other bonus prizes this one has a
    # maximum length of 12 characters (instead of 18).
    ReplaceTblTextHack(
        'Replace the prize name for the “Gup B Race”',
        'Gup B Racing Trip ',
        range(0x46ab, 0x46bd)
    ),



]
