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
  call defx#util#rpcrequest('_defx_start', [paths, context], v:false)
  call defx#_async_action('redraw', [context['search']])
endfunction

function! defx#do_action(action, ...) abort
  if &l:filetype !=# 'defx'
    return ''
  endif

  let args = defx#util#convert2list(get(a:000, 0, []))
  return printf(":\<C-u>call defx#_do_action(%s, %s)\<CR>",
        \ string(a:action), string(args))
endfunction
function! defx#async_action(action, ...) abort
  if &l:filetype !=# 'defx'
    return ''
  endif

  let args = defx#util#convert2list(get(a:000, 0, []))
  return printf(":\<C-u>call defx#_async_action(%s, %s)\<CR>",
        \ string(a:action), string(args))
endfunction
function! defx#_do_action(action, args) abort
  if &l:filetype !=# 'defx'
    return
  endif

  let context = defx#init#_context({})
  call defx#util#rpcrequest(
        \ '_defx_do_action', [a:action, a:args, context], v:false)
endfunction
function! defx#_async_action(action, args) abort
  if &l:filetype !=# 'defx'
    return
  endif

  let context = defx#init#_context({})
  call defx#util#rpcrequest(
        \ '_defx_do_action', [a:action, a:args, context], v:true)
endfunction
