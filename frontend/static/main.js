// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.innerHTML = `
                <h2>${post.title}</h2>
                <h3>${post.author}</h3>
                <p>${post.content}</p>
                <p>Posted: ${post.date}</p>
                <button class="delete-button" onclick="deletePost(${post.id})">Delete</button>
                <button class="update-button" onclick="enterEditMode(${post.id}, '${post.title}', '${post.author}', '${post.content}', '${post.date}')">Update</button>
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent, author: postAuthor })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}


function enterEditMode(postId, title, author, content, date) {
    // Get the specific post element
    const postDiv = document.querySelector(`.post button.update-button[onclick="enterEditMode(${postId}, '${title}', '${author}', '${content}', '${date}')"]`).parentElement;

    // Add the `post-edit-mode` class to the container for styling
    postDiv.classList.add('post-edit-mode');

    // Replace the post display with editable fields
    postDiv.innerHTML = `
        <input type="text" id="edit-title-${postId}" value="${title}" placeholder="Edit Title">
        <input type="text" id="edit-author-${postId}" value="${author}" placeholder="Edit Author">
        <textarea id="edit-content-${postId}" placeholder="Edit Content">${content}</textarea>
        <button class="save-button" onclick="savePost(${postId})">Save</button>
        <button class="cancel-button" onclick="cancelEdit(${postId}, '${title}', '${author}', '${content}', '${date}')">Cancel</button>
    `;
}


function savePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;
    const postTitle = document.getElementById(`edit-title-${postId}`).value;
    const postAuthor = document.getElementById(`edit-author-${postId}`).value;
    const postContent = document.getElementById(`edit-content-${postId}`).value;


    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent, author: postAuthor })
    })
    .then(response => response.json()
    .then(post =>{
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error)));  // If an error occurs, log it to the console
}


function cancelEdit(postId, title, author, content, date) {
    // Revert back to the original post display
    const postDiv = document.querySelector(`.post button.save-button[onclick="savePost(${postId})"]`).parentElement;
    postDiv.classList.remove('post-edit-mode')
    postDiv.innerHTML = `
        <h2>${title}</h2>
        <h3>${author}</h3>
        <p>${content}</p>
        <p>Posted: ${date}</p>
        <button class="delete-button" onclick="deletePost(${postId})">Delete</button>
        <button class="update-button" onclick="enterEditMode(${postId}, '${title}', '${author}', '${content}', '${date}')">Update</button>
    `;
}