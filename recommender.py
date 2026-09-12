import pandas as pd
from pathlib import Path
from difflib import get_close_matches

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================
# LOAD DATASET
# =========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "Content Catalog (Netflix - Prime Video).xlsx"

# If dataset is inside a dataset folder, use this automatically
if not DATA_PATH.exists():
    DATA_PATH = (
        BASE_DIR
        / "dataset"
        / "Content Catalog (Netflix - Prime Video).xlsx"
    )


@pd.api.extensions.register_dataframe_accessor("cineverse")
class CineVerseAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj


try:
    content_df = pd.read_excel(
        DATA_PATH,
        sheet_name="Combined"
    )

except Exception as e:
    raise Exception(
        f"Unable to load dataset. Check the file path.\n{e}"
    )


# =========================================
# CLEAN DATA
# =========================================

content_df["title"] = (
    content_df["title"]
    .fillna("")
    .astype(str)
)

content_df["type"] = (
    content_df["type"]
    .fillna("Unknown")
    .astype(str)
)

content_df["listed_in"] = (
    content_df["listed_in"]
    .fillna("Unknown")
    .astype(str)
)

content_df["description"] = (
    content_df["description"]
    .fillna("")
    .astype(str)
)

content_df["cast"] = (
    content_df["cast"]
    .fillna("")
    .astype(str)
)

content_df["director"] = (
    content_df["director"]
    .fillna("")
    .astype(str)
)

content_df["Platform"] = (
    content_df["Platform"]
    .fillna("Unknown")
    .astype(str)
)

content_df["rating"] = (
    content_df["rating"]
    .fillna("Not Rated")
    .astype(str)
)

content_df["release_year"] = (
    content_df["release_year"]
    .fillna(0)
)


# =========================================
# REMOVE DUPLICATE TITLES
# =========================================

content_df = content_df.drop_duplicates(
    subset=["title", "type", "Platform"]
).reset_index(drop=True)


# =========================================
# CREATE CONTENT FEATURES
# =========================================

content_df["content"] = (
    content_df["listed_in"] + " " +
    content_df["description"] + " " +
    content_df["cast"] + " " +
    content_df["director"]
)


# =========================================
# TF-IDF MODEL
# =========================================

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000
)

tfidf_matrix = vectorizer.fit_transform(
    content_df["content"]
)


# =========================================
# CONVERT ROW TO DICTIONARY
# =========================================

def row_to_dict(row):

    return {
        "id": str(row.get("show_id", "")),
        "title": str(row.get("title", "")),
        "type": str(row.get("type", "")),
        "genres": str(row.get("listed_in", "Unknown")),
        "rating": str(row.get("rating", "Not Rated")),
        "year": int(row.get("release_year", 0))
        if pd.notna(row.get("release_year", 0))
        else 0,
        "platform": str(row.get("Platform", "Unknown")),
        "description": str(row.get("description", "")),
        "duration": str(row.get("duration", "")),
        "country": str(row.get("country", ""))
    }


# =========================================
# SEARCH CONTENT
# =========================================

def search_content(search_text, limit=20):

    search_text = str(search_text).strip()

    if not search_text:
        return []

    results = content_df[
        content_df["title"]
        .str.lower()
        .str.contains(
            search_text.lower(),
            na=False,
            regex=False
        )
    ]

    return [
        row_to_dict(row)
        for _, row in results.head(limit).iterrows()
    ]


# =========================================
# GET CONTENT BY TYPE
# =========================================

def get_content_by_type(content_type, limit=20):

    results = content_df[
        content_df["type"]
        .str.lower() == content_type.lower()
    ]

    # Show newer content first
    results = results.sort_values(
        by="release_year",
        ascending=False
    )

    return [
        row_to_dict(row)
        for _, row in results.head(limit).iterrows()
    ]


# =========================================
# GET CONTENT BY PLATFORM
# =========================================

def get_content_by_platform(platform, limit=20):

    results = content_df[
        content_df["Platform"]
        .str.lower() == platform.lower()
    ]

    results = results.sort_values(
        by="release_year",
        ascending=False
    )

    return [
        row_to_dict(row)
        for _, row in results.head(limit).iterrows()
    ]


# =========================================
# GET ALL CONTENT
# =========================================

def get_all_content(limit=20):

    results = content_df.sort_values(
        by="release_year",
        ascending=False
    )

    return [
        row_to_dict(row)
        for _, row in results.head(limit).iterrows()
    ]


# =========================================
# RECOMMEND MOVIES / TV SHOWS
# =========================================

def recommend_movies(content_name, number=5):

    content_name = str(content_name).strip()

    if not content_name:
        return None, []

    titles = content_df["title"].fillna("").tolist()

    # -------------------------------------
    # EXACT MATCH
    # -------------------------------------

    exact_match = content_df[
        content_df["title"].str.lower()
        == content_name.lower()
    ]

    if not exact_match.empty:

        content_index = exact_match.index[0]

    else:

        # ---------------------------------
        # PARTIAL MATCH
        # ---------------------------------

        partial_match = content_df[
            content_df["title"]
            .str.lower()
            .str.contains(
                content_name.lower(),
                na=False,
                regex=False
            )
        ]

        if not partial_match.empty:

            content_index = partial_match.index[0]

        else:

            # -----------------------------
            # CLOSEST SPELLING MATCH
            # -----------------------------

            lower_titles = [
                title.lower()
                for title in titles
            ]

            close_matches = get_close_matches(
                content_name.lower(),
                lower_titles,
                n=1,
                cutoff=0.55
            )

            if not close_matches:
                return None, []

            closest_title = close_matches[0]

            matching_indexes = content_df[
                content_df["title"].str.lower()
                == closest_title
            ].index

            if len(matching_indexes) == 0:
                return None, []

            content_index = matching_indexes[0]

    # -------------------------------------
    # SELECTED CONTENT
    # -------------------------------------

    selected_row = content_df.iloc[content_index]

    selected_content = row_to_dict(selected_row)

    # -------------------------------------
    # CALCULATE SIMILARITY
    # -------------------------------------

    similarity_scores = cosine_similarity(
        tfidf_matrix[content_index],
        tfidf_matrix
    ).flatten()

    similar_indexes = similarity_scores.argsort()[::-1]

    recommendations = []

    selected_title = selected_content["title"]

    for index in similar_indexes:

        if index == content_index:
            continue

        row = content_df.iloc[index]

        movie = row_to_dict(row)

        # Avoid duplicate titles
        if movie["title"] == selected_title:
            continue

        if movie["title"] not in [
            item["title"]
            for item in recommendations
        ]:

            recommendations.append(movie)

        if len(recommendations) >= number:
            break

    return selected_content, recommendations