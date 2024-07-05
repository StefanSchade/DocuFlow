# Function to wait for a Docker container to be up and running
wait_for_container() {
  local container_name="$1"
  local retries=10
  local count=0

  while [ $count -lt $retries ]; do
    if docker ps | grep -q "$container_name"; then
      echo "Container $container_name is running."
      return 0
    fi
    count=$((count + 1))
    echo "Waiting for container $container_name to start... ($count/$retries)"
    sleep 1
  done

  echo "Error: Container $container_name did not start within expected time."
  return 1
}