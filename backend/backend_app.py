from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
import json


JSON_PATH = 'posts.json'

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL = "/api/docs"  # (1) Swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/masterblog.json"  # (2) Ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'  # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


def load_data():
    """
    Load data from the JSON file specified by JSON_PATH.

    Returns:
        list: A list of posts if the file exists and contains valid JSON.
        dict: An empty list if the file is missing, empty, or corrupted.
    """
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as file:
            print(f"Data successfully read from {JSON_PATH}.")
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {JSON_PATH}. Creating a new empty database.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. The file might be empty or corrupted.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return []


def get_data():
    """
    Provide cached access to the data from the JSON file.
    Loads data from the file if it is not already cached.

    Returns:
        list: The cached data loaded from the JSON file.
    """
    if not hasattr(get_data, "_cache"):
        get_data._cache = load_data()
    return get_data._cache


def save_data(data):
    """
    Save the provided data to the JSON file specified by JSON_PATH.

    Args:
        data (list): The list of posts to save.

    Returns:
        None
    """
    try:
        with open(JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
            print(f"Data successfully saved to {JSON_PATH}.")
    except Exception as e:
        print(f"Error: An unexpected error occurred while saving data: {e}")


def fetch_post(id):
    """
    Retrieve a post by its ID.

    Args:
        id (int): The ID of the post to fetch.

    Returns:
        dict: The post with the specified ID, or None if not found.
    """
    data = get_data()
    return next((post for post in data if post['id'] == id), None)


@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    """
    Handle GET and POST requests for blog posts.

    GET:
        Retrieve a list of posts, optionally sorted by a specified field and direction.

        Query Parameters:
            - sort (str): Field to sort by ('id', 'title', 'content', 'author', 'date').
            - direction (str): Sort direction ('asc' or 'desc').

    POST:
        Create a new post with the provided title, content, and author.

        Request Body:
            - title (str): The title of the post.
            - content (str): The content of the post.
            - author (str): The author of the post.

    Returns:
        - 200: A list of posts (GET).
        - 201: The newly created post (POST).
        - 400: Validation error or invalid sort field.
    """
    data = get_data()
    if request.method == 'POST':
        post_data = request.get_json()

        if (not post_data or not post_data.get('title') or not post_data.get('content')
                or not post_data.get('author')):
            return jsonify({"error": "All the fields 'title', 'content' and 'author' are required."}), 400

        new_post = {
            'id': max((post['id'] for post in data), default=0) + 1,
            'title': post_data['title'],
            'content': post_data['content'],
            'author': post_data['author'],
            'date': datetime.now().strftime('%Y-%m-%d'),
        }
        data.append(new_post)
        save_data(data)
        return jsonify({"message": "Post created", "post": new_post}), 201

    elif request.method == 'GET':
        sort = request.args.get('sort', '').strip().lower()
        reverse_direction = request.args.get('direction', '').strip().lower() == 'desc'

        if sort in ['id', 'title', 'content', 'author', 'date']:
            try:
                sorted_posts = sorted(
                    data,
                    key=lambda post: post[sort].lower()
                    if isinstance(post[sort], str) else post[sort],
                    reverse=reverse_direction
                )
                return jsonify(sorted_posts), 200
            except KeyError:
                return jsonify({"error": f"Invalid sort field: {sort}"}), 400

    return jsonify(data), 200


@app.route('/api/posts/<int:id>', methods=['DELETE', 'PUT'])
def handle_post(id):
    """
    Handle DELETE and PUT requests for a specific blog post.

    DELETE:
        Remove the post with the specified ID.

    PUT:
        Update the fields of the post with the specified ID.

        Request Body:
            - title (str): Updated title of the post.
            - content (str): Updated content of the post.
            - author (str): Updated author of the post.

    Args:
        id (int): The ID of the post to handle.

    Returns:
        - 200: Success message or updated post data.
        - 400: Validation error or invalid input.
        - 404: Post not found.
    """
    data = get_data()
    post = fetch_post(id)
    if not post:
        return jsonify({"error": "Post ID not found"}), 404

    if request.method == 'DELETE':
        data.remove(post)
        save_data(data)
        return jsonify({"message": f"Post with ID {id} has been deleted successfully."}), 200

    if request.method == 'PUT':
        new_post = request.get_json()
        if not new_post:
            return jsonify({"error": "No data provided"}), 400

        post.update({key: value for key, value in new_post.items() if key and value})
        save_data(data)
        return jsonify({"message": "Post updated", "post": post}), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts based on query parameters.

    Query Parameters:
        - title (str): Search term for the post title.
        - content (str): Search term for the post content.
        - author (str): Search term for the post author.
        - date (str): Search term for the post date (YYYY-MM-DD).

    Returns:
        - 200: A list of posts matching the search criteria.
    """
    data = get_data()
    query_params = {
        'title': request.args.get('title', '').lower(),
        'content': request.args.get('content', '').lower(),
        'author': request.args.get('author', '').lower(),
        'date': request.args.get('date', '').lower()
    }

    if not any(query_params.values()):
        return jsonify(data), 200

    results = [
        post for post in data
        if (
                (query_params['title'] and query_params['title'] in post['title'].lower()) or
                (query_params['content'] and query_params['content'] in post['content'].lower()) or
                (query_params['author'] and query_params['author'] in post['author'].lower()) or
                (query_params['date'] and query_params['date'] in post['date'].lower())
        )
    ]

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)