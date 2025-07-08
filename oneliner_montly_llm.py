import os
import ollama

# Input and output folders
input_folder = "./monthly_oneliners"
output_folder = "./monthly_digests"
os.makedirs(output_folder, exist_ok=True)

# LLM model name
MODEL_NAME = 'llama3:8b'  # or 'deepseek-r1:7b'

# Prompt template
PROMPT_TEMPLATE = """
You are analyzing an archive of short messages posted publicly by users of the demoscene community on the site pouet.net. The archive is a single monthly file, containing a mix of languages (mostly English and French), humor, technical chat, and scene-specific expressions.

Your task is to extract and summarize the following from this text:
- the **technical points** discussed (e.g., programming, demos, rendering, tools),
- any **social facts or dynamics** (e.g., user behavior, jokes, conflicts, memes),
- the **notable individuals** (e.g., recurring names, respected users, people getting attention),
- any **events** (e.g., birthdays, demoparties, deadlines, releases).

Write in plain English (markdown format), in four clearly labeled sections.

Here is the raw text archive to analyze:
---
{text}
"""

# Loop over each .txt file
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".txt"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Build prompt
        prompt = PROMPT_TEMPLATE.format(text=text)

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
            with open(output_path.replace(".txt", ".md"), "w", encoding="utf-8") as out_f:
                out_f.write(response["message"]["content"])

        except Exception as e:
            print(f"Error processing {filename}: {e}")

print(f"Monthly digests saved to {output_folder}")
