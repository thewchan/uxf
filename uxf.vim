" Vim syntax file
" Language:	        UXF
" Author:	          Mark Summerfield <mark@qtrac.eu>
" URL:		          https://github.com/mark-summerfield/uxf
" Licence:	        Public Domain
" Latest Revision:  2022-04-12

if exists("b:current_syntax")
  finish
endif

syn clear
syn sync fromstart linebreaks=3 minlines=50

" Order matters!

syn keyword uxfTodo TODO FIXME DELETE CHECK TEST XXX
syn keyword uxfConst yes true no false
syn keyword uxfNull null
syn keyword uxfType bool int real date datetime str bytes list map table
syn match uxfPunctuation /[][{}()=]/
syn region uxfComment start="#<" end=">" contains=uxfTodo,uxfIdentifier
syn region uxfStr start="<" end=">" contains=uxfIdentifier keepend
syn match uxfIdentifier /\u\w*/ transparent contained contains=NONE
syn match uxfBytes /(:[A-Fa-f0-9\s]\+:)/ contains=uxfIdentifier keepend
syn match uxfNumber /\<[-+]\=\d\+\(\.\d\+\([Ee][-+]\=\d\+\)\=\)\=\>/
syn match uxfDateTime /\<\d\d\d\d-\d\d-\d\d\(T\d\d\(:\d\d\(:\d\d\)\=\)\=\)\=\>/
syn match uxfHeader /^uxf\s*\d\+.\d\+/

hi uxfTodo guibg=yellow term=italic cterm=italic gui=italic
hi uxfConst guifg=navy
hi uxfNull guifg=red
hi uxfType  guifg=purple
hi uxfPunctuation guifg=darkyellow term=bold   cterm=bold   gui=bold
hi uxfComment	guifg=darkgreen term=italic cterm=italic gui=italic
hi uxfStr  guifg=teal
hi uxfBytes  guifg=darkyellow
hi uxfNumber  guifg=blue
hi uxfDateTime  guifg=darkmagenta
hi uxfIdentifier  guifg=red
hi uxfHeader  guifg=navy guibg=#FFDAE0
hi uxfMagic  guifg=brown
