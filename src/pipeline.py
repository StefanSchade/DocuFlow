import subprocess
import os

def run_script(script_path, args):
    command = ['python', script_path] + args
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"Error running {script_path}: {result.stderr.decode()}")
    print(result.stdout.decode())

def main():
    directory = "/app/data"
    language = "deu"
    threshold = 0
    save_preprocessed = False
    check_orientation = 1

    ocr_args = [directory, '--language', language, '--threshold', str(threshold), '--check-orientation', str(check_orientation)]
    if save_preprocessed:
        ocr_args.append('--save-preprocessed')

    if not os.path.exists(os.path.join(directory, 'ocr_result.txt')):
        run_script('/app/src/ocr_batch.py', ocr_args)

    # Add more steps as needed
    # if not os.path.exists(os.path.join(directory, 'sanitized_result.txt')):
    #     run_script('/app/src/sanitize_ocr.py', [directory, '--language', language])

if __name__ == "__main__":
    main()
