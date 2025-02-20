#!/bin/env python3

import argparse
import ast
import copy
import pathlib
import random
import re
import sys

from collections import OrderedDict
from dataclasses import dataclass
from hashlib     import sha1
from PIL         import Image

COL_RST = '\033[0m'
COL_BLD = '\033[1m'
COL_FNT = '\033[2m'
COL_RED = '\033[31m'
COL_GRN = '\033[32m'
COL_YLW = '\033[33m'
COL_BLU = '\033[34m'
COL_MGT = '\033[35m'
COL_CYN = '\033[36m'
COL_WHT = '\033[37m'
COL_BLD = '\033[1m'
COL_FNT = '\033[2m'
COL_NRM = '\033[22m'

M_DBG = COL_BLU + COL_FNT
M_VBS = COL_CYN + COL_FNT
M_NFO = COL_CYN
M_WRN = COL_YLW
M_ERR = COL_RED
M_SUC = COL_GRN + COL_BLD

LOG_LEVELS = OrderedDict({
        'DEBUG':   M_DBG,
        'VERBOSE': M_VBS,
        'INFO':    M_NFO,
        'WARN':    M_WRN,
        'ERROR':   M_ERR,
        })
LOG_LEVELS_ORDER = ['DEBUG', 'VERBOSE', 'INFO', 'WARN', 'ERROR']
log_level = 2


PATTERN_CATEGORY_LINE = re.compile("\s*\[([a-zA-Z0-9 '$?-]+)\]\s*")

TBL_FILE = "assets/wheel.tbl"

WEDGE_VALUES= {
    100:         0xac,
    150:         0x2c,
    200:         0xad,
    250:         0x2d,
    300:         0xae,
    350:         0x2e,
    400:         0xaf,
    450:         0x2f,
    500:         0xb0,
    550:         0x30,
    600:         0xb1,
    650:         0x31,
    700:         0xb2,
    750:         0x32,
    800:         0xb3,
    850:         0x33,
    1000:        0x0c,
    2000:        0x0d,
    3000:        0x0e,
    4000:        0x0f,
    5000:        0x10,
    6000:        0x11,
    7000:        0x12,
    8000:        0x13,
    'lose_turn': 0xb6,
    'free_spin': 0xb7,
    'bankrupt':  0xb8,
}

# Taken from https://stackoverflow.com/a/61411431
class IntRange:
    def __init__(self, imin=None, imax=None):
        self.imin = imin
        self.imax = imax

    def parse_hex(self, arg):
        try:
            return ast.literal_eval(arg)
        except ValueError:
            return None

    def parse_dec(self, arg):
        try:
            return int(arg)
        except ValueError:
            return None

    def parse(self, arg):
        hexval = self.parse_hex(arg)
        if hexval:
            return hexval
        decval = self.parse_dec(arg)
        if decval:
            return decval
        return None

    def __call__(self, arg):
        value = self.parse(arg)
        if not value:
            raise self.exception()
        if (self.imin is not None and value < self.imin) or (self.imax is not None and value > self.imax):
            raise self.exception()
        return value

    def exception(self):
        if self.imin is not None and self.imax is not None:
            return argparse.ArgumentTypeError(f"Must be an integer between {self.imin} to {self.imax} (inclusive)")
        elif self.imin is not None:
            return argparse.ArgumentTypeError(f"Must be an integer >= {self.imin}")
        elif self.imax is not None:
            return argparse.ArgumentTypeError(f"Must be an integer <= {self.imax}")
        else:
            return argparse.ArgumentTypeError("Must be an integer")


@dataclass(frozen=True)
class Puzzle:
    category:     str
    category_idx: int
    puzzle:       list[str]


@dataclass(frozen=False)
class CategoryWithPuzzles:
    category_name: str
    puzzles:       list[Puzzle]


@dataclass(frozen=False)
class Preset:
    category_addr_range:           range
    category_name_length:          int
    no_of_categories:              int
    no_of_puzzles:                 1000
    length_of_puzzles:             tuple[int, int, int, int]
    puzzle_addr_range:             range
    puzzle_pointers_start_add:     int   # FIXME: For consistency this should be a 'puzzle_pointer_area_addr_range'
    puzzle_pointers_first_value:   bytes
    puzzle_category_ranges:        list[range]
    puzzle_hack_function:          str
    no_of_player_names:            int
    length_of_player_names:        10
    player_names_addr_range:       range
    title_text_addr_range:         range
    marquee_text_addr_range:       range
    timer_addr_choose_action:      int   # except the first action + selection in speed round
    timer_addr_select_consonant:   int   # + first choose action
    timer_addr_bonus_round_select: int   # FIXME: Im Family-Spiel wird der Wert von SELECT_ACTION genommen
    timer_addr_select_vowel:       int
    timer_addr_solve:              int
    timer_addr_solve_bonus:        int
    wedge_bankrupt_addr:           int
    wedge_lose_turn_addr:          int
    tile_range_letter_wall_deco:   range
    pal_addr_letter_wall_deco:     int
    tile_range_letter_wall_floor:  range
    pal_addr_letter_wall_floor:    int
    bg_addr_letter_wall:           int
    tile_range_big_logo:           range
    tilemap_range_big_logo:        range

# Classic edition Rev 0
preset_classic_prg0 = Preset(
   category_addr_range=           range(0x1483, 0x14ca),
   category_name_length=          8,
   no_of_categories=              9,
   no_of_puzzles=                 1000,
   length_of_puzzles=             (11, 13, 13, 11),
   puzzle_addr_range=             range(0x109d0, 0x14618),
   puzzle_pointers_start_add=     0x101fc,
   puzzle_pointers_first_value=   bytes([0xc0, 0x89]),
   puzzle_category_ranges=        [
                                    range(0, 166),
                                    range(166, 357),
                                    range(357, 515),
                                    range(515, 536),
                                    range(536, 724),
                                    range(724, 751),
                                    range(751, 856),
                                    range(856, 898),
                                    range(898, 1000)
                                  ],
   puzzle_hack_function=          'classic',
   no_of_player_names=            20,
   length_of_player_names=        10,
   player_names_addr_range=       range(0x409f, 0x4166),
   title_text_addr_range=         range(0x00, 0x00),   # what is the correct range for the classic edition? Is the text encoded like in the family edition?
   marquee_text_addr_range=       range(0x00, 0x00),   # what is the correct range for the classic edition? Is the text encoded like in the family edition?
   timer_addr_choose_action=      0x1c17,
   timer_addr_select_consonant=   0x1464,
   timer_addr_bonus_round_select= 0x418e,
   timer_addr_select_vowel=       0x1abb,
   timer_addr_solve=              0x4178,
   timer_addr_solve_bonus=        0x45fd,
   wedge_bankrupt_addr=           0x807,
   wedge_lose_turn_addr=          0x7fe,
   tile_range_letter_wall_deco=   range(0xa61f, 0xac6f),
   pal_addr_letter_wall_deco=     0x0000,
   tile_range_letter_wall_floor=  range(0xac6f, 0xae3f),
   pal_addr_letter_wall_floor=    0x0000,
   bg_addr_letter_wall=           0x0000,
   tile_range_big_logo=           0x0000,
   tilemap_range_big_logo=        0x0000,
)
# Classic edition Rev 1
preset_classic_prg1 = copy.deepcopy(preset_classic_prg0)
preset_classic_prg1.puzzle_addr_range       = range(0x109d0, 0x14619)
# Family edition
preset_family       = copy.deepcopy(preset_classic_prg0)
preset_family.category_addr_range           = range(0x112c, 0x118c)
preset_family.no_of_categories              = 10
preset_family.no_of_puzzles                 = 1090
preset_family.puzzle_addr_range             = range(0x10fee, 0x15af1)
preset_family.puzzle_pointers_start_add     = 0x1076c
preset_family.puzzle_pointers_first_value   = bytes([0x00, 0x00])   # Attention! In the family edition the first puzzle is not referenced from the puzzle area, but is implicitly addressed. The first pointer therefore points to the second puzzle. The start addr of that one depends on the length of the first one
preset_family.puzzle_category_ranges        = [] # Irrelevant as the category is defined after the puzzle itself
preset_family.puzzle_hack_function          = 'family'
preset_family.player_names_addr_range       = range(0x346e, 0x3537)
preset_family.title_text_addr_range         = range(0xc85, 0xdb1)
preset_family.marquee_text_addr_range       = range(0x316, 0x475)
preset_family.timer_addr_choose_action      = 0x18d1
preset_family.timer_addr_select_consonant   = 0x110d
preset_family.timer_addr_bonus_round_select = 0x3563
preset_family.timer_addr_select_vowel       = 0x177a
preset_family.timer_addr_solve              = 0x354d
preset_family.timer_addr_solve_bonus        = 0x39d6
preset_family.wedge_bankrupt_addr           = 0x735
preset_family.wedge_lose_turn_addr          = 0x72c
preset_family.tile_range_letter_wall_deco   = range(0xa471, 0xaac1)
preset_family.pal_addr_letter_wall_deco     = 0x822
preset_family.tile_range_letter_wall_floor  = range(0xaac1, 0xac91)
preset_family.pal_addr_letter_wall_floor    = 0x826
preset_family.bg_addr_letter_wall           = 0x871
preset_family.tile_range_big_logo           = range(0xb2b1, 0xbff1)    # Oktonautenlogo
preset_family.tilemap_range_big_logo        = range(0x101d5, 0x101df)

PRESETS = {
    'classic_prg0':   preset_classic_prg0,
    'classic_prg1':   preset_classic_prg1,
    'family':         preset_family,
}
ROM_PRESETS = {
    '6b395e3b7f273a256bc96c686419045200c73852': preset_classic_prg0,
    '75d98152f4a204b1a4e1087b82bc3d555c580a1f': preset_classic_prg1,
    'cbe5eaaf9a37c7f6e1e7dfcb79c48a50dee815d9': preset_family,
}


cmd_args = argparse.Namespace()
preset = None


def parse_arguments() -> None:
    parser = argparse.ArgumentParser(description = 'Convert videos via ffmpeg')

    parser.add_argument('romfile',                                 type=pathlib.Path,    help='the ROM file to operate on')
    parser.add_argument('outfile',                                 type=pathlib.Path,    help='the ROM file to write to')
    parser.add_argument(      '--preset', choices=PRESETS,         type=str,             help='the preset to use for the ROM addresses (if it could not be autodetected)')
    parser.add_argument('-z', '--puzzles',                         type=pathlib.Path,    help='the file containing the puzzles to use for the hack')
    parser.add_argument('-p', '--players',                         type=pathlib.Path,    help='the file containing the computer player names to use for the hack')
    parser.add_argument(      '--custom-hacks',                    type=pathlib.Path,    help='the (python) file containing the additional custom hacks')

    parser.add_argument('-c', '--select-consonant-timer',          type=IntRange(1,128), help='The number of seconds to allow for selecting a consonant after spinning the wheel')
    parser.add_argument('-a', '--select-action-timer',             type=IntRange(1,128), help='The number of seconds to allow for selecting an action when getting a turn')
    parser.add_argument('-r', '--select-bonus-letter-timer',       type=IntRange(1,128), help='The number of seconds to allow for selecting 5 consonants and a vowel in the bonus round')
    parser.add_argument('-v', '--select-vowel-timer',              type=IntRange(1,128), help='The number of seconds to allow for selecting a vowel')
    parser.add_argument('-s', '--solve-timer',                     type=IntRange(1,128), help='The number of seconds to allow for solving a normal puzzle')
    parser.add_argument('-b', '--bonus-solve-timer',               type=IntRange(1,128), help='The number of seconds to allow for solving a bonus puzzle')
    parser.add_argument(      '--timers',                          type=IntRange(1,128), help='The number of seconds to set for all timers (unless explicitly set)')

    parser.add_argument('-l', '--logo',                            type=pathlib.Path,    help='the file containing the logo to use in the second start screen')
    parser.add_argument(      '--rare-logo',                       type=pathlib.Path,    help='the file containing the RARE logo sprite replacement')
    parser.add_argument('-w', '--wof-logo',                        type=pathlib.Path,    help='the file containing the Wheel of Fortune logo sprite replacement')
    parser.add_argument(      '--title-text',                      type=pathlib.Path,    help='the file containing the text for the title screen')
    parser.add_argument(      '--marquee',                         type=pathlib.Path,    help='the file containing the marquee text')
    parser.add_argument(      '--no-harm',                         action='store_true',  help='Replace harmful wheel slices with money slices')
    parser.add_argument(      '--tiles-wall-deco',                 type=pathlib.Path,    help='Image file with tiles to replace the letter wall decoration')
    parser.add_argument(      '--palette-wall-deco',               type=str,             help='Palette (3 colors) to use for the letter wall deco tiles')
    parser.add_argument(      '--tiles-wall-floor',                type=pathlib.Path,    help='Image file with tiles to replace the letter wall floor')
    parser.add_argument(      '--palette-wall-floor',              type=str,             help='Palette (3 colors) to use for the letter wall floor tiles, e.g: (0x01, 0x2a, 0x3c')
    parser.add_argument(      '--bg-color-wall',                   type=IntRange(0x00,0x3f),  help='Backdrop color of the screen with the letter wall')

    parser.add_argument('-f', '--force',                           action='store_true',  help='force overwriting an existing target file')
    parser.add_argument('-g', '--loglevel', choices=LOG_LEVELS,    type=str,             help='log level to use') # FIXME: Should be choice

    args = parser.parse_args()
    return args


def autodetect_preset(rom: bytes) -> Preset:
    # FIXME: First evaluate cmdline param 'preset'. raise exc if not found

    hash = sha1(rom).hexdigest()
    if hash in ROM_PRESETS:
        return ROM_PRESETS[hash]

    raise LookupError(f'No preset found for ROM with hash {hash}. Please provide explicit preset to use with the “--preset” parameter.')


def log(lvl: str, *args):
    if log_level <= LOG_LEVELS_ORDER.index(lvl):
        col = LOG_LEVELS[lvl]
        print(col, *args, COL_RST)
def log_dbg(*args):
    log('DEBUG', *args)
def log_vbs(*args):
    log('VERBOSE', *args)
def log_nfo(*args):
    log('INFO', *args)
def log_wrn(*args):
    log('WARN', *args)
def log_err(*args):
    log('ERROR', *args)


def read_rom_from_file(romfile: str) -> bytes:
    rom = open(romfile, 'rb').read()
    return rom


def write_rom_to_file(rom: bytes, outfile: pathlib.Path, force: bool = False):
    if outfile.is_file() and not force:
        log_err(f'Target file {outfile} already exists. Cowardly refusing to overwrite unless “--force” is specified')
        sys.exit(1)

    with open(outfile, 'wb') as outfile:
        outfile.write(rom)


def hack_puzzles(old_rom: bytearray, puzzles: list[CategoryWithPuzzles]) -> None:
    if preset.puzzle_hack_function == 'classic':
        _hack_puzzles_classic_edition(old_rom, puzzles)
    elif preset.puzzle_hack_function == 'family':
        _hack_puzzles_family_edition(old_rom, puzzles)
    else:
        raise Exception('Unsupported hack function: ' + str(preset.puzzle_hack_function) + ' This seems to be a bug.')


def _convert_puzzlelist_for_classic(puzzlelist: list[CategoryWithPuzzles]) -> list[(str, list[str])]:
    result = []
    for cwp in puzzlelist:
        category = cwp.category_name
        result.append((category, cwp.puzzles))

    return result


def _hack_puzzles_family_edition(old_rom: bytearray, puzzles: list[CategoryWithPuzzles]) -> None:
    cur_puzzle_addr          = preset.puzzle_addr_range.start
    cur_puzzle_pointer_addr  = preset.puzzle_pointers_start_add
    cur_puzzle_pointer_value = preset.puzzle_pointers_first_value

    # write the category name into the ROM file
    cat_names = [puzzle.category_name for puzzle in puzzles]
    for cat_idx, cat_name in enumerate(cat_names):
        cat_name_rom_addr = preset.category_addr_range.start + cat_idx * 8
        encoded_cat_name = tbl_encode(cat_name, 8, tbl)
        new_rom[cat_name_rom_addr:cat_name_rom_addr+8] = encoded_cat_name

    # we don’t need the categories anymore (they are contained in the puzzle list)
    new_puzzles = []
    for cwp in puzzles:
        new_puzzles.extend(cwp.puzzles)
    puzzles = new_puzzles
    sane_puzzles = sanitize_puzzles(puzzles)
    random.shuffle(sane_puzzles)
    puzzle_count = preset.no_of_puzzles

    while len(sane_puzzles) < puzzle_count:
        sane_puzzles.extend(sane_puzzles)

    log_vbs('Importing', len(sane_puzzles), 'puzzles.')

    # encode all puzzles to get their actual lengths
    encoded_puzzles = [encode_family_puzzle(puzzle) for puzzle in sane_puzzles]
    puzzles_to_use = reduce_to_bounds(encoded_puzzles, puzzle_count, len(preset.puzzle_addr_range))

    # Write the first puzzle without specifying the pointer address which
    # is implicitly set to 0xff 0xff. Then prepare the next pointer address.
    puzzle = puzzles_to_use[0]
    new_rom[cur_puzzle_addr:cur_puzzle_addr+len(puzzle)] = puzzle
    cur_puzzle_addr += len(puzzle)
    cur_puzzle_pointer_value = inc_ptr_by(cur_puzzle_pointer_value, len(puzzle) - 1, False) # -1 because the first puzzle is not on addr 0x00 0x00, but 0xff 0xff

    # write the remaining puzzles and their pointers into the ROM file
    for i in range(1, puzzle_count):
        puzzle = puzzles_to_use[i]
        log_dbg('Importing puzzle:', puzzle)
        new_rom[cur_puzzle_addr:cur_puzzle_addr+len(puzzle)] = puzzle
        new_rom[cur_puzzle_pointer_addr:cur_puzzle_pointer_addr+2] = cur_puzzle_pointer_value
        cur_puzzle_addr += len(puzzle)
        cur_puzzle_pointer_addr += 2
        cur_puzzle_pointer_value = inc_ptr_by(cur_puzzle_pointer_value, len(puzzle), False)

    # Fill the remaining parts of the puzzle area with dummy text.
    # This is only done for fun.
    # FIXME: May be replaced by Lorem Ipsum or some ascii art
    remaining_puzzle_space = preset.puzzle_addr_range.stop - cur_puzzle_addr
    for i in range(remaining_puzzle_space):
        new_rom[cur_puzzle_addr] = 0xfa
        cur_puzzle_addr += 1



def _hack_puzzles_classic_edition(new_rom: bytearray, puzzles: list[CategoryWithPuzzles]) -> None:
    cur_puzzle_addr          = preset.puzzle_addr_range.start
    cur_puzzle_pointer_addr  = preset.puzzle_pointers_start_add
    cur_puzzle_pointer_value = preset.puzzle_pointers_first_value

    #puzzles = _convert_puzzlelist_for_classic(puzzles)
    puzzles = [(cwp.category_name, cwp.puzzles) for cwp in puzzles]

    for cat_idx, bounds in enumerate(preset.puzzle_category_ranges):
        # FIXME: Handle missing categories here!
        cat_name = puzzles[cat_idx][0]
        puzzles_in_cat = puzzles[cat_idx][1]
        sane_puzzles = sanitize_puzzles(puzzles_in_cat)
        random.shuffle(sane_puzzles)
        puzzle_count = bounds.stop - bounds.start
        # We need to assure that each category has at least one
        # puzzle. Therefore, if this is not the case, we add a default
        # “Wheel of Fortune” to each empty category.
        if sane_puzzles == []:
            sane_puzzles.append(Puzzle(cat_name, cat_idx, 'WHEEL\nOF\nFORTUNE'))
        while len(sane_puzzles) < puzzle_count:
            sane_puzzles.extend(sane_puzzles)

        log_vbs('Importing', len(sane_puzzles), 'puzzles into category “' + cat_name + '” with', puzzle_count, 'slots.')

        # encode all puzzles to get their actual lengths
        encoded_puzzles = [encode_classic_puzzle(puzzle) for puzzle in sane_puzzles]
        puzzles_to_use = reduce_to_bounds(encoded_puzzles, puzzle_count, len(preset.puzzle_addr_range))

        # FIXME: The first pointer is always on FF FF and should not explicitly been set
        # write the puzzles and their pointers into the ROM file
        for i in range(puzzle_count):
            puzzle = puzzles_to_use[i]
            log_dbg('Importing puzzle:', puzzle)
            new_rom[cur_puzzle_addr:cur_puzzle_addr+len(puzzle)] = puzzle
            new_rom[cur_puzzle_pointer_addr:cur_puzzle_pointer_addr+2] = cur_puzzle_pointer_value
            cur_puzzle_addr += len(puzzle)
            cur_puzzle_pointer_addr += 2
            cur_puzzle_pointer_value = inc_ptr_by(cur_puzzle_pointer_value, len(puzzle))

        # write the category name into the ROM file
        cat_name_rom_addr = preset.category_addr_range.start + cat_idx * 8
        encoded_cat_name = tbl_encode(cat_name, 8, tbl)
        new_rom[cat_name_rom_addr:cat_name_rom_addr+8] = encoded_cat_name

    # Fill the remaning parts of the puzzle area with dummy text.
    # This is only done for fun.
    # FIXME: May be replaced by Lorem Ipsum or some ascii art
    remaining_puzzle_space = preset.puzzle_addr_range.stop - cur_puzzle_addr
    for i in range(remaining_puzzle_space):
        new_rom[cur_puzzle_addr] = 0xfa
        cur_puzzle_addr += 1


def hack_players(new_rom: bytearray, players: list[str]) -> None:
    cur_player_name_addr = preset.player_names_addr_range.start

    players = [n.ljust(preset.length_of_player_names) for n in
                    players]
    random.shuffle(players)
    players = players[:preset.no_of_player_names]
    log_vbs('Importing', len(players), 'player names.')
    for i, player in enumerate(players):
        log_dbg('Importing player name:', player)
        new_rom[cur_player_name_addr:cur_player_name_addr+preset.length_of_player_names] = encode_str(player)
        cur_player_name_addr += preset.length_of_player_names


def hack_title_screen(new_rom: bytearray, title_text: list[str]) -> None:
    tbl = read_tbl_file('assets/title.tbl')
    encoded_text = encode_title_text(title_text, len(preset.title_text_addr_range), tbl)

    log_vbs('Importing custom text for the title screen.')
    new_rom[preset.title_text_addr_range.start:preset.title_text_addr_range.stop] = encoded_text


def hack_marquee_text(new_rom: bytearray, marquee_text: list[str]) -> None:
    tbl = read_tbl_file('assets/marquee.tbl')
    encoded_text = encode_marquee_text(marquee_text, len(preset.marquee_text_addr_range), tbl)

    log_vbs('Importing custom marquee text.')
    new_rom[preset.marquee_text_addr_range.start:preset.marquee_text_addr_range.stop] = encoded_text


def hack_big_logo(new_rom: bytearray, image_path: pathlib.Path) -> None:
    tiles         = image_to_nes(image_path)
    tiles_and_map = generate_tilemap(tiles)
    tiles         = tiles_and_map[0]

    if len(tiles) * 16 > len(preset.tile_range_big_logo):
        print(f"Error: Too many tiles: {len(tiles)} tiles with {len(tiles) * 16} bytes for a {len(preset.tile_range_big_logo)} byte area.")
        sys.exit(1)

    i= preset.tile_range_big_logo.start
    for x in range(2, len(tiles)):
        tile = tiles[x]
        new_rom[i:i+len(tile)] = tile
        i += len(tile)

    i= preset.tilemap_range_big_logo.start
    for b in tiles_and_map[1]:
        new_rom[i] = b
        i += 1


def sanitize_puzzles(l: list[Puzzle])  -> list[Puzzle]:
    r = []
    for item in l:
        try:
            if '@' in item.puzzle:
                wrapped_puzzle = force_wrap(item.puzzle)
                r.append(Puzzle(item.category, item.category_idx, wrapped_puzzle))
            else:
                wrapped_puzzle = auto_wrap(item.puzzle)
                r.append(Puzzle(item.category, item.category_idx, wrapped_puzzle))
        except ValueError as err:
            log_wrn('Cannot import puzzle:', err)
    return r


def sanitize(l: list[str]) -> list[str]:
    r = []
    for item in l:
        try:
            if '@' in item:
                r.append(force_wrap(item))
            else:
                r.append(auto_wrap(item))
        except ValueError as err:
            log_wrn('Cannot import puzzle:', err)
    return r


# FIXME: This method is still mainly untested
def reduce_to_bounds(encoded_puzzles: list[bytes], puzzle_count: int, addr_range: int) -> list[bytes]:
    """
    Reduces the given list of puzzles to 'puzzle_count', ensuring that they don’t exceed 'addr_range'.

    In the most simple case 'encoded_puzzles[:puzzle_count] is returned.
    This is the case if the length of all these items does not exceed 'addr_range'.

    If these items do exceed the given range, the longest item if them is
    replaced by the shortest one in 'encoded_puzzles[puzzle_count:]. This
    is repeated until the resulting list is <= 'addr_range'.

    The method does _not_ fill the new list with additional entries in case
    'len(encoded_puzzles) < puzzle_count'.

    This method does not alter the given list of puzzles, but instead
    returns a new list.

    Args:
      encoded_puzzles (list[bytes]): the list to reduce
      puzzle_count    (int):         the number of items to reduce the given list to
      addr_range      (int):         the number of bytes that may not be exceeded
    Returns:
      A new list[bytes] of 'puzzle_count' puzzles with a length of <= 'addr_range'.
    Raises:
      OverflowError: If the list cannot be reduced to 'puzzle_count' items
                     while not exceeding 'addr_range'.
    """
    reduced_puzzles   = encoded_puzzles[:puzzle_count]
    remaining_puzzles = encoded_puzzles[puzzle_count:]

    while sum_bytes(reduced_puzzles) > addr_range:
        if len(remaining_puzzles) == 0:
            raise OverflowError(f"Cannot reduce the size of the given list below {addr_range}. Min size is {sum_bytes(reduced_puzzles)}.")

        longest_puzzle  = max(reduced_puzzles,   key = len)
        reduced_puzzles.remove(longest_puzzle)
        shortest_puzzle = min(remaining_puzzles, key = len)
        reduced_puzzles.append(shortest_puzzle)

    return reduced_puzzles


def sum_bytes(lst: list[bytes]) -> int:
    return sum(len(item) for item in lst)


def inc_ptr_by(ptr_value: bytes, amount: int, reverse: bool = True) -> bytes:
    val = ptr_value
    for i in range(amount):
        if reverse:
            val = inc_ptr_reverse(val)
        else:
            val = inc_ptr(val)
    return val


def inc_ptr(ptr_value: bytes) -> bytes:
    lo = ptr_value[1]
    hi = ptr_value[0]
    if lo == 0xFF:
        return bytes([hi+1, 0x00])
    else:
        return bytes([hi, lo+1])


def inc_ptr_reverse(ptr_value: bytes) -> bytes:
    lo = ptr_value[0]
    hi = ptr_value[1]
    if lo == 0xFF:
        return bytes([0x00, hi+1])
    else:
        return bytes([lo+1, hi])


def read_player_names_file(players_file: str) -> list[str]:
    player_names = []

    with open(players_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue

            player_name = line
            if len(player_name) > preset.length_of_player_names:
                log_wrn('Player name “' + player_name + '” is too long. Only ' + preset.length_of_player_names + ' characters are allowed.')
                continue

            player_names.append(player_name.upper())

    return player_names


def read_puzzle_file(puzzlefile: str) -> list[CategoryWithPuzzles]:
    categories = []  # a list of tuples: (category, [puzzles])

    with open(puzzlefile, 'r') as f:
        cur_category = None
        category_idx = -1
        for line in f:
            line = line.strip().upper()
            if line == '' or line.startswith('#'):
                continue

            category_match = re.search(PATTERN_CATEGORY_LINE, line)
            if category_match is not None:
                category_name = category_match.group(1)
                cur_category = CategoryWithPuzzles(category_name, [])
                category_idx += 1
                categories.append(cur_category)
                continue

            cur_category.puzzles.append(Puzzle(category_name, category_idx, line))

    return categories


def read_title_text_file(file: str) -> list[str]:
    with open(file, 'r') as f:
        content = f.read()
        lines = content.splitlines()

        # Filter out all lines that are not part of the actual text.
        lines = filter_title_text_lines(lines)

        # Cut off trailing comments
        lines = [line.split('#')[0] for line in lines]

        # Cut off trailing whitespace
        lines = [line.rstrip() for line in lines]

        return lines


def read_marquee_text_file(file: str) -> list[str]:
    with open(file, 'r') as f:
        content = f.read()
        lines = content.splitlines()

        # Filter out all comment lines
        lines = [line for line in lines if not line.startswith('#')]

        # Filter out all empty lines
        lines = [line for line in lines if line != '']

        return lines


def force_wrap(line: str) -> str:
    """
    Wrap a string at predefined positions.
    The character indicating the wrap position is the '@'.

    Raises:
        ValueError: If the line is incorrecly split.
    """
    words = line.split('@')
    if puzzle_fits(words):
        return '\n'.join(words)
    else:
        raise ValueError('Line is incorrectly split: ' + line)


def auto_wrap(line: str) -> str:
    """
    Automatically wraps the given string into up to 4 lines of length 11,13,13,11.

    Returns (list[str]):
      A list of strings with 1 to 4 lines into which the string was split.

    Raises:
      ValueError: If the string could not be split to fit into the defined lengths.
    """

    LINE_LENGTHS = [11, 13, 13, 11]

    # Up to 13 characters fit into 1 line (line 2)
    words = line.split()
    if chars(words) <= 13:
        return ' '.join(words)

    # Try to split into 2 lines
    words = line.split()
    line2 = ''
    line1 = ''
    for word in reversed(words):
        new_line = (word + ' ' + line2).strip()
        if len(new_line) <= 13:
            line2 = new_line
            del words[-1]
            continue
        line1 = ' '.join(words)
        break

    if len(line1) <= 13:
        return line1 + '\n' + line2


    # Try to split line1 even further (into 3 lines)
    words = line1.split()
    line3 = line2
    line2 = ''
    line1 = ''
    for word in reversed(words):
        new_line = (word + ' ' + line2).strip()
        if len(new_line) <= 13:
            line2 = new_line
            del words[-1]
            continue
        line1 = ' '.join(words)

    if len(line1) <= 11:
        return line1 + '\n' + line2 + '\n' + line3

    # Try to split into 4 lines (need to start again since the 4th line may
    # only accomodate 11 chars)
    words = line.split()
    lines = ['           ',
             '             ',
             '             ',
             '           ']
    for i in reversed(range(4)):
        for word in reversed(words):
            new_line = (word + ' ' + lines[i]).strip()
            if len(new_line) <= LINE_LENGTHS[i]:
                lines[i] = new_line
                del words[-1]
                continue
            break

    if words == []:
        return '\n'.join(lines)

    # If even that didn’t work, we are not able to split the line correctly
    raise ValueError('Line cannot be split automatically: ' + line)


def chars(words: list[str]) -> int:
    """
    Get the number of characters of a string of the given words separated by spaces.
    """
    return len(' '.join(words))


def puzzle_fits(puzzle: list[str]) -> bool:
    """
    Check whether the given lines would fit as a puzzle.
    """

    if len(puzzle) == 1:
        return len(puzzle[0]) <= 13
    elif len(puzzle) == 2:
        return len(puzzle[0]) <= 13 and \
               len(puzzle[1]) <= 13
    elif len(puzzle) == 3:
        return len(puzzle[0]) <= 11 and \
               len(puzzle[1]) <= 13 and \
               len(puzzle[2]) <= 13
    elif len(puzzle) == 4:
        return len(puzzle[0]) <= 11 and \
               len(puzzle[1]) <= 13 and \
               len(puzzle[2]) <= 13 and \
               len(puzzle[3]) <= 11
    else:
        return False


def middle(line: str) -> int:
    """
    Get the number of the middle index of the given string.

    For strings with an uneven number of characters this will be actually
    the middle position. For strings with an even number of characters this
    will be the index of the character /after/ the middle.
    """
    return round(len(line) / 2)


def encode(clue):
    result = []
    for c in clue:
        if c == '\n':
            result[-1] |= 0x80
        else:
            result.append(ord(c))
    result[-1] |= 0x80
    result[-2] |= 0x80
    return bytes(result)


def encode_classic_puzzle(puzzle):
    result = []
    for c in puzzle.puzzle:
        if c == '\n':
            result[-1] |= 0x80
        else:
            result.append(ord(c))
    result[-1] |= 0x80
    result[-2] |= 0x80
    return bytes(result)


def encode_family_puzzle(puzzle: Puzzle):
    result = []
    for c in puzzle.puzzle:
        if c == '\n':
            result[-1] |= 0x80
        else:
            result.append(ord(c))
    result[-1] |= 0x80
    result.append(puzzle.category_idx)
    return bytes(result)


def encode_str(s: str) -> bytes:
    result = []
    for c in s:
        result.append(ord(c))
    return bytes(result)


def tbl_encode(s: str, n: int, tbl: dict[str, int]) -> bytes:
    result = [0x00] * n
    for i, c in enumerate(s):
        hex_value = tbl[c]
        result[i] = hex_value
    return bytes(result)


def encode_title_text(lines: list[str], n: int, tbl: dict[str, int]) -> bytes:
    result = []

    for i, line in enumerate(lines):
        if line.strip() == '':
            # Empty lines can be skipped
            continue

        text_in_line = line.lstrip()           # Get the text without leading whitespace
        h_idx = len(line) - len(text_in_line)  # calculate the horizontal offset
        line_offset = calc_title_row_offset(i, h_idx)
        result.append(line_offset[0])
        result.append(line_offset[1])
        for c in text_in_line:
            if c == '\n':
                result[-1] |= 0x80  # Mark the end of a line on the last character
            else:
                result.append(tbl[c.upper()])
        result[-1] |= 0x80  # Mark the end of a line on the last character

    result[-1] |= 0x80  # The last character must be indicated as the end of the line

    if len(result) > n:
        raise IndexError(f"Error: Title screen text is too big: {len(result)} bytes for a {n} byte area.")

    # Extend the result to the required number of bytes
    diff = n - len(result)
    # Appending the zerofill leads to strange glitches. Putting them at the
    # beginning works (most of the time…)
    #result.extend([tbl[' ']] * diff)
    zerofill= [tbl[' ']] * diff
    zerofill[0:2] = [0x23, 0x00]
    zerofill[-1] |= 0x80
    result = zerofill + result

    return bytes(result)


def encode_marquee_text(lines: list[str], n: int, tbl: dict[str, int]) -> bytes:
    result = []

    for line in lines:
        if line[0] == '$':
            bytevalues = line[1:].split()
            hex_values = [int(b, 16) for b in bytevalues]
            result.extend(hex_values)
        else:
            for c in line:
                result.append(tbl[c.upper()])

    result.append(0x00)   # Text end marker

    if len(result) > n:
        raise IndexError(f"Error: Marquee text is too big: {len(result)} bytes for a {n} byte area.")

    # Extend the result to the required number of bytes
    diff = n - len(result)
    result.extend([0x05] * diff)

    result[-1] = 0x00     # Text end marker

    return bytes(result)


def calc_title_row_offset(lineidx: int, h_offset: int) -> tuple[int, int]:
    hi= 0x20
    lo= lineidx * 32
    while lo > 0xf0:
      hi = hi + 0x01
      lo = lo - 0xff - 1
    return (hi, lo + h_offset)


def filter_title_text_lines(lines: list[str]) -> list[str]:
    result= []
    text_start= False
    empty_line_buffer= []
    for line in lines:
        if re.match('^#START#+', line):
            text_start= True
            continue

        if re.match('^#END#+', line):
            text_start= False
            break

        if text_start:
            result.append(line)

    return result


def read_tbl_file(f: str) -> dict[str, int]:
    result = {}
    with open(f) as tbl:
        for line in tbl:
            mapping = line.rstrip('\n\r').split('=', 1)
            if len(mapping) == 2:
                hex_value = int(mapping[0], 16)
                printable = mapping[1]
                result[printable] = hex_value
    return result


def image_to_nes(image_path: pathlib.Path) -> list[bytes]:
    """
    Convert an image (usually an indexed .png with at max 4 colors) to the
    NES internal representation if tiles.

    Parameters:
      - image_path:
          the path to the image file containing the tiles

    Returns:
      A list of byte sequences. Each tile is represented by two byte
      sequences of length 16. The bytes in that list can directly be
      written to rom sequentially.
    """
    with Image.open(image_path) as im:
        im = im.convert('P')
    pix_data = tuple(im.getdata())
    tile_count = len(pix_data) // 64
    twidth = im.width // 8

    tiles = []

    for i in range(tile_count):
        t = bytearray(16)
        x = i % twidth * 8
        y = i // twidth * 8
        for iy in range(8):
            for ix in range(8):
                c = pix_data[(y + iy) * twidth * 8 + x + ix]
                t[iy    ] |=  (c & 1)       << (7 - ix)
                t[iy + 8] |= ((c & 2) >> 1) << (7 - ix)
        t = bytes(t)
        tiles.append(t)

    return tiles


def generate_tilemap(tiles: list[bytes]):
    no_dup_tiles = {
      bytes.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"): 0
    , bytes.fromhex("00 00 00 00 00 00 00 00 FF FF FF FF FF FF FF FF"): 1
    }
    tilemap      = []

    next_tindex = 2
    for i in range(len(tiles)):
        tile = tiles[i]
        if tile in no_dup_tiles:
            tindex = no_dup_tiles[tile]
        else:
            tindex = next_tindex
            no_dup_tiles[tile] = tindex
            next_tindex += 1
        tilemap.append(tindex)

    no_dup_tiles = {v: k for k, v in no_dup_tiles.items()}
    return (no_dup_tiles, tilemap)


def generate_tilemap2(tiles: list[bytes], no_dup_tiles: dict[bytes, int] = {}):
    tilemap      = []

    next_tindex = 0
    for i in range(len(tiles)):
        tile = tiles[i]
        if tile in no_dup_tiles:
            tindex = no_dup_tiles[tile]
        else:
            tindex = next_tindex
            no_dup_tiles[tile] = tindex
            next_tindex += 1
        tilemap.append(tindex)

    no_dup_tiles = {v: k for k, v in no_dup_tiles.items()}
    return (no_dup_tiles, tilemap)


def replace_tiles(rom: bytearray, image_path: pathlib.Path, addr_range: range):
    tiles = image_to_nes(image_path)

    # Check that the tiles from the image don’t exceed the given range
    if len(tiles) * 16 > len(addr_range):
        # FIXME: Generate an error message instead and go on with the execution?
        raise IndexError(f"Error: Too many tiles: {len(tiles)} tiles with {len(tiles) * 16} bytes for a {len(addr_range)} byte area.")

    log_vbs('Writing tiles with ', len(tiles) * 16, 'bytes into addr range of ', len(addr_range), 'bytes.')

    i= addr_range.start
    for t in tiles:
        rom[i:i+len(t)] = t
        i += len(t)


def replace_tiles_and_map(rom: bytearray, image_path: pathlib.Path, tiles_addr_range: range, tilemap_addr_range: range) -> None:
    tiles         = image_to_nes(image_path)
    tiles_and_map = generate_tilemap2(tiles)
    tiles         = tiles_and_map[0]
    tilemap       = tiles_and_map[1]

    if len(tiles) * 16 > len(tiles_addr_range):
        print(f"Error: Too many tiles: {len(tiles)} tiles with {len(tiles) * 16} bytes for a {len(tiles_addr_range)} byte area.")
        sys.exit(1)

    i= tiles_addr_range.start
    for x in range(0, len(tiles)):
        tile = tiles[x]
        rom[i:i+len(tile)] = tile
        i += len(tile)

    i= tilemap_addr_range.start
    for b in tilemap:
        rom[i] = b+1
        i += 1


def replace_palette(rom: bytearray, palette: tuple[int, int, int], addr: int):
    palette = ast.literal_eval(palette)

    if len(palette) != 3:
        raise ValueError('Given palette must be a tuple of exactly 3 values. ', len(palette), 'were given.')

    rom[addr:addr+3] = palette


if __name__ == "__main__":
    cmd_args = parse_arguments()
    if cmd_args.loglevel:
        log_level = LOG_LEVELS_ORDER.index(cmd_args.loglevel)

    tbl = read_tbl_file(TBL_FILE)
    rom = read_rom_from_file(cmd_args.romfile)
    new_rom = bytearray(rom)
    if cmd_args.preset:
        preset = PRESETS[cmd_args.preset]
    else:
        preset = autodetect_preset(rom)

    if cmd_args.puzzles:
        log_nfo('Importing custom puzzles')
        puzzles = read_puzzle_file(cmd_args.puzzles)
        hack_puzzles(new_rom, puzzles)

    if cmd_args.players:
        log_nfo('Importing custom computer player names')
        players = read_player_names_file(cmd_args.players)
        hack_players(new_rom, players)

    if cmd_args.title_text:
        log_nfo('Importing custom title text')
        title_text= read_title_text_file(cmd_args.title_text)
        hack_title_screen(new_rom, title_text)

    if cmd_args.marquee:
        log_nfo('Importing custom marquee text')
        marquee_text= read_marquee_text_file(cmd_args.marquee)
        hack_marquee_text(new_rom, marquee_text)

    if cmd_args.select_consonant_timer:
        log_nfo('Setting timer for selecting consonants')
        new_rom[preset.timer_addr_select_consonant] = cmd_args.select_consonant_timer
    elif cmd_args.timers:
        log_nfo('Setting timer for selecting consonants')
        new_rom[preset.timer_addr_select_consonant] = cmd_args.timers

    if cmd_args.select_action_timer:
        log_nfo('Setting timer for selecting next action')
        new_rom[preset.timer_addr_choose_action] = cmd_args.select_action_timer
    elif cmd_args.timers:
        log_nfo('Setting timer for selecting next action')
        new_rom[preset.timer_addr_choose_action] = cmd_args.timers

    if cmd_args.select_bonus_letter_timer:
        log_nfo('Setting timer for selecting letters in bonus round')
        new_rom[preset.timer_addr_bonus_round_select] = cmd_args.select_bonus_letter_timer
    elif cmd_args.timers:
        log_nfo('Setting timer for selecting letters in bonus round')
        new_rom[preset.timer_addr_bonus_round_select] = cmd_args.timers

    if cmd_args.select_vowel_timer:
        log_nfo('Setting timer for selecting vowels')
        new_rom[preset.timer_addr_select_vowel] = cmd_args.select_vowel_timer
    elif cmd_args.timers:
        log_nfo('Setting timer for selecting vowels')
        new_rom[preset.timer_addr_select_vowel] = cmd_args.timers

    if cmd_args.solve_timer:
        log_nfo('Setting timer for solving a normal puzzle')
        new_rom[preset.timer_addr_solve] = cmd_args.solve_timer
    elif cmd_args.timers:
        log_nfo('Setting timer for solving a normal puzzle')
        new_rom[preset.timer_addr_solve] = cmd_args.timers

    if cmd_args.bonus_solve_timer:
        log_nfo('Setting timer for solving the bonus puzzle')
        new_rom[preset.timer_addr_solve_bonus] = cmd_args.bonus_solve_timer
    elif cmd_args.timers:
        log_nfo('Setting timer for solving the bonus puzzle')
        new_rom[preset.timer_addr_solve_bonus] = cmd_args.timers

    if cmd_args.no_harm:
        log_nfo('Replacing harmful wheel wedges with money wedges')
        new_rom[preset.wedge_lose_turn_addr] = WEDGE_VALUES[2000]
        new_rom[preset.wedge_bankrupt_addr] = WEDGE_VALUES[3000]

    if cmd_args.tiles_wall_deco:
        log_nfo('Replacing tiles for the letter wall decoration')
        replace_tiles(new_rom, cmd_args.tiles_wall_deco, preset.tile_range_letter_wall_deco)

    if cmd_args.tiles_wall_floor:
        log_nfo('Replacing tiles for the letter wall floor')
        replace_tiles(new_rom, cmd_args.tiles_wall_floor, preset.tile_range_letter_wall_floor)

    if cmd_args.palette_wall_floor:
        log_nfo('Replacing palette for the letter wall floor')
        replace_palette(new_rom, cmd_args.palette_wall_floor, preset.pal_addr_letter_wall_floor)

    if cmd_args.palette_wall_deco:
        log_nfo('Replacing palette for the letter wall deco')
        replace_palette(new_rom, cmd_args.palette_wall_deco, preset.pal_addr_letter_wall_deco)

    if cmd_args.bg_color_wall:
        log_nfo('Replacing backdrop color for the letter wall screen')
        new_rom[preset.bg_addr_letter_wall] = cmd_args.bg_color_wall

    if cmd_args.logo:
        log_nfo('Replacing big logo in the second title screen')
        hack_big_logo(new_rom, cmd_args.logo)

    if cmd_args.custom_hacks:
        with open(cmd_args.custom_hacks, 'r') as custom_hacks_file:
            hack_src = custom_hacks_file.read()
        # Attention! We execute arbitrary code here! Do not execute
        # untrusted code!
        exec(hack_src)
        for hack in custom_hacks:
            if isinstance(hack, ReplaceBytesHack):
                if len(hack.addr_range) != len(hack.new_bytes):
                    raise ValueError(f'Number of bytes to write must be equal to the addr range. {len(hack.new_bytes)} bytes, {len(hack.addr_range)} addr range')
                new_rom[hack.addr_range.start:hack.addr_range.stop] = hack.new_bytes
            elif isinstance(hack, ReplaceSingleBytesHack):
                for addr, value in hack.new_bytes.items():
                    new_rom[addr] = value
            elif isinstance(hack, ReplaceTilesHack):
                replace_tiles(new_rom, hack.image_path, hack.addr_range)
            elif isinstance(hack, ReplaceTilesAndMapHack):
                replace_tiles_and_map(new_rom, hack.image_path, hack.tiles_addr_range, hack.tilemap_addr_range)
            elif isinstance(hack, ReplaceTblTextHack):
                encoded_text = tbl_encode(hack.text.upper(), len(hack.text), tbl)
                if len(encoded_text) != len(hack.addr_range):
                    raise ValueError(f'Number of characters to write must be equal to the length of the addr range. text length={len(encoded_text)} ({hack.text}), byte range={len(hack.addr_range)}')
                new_rom[hack.addr_range.start:hack.addr_range.stop] = encoded_text
            else:
                raise ValueError('Unsupported hack type: '+str(type(hack)))

    if rom == new_rom:
        log_wrn('No changes detected. New ROM will be exactly the same as the original one.')

    write_rom_to_file(bytes(new_rom), cmd_args.outfile, cmd_args.force)
    log_nfo('New ROM written to:', cmd_args.outfile)

