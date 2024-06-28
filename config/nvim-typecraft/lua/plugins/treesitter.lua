return {
    "nvim-treesitter/nvim-treesitter", 
    build = ":TSUpdate",
    config = function()
        local config = require("nvim-treesitter.configs")
        config.setup({
            ensure_installed = { "c", "lua", "vim", "vimdoc", "query", "elixir", "heex", "javascript", "html", "rust", "python","java"},
            sync_install = false,
            highlight = { enable = true },
            indent = { enable = true }    
        })
        -- This binds the leader key followed by i in visual mode to automatically indent the selected code.
        vim.api.nvim_set_keymap('v', '<leader>i', ':normal! =<CR>', { noremap = true, silent = true })
    end
}