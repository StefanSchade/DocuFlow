#!/bin/bash

log_script_name() {
    local script_name=$(basename "$0")
    local star_line=$(printf '%*s' "${#script_name}" | tr ' ' '*')

    echo "**""${star_line}""**"
    echo "* ""${script_name}"" *"
    echo "**""${star_line}""**"
}
