"=============================================================================
" FILE: init.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! defx#init#_initialize() abort
  if exists('g:defx#_channel_id')
    return
  endif

  call defx#init#_channel()

  augroup defx
    autocmd!
  augroup END

  let g:defx#_histories = []
endfunction
function! defx#init#_channel() abort
  if !has('python3')
    call defx#util#print_error(
          \ 'defx requires Python3 support("+python3").')
    return v:true
  endif
  if has('nvim') && !has('nvim-0.3.0')
    call defx#util#print_error('defx requires nvim 0.3.0+.')
    return v:true
  endif
  if !has('nvim') && v:version < 801
    call defx#util#print_error('defx requires Vim 8.1+.')
    return v:true
  endif

  try
    if defx#util#has_yarp()
      let g:defx#_yarp = yarp#py3('defx')
      call g:defx#_yarp.request('_defx_init')
      let g:defx#_channel_id = 1
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

    return v:true
  endtry
endfunction
function! defx#init#_check_channel() abort
  return exists('g:defx#_channel_id')
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
  return {
        \ 'auto_cd': v:false,
        \ 'buffer_name': 'default',
        \ 'columns': 'mark:filename:type',
        \ 'direction': '',
        \ 'fnamewidth': 100,
        \ 'listed': v:false,
        \ 'new': v:false,
        \ 'profile': v:false,
        \ 'resume': v:false,
        \ 'search': '',
        \ 'split': 'no',
        \ 'toggle': v:false,
        \ 'winheight': 0,
        \ 'winwidth': 0,
        \ }
endfunction
function! s:internal_options() abort
  return {
        \ 'cursor': line('.'),
        \ 'prev_bufnr': bufnr('%'),
        \ }
endfunction
function! defx#init#_context(user_context) abort
  let context = s:internal_options()
  call extend(context, defx#init#_user_options())
  call extend(context, a:user_context)
  return context
endfunction
