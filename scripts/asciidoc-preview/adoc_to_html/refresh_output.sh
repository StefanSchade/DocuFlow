
# Function to clean all output and generate everything again
full_refresh_output() {

  source "$SCRIPT_DIR/adoc_to_html/_check_input_directory.sh"
  
  
  check_input_directory "${INPUT_DIR}"
  full_refresh_output
  partial_refresh_output "."
}
