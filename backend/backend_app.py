from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


def fetch_post(id):
    return next((post for post in POSTS if post['id'] == id), None)


@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.get_json()

        # Validate the presence of 'title' and 'content'
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({"error": "Both 'title' and 'content' are required."}), 400

        # Create a new post with the next available ID
        new_post = {
            'id': max((post['id'] for post in POSTS), default=0) + 1,
            'title': data['title'],
            'content': data['content'],
        }
        POSTS.append(new_post)
        return jsonify({"message": "Post created", "post": new_post}), 201

    elif request.method == 'GET':
        # Get query parameters for sorting
        sort = request.args.get('sort', '').strip().lower()
        reverse_direction = request.args.get('direction', '').strip().lower() == 'desc'

        # Sort only if the 'sort' field is valid
        if sort in ['id', 'title', 'content']:
            try:
                sorted_posts = sorted(
                    POSTS,
                    key=lambda post: post[sort].lower()
                    if isinstance(post[sort], str) else post[sort],
                    reverse=reverse_direction
                )
                return jsonify(sorted_posts), 200
            except KeyError:
                return jsonify({"error": f"Invalid sort field: {sort}"}), 400

    # Default: Return all posts
    return jsonify(POSTS), 200


@app.route('/api/posts/<int:id>', methods=['DELETE', 'PUT'])
def handle_post(id):
    post = fetch_post(id)
    if not post:
        return jsonify({"error": "Post ID not found"}), 404

    if request.method == 'DELETE':
        POSTS.remove(post)
        return jsonify({"message": f"Post with ID {id} has been deleted successfully."}), 200

    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update only non-None, valid fields
        post.update({key: value for key, value in data.items() if key and value})
        return jsonify({"message": "Post updated", "post": post}), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Get the search term from query parameters
    title = request.args.get('title', '').lower()
    content = request.args.get('content', '').lower()

    # If no query is provided, return all posts
    if not title and not content:
        return jsonify(POSTS), 200

    # Filter posts by title or content matching the query
    results = [
        post for post in POSTS
            if (title and title in post['title'].lower())
               or (content and content in post['content'].lower())
    ]

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

