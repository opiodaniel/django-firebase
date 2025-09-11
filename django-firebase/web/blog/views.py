from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
# This line correctly imports the 'db' object using the absolute path from the project root.
from djangofirebase.settings import db
from firebase_admin import firestore

def post_list(request):
    """
    Retrieves and displays a list of all blog posts from Firestore.
    """
    posts_ref = db.collection('posts').order_by('created_at', direction=firestore.Query.DESCENDING)
    docs = posts_ref.stream()
    posts = []
    for doc in docs:
        post_data = doc.to_dict()
        post_data['id'] = doc.id
        # Format the timestamp here in the view
        if post_data.get('created_at'):
            post_data['created_at_formatted'] = post_data['created_at'].strftime("%Y-%m-%d %H:%M")
        else:
            post_data['created_at_formatted'] = 'N/A'
        posts.append(post_data)
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, post_id):
    """
    Retrieves and displays a single blog post.
    """
    post_ref = db.collection('posts').document(post_id)
    post_doc = post_ref.get()

    if not post_doc.exists:
        return HttpResponseNotFound("Post not found.")

    post = post_doc.to_dict()
    post['id'] = post_doc.id
    if post.get('created_at'):
        post['created_at_formatted'] = post['created_at'].strftime("%Y-%m-%d %H:%M")
    else:
        post['created_at_formatted'] = 'N/A'
    return render(request, 'blog/post_detail.html', {'post': post})


def post_create(request):
    """
    Handles the creation of a new blog post.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author')

        # Add a new document with an auto-generated ID
        db.collection('posts').add({
            'title': title,
            'content': content,
            'author': author,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return redirect('post_list')

    return render(request, 'blog/post_form.html', {'form_title': 'Create New Post'})

def post_update(request, post_id):
    """
    Handles the updating of an existing blog post.
    """
    post_ref = db.collection('posts').document(post_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author')

        # Update the document
        post_ref.update({
            'title': title,
            'content': content,
            'author': author
        })
        return redirect('post_list')

    post_doc = post_ref.get()
    if not post_doc.exists:
        return HttpResponseNotFound("Post not found.")

    post = post_doc.to_dict()
    post['id'] = post_doc.id
    return render(request, 'blog/post_form.html', {'form_title': 'Update Post', 'post': post})

def post_delete(request, post_id):
    """
    Deletes a specific blog post.
    """
    db.collection('posts').document(post_id).delete()
    return redirect('post_list')
