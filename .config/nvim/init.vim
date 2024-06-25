" Set up basic options
set number
set relativenumber
set tabstop=4
set shiftwidth=4
set expandtab
set autoindent

" Install vim-plug plugin manager
call plug#begin('~/.vim/plugged')

" Install Python-specific plugins
Plug 'davidhalter/jedi-vim'

call plug#end()

" Enable Jedi-vim for Python autocompletion
let g:jedi#completions_enabled = 1
