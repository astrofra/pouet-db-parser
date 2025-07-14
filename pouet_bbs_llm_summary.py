import os
import ollama

# Input and output folders
input_folder = "./bbs"
output_folder = "./bbs"
os.makedirs(output_folder, exist_ok=True)

# LLM model name
MODEL_NAME = 'llama3:8b'  # or 'deepseek-r1:7b'

# Prompt template
PROMPT_TEMPLATE = """
You are a researcher studying demoscene culture in 2025 through its online archives (from 2000 up to 2025).
Here is a raw excerpt from the Pouet.net BBS forum, on a specific topic :

--- START OF TEXT ---
{bbs_text}
--- END OF TEXT ---

Your task is to produce a thematic synthesis, in the form of a structured, analytical text in English. Maximum 150 words.
"""

# Loop over each .txt file
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_folder, filename)
        output_filename = filename.replace(".txt", "_llm_summary.md")
        output_path = os.path.join(output_folder, output_filename)

        if not os.path.isfile(output_path):
            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Build prompt
            prompt = PROMPT_TEMPLATE.format(bbs_text=text)

            try:
                print(f"Processing {filename}...")
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[{
                        'role': 'user',
                        'content': prompt
                    }]
                )

                # Save result
                with open(output_path, "w", encoding="utf-8") as out_f:
                    out_f.write(response["message"]["content"])

            except Exception as e:
                print(f"Error processing {filename}: {e}")

print(f"Monthly digests saved to {output_folder}")
