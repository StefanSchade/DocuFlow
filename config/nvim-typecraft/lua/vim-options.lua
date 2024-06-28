vim.g.mapleader = " "
vim.cmd("set expandtab")
vim.cmd("set tabstop=2")
vim.cmd("set softtabstop=2")
vim.cmd("set shiftwidth=3")
-- Disable Ctrl-Z in normal and insert mode
vim.api.nvim_set_keymap('n', '<C-z>', '<Nop>', { noremap = true, silent = true })
vim.api.nvim_set_keymap('i', '<C-z>', '<Nop>', { noremap = true, silent = true })
