import os
from flask import Blueprint, session, render_template, flash, redirect, request, url_for
from slugify import slugify
from uuid import uuid4
from PIL import Image

from settings import BLOG_POST_IMAGES_PATH
from application import db
from blog.models import Post
from comment.models import Comment
from tag.models import Tag
from category.models import Category
from author.models import Author
from blog.forms import PostForm
from author.decorators import login_required
from settings import POSTS_PER_PAGE

blog_app = Blueprint('blog_app', __name__)


@blog_app.route('/')
def index():
    page = int(request.values.get('page', '1'))
    posts = Post.query.filter_by(live=True).order_by(Post.publish_date.desc()).paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('blog/index.html', posts=posts, title='Latest Posts')


@blog_app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    tags_field = request.values.get('tags_field', '')

    if form.validate_on_submit():
        image_id = None

        if form.image.data:
            image_data = form.image.data
            image_id = str(uuid4())
            file_name = image_id + '.png'
            file_path = os.path.join(BLOG_POST_IMAGES_PATH, file_name)
            Image.open(image_data).save(file_path)
            _resize_image(BLOG_POST_IMAGES_PATH, image_id, 600, 'lg')
            _resize_image(BLOG_POST_IMAGES_PATH, image_id, 300, 'sm')

        if form.new_category.data:
            new_category = Category(form.new_category.data)
            db.session.add(new_category)
            db.session.flush()
            category = new_category
        else:
            category = form.category.data

        author = Author.query.get(session['id'])
        title = form.title.data.strip()
        body = form.body.data.strip()
        blog_post = Post(author=author, title=title, body=body, image=image_id, category=category)
        db.session.add(blog_post)
        _save_tags(blog_post, tags_field)
        db.session.commit()

        blog_post.slug = f'{blog_post.id}/{slugify(blog_post.title)}'
        db.session.commit()

        flash(f'"{blog_post.title}" posted.')
        return redirect(url_for('.article', slug=blog_post.slug))
    return render_template('blog/post.html', form=form, action='new', tags_field=tags_field)


@blog_app.route('/posts/<path:slug>')
def article(slug):
    blog_post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('blog/article.html', post=blog_post)


@blog_app.route('/posts/<path:slug>/edit', methods=['GET', 'POST'])
@login_required
def edit(slug):
    blog_post = Post.query.filter_by(slug=slug).first_or_404()
    form = PostForm(obj=blog_post)
    tags_field = request.values.get('tags_field', _load_tags_field(blog_post))

    if form.validate_on_submit():
        original_image = blog_post.image
        original_title = blog_post.title
        form.populate_obj(blog_post)

        if form.image.data:
            image_data = form.image.data
            image_id = str(uuid4())
            file_path = os.path.join(BLOG_POST_IMAGES_PATH, f'{image_id}.png')
            Image.open(image_data).save(file_path)

            _resize_image(BLOG_POST_IMAGES_PATH, image_id, 600, 'lg')
            _resize_image(BLOG_POST_IMAGES_PATH, image_id, 300, 'sm')

            blog_post.image = image_id
        else:
            blog_post.image = original_image

        if form.new_category.data:
            new_category = Category(form.new_category.data)
            db.session.add(new_category)
            db.session.flush()
            blog_post.category = new_category

        if form.title.data != original_title:
            blog_post.slug = f'{blog_post.id}/{slugify(form.title.data)}'

        _save_tags(blog_post, tags_field)

        db.session.commit()
        flash(f'Your changes to "{blog_post.title}" have been saved.')
        return redirect(url_for('.article', slug=blog_post.slug))

    return render_template('blog/post.html', form=form, post=blog_post, action='edit', tags_field=tags_field)


@blog_app.route('/posts/<path:slug>/delete')
@login_required
def delete(slug):
    blog_post = Post.query.filter_by(slug=slug).first_or_404()
    blog_post.live = False
    db.session.commit()
    flash(f'"{blog_post.title}" has been deactivated.')
    return redirect(url_for('.index'))


@blog_app.route('/categories/<category_id>')
def list_category(category_id):
    category = Category.query.filter_by(id=category_id).first_or_404()
    page = int(request.values.get('page', '1'))
    posts = category.posts.filter_by(live=True)\
        .order_by(Post.publish_date.desc())\
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('blog/category_posts.html', posts=posts, title=category, category_id=category_id)


@blog_app.route('/tags/<tag>')
def list_tag(tag):
    tag = Tag.query.filter_by(name=tag).first_or_404()
    page = int(request.values.get('page', '1'))
    posts = tag.posts.filter_by(live=True)\
        .order_by(Post.publish_date.desc())\
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('blog/tag_posts.html', posts=posts, title=f'Tag: {tag}', tag=str(tag))


def _resize_image(original_file_path, image_id, image_base, extension):
    file_path = os.path.join(original_file_path, f'{image_id}.png')
    image = Image.open(file_path)
    width_percent = (image_base / float(image.size[0]))
    height = int(float(image.size[1]) * float(width_percent))
    image = image.resize((image_base, height), Image.ANTIALIAS)
    modified_file_path = os.path.join(original_file_path, f'{image_id}.{extension}.png')
    image.save(modified_file_path)


def _save_tags(blog_post, tags_field):
    blog_post.tags.clear()
    for tag_item in tags_field.split(','):
        slug = slugify(tag_item)
        tag = Tag.query.filter_by(name=slug).first()
        if not tag:
            tag = Tag(name=slug)
            db.session.add(tag)
        blog_post.tags.append(tag)
    return blog_post


def _load_tags_field(blog_post):
    tags = [tag.name for tag in blog_post.tags]
    return ', '.join(tags)
