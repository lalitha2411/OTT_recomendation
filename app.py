import streamlit as st

from recommender import (
    recommend_movies,
    search_content,
    get_content_by_type,
    get_content_by_platform,
    get_all_content
)


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="CineVerse",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================
# SESSION STATE
# =========================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "my_list" not in st.session_state:
    st.session_state.my_list = []

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = ""

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []


# =========================================
# THEME
# =========================================

if st.session_state.dark_mode:

    background = "#0f0f0f"
    text_color = "#ffffff"
    secondary_color = "#bdbdbd"
    card_color = "#1c1c1c"
    border_color = "#333333"

else:

    background = "#f5f5f5"
    text_color = "#111111"
    secondary_color = "#555555"
    card_color = "#ffffff"
    border_color = "#dddddd"


# =========================================
# CSS
# =========================================

st.markdown(
    f"""
    <style>

    [data-testid="stHeader"] {{
        display: none;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    .stApp {{
        background-color: {background};
        color: {text_color};
    }}

    .block-container {{
        padding-top: 1rem !important;
        padding-left: 4% !important;
        padding-right: 4% !important;
        padding-bottom: 2rem !important;
    }}

    .movie-card {{
        background-color: {card_color};
        border: 1px solid {border_color};
        border-radius: 15px;
        padding: 18px;
        min-height: 260px;
        margin-bottom: 15px;
    }}

    .hero {{
        background-color: {card_color};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
    }}

    .content-title {{
        font-size: 18px;
        font-weight: bold;
        color: {text_color};
    }}

    .content-text {{
        color: {secondary_color};
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================
# FUNCTIONS
# =========================================

def add_to_my_list(item):

    exists = any(
        movie["title"] == item["title"]
        and movie["type"] == item["type"]
        and movie["platform"] == item["platform"]
        for movie in st.session_state.my_list
    )

    if not exists:
        st.session_state.my_list.append(item)


def save_search(title):

    if title in st.session_state.search_history:
        st.session_state.search_history.remove(title)

    st.session_state.search_history.insert(
        0,
        title
    )

    st.session_state.search_history = (
        st.session_state.search_history[:5]
    )


def show_card(item, key_prefix):

    st.markdown(
        f"""
        <div class="movie-card">

        <div class="content-title">
        🎬 {item["title"]}
        </div>

        <br>

        <div class="content-text">
        📺 Type: {item["type"]}<br>
        🎭 Genre: {item["genres"]}<br>
        📅 Year: {item["year"]}<br>
        ⭐ Rating: {item["rating"]}<br>
        📱 Platform: {item["platform"]}<br>
        ⏱️ Duration: {item["duration"]}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "❤️ Add to My List",
        key=f"{key_prefix}_{item['id']}_{item['title']}"
    ):

        add_to_my_list(item)

        st.success("Added to My List ❤️")


def show_content_grid(items, prefix):

    if not items:

        st.info("No content available.")

        return

    cols = st.columns(4)

    for i, item in enumerate(items):

        with cols[i % 4]:

            show_card(
                item,
                f"{prefix}_{i}"
            )


# =========================================
# NAVIGATION BAR
# =========================================

logo, home, movies, tv, mylist, theme = st.columns(
    [3, 1.2, 1.2, 1.5, 1.5, 1.2]
)


with logo:

    st.markdown("## 🎬 CineVerse")


with home:

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):

        st.session_state.page = "Home"
        st.rerun()


with movies:

    if st.button(
        "🎬 Movies",
        use_container_width=True
    ):

        st.session_state.page = "Movies"
        st.rerun()


with tv:

    if st.button(
        "📺 TV Shows",
        use_container_width=True
    ):

        st.session_state.page = "TV Shows"
        st.rerun()


with mylist:

    if st.button(
        "❤️ My List",
        use_container_width=True
    ):

        st.session_state.page = "My List"
        st.rerun()


with theme:

    if st.button(
        "🌙 / ☀️",
        use_container_width=True
    ):

        st.session_state.dark_mode = (
            not st.session_state.dark_mode
        )

        st.rerun()


st.divider()


# =========================================
# HOME PAGE
# =========================================

if st.session_state.page == "Home":

    st.markdown(
        """
        <div class="hero">

        <h1>🎥 Discover Movies You'll Love</h1>

        <p>
        Tell us what you enjoy watching and CineVerse will
        recommend movies and TV shows based on similar
        stories, genres, and themes.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================
    # SEARCH
    # =====================================

    st.subheader("🔍 Search Movies and TV Shows")

    search_col, button_col = st.columns([5, 1])

    with search_col:

        search_name = st.text_input(
            "Search",
            placeholder="Search any movie or TV show...",
            label_visibility="collapsed"
        )

    with button_col:

        search_button = st.button(
            "🔍 Search",
            use_container_width=True
        )


    if search_button:

        if search_name.strip() == "":

            st.warning(
                "⚠️ Please enter a movie or TV show name."
            )

        else:

            selected, recommendations = recommend_movies(
                search_name
            )

            if selected is None:

                st.error(
                    "❌ Content not found in the dataset."
                )

                results = search_content(search_name)

                st.session_state.search_results = results

            else:

                st.session_state.selected_movie = (
                    selected["title"]
                )

                st.session_state.recommendations = (
                    recommendations
                )

                save_search(selected["title"])

                st.session_state.search_results = [
                    selected
                ]


    # =====================================
    # SEARCH RESULT
    # =====================================

    if st.session_state.search_results:

        st.divider()

        st.subheader("🔎 Search Result")

        show_content_grid(
            st.session_state.search_results[:4],
            "search"
        )


    # =====================================
    # RECENT SEARCHES
    # =====================================

    if st.session_state.search_history:

        st.divider()

        st.subheader("🕒 Recently Searched")

        history_cols = st.columns(
            min(
                len(st.session_state.search_history),
                5
            )
        )

        for i, title in enumerate(
            st.session_state.search_history
        ):

            with history_cols[i]:

                if st.button(
                    f"🎬 {title}",
                    key=f"history_{i}"
                ):

                    selected, recommendations = (
                        recommend_movies(title)
                    )

                    if selected:

                        st.session_state.selected_movie = (
                            selected["title"]
                        )

                        st.session_state.recommendations = (
                            recommendations
                        )

                        st.rerun()


    # =====================================
    # RECOMMENDATIONS
    # =====================================

    if st.session_state.recommendations:

        st.divider()

        st.subheader(
            f"🎯 Because You Searched: "
            f"{st.session_state.selected_movie}"
        )

        show_content_grid(
            st.session_state.recommendations[:8],
            "recommendation"
        )


    # =====================================
    # BASED ON SEARCH HISTORY
    # =====================================

    if len(st.session_state.search_history) >= 2:

        st.divider()

        st.subheader(
            "🔥 Recommended Based on Your Recent Searches"
        )

        all_recommendations = []

        searched_titles = [
            title.lower()
            for title in st.session_state.search_history
        ]

        for title in st.session_state.search_history:

            selected, recs = recommend_movies(
                title,
                number=8
            )

            for item in recs:

                already_exists = any(
                    movie["title"].lower()
                    == item["title"].lower()
                    for movie in all_recommendations
                )

                if (
                    item["title"].lower()
                    not in searched_titles
                    and not already_exists
                ):

                    all_recommendations.append(item)

        show_content_grid(
            all_recommendations[:8],
            "history_recommendation"
        )


    # =====================================
    # EXPLORE CONTENT
    # =====================================

    st.divider()

    st.subheader("🔥 Explore Popular Content")

    all_content = get_all_content(limit=8)

    show_content_grid(
        all_content,
        "explore"
    )


# =========================================
# MOVIES PAGE
# =========================================

elif st.session_state.page == "Movies":

    st.title("🎬 Movies")

    st.write(
        "Explore movies available on Netflix and Prime Video."
    )

    st.divider()


    # Platform Filter
    platform = st.selectbox(
        "Select Platform",
        [
            "All Platforms",
            "Netflix",
            "Prime Video"
        ]
    )


    if platform == "All Platforms":

        movies_list = get_content_by_type(
            "Movie",
            limit=40
        )

    else:

        platform_content = get_content_by_platform(
            platform,
            limit=100
        )

        movies_list = [
            item
            for item in platform_content
            if item["type"].lower() == "movie"
        ][:40]


    show_content_grid(
        movies_list,
        "movies"
    )


# =========================================
# TV SHOWS PAGE
# =========================================

elif st.session_state.page == "TV Shows":

    st.title("📺 TV Shows")

    st.write(
        "Explore TV Shows available on Netflix and Prime Video."
    )

    st.divider()


    platform = st.selectbox(
        "Select Platform",
        [
            "All Platforms",
            "Netflix",
            "Prime Video"
        ]
    )


    if platform == "All Platforms":

        tv_list = get_content_by_type(
            "TV Show",
            limit=40
        )

    else:

        platform_content = get_content_by_platform(
            platform,
            limit=100
        )

        tv_list = [
            item
            for item in platform_content
            if item["type"].lower() == "tv show"
        ][:40]


    show_content_grid(
        tv_list,
        "tv"
    )


# =========================================
# MY LIST PAGE
# =========================================

elif st.session_state.page == "My List":

    st.title("❤️ My List")

    if not st.session_state.my_list:

        st.info(
            "Your list is empty. "
            "Add Movies or TV Shows to your list!"
        )

    else:

        st.subheader(
            f"❤️ Saved Content "
            f"({len(st.session_state.my_list)})"
        )

        cols = st.columns(4)

        for i, item in enumerate(
            st.session_state.my_list
        ):

            with cols[i % 4]:

                st.markdown(
                    f"""
                    <div class="movie-card">

                    <div class="content-title">
                    🎬 {item["title"]}
                    </div>

                    <br>

                    <div class="content-text">
                    📺 {item["type"]}<br>
                    🎭 {item["genres"]}<br>
                    📅 {item["year"]}<br>
                    📱 {item["platform"]}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "🗑️ Remove",
                    key=f"remove_{i}_{item['title']}"
                ):

                    st.session_state.my_list.pop(i)

                    st.rerun()