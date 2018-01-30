"=============================================================================
" FILE: util.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! defx#util#print_error(string) abort
  echohl Error | echomsg '[defx] '
        \ . defx#util#string(a:string) | echohl None
endfunction
function! defx#util#print_warning(string) abort
  echohl WarningMsg | echomsg '[defx] '
        \ . defx#util#string(a:string) | echohl None
endfunction
function! defx#util#print_debug(string) abort
  echomsg '[defx] ' . defx#util#string(a:string)
endfunction

function! defx#util#convert2list(expr) abort
  return type(a:expr) ==# type([]) ? a:expr : [a:expr]
endfunction
function! defx#util#string(expr) abort
  return type(a:expr) ==# type('') ? a:expr : string(a:expr)
endfunction

function! defx#util#has_yarp() abort
  return !has('nvim') || get(g:, 'defx#enable_yarp', 0)
endfunction
