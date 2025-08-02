import os
import ollama

# Input and output folders
input_folder = "./bbs"
output_folder = "./bbs"
os.makedirs(output_folder, exist_ok=True)

# LLM model name
MODEL_NAME = 'magistral:24b'  # 'deepseek-r1:32b'  # 'llama3:8b'  # or 'deepseek-r1:7b'

# Prompt template
PROMPT_TEMPLATE_EN = """
You are a researcher studying demoscene culture in 2025 through its online archives (from 2000 to 2025).
Here is a raw excerpt from the Pouet.net BBS forum, focusing on a specific topic:

--- START OF TEXT ---
{bbs_text}
--- END OF TEXT ---

Your task is to produce a structured thematic synthesis in English, as an analytical text of no more than 550 words.

To guide your analysis, consider the following axes:
1. The main topic of the original (first) post
2. The overall tone of the thread (nostalgia, tension, enthusiasm, irony…)
3. How the discussion evolves across replies
4. Technical aspects or creative projects mentioned
5. Prominent users that contribute to this thread
6. Humorous elements or culturally specific references to the scene

**Pouet.net glossary**:
- A *demo* is a real-time audiovisual creation, often technically impressive.
- An *intro* is a size-limited demo (e.g. 64k or 4k).
- A *scener* is an active member of the demoscene.
- A *glop* is a reputation score: the more a user contributes (e.g. adding productions, commenting), the more their glop increases.
- A *gloperator* is a content moderator on Pouet.net.

Be structured and reflect the spirit of the conversation.
"""

PROMPT_TEMPLATE = """
Tu es un chercheur qui étudie la culture de la demoscene en 2025 à partir de ses archives en ligne (de 2000 à 2025).
Voici un extrait brut du forum BBS de Pouet.net, centré sur un sujet particulier :

--- DÉBUT DU TEXTE ---
{bbs_text}
--- FIN DU TEXTE ---

Ta tâche est de produire une synthèse thématique structurée et analytique en français, sous la forme d’un texte ne dépassant pas 550 mots.

Tu dois restituer fidèlement l’esprit de la discussion, tout en adoptant une posture interprétative lorsque c’est pertinent. N’hésite pas à formuler des hypothèses sur les dynamiques sociales, les implicites culturels ou les tensions entre générations ou styles de communication.

Pour guider ton analyse, tu peux t’appuyer sur les axes suivants :
1. Le sujet principal évoqué dans le premier message
2. L’ambiance générale du fil (nostalgie, tension, enthousiasme, ironie…)
3. L’évolution de la discussion au fil des réponses
4. Les aspects techniques ou les projets créatifs mentionnés
5. Les utilisateurs marquants qui interviennent dans le fil
6. Les touches d’humour ou les références culturelles propres à la demoscene

Essaie de relier les éléments entre eux (par exemple : un changement de ton peut être causé par un post technique ; un troll peut révéler une tension latente, etc.). Tu peux, si besoin, comparer à d’autres échanges typiques du BBS ou commenter la manière dont cette discussion reflète des logiques propres à la communauté demoscene.

**Glossaire Pouet.net** :
- Une *demo* est une création audiovisuelle en temps réel, souvent impressionnante techniquement.
- Une *intro* est une demo très limitée en taille (par exemple 64k ou 4k).
- Un *scener* est un membre actif de la demoscene.
- Un *glop* est un indicateur de réputation : plus un utilisateur contribue (ajout de productions, commentaires…), plus son score de glop augmente.
- Un *gloperator* est un modérateur du contenu sur Pouet.net.

Tu peux expliquer brièvement d’autres termes propres à cette communauté s’ils apparaissent dans le fil.

Sois structuré, synthétique, mais pas purement descriptif. Ton texte doit refléter une compréhension profonde de la culture et des dynamiques sociales à l’œuvre dans ce fil.
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
