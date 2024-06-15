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
        self.whitelist = self.load_whitelists(args.language, args.whitelist_filter)

    def load_dictionary(self, language):
        try:
            dictionary = enchant.Dict(language)
            logging.info(f"Preparing Enchant dictionary {language}")
        except enchant.DictNotFoundError:
            raise ValueError(f"No dictionary found for language: {language}")
        return dictionary

    def load_whitelists(self, language, filter_keywords):
        whitelist = set()
        project_whitelist_path = f"/workspace/resources"
        input_whitelist_path = f"{self.args.input_dir}"

        def process_whitelist_file(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.split('#', 1)[0].strip()
                    if line:
                        whitelist.add(line)

        if os.path.exists(project_whitelist_path):
            for filename in os.listdir(project_whitelist_path):
                if filename.startswith(f"spelling-whitelist-{language}") and self.filter_file(filename, filter_keywords):
                    process_whitelist_file(os.path.join(project_whitelist_path, filename))
                    logging.info(f"Loaded project-specific whitelist from {filename}")

        if os.path.exists(input_whitelist_path):
            for filename in os.listdir(input_whitelist_path):
                if filename.startswith(f"spelling-whitelist-{language}"):
                    process_whitelist_file(os.path.join(input_whitelist_path, filename))
                    logging.info(f"Loaded input directory whitelist from {filename}")

        if not whitelist:
            logging.warning(f"No whitelists found for language: {language}")

        return whitelist

    def filter_file(self, filename, filter_keywords):
        if not filter_keywords:
            return True
        for keyword in filter_keywords.split(','):
            if keyword.strip() in filename:
                return True
        return False

    def run(self, input_data):
        input_file = f"{input_data}/ocr_result/ocr_result.json"
        output_dir = f"{input_data}/sanitized"
        suggestions_file = f"{output_dir}/suggestions.txt"
        whitelist_candidates_file = f"{output_dir}/whitelist_candidates.txt"
        output_file = f"{output_dir}/sanitized_output.json"

        logging.info(f"Input file: {input_file} suggestion file: {suggestions_file}, output file: {output_file}")

        os.makedirs(output_dir, exist_ok=True)

        with open(input_file, "r") as f:
            ocr_output = json.load(f)

        suggestions = []
        for page_index, page in enumerate(ocr_output):
            text_lines = page.get("text_lines", [])
            for line_index, line in enumerate(text_lines):
                logging.debug(f"Preparing suggestions for page {page_index} line {line_index}")
                line_suggestions = self.generate_suggestions(line, text_lines, line_index)
                suggestions.extend([(page_index, line_index, word, sugg) for word, sugg in line_suggestions])

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

        original_words = set(original for _, _, original, _ in suggestions)
        with open(whitelist_candidates_file, "w") as wf:
            for word in original_words:
                wf.write(word + "\n")

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

    def generate_suggestions(self, text, text_lines, line_index):
        suggestions = []
        words = text.split()
        for word in words:
            if not re.match(r'^[a-zA-ZäöüÄÖÜß]+$', word):
                continue
            if len(word) == 1:
                continue
            if word in self.whitelist:
                continue
            if not self.dictionary.check(word):
                suggestions.append((word, self.dictionary.suggest(word)))

        if words and words[-1].endswith('-'):
            next_line = self.get_next_line(text_lines, line_index)
            if next_line and next_line.strip():
                next_words = next_line.split()
                if next_words:
                    next_word = next_words[0]
                    combined_word = words[-1][:-1] + next_word
                    if not self.dictionary.check(combined_word):
                        suggestions.append((words[-1], self.dictionary.suggest(combined_word)))

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
