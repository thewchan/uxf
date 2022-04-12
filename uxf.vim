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
syn keyword uxfConst yes true no false null
syn region uxfComment start="#<" end=">" contains=uxfTodo
syn region uxfStr start="<" end=">"
syn region uxfBytes start="(" end=")"
syn match uxfNumber /[-+]\=\d\+\(\.\d\+\([Ee][-+]\=\d\+\)\=\)\=/
syn region uxfNTuple start="(:" end=":)"
syn match uxfDateTime /\d\d\d\d-\d\d-\d\d\(T\d\d\(:\d\d\(:\d\d\)\=\)\=\)\=/
syn match uxfPunctuation /\[=|=\]|[[]{}()<>=]/

hi uxfTodo guibg=yellow term=italic cterm=italic gui=italic
hi uxfConst guifg=navy
hi uxfPunctuation guifg=darkyellow term=bold   cterm=bold   gui=bold
hi uxfComment	guifg=darkgreen term=italic cterm=italic gui=italic
hi uxfStr  guifg=teal
hi uxfBytes  guifg=darkyellow
hi uxfNTuple  guifg=purple
hi uxfNumber  guifg=blue
hi uxfDateTime  guifg=darkmagenta
