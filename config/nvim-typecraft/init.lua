vim.g.clipboard = {
  name = 'tmux',
  copy = {
    ['+'] = 'tmux load-buffer -w -',
    ['*'] = 'tmux load-buffer -w -',
  },
  paste = {
    ['+'] = 'tmux save-buffer -',
    ['*'] = 'tmux save-buffer -',
  },
  cache_enabled = 1,
}


if vim.fn.has("termguicolors") == 1 then
  vim.opt.termguicolors = true
end


-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = "https://github.com/folke/lazy.nvim.git"
  vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
end
vim.opt.rtp:prepend(lazypath)

local opts = {}

require("vim-options")
require("lazy").setup("plugins", opts)

-- swap splits
vim.api.nvim_exec([[
function! SwapSplits()
    wincmd L
    wincmd K
    wincmd J
    wincmd H
endfunction

command! SwapSplits call SwapSplits()
]], false)



