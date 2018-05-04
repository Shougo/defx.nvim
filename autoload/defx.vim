"=============================================================================
" FILE: defx.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! defx#initialize() abort
  return defx#init#_initialize()
endfunction

function! defx#do_action(action) abort
  call _defx_do_action(a:action)
  return ":\<C-u>redraw\<CR>"
endfunction
