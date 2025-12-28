import streamlit as st
import pickle
import requests

# change title name
st.set_page_config(
    page_title="Movie Recommender",  
    page_icon="🎬",                    
)

@st.cache_resource               # Run this function only once, save (“cache”) the result, and reuse it every time the app reruns
def load_data():
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarities.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()
movies = movies.reset_index(drop=True)   #  Pandas dataframe ka index random / old ho sakta hai
movie_list = movies['title'].values

# fetch movies poster from TMDB API
def fetch_poster(movie_id):
    
    try:
        api_key = st.secrets["TMDB_API_KEY"] 
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
        
        response = requests.get(url, timeout=10)
        data = response.json()
        poster_path = data.get('poster_path')
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
        
    except:
        return "https://via.placeholder.com/500x750?text=No+Poster"

# movie recommendation 
def recommend(movie):
    
    indices = movies[movies['title'] == movie].index
    if len(indices) == 0:
       st.error("Movie not found")
       return [], []
    movie_index = indices[0]

    distance = similarity[movie_index]
    similar_movie = sorted(list(enumerate(distance)), reverse = True, key = lambda x:x[1])[1:11]

    recommended_movie = []
    recommended_movie_posters = []

    for i in similar_movie:
        movie_id = movies.iloc[i[0]].movie_id

        recommended_movie.append(movies.iloc[i[0]]['title'])
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie , recommended_movie_posters  

st.title("Movie Recommender System")

selected_movie = st.selectbox("Select a movie to get recommendation",movie_list)

if st.button("Show recommendation"):
    st.write("Top 10 similar movies:")

    names, posters = recommend(selected_movie)
    cols = st.columns(10)
    
    for i in range(len(names)):
        with cols[i]:
            st.write(names[i])
            st.image(posters[i])
            
