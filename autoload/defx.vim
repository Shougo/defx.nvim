"=============================================================================
" FILE: defx.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! defx#initialize() abort
  return defx#init#_initialize()
endfunction

function! defx#start(paths, user_context) abort
  call defx#initialize()
  let context = defx#init#_context(a:user_context)
  let paths = a:paths
  if empty(paths)
    let paths = [getcwd()]
  endif
  let paths = map(paths, "fnamemodify(v:val, ':p')")
  return _defx_start(paths, context)
endfunction

function! defx#do_action(action, ...) abort
  let args = get(a:000, 0, [])
  let context = defx#init#_context({})
  call _defx_do_action(a:action, args, context)
  return ":\<C-u>redraw\<CR>"
endfunction
