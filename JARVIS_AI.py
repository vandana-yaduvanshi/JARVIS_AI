from flask import Flask, render_template, request
import wikipedia
import sympy as sp
import urllib.parse
from pytube import Search
import time

app = Flask(__name__)

# --- Wikipedia Summary (10 sentences) ---
def get_wikipedia_summary(query):
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return "No relevant Wikipedia pages found."
        page_title = search_results[0]
        return wikipedia.summary(page_title, sentences=10)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Your query is too broad. Try one of these: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find anything on that topic."

# --- Math Solver (Differentiation & Integration) ---
def solve_math(query):
    try:
        x = sp.symbols('x')
        q = query.lower().strip()
        if "differentiate" in q:
            expr = q.replace("differentiate", "").strip()
            result = sp.diff(sp.sympify(expr), x)
            return f"The derivative of {expr} is: {result}"
        elif "integrate" in q:
            expr = q.replace("integrate", "").strip()
            result = sp.integrate(sp.sympify(expr), x)
            return f"The integral of {expr} is: {result} + C"
        else:
            return "I can currently help with differentiation and integration."
    except Exception as e:
        return f"Error: {str(e)}"

# --- Google Search Top 5 Links ---
def get_google_links(query, num=5):
    search_query = urllib.parse.quote(query)
    return [f"https://www.google.com/search?q={search_query}" for _ in range(num)]

# --- YouTube Search Top 5 Videos using pytube ---
def get_youtube_links(query, num=5):
    """
    Returns top `num` YouTube video URLs using pytube.Search.
    """
    query = query.strip()
    if query.startswith("https://www.youtube.com") or query.startswith("https://youtu.be"):
        return [query]  # direct URL

    links = []
    try:
        s = Search(query)
        time.sleep(1)  # allow pytube to fetch results
        for video in s.results[:num]:
            links.append(f"https://www.youtube.com/watch?v={video.video_id}")
    except Exception as e:
        links.append(f"Error fetching YouTube links: {e}")
    return links

# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    links = []
    if request.method == "POST":
        user_query = request.form["query"].strip().lower()

        # Math queries
        if "differentiate" in user_query or "integrate" in user_query:
            result = solve_math(user_query)

        # YouTube queries
        elif "youtube" in user_query:
            topic = user_query.replace("youtube", "").replace("give me links for", "").replace("on youtube", "").strip()
            links = get_youtube_links(topic)
            result = f"Here are top YouTube videos for: {topic}"

        # Google queries
        elif "google" in user_query:
            topic = user_query.replace("google", "").replace("search for", "").replace("on google", "").strip()
            links = get_google_links(topic)
            result = f"Here are Google search results for: {topic}"

        # Default: Wikipedia summary
        else:
            result = get_wikipedia_summary(user_query)

    return render_template("index.html", result=result, links=links)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
