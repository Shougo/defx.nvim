"=============================================================================
" FILE: init.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

if !exists('s:is_enabled')
  let s:is_enabled = 0
endif

function! defx#init#_is_enabled() abort
  return s:is_enabled
endfunction

function! defx#init#_initialize() abort
  call defx#init#_channel()

  augroup defx
    autocmd!
  augroup END
endfunction
function! defx#init#_channel() abort
  if !has('python3')
    call defx#util#print_error(
          \ 'defx requires Python3 support("+python3").')
    return
  endif

  try
    if defx#util#has_yarp()
      let g:defx#_yarp = yarp#py3('defx')
      call g:defx#_yarp.notify('defx_init')
    else
      " rplugin.vim may not be loaded on VimEnter
      if !exists('g:loaded_remote_plugins')
        runtime! plugin/rplugin.vim
      endif

      call _defx_init()
    endif
  catch
    call defx#util#print_error(v:exception)
    call defx#util#print_error(v:throwpoint)

    let python_version_check = defx#init#_python_version_check()
    if python_version_check
      call defx#util#print_error(
            \ 'defx requires Python 3.6.1+.')
    endif

    if defx#util#has_yarp()
      if !has('nvim') && !exists('*neovim_rpc#serveraddr')
        call defx#util#print_error(
              \ 'defx requires vim-hug-neovim-rpc plugin in Vim.')
      endif

      if !exists('*yarp#py3')
        call defx#util#print_error(
              \ 'defx requires nvim-yarp plugin.')
      endif
    else
      call defx#util#print_error(
          \ 'defx failed to load. '
          \ .'Try the :UpdateRemotePlugins command and restart Neovim. '
          \ .'See also :CheckHealth.')
    endif

    return 1
  endtry
endfunction
function! defx#init#_check_channel() abort
  return !exists('g:defx#_initialized')
endfunction

function! defx#init#_python_version_check() abort
  python3 << EOF
import vim
import sys
vim.vars['defx#_python_version_check'] = (
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro) < (3, 6, 1)
EOF
  return g:defx#_python_version_check
endfunction
function! defx#init#_user_options() abort
  return {}
endfunction
function! defx#init#_context(user_context) abort
  return {
        \ 'cursor': line('.'),
        \ }
endfunction
