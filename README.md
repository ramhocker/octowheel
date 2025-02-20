The Octonauts Wheel (Hack of the NES Game “Wheel of Fortune”)
=============================================================

This is a script (or rather a collection of scripts and assets) to create a
hack of the NES Game
[“Wheel of Fortune”](https://www.mobygames.com/game/16631/wheel-of-fortune/)
and its descendants
[“Wheel of Fortune – Family Edition”](https://www.mobygames.com/game/31769/wheel-of-fortune-family-edition/)
and
[“Weel of Fortune – Junior Edition”](https://www.mobygames.com/game/31770/wheel-of-fortune-junior-edition/).[^1]

[^1]: While this script basically supports all three variants of the game,
I ended up concentrating on “Wheel of Fortune – Family Edition”. The script
will partly work for all three variants, but there will be some modifications
that don’t work for the other two. It is not hard to implement support for
these as well, but I didn’t invest the time and effort into it. I am happy to
integrate PRs providing the missing pieces though.

This repository provides the corresponding assets for creating an [Octonauts](https://en.wikipedia.org/wiki/Octonauts)
themed variant. But the script itself is agnostic to the content.
By providing different assets it can be used to build a hack with a different
theme. See [below](#customization) on how to do that.

I created this script to build a hack of this game for my daughter who loves
the Octonauts (almost as much as I do) and knows a lot about the animals that are
covered by the show and who just started her 1st grade in school and therefore
is starting to learn to read and write. I hope that is a fun way to support her
in that respect.

Be aware that the puzzles are rather short and mostly consist of a single word
(to not make them too complicated for a grade 1 student).

While the script was written from scratch it is based on and has been
influenced by lots of other resources. See [the corresponding section
below](#resources) for a list of those.


Screenshots
-----------

See [this page](screenshots.md).


Usage
-----

For convenience IPS patches for a German and an English version can be found on
the [release page](https://github.com/ramhocker/octowheel/releases/tag/v1.0.0).
To build your own hacked version, read on about using the script.

To use this script for generating your own hack you will need the original ROM
of the game. You also need an NES emulator for actually playing the game (like
[FCEUX](https://fceux.com/) or [Mesen](https://mesen.ca) or an installation of
one of the Retro Game distributions like [RetroPie](https://retropie.org.uk),
[Recalbox](https://recalbox.com), [Batocera](https://batocera.org) or
[Lakka](https://lakka.tv). As this script is a python script you will also need
to have python 3 installed to run it.

The script needs to be applied to the original ROM and it will create a patched
ROM containing the hacked version. What hacks are actually applied is defined
by a lot of options given to the script. If no options are given no patches
will be applied and the resulting ROM will be the same as the original one.

The syntax is: `python3 ./src/hack-game.py <original ROM> <patched ROM>`.

A Linux Shell script
[`patch_game.sh`](https://github.com/ramhocker/octowheel/blob/master/patch_game.sh)
is provided with some default settings to generate an Octonauts themed game
with some Quality-of-Life hacks (like more time for choosing an action and
removal of harmful wedges from the Wheel). It can be used as a template for
your own variant.

A list of all possible options can be seen by calling the script with the option `--help`.

<!--
TODO: Need original ROM
TODO: Need NES emulator for playing (e.g. FCEUX / Mesen)
TODO: Call hack script. See patch_game.sh for an example. May be used as template for custom shell script.
      Call 'python3 src/hack-game.py -h' for a short help.

TODO: Script can be used to make a totally different themed game, but that
      requires changing the images, puzzles, etc.
-->


Short description of changes to the original game
-------------------------------------------------

This script allows for changing the following features:

- Several timers (for selecting an action, selecting a consonant or vowel, selecting 5 consonants and a vowel in the bonus round, solving a puzzle)
- Removing harmful wedges from the wheel (bankrupt, miss a turn)
- Replacing the puzzles (and the corresponding categories)
- Changing a lot of the texts, e.g:
  * The names of computer players
  * The text on the first title screen
  * The marquee text on the second title screen
- Changing of lot of the images, e.g:
  * The logo on the second title screen
  * The wall image of the actual game screen
  * The floor image of the actual game screen
  * The background color of the actual game screen

Additionally custom hacks can be applied by changing specific byte sequences in
a declarative manner via the `--custom-hacks` option. See [the corresponding
section below](#custom-hacks) for a usage description.

Due to the evolution of this script there are some inconsistencies. For
example, while the wheel background and floor can be defined via specific
script options, the provided patches actually use the `--custom-hacks` script.

The script tries to differentiate between the 3 variants of the game (e.g. the
puzzles have a bit of a different format in the original game than in the other
two and the byte locations for all the hacks are different). But this hasn’t
been done thoroughly. Therefore testing all the hacks with the other 2 variants
are necessary (and of course fixing the parts that don’t work correctly).

The game supports around 1000 puzzles. This script will fill these with the
ones given in the puzzlelist. If there are more puzzles than available puzzle
slots, they will be randomly chosen from the puzzlelist. If there are less
puzzles than available puzzle slots, some of them will be duplicated until all
puzzle slots are filled.


### Custom Hacks

The script that can be provided via `--custom-hacks` is a python script that
needs to obey to a specific structure.

At the top some dataclasses are defined that are used to declaratively define
specific hacks that are defined later in this script. These dataclasses cannot
be defined freely as the main hack script references these.

Afterwards a list with the name `custom_hacks` is defined that lists instances
of the aforementioned dataclasses.

This script is a flexible way to hack more aspects of the game that have no explicit support in the main script. The following dataclasses are provided:

*`ReplaceTilesHack`*
: Replace a byte sequence with the content of a .png image. The image must
  exactly match the tiles in the original ROM file.

*`ReplaceTilesAndMapHack`*
: Replace a byte sequence with the content of a .png image and replace the
  tiles map referencing these tiles. A more flexible way to define images as it
  allows reordering of the tiles.

*`ReplaceBytesHack`*
: Replace a byte sequence with the given bytes. The most flexible hack as it
  allows freely exchanging specific bytes.

*`ReplaceSingleBytesHack`*
: Replace single bytes with a specific value. The bytes do not need to be in
  sequence in the ROM file.

*`ReplaceTblTextHack`*
: Replace a byte sequence with a specific text. The text will be encoded
  according to the TBL file
  [assets/wheel.tbl](https://github.com/ramhocker/octowheel/blob/master/assets/wheel.tbl).

Such a custom_hacks script gives a lot of freedom for patching the ROM, but
also requires some knowledge of ROM hacking.


Customization
-------------

If you want to customize the patches in this script, fork it and apply the
necessary changes to your fork.

Please think about whether your changes can be beneficial for other users of
this repo (e.g. if you are replacing an image with an octonauty one). In that
case please consider creating a pull request for integrating your changes into
this repo.


Architecture
------------

This repo has the following structure:

`patch_game.sh`
: A Linux Shell script containing the options for creating an english Octonauts Wheel hack.

`src/hack-game.py`
: The actual hack script containing the main logic and the differentiation between the 3 variants of the game.

`src/scrape.py`
: A script for scraping the [Wheel of Fortune Puzzle
  Compendium](https://buyavowel.boards.net/page/compendium) puzzles into
  a puzzlelist suitable to be used in this hack script. This one is actually not
  used in this repository, but may be of interest to others who want to play with
  the original puzzles from the game show. It is an updated variant of the script
  from [Chris Beaumont](https://chrisbeaumont.org/infinite_wheel/).

`assets/`
: Assets that are necessary for the hack script. At the moment it only contains different TBL mapping files.

`images/patches/`
: Images used by the hack script(s) that replace original images with octonauty ones.

`images/sources/`
: The original assets the files in `images/patches/` were created from.
  These have been created with [Aseprite](https://aseprite.org) and need to be edited with that (excellent) tool.

`okto_patches-{de,en}/`
: Assets for patching the game to an “Octonauts Wheel” in German and English. Contains a `custom_hacks.py` script, a list of the puzzles and files containing some replacement texts. The assets are heavily commented to describe their format.

`vim/syntax/`
: [Vim](https://en.wikipedia.org/wiki/Vim_(text_editor)) syntax files for syntax highlighting the assets for puzzles, title text and marquee texts. They are a lot of help when editing these assets.


Bugs / Flaws
------------

- The script is a bit brittle. While I tried my best to prohibit changes that
  would clearly break the ROM, there are certainly also lots of locations
  without proper validity checks.

  Be careful when using it for your own hacks and apply changes one by one.
  Otherwise you may end with a broken ROM and have to rollback all changes
  to find the culprit.

  Especially text replacements in the title screen and the marquee text are
  subject to subtle problems. The script already checks the max length of
  these texts, but it may still happen occasionally that specific lines
  or characters lead to graphical glitches somewhere. It may be worthwhile
  to play around with different line breaks and positioning of the lines
  to fix these glitches.

- The script was intended to be usable with all variants of the game, but due
  to the amount of work required I got exhausted and concentrated on the
  “Family Edition”. So it may still be possible that some hacks work with the
  other variants, but there are certainly some that don’t.

  If you have an interest to make the script fully compatible with all
  variants, please invest the time to fix the remaining parts. Most of
  the time this means only correcting the byte areas on which to apply
  the hacks (but that will likely require some hacking skills to find
  the correct byte addresses).

- The code grew organically over time and is now rather unclean with many
  redundancies and way too few comments.

- The puzzle list for the Octonauts patches is still too small. At the moment
  it provides around 500 puzzles while the game supports around 1000 puzzles.
  The included puzzles provide puzzles from season 1 – 4 of the original show
  and the 3 movies.

  Not included are Season 5 (which is not available in German and only 5
  episodes are available in English) and the Above and Beyond seasons.
  Including puzzles from Above and Beyond may be enough to stretch the
  puzzle list to 1000 puzzles, but I didn’t find the time yet.

- The puzzlelist allows for changing the name of the categories. While the ROM
  reserves space for 8 characters for each category they are not correctly
  rendered if the category names are longer than the original ones. There seems
  to be some hardcoded length in the code for each category that would need to
  be updated as well.

Contributing
------------

Any help for improving this script is welcome. Here are some examples of
possible contributions:


### Fixing bugs / Adding functionality

This hacking script is rather unclean and probably buggy. If you can make it more robust, please do so.
It is also somehow unclean as it grew rather unexpectedly and probably contains a good amount of redundancy.

When changing anything in the code, bear in mind that readability is always more valuable than efficiency.

Also don’t fix anything for one specific version of the game if that breaks it
for another (e.g. fixing a bug in the Classic Edition would break the Family Edition).


### Make it usable for all versions of the game

While this script was initially written to support different versions of the
game (and many parts indeed do apply to multiple versions) it was too much work
for me to apply this to all the functionality. Therefore it does work for the
Family Edition, but some parts (and especially custom-hacks.py script) will not
work for other editions.

Somewhere at the beginning of the hack script is a list of presets that define
different byte ranges for different versions of the game. There are even some
functions that differentiate between different versions (e.g. the puzzlelist
has a different format in the Classic Edition and the Family Edition).

It would be great if the script could be cleaned up to support all versions of the game.

The following versions are known to me:

- Classic Edition Rev 0
- Classic Edition Rev 1 (only change to Rev 0 is one different puzzle, leading to a different end byte of the puzzle area)
- Family Edition
- Junior Edition


### Adding puzzles

The puzzlelist currently contains around 500 puzzles in English and German. It
covers the first 4 seasons of the original series as well as the 3 movies. What
is currently missing is the 5th season (which is not available in German at all
and only 5 episodes are available in English) and Above and Beyond (from which
only the first 2 seasons are available in German at the moment).

I am actually planning on integrating more puzzles, especially from Above and
Beyond, but am not sure when I will find the time to do so.

If you want to add puzzles, please add them to all languages. If you don’t know
the correct term in on language, enter an empty line in that corresponding
file. This is necessary to always keep the puzzlelists in different languages
in sync. That means a specific line in one puzzlelist needs to contain the same
term in the puzzlelist of all other languages.

Of course if you find errors in the puzzlelists (e.g. typos), feel free to
provide a PR for correcting these.


### Translations

The provided patches currently provide texts and especially the puzzlelist in
English and German. If you want support for other languages, feel free to
provide the corresponding assets in a PR. As mentioned above, please adhere to
the structure of the existing puzzlelists so that each line in each of the
puzzlelists refers to the same term.

This is probably a lot of work, especially since the existing puzzlelists have
no way to indicate from which episode the terms have been taken from.


References
----------

I got a lot of information from preexisting resources. The following is a
non-comprehensive list of resources and tools I used for creating this
hack script.


### Resources

[Wheel of Infinite Fortune (by Chris Beaumont)](https://chrisbeaumont.org/infinite_wheel/)
: My main source of inspiration for this hack. Chris already did the hard work
  of identifying the format of the puzzles in the Classic game and wrote a python
  script for hacking the game. While he had some small misconceptions of the
  format and I massively extended (or rather rewrote) his script, I would
  probably never have attempted to hack this game without his prior work.

[TASVideos](https://tasvideos.org/GameResources/NES/WheelOfFortune)
: A list of the byte areas for the actual puzzles in the ROM and the pointers
  to them. This information helped in defining puzzles of differing lengths than
  the original ones.

[Dr. Floppy’s Guide to Attribute Hacking](https://www.baddesthacks.net/?p=2308)
: The most thorough description of palette attribute modification
  (changing color information in specific areas) I have found.

[An overview of NES rendering (by Austin Morlan)](https://austinmorlan.com/posts/nes_rendering_overview/)
: A good overview over the NES internal graphics format.

[GameHacking.org](https://gamehacking.org/game/31328)
: Game Genie Codes for Wheel of Fortune (multiple editions) for changing
  certain variables of the game (mostly timers). In combination with FCEUX it can
  be used to find and hack the bytes defining those variables.

[The Cutting Room Floor](https://tcrf.net/Wheel_of_Fortune_(NES))
: List of the values that can be used to alter the Wheel wedges.

[NesDev](https://nesdev.org)
: Wiki containing in-depth information of all NES internals as very helpful
  descriptions of graphics format, palettes, etc.

[r/romhacking](https://reddit.com/r/romhacking)
: A reddit sub dedicated to ROM hacking. There are many people giving help
  and advice even on very specific questions.


### Tools

[Tile Molester](https://github.com/toruzz/TileMolester)
: Graphics editor for game consoles. Can be used to locate graphics in the ROM
  and to export (“Copy to…”) tilesets to .png for editing in a graphics program
  (like Aseprite).

[Aseprite](https://aseprite.org)
: Pixel art editor. Can be used to import tilesets in .png format and edit them
  for exchanging graphics.

[FCEUX](https://fceux.com/)
: NES emulator. Used for testing and playing the hack, but also provides
  debugging tools to view and alter ROM and RAM values, change graphics and
  palettes, etc.

[Mesen](https://mesen.ca)
: Another NES emulator. More accurate than FCEUX (but also more demanding).
  Has partly better debugging tools than FCEUX.

[OpenSearch](https://github.com/ramhocker/OpenSearch)
: Tool to find non-ASCII encoded texts in ROM files via relative search.
  Also allows automatically generating a corresponding .tbl file.
