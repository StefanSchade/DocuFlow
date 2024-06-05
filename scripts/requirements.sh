# Update requirements.txt
echo -e "pyenchant\ntqdm\nfuzzywuzzy\npillow\npytesseract\nprompt_toolkit" > requirements.txt

# Rebuild Docker image
#docker build -f docker/Dockerfile.dev -t dev-environment .

# Start Docker container
#docker run -it --rm -v $(pwd):/workspace -w /workspace dev-environment

# Inside Docker container, check installed packages
python -m pip list | grep -E 'pyenchant|tqdm|fuzzywuzzy|pillow|pytesseract|prompt_toolkit'

# Start Python interactive session to check imports
python -c "import PIL; import pytesseract; import enchant; import tqdm; import fuzzywuzzy; import prompt_toolkit; print('All imports are successful')"
