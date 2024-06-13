# src/steps/sanitization_step.py
import os
import enchant
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

    def run(self, input_data):
        input_file = f"{input_data}/ocr_result/ocr_result.json"
        output_dir = f"{input_data}/sanitized"
        suggestions_file = f"{output_dir}/suggestions.txt"
        output_file = f"{output_dir}/sanitized_output.txt"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Read the OCR output
        with open(input_file, "r") as f:
            ocr_output = f.read()

        # Generate suggestions
        suggestions = self.generate_suggestions(ocr_output)
        with open(suggestions_file, "w") as f:
            for idx, (original, proposed) in enumerate(suggestions):
                context = self.get_context(ocr_output, original)
                f.write(f"-------------------------------\n")
                f.write(f"Proposed Change {idx+1}:\n\n")
                f.write(f"{context}\n\n")
                f.write(f"now:      {original}\n")
                f.write(f"then:      {proposed[0] if proposed else original}\n\n")
                f.write(f"{original}  --->   {proposed[0] if proposed else original}\n")
                f.write(f"--------------------------------------------\n\n")

        if self.args.interactive_mode:
            input("Review the suggestions and press Enter to apply changes...")

        # Apply changes
        with open(suggestions_file, "r") as f:
            reviewed_suggestions = self.parse_suggestions(f.read())

        sanitized_text = self.apply_suggestions(ocr_output, reviewed_suggestions)

        with open(output_file, "w") as f:
            f.write(sanitized_text)

        return output_dir

    def get_context(self, text, word, window=30):
        start_index = max(text.find(word) - window, 0)
        end_index = min(start_index + len(word) + 2 * window, len(text))
        return text[start_index:end_index]

    def parse_suggestions(self, suggestions_text):
        suggestions = {}
        lines = suggestions_text.split("\n")
        for line in lines:
            if " ---> " in line:
                original, corrected = line.split(" ---> ")
                suggestions[original.strip()] = corrected.strip()
        return suggestions

    def apply_suggestions(self, text, suggestions):
        words = text.split()
        corrected_text = ""
        for word in words:
            corrected_text += suggestions.get(word, word) + " "
        return corrected_text.strip()
