import os
import enchant
import logging
import json
import re
from pipeline_step import PipelineStep

class HyphenationStep(PipelineStep):
    CONTEXT_WORD_COUNT = 10  # Number of words before and after the word in question for context

    def __init__(self, args):
        self.args = args
        self.dictionary = self.load_dictionary(args.language_enchanted)

    def load_dictionary(self, language):
        try:
            dictionary = enchant.Dict(language)
            logging.info(f"Preparing Enchant dictionary {language}")
        except enchant.DictNotFoundError:
            raise ValueError(f"No dictionary found for language: {language}")
        return dictionary

    def run(self, input_data):
        input_file = f"{input_data}/ocr_result/ocr_result.json"
        output_dir = f"{input_data}/hyphenation"
        suggestions_file = f"{output_dir}/hyphenation_suggestions.txt"
        output_file = f"{output_dir}/hyphenation_output.json"

        logging.info(f"Input file: {input_file} suggestion file: {suggestions_file}, output file: {output_file}")

        os.makedirs(output_dir, exist_ok=True)

        with open(input_file, "r") as f:
            ocr_output = json.load(f)

        suggestions = []
        for page_index, page in enumerate(ocr_output):
            text_lines = page.get("text_lines", [])
            for line_index, line in enumerate(text_lines):
                logging.debug(f"Preparing suggestions for page {page_index} line {line_index}")
                line_suggestions = self.generate_suggestions(page_index, line_index, text_lines)
                suggestions.extend(line_suggestions)

        with open(suggestions_file, "w") as f:
            for idx, (page_index, line_index, original, proposed) in enumerate(suggestions):
                if not proposed:
                    continue  # Skip if there are no suggestions
                context = self.get_context(ocr_output[page_index]["text_lines"], line_index, original)
                f.write(f"Proposed Change {idx+1}:\n\n")
                f.write(f"Source File: {ocr_output[page_index]['source_file']}\n")
                f.write(f"Page Number: {page_index + 1}\n")
                f.write(f"Line Number: {line_index}\n")
                f.write(f"Context: {context}\n\n")
                f.write(f"now:      {original}\n")
                f.write(f"then:      {proposed}\n\n")
                f.write(f"{original}  --->   {proposed}\n")
                f.write(f"--------------------------------------------\n\n")

        if self.args.interactive_mode:
            input("Review the suggestions and press Enter to apply changes...")

        # Apply suggestions to the output JSON structure
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

    def generate_suggestions(self, page_index, line_index, text_lines):
        suggestions = []
        current_line = text_lines[line_index].split()
        if current_line and current_line[-1].endswith('-'):
            next_line = self.get_next_line(text_lines, line_index)
            if next_line:
                next_word = next_line.split()[0]
                if self.is_word_valid(next_word):
                    combined_word_with_hyphen = current_line[-1][:-1] + '-' + next_word
                    combined_word_no_hyphen = current_line[-1][:-1] + next_word
                    if self.dictionary.check(current_line[-1][:-1]) and self.dictionary.check(next_word):
                        suggestions.append((page_index, line_index, current_line[-1], combined_word_with_hyphen))
                    elif self.dictionary.check(combined_word_no_hyphen):
                        suggestions.append((page_index, line_index, current_line[-1], combined_word_no_hyphen))
                    else:
                        sanitized_combined_word = current_line[-1][:-1] + next_word
                        suggestions.append((page_index, line_index, current_line[-1], sanitized_combined_word))
        return suggestions

    def get_next_line(self, text_lines, line_index):
        if line_index + 1 < len(text_lines):
            return text_lines[line_index + 1]
        return None

    def get_context(self, text_lines, line_index, word):
        words = text_lines[line_index].split()
        try:
            index = words.index(word)
        except ValueError:
            logging.warning(f"Word '{word}' not found in line: {text_lines[line_index]}")
            return text_lines[line_index]  # Return the whole line as context if the word is not found
        start = max(0, index - self.CONTEXT_WORD_COUNT)
        end = min(len(words), index + self.CONTEXT_WORD_COUNT + 1)
        return " ".join(words[start:end])

    def apply_suggestion(self, word, suggestions):
        for page_index, line_index, original, proposed in suggestions:
            if word == original:
                return proposed if proposed else word
        return word

    def is_word_valid(self, word):
        if not word.isalpha():
            return False
        if re.match(r'^[IVXLCDM]+$', word):  # Check for Roman numerals
            return False
        if word.isupper() or word.islower():  # Check if the word is all uppercase or all lowercase
            return True
        return False
