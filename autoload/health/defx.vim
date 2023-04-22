"=============================================================================
" FILE: defx.vim
" AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
" License: MIT license
"=============================================================================

function! s:check_required_python_for_defx() abort
  if has('python3')
    call s:report_ok('has("python3") was successful')
  else
    call s:report_error('has("python3") was not successful')
  endif

  if defx#init#_python_version_check()
    call s:report_error('Python 3.6.1+ was successful')
  else
    call s:report_ok('Python 3.6.1+ was successful')
  endif
endfunction

function! health#defx#check() abort
  call health#report_start('defx.nvim')

  call s:check_required_python_for_defx()
endfunction

function! s:report_ok(report) abort
  if has('nvim-0.10')
    call v:lua.vim.health.ok(a:report)
  else
    call health#report_ok(a:report)
  endif
endfunction

function! s:report_error(report) abort
  if has('nvim-0.10')
    call v:lua.vim.health.error(a:report)
  else
    call health#report_error(a:report)
  endif
endfunction
