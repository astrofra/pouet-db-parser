import os
import re
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Folders
input_folder = "./pouet_oneliners"
output_folder = "./word_clouds"
os.makedirs(output_folder, exist_ok=True)

# Regex for valid oneliner lines
line_regex = re.compile(r"^(\d{2}:\d{2})\s+(.*?)\[(\d+)\]\s+:\s+(.*)$")

# Data storage
data = []

cloud_size = 40

# Read all .txt files
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".txt"):
        with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
            current_date = None
            for line in f:
                line = line.strip()
                if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
                    current_date = line
                else:
                    match = line_regex.match(line)
                    if match and current_date:
                        time_text, nickname, pouet_id, message = match.groups()
                        year = current_date.split("-")[0]
                        data.append({
                            "year": int(year),
                            "message": message
                        })

# Convert to DataFrame
df = pd.DataFrame(data)

# Basic stopwords (can be extended)
custom_stopwords = set(STOPWORDS)
custom_stopwords.update(["the", "and", "to", "is", "a", "of", "in", "on", "for", "it's", "i'm", "im", "are", "at", "with", "you", "that", "we", "da", "yo", "plouf", "glop"])
custom_stopwords.update([
    "the", "and", "to", "is", "a", "of", "in", "on", "for", "it's", "i'm", "im", "are", "at",
    "with", "you", "that", "we", "this", "was", "be", "by", "have", "has", "had", "from",
    "as", "but", "if", "or", "so", "an", "it's", "i", "me", "my", "your", "our", "their",
    "they", "he", "she", "it", "his", "her", "him", "them", "who", "whom", "which", "what",
    "when", "where", "why", "how", "can", "could", "would", "should", "will", "shall",
    "may", "might", "must", "been", "being", "do", "does", "did", "doing", "no", "not",
    "yes", "up", "down", "out", "about", "just", "more", "less", "only", "also", "very",
    "all", "some", "any", "each", "other", "than", "then", "now", "there", "here", "too",
    "over", "again", "ever", "never", "much", "many", "such", "own", "same", "both",
    "because", "into", "onto", "off", "among", "between", "during", "before", "after",
    "under", "above", "against", "upon",
    "back", "see", "great", "need", "ok", "doesnt",

    # Demoscene-specific or irrelevant in this context
    "plouf", "glop", "yo", "da", "fuck", "good", "bad", "dont", "world", "say", "go", "let", "year",
    "de", "du", "des", "le", "la", "les", "php", "html"
])

custom_stopwords.update([
    "one", "new", "want", "please", "think", "know", "nice", "make", "still", "time", "people",
    "really", "something", "better", "oh", "someone", "use", "first", "going", "maybe",
    "well", "anyone", "work", "right", "us", "day", "always", "today", "sure", "find", "feel",
    "thing", "things", "another", "way", "try", "come", "start", "stop", "already", "look",
    "next", "real", "actually", "said", "long", "without", "mean",
    "add", "added", "check", "stop", "seems", "maybe",
    "created", "users", "hot", "cold", "http", "jpg", "url", "https", "htm",
])

custom_stopwords.update([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "anyway",
    "b", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "c", "can", "can't", "cannot", "could", "couldn't",
    "d", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "e", "each", "even", "ever",
    "f", "few", "for", "from", "further", "fuck",
    "g", "get", "got",
    "h", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's",
    "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "j", "just",
    "k", "keep",
    "l", "let's",
    "m", "me", "more", "most", "mustn't", "my", "myself", "mean"
    "n", "no", "nor", "not", "now",
    "o", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "p", "plouf", "put"
    "q", "quite",
    "rather", "re",
    "s", "same", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "t", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
    "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "u", "under", "until", "up", "upon",
    "v", "very",
    "w", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "will", "with", "won't", "would",
    "wouldn't", "want",
    "x",
    "y", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "z"
])

custom_stopwords.update([
    "un", "une", "au", "aux", "après", "avant", "avec", "autre", "autres", "aucun", "aucune", "a", "à",
    "beaucoup", "bien", "bon", "bonne", "bref",
    "ce", "ces", "cette", "cet", "c'", "cela", "celle", "celui", "celles", "ceux", "comme", "comment", "contre",
    "dans", "de", "des", "du", "donc", "depuis", "dedans", "dehors", "dernier", "dernière", "déjà",
    "elle", "elles", "en", "encore", "entre", "est", "et", "eux",
    "fait", "faut", "fais", "faisait", "ferait",
    "grand", "grande",
    "hier", "hors",
    "il", "ils", "ici",
    "je", "jamais", "jusque", "juste",
    "kikoo",
    "la", "le", "les", "leur", "leurs", "là", "lui",
    "mais", "mal", "ma", "me", "même", "mes", "mon", "moins",
    "ne", "ni", "non", "notre", "nous", "nos", "nouveau", "nouvelle",
    "on", "ou", "où",
    "par", "parce", "pas", "peu", "peut", "plus", "pour", "pouvoir", "presque", "plouf",
    "quand", "que", "quel", "quelle", "quelles", "quels", "qui", "quoi",
    "rien",
    "sa", "se", "ses", "si", "sien", "sienne", "sont", "sans", "sur", "sous",
    "ta", "te", "tes", "toi", "ton", "tous", "tout", "toute", "toutes", "très", "tu",
    "un", "une",
    "vers", "vieux", "vielle", "vos", "votre", "vous",
    "wesh",
    "zut", "zéro",
    "merde", "fuck", "yo", "putain", "bordel"
])




# Generate word clouds by year
for year in sorted(df["year"].unique()):
    yearly_df = df[df["year"] == year]
    text = " ".join(yearly_df["message"].tolist()).lower()
    
    wordcloud = WordCloud(width=1200, height=600, background_color="white", prefer_horizontal=1.0, stopwords=custom_stopwords, max_words=cloud_size, font_path="./roboto.ttf").generate(text)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Word Cloud - {year}")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"wordcloud_{year}.png"))
    plt.close()

    # Count word frequencies excluding stopwords
    words = text.split()
    filtered_words = [word for word in words if word.isalpha() and word not in custom_stopwords]
    word_series = pd.Series(filtered_words)
    word_counts = word_series.value_counts().head(cloud_size)

    # Save to .txt file
    txt_path = os.path.join(output_folder, f"wordcloud_{year}_top{cloud_size}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for word, count in word_counts.items():
            f.write(f"{word} ({count})\n")


print(f"Word clouds saved to {output_folder}")
