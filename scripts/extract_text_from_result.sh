jq -r '
  .[] as $page |
  $page.text_lines[] |
  if . == ($page.text_lines | last) then
    . + "\n\n\n" + $page.source_file + "\n\n\n"
  else
    .
  end
' /workspace/data/ocr_result/ocr_result.json 
