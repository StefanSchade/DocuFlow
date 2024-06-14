import os
import enchant
import logging
import json
import re
from pipeline_step import PipelineStep

class SanitizationStep(PipelineStep):
    CONTEXT_WORD_COUNT = 10  # Number of words before and after the word in question for context

    def __init__(self, args):
        self.args = args
        self.dictionary = self.load_dictionary(args.language_enchanted)
        self.whitelist = self.load_whitelist(args.language)

    def load_dictionary(self, language):
        try:
            dictionary = enchant.Dict(language)
            logging.info(f"Preparing Enchant dictionary {language}")
        except enchant.DictNotFoundError:
            raise ValueError(f"No dictionary found for language: {language}")
        return dictionary

    def load_whitelist(self, language):
        whitelist = set()
        project_whitelist_path = f"/resources/spelling-whitelist-{language}.txt"
        input_whitelist_path = f"{self.args.input_dir}/spelling-whitelist-{language}.txt"

        if os.path.exists(project_whitelist_path):
            with open(project_whitelist_path, "r") as f:
                project_whitelist = f.read().splitlines()
                whitelist.update(project_whitelist)
                logging.info(f"Loaded project-specific whitelist from {project_whitelist_path}")

        if os.path.exists(input_whitelist_path):
            with open(input_whitelist_path, "r") as f:
                input_whitelist = f.read().splitlines()
                whitelist.update(input_whitelist)
                logging.info(f"Loaded input directory whitelist from {input_whitelist_path}")

        if not whitelist:
            logging.warning(f"No whitelists found for language: {language}")

        return whitelist

    def run(self, input_data):
        input_file = f"{input_data}/ocr_result/ocr_result.json"
        output_dir = f"{input_data}/sanitized"
        suggestions_file = f"{output_dir}/suggestions.txt"
        output_file = f"{output_dir}/sanitized_output.json"

        logging.info(f"input file: {input_file} suggestion file: {suggestions_file}, output file: {output_file}")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Read the OCR output
        with open(input_file, "r") as f:
            ocr_output = json.load(f)

        # Generate suggestions only for text within `text_lines`
        suggestions = []
        for page_index, page in enumerate(ocr_output):
            text_lines = page.get("text_lines", [])
            for line_index, line in enumerate(text_lines):
                logging.debug(f"Preparing suggestions for page {page_index} line {line_index}")            
                line_suggestions = self.generate_suggestions(line)
                suggestions.extend([(page_index, line_index, word, sugg) for word, sugg in line_suggestions])

        if self.args.log_level == 'DEBUG':
            debug_file = f"{output_dir}/sanitized_debug.txt"
            with open(debug_file,"w") as dbgf:
                dbgf.write(f"suggestions: {suggestions}")
                               
        with open(suggestions_file, "w") as f:
            for idx, (page_index, line_index, original, proposed) in enumerate(suggestions):
                if not proposed:
                    continue  # Skip if there are no suggestions
                try:
                    context = self.get_context(text_lines[line_index], original)
                except IndexError as e:
                    logging.error(f"IndexError: {e} for page_index: {page_index}, line_index: {line_index}, original: {original}")
                    continue
                f.write(f"Proposed Change {idx+1}:\n\n")
                f.write(f"Source File: {ocr_output[page_index]['source_file']}\n")
                f.write(f"Page Number: {page_index + 1}\n")
                f.write(f"Line Number: {line_index}\n")
                f.write(f"Context: {context}\n\n")
                f.write(f"now:      {original}\n")
                f.write(f"then:      {proposed[0] if proposed else original}\n\n")
                f.write(f"{original}  --->   {proposed[0] if proposed else original}\n")
                f.write(f"--------------------------------------------\n\n")

        if self.args.interactive_mode:
            input("Review the suggestions and press Enter to apply changes...")

        # Apply changes
        for page in ocr_output:
            text_lines = page.get("text_lines", [])
            for i, line in enumerate(text_lines):
                words = line.split()
                corrected_line = " ".join([self.apply_suggestion(word, suggestions) for word in words])
                text_lines[i] = corrected_line
            page["text_lines"] = text_lines

        with open(output_file, "w") as f:
            json.dump(ocr_output, f, indent=4)
        return output_dir



    def generate_suggestions(self, text):
        suggestions = []
        words = text.split()
        for word in words:
            if not re.match(r'^[a-zA-ZäöüÄÖÜß]+$', word):  # Filter out non-letter symbols
                continue
            if len(word) == 1:  # Filter out single-character words
                continue
            if word in self.whitelist:  # Skip whitelisted words
                continue
            if not self.dictionary.check(word):
                suggestions.append((word, self.dictionary.suggest(word)))
        return suggestions


    def get_context(self, line, word):
        words = line.split()
        try:
            index = words.index(word)
        except ValueError:
            logging.warning(f"Word '{word}' not found in line: {line}")
            return line  # Return the whole line as context if the word is not found
        start = max(0, index - self.CONTEXT_WORD_COUNT)
        end = min(len(words), index + self.CONTEXT_WORD_COUNT + 1)
        return " ".join(words[start:end])

    def apply_suggestion(self, word, suggestions):
        for _, _, original, proposed in suggestions:
            if word == original:
                return proposed[0] if proposed else word
        return word

    def parse_suggestions(self, suggestions_text):
        suggestions = []
        lines = suggestions_text.split("\n")
        for line in lines:
            if " ---> " in line:
                original, corrected = line.split(" ---> ")
                suggestions.append((original.strip(), corrected.strip()))
        return suggestions
