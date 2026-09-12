import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches


# =========================================
# LOAD DATASET
# =========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "Content Catalog (Netflix - Prime Video).xlsx"

try:
    movies = pd.read_excel(DATA_PATH)
except Exception as e:
    raise Exception(
        f"Unable to load dataset. Check the file path.\n{e}"
    )


# =========================================
# CHECK DATASET COLUMNS
# =========================================

print("Dataset columns:", movies.columns.tolist())


# Convert all column names to lowercase
movies.columns = movies.columns.str.strip().str.lower()


# =========================================
# FIND TITLE COLUMN
# =========================================

possible_title_columns = [
    "title",
    "name",
    "show",
    "show title"
]

title_column = None

for col in possible_title_columns:
    if col in movies.columns:
        title_column = col
        break


if title_column is None:
    title_column = movies.columns[0]


# =========================================
# CREATE CONTENT FOR RECOMMENDATION
# =========================================

movies[title_column] = movies[title_column].fillna("").astype(str)

# Combine all useful text columns
text_columns = movies.select_dtypes(include=["object"]).columns.tolist()

movies["content"] = ""

for col in text_columns:
    movies["content"] += " " + movies[col].fillna("").astype(str)


# =========================================
# TF-IDF MODEL
# =========================================

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000
)

tfidf_matrix = vectorizer.fit_transform(
    movies["content"]
)


# =========================================
# COSINE SIMILARITY
# =========================================

similarity = cosine_similarity(tfidf_matrix)


# =========================================
# RECOMMEND CONTENT
# =========================================

def recommend_movies(movie_name, number=5):

    movie_name = str(movie_name).strip()

    if not movie_name:
        return None, []

    titles = movies[title_column].fillna("").astype(str)

    # Exact match
    exact_match = movies[
        titles.str.lower() == movie_name.lower()
    ]

    if not exact_match.empty:

        movie_index = exact_match.index[0]

    else:

        # Partial match
        partial_match = movies[
            titles.str.lower().str.contains(
                movie_name.lower(),
                na=False,
                regex=False
            )
        ]

        if not partial_match.empty:

            movie_index = partial_match.index[0]

        else:

            # Closest match
            title_list = titles.tolist()

            close_matches = get_close_matches(
                movie_name.lower(),
                [title.lower() for title in title_list],
                n=1,
                cutoff=0.4
            )

            if not close_matches:
                return None, []

            closest_title = close_matches[0]

            matching_indexes = movies[
                titles.str.lower() == closest_title
            ].index

            if len(matching_indexes) == 0:
                return None, []

            movie_index = matching_indexes[0]


    # Selected title
    selected_movie = movies.loc[
        movie_index,
        title_column
    ]


    # Similarity scores
    similarity_scores = list(
        enumerate(similarity[movie_index])
    )

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )


    # Recommendations
    recommendations = []

    for index, score in similarity_scores[1:number + 1]:

        item = movies.iloc[index]

        recommendations.append({
            "title": str(item[title_column])
        })


    return selected_movie, recommendations
