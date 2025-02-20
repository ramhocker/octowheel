" Vim syntax file
" Language:	    Syntax highlighting for the marquee text definition for NES Wheel of Fortune
" Maintainer:	    Marco Herrn <marco@mherrn.de>
"/Original Creator: Drew Neil <andrew.jr.neil@gmail.com>

" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if !exists("main_syntax")
  if version < 600
     syntax clear
  elseif exists("b:current_syntax")
     finish
  endif
  let main_syntax = 'wheelmarquee'
endif

syntax match   WheelComment          /\v^#.*/
syntax match   WheelByteLine         /\v^\$.*/                      contains=WheelByteIndicator
syntax match   WheelByteIndicator    /\v\$/                         contained
syntax match   WheelInvalidChar      /\v[^- a-zA-Z0-9,\.\/©℗?=←\*]/ contained containedin=ALLBUT,WheelComment,WheelByteLine
syntax match   WheelTrailingSpaces   /\v\s+$/                       contained containedin=ALLBUT,WheelComment,WheelByteLine

highlight default link WheelComment          Comment
highlight default link WheelInvalidChar      WarningMsg
highlight default link WheelByteIndicator    Operator
highlight default link WheelByteLine         Number
highlight              WheelTrailingSpaces   ctermbg=lightblue

let b:current_syntax = "wheelmarquee"

if main_syntax == 'wheelmarquee'
   unlet main_syntax
endif

" vim: ts=8
