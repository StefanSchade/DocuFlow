#!/bin/bash

jq -r '.text | join(" ")' /workspace/data/ocr_debug/ocr_debug_data.json 

jq -r '[.conf[] | tostring] | join("  ")' /workspace/data/ocr_debug/ocr_debug_data.json 

jq -r '[
    .text as $texts | 
    .conf as $confs | 
    range(0; ($texts | length)) | 
    "(" + $texts[.] + " | " + ($confs[.] | tostring) + ")" 
] | join(" ")' /workspace/data/ocr_debug/ocr_debug_data.json
