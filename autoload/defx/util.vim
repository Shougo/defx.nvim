"=============================================================================
" FILE: util.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

let s:is_windows = has('win32') || has('win64')

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

function! defx#util#execute_path(command, path) abort
  let save_wildignore = &wildignore
  try
    execute a:command '`=s:expand(a:path)`'
    if &l:filetype ==# ''
      filetype detect
    endif
  catch /^Vim\%((\a\+)\)\=:E325/
    " Ignore swap file error
  catch
    call defx#util#print_error(v:throwpoint)
    call defx#util#print_error(v:exception)
  finally
    let &wildignore = save_wildignore
  endtry
endfunction
function! s:expand(path) abort
  return s:substitute_path_separator(
        \ (a:path =~# '^\~') ? fnamemodify(a:path, ':p') :
        \ (a:path =~# '^\$\h\w*') ? substitute(a:path,
        \             '^\$\h\w*', '\=eval(submatch(0))', '') :
        \ a:path)
endfunction
function! s:substitute_path_separator(path) abort
  return s:is_windows ? substitute(a:path, '\\', '/', 'g') : a:path
endfunction
