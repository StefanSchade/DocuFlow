# src/steps/sanitization_step.py
import os
import enchant
import logging
import json
from pipeline_step import PipelineStep

class SanitizationStep(PipelineStep):
    def __init__(self, args):
        self.args = args
        self.dictionary = self.load_dictionary(args.language_enchanted)

    def load_dictionary(self, language):
        try:
            dictionary = enchant.Dict(language)
            logging.info(f"Preparing Enchanted dictionary {language}")
        except enchant.DictNotFoundError:
            raise ValueError(f"No dictionary found for language: {language}")
        return dictionary

    def generate_suggestions(self, text):
        suggestions = []
        words = text.split()
        for word in words:
            if not self.dictionary.check(word):
                suggestions.append((word, self.dictionary.suggest(word)))
        return suggestions

    def run(self, input_data):
        input_file = f"{input_data}/ocr_result/ocr_result.json"
        output_dir = f"{input_data}/sanitized"
        suggestions_file = f"{output_dir}/suggestions.txt"
        output_file = f"{output_dir}/sanitized_output.txt"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Read the OCR output
        with open(input_file, "r") as f:
            ocr_output = json.load(f)

        # Generate suggestions only for text within `text_lines`
        suggestions = []
        for page in ocr_output:
            text_lines = page.get("text_lines", [])
            for line in text_lines:
                line_suggestions = self.generate_suggestions(line)
                suggestions.extend(line_suggestions)

        with open(suggestions_file, "w") as f:
            for idx, (original, proposed) in enumerate(suggestions):
                f.write(f"-------------------------------\n")
                f.write(f"Proposed Change {idx+1}:\n\n")
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

    def get_context(self, text, word, window=30):
        start_index = max(text.find(word) - window, 0)
        end_index = min(start_index + len(word) + 2 * window, len(text))
        return text[start_index:end_index]

    def apply_suggestions(self, text, suggestions):
        words = text.split()
        corrected_text = ""
        for word in words:
            corrected_text += suggestions.get(word, word) + " "
        return corrected_text.strip()

    def parse_suggestions(self, suggestions_text):
        suggestions = {}
        lines = suggestions_text.split("\n")
        for line in lines:
            if " ---> " in line:
                original, corrected = line.split(" ---> ")
                suggestions[original.strip()] = corrected.strip()
        return suggestions