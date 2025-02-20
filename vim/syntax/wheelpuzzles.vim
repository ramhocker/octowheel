" Vim syntax file
" Language:	        Syntax highlighting for puzzlelist for NES Wheel of Fortune
" Maintainer:	      Marco Herrn <marco@mherrn.de>
"/Original Creator: Drew Neil <andrew.jr.neil@gmail.com>

" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if !exists("main_syntax")
  if version < 600
     syntax clear
  elseif exists("b:current_syntax")
     finish
  endif
  let main_syntax = 'wheelpuzzles'
endif

syntax match  WheelComment          /\v^\s*#.*/
syntax match  WheelLineBreak        /\v\@/
syntax match  WheelCategory         /\v^\s*\[[a-zA-Z0-9 '$?-]+\]\s*$/ contains=WheelCategoryBrackets
syntax match  WheelCategoryBrackets /\v[\\[\]]/ contained
syntax match  WheelPuzzleLine       /\v^\s*[^#\[]+/ contains=WheelInvalidChar,WheelLineBreak
syntax match  WheelWordTooLong      /\v[a-zA-Z]{14,}/
syntax match  WheelWordTooLong      /\v^[- a-zA-Z]{14,}\@/
syntax match  WheelWordTooLong      /\v\@[- a-zA-Z]{14,}$/
syntax match  WheelWordTooLong      /\v\@[- a-zA-Z]{14,}\@/
syntax match  WheelLineTooLong      /\v[- a-zA-Z]{48,}/
syntax match  WheelInvalidChar      /\v[^-' a-zA-Z@]/ contained

highlight default link WheelPuzzleLine       Normal
highlight default link WheelComment          Comment
highlight default link WheelLineBreak        Delimiter
highlight default link WheelCategory         String
highlight default link WheelCategoryBrackets SpecialKey
highlight default link WheelWordTooLong      Error
highlight default link WheelLineTooLong      Error
highlight default link WheelInvalidChar      Error

let b:current_syntax = "wheelpuzzles"

if main_syntax == 'wheelpuzzles'
   unlet main_syntax
endif

" vim: ts=8
