return {
    "3rd/image.nvim",
    priority = 1000, -- Very high priority is required, luarocks.nvim should run as the first plugin in your config.
    rocks = {'image'},
    config = function()
        backend = 'ueberzug'
    end,
}