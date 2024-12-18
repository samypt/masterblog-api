from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def fetch_post(id):
    return next((post for post in POSTS if post['id'] == id), None)


@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.get_json()

        # Validate the presence of 'title' and 'content'
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({"error": "Both 'title' and 'content' are required."}), 400

        new_post = {
            'id': max(post['id'] for post in POSTS) + 1,  # Find the next available ID
            'title': data['title'],
            'content': data['content'],
        }
        POSTS.append(new_post)
        return jsonify({"message": "Post created", "post": new_post}), 201

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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

