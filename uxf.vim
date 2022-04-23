" Vim syntax file
" Language:        UXF
" Author:          Mark Summerfield <mark@qtrac.eu>
" URL:             https://github.com/mark-summerfield/uxf
" Licence:         Public Domain
" Latest Revision: 2022-04-21

if exists("b:current_syntax")
  finish
endif

syn clear
syn sync fromstart linebreaks=3 minlines=50

" Order matters!

syn keyword uxfTodo TODO FIXME DELETE CHECK TEST XXX
syn keyword uxfConst yes true no false
syn match uxfNull /[?]/
syn keyword uxfType bool int real date datetime str bytes list map table
syn match uxfPunctuation /[][{}()=:]/
syn match uxfIdentifier /\<\u\w*\>/ 
syn region uxfStr start="<" end=">"
syn region uxfComment start="#<" end=">"
syn match uxfBytes /(:[A-Fa-f0-9\s]\+:)/ contains=uxfIdentifier keepend
syn match uxfNumber /\<[-+]\=\d\+\(\.\d\+\([Ee][-+]\=\d\+\)\=\)\=\>/
syn match uxfDateTime /\<\d\d\d\d-\d\d-\d\d\(T\d\d\(:\d\d\(:\d\d\)\=\)\=\)\=\>/
syn match uxfHeader /^uxf\s*\d\+.\d\+.*$/

" See https://sashamaps.net/docs/resources/20-colors/
" yellow
hi uxfTodo guibg=#FFE119 term=italic cterm=italic gui=italic
" navy
hi uxfConst guifg=#000075
" red
hi uxfNull guifg=#E6194B
" purple
hi uxfType guifg=#911EB4
" magenta
hi uxfPunctuation guifg=#F032E6 term=bold   cterm=bold   gui=bold
" olive
hi uxfComment	guifg=#808000 term=italic cterm=italic gui=italic
" teal
hi uxfStr  guifg=#469990
" orange
hi uxfBytes  guifg=#F58231
" blue
hi uxfNumber  guifg=#4363D8
" cyan
hi uxfDateTime guifg=#42D4F4
" brown
hi uxfIdentifier guifg=#9A6324
" beige
hi uxfHeader  guifg=navy guibg=#FFFAC8
