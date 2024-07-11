# Function to clean the output directory
clean_output_directory() {
  local output_dir=$1
  rm -rf "$output_dir"/*
  mkdir -p "$output_dir"
}
