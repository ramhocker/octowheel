" Vim syntax file
" Language:	    Syntax highlighting for the title text definition for NES Wheel of Fortune
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
  let main_syntax = 'wheeltitle'
endif

syntax match   WheelComment          /\v^\s*#.*/                        containedin=ALLBUT,WheelTextArea
syntax region  WheelTextArea         start=/\v^#START#/ end=/\v^#END#/  contains=WheelInvalidChar,WheelLineTooLong,WheelInTextComment
syntax match   WheelLineTooLong      /\%>32v.*/                         contained
syntax match   WheelInvalidChar      /\v[^- a-zA-Z0-9,\.\/&©℗?!"=’←\*]/ contained
syntax match   WheelInTextComment    /\v#.*/                            contained

highlight default link WheelTextArea         Normal
highlight default link WheelComment          Comment
highlight default link WheelLineTooLong      Error
highlight default link WheelInvalidChar      WarningMsg
highlight default link WheelInTextComment    Conceal

let b:current_syntax = "wheeltitle"

if main_syntax == 'wheeltitle'
   unlet main_syntax
endif

" vim: ts=8
