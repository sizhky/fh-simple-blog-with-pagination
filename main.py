#! python
from fasthtml.common import *
from torch_snippets import *

app, rt = fast_app(hdrs=[MarkdownJS()])
root = P("posts")


def blog_file_to_title(blog_name):
    title = " ".join(blog_name.split("-")[1:]).title()
    return title


def Navbar():
    return Div(
        P("-" * 60),
        Div(A("Home", href="/"), A("Hello", href="https://www.twitter.com/sizhky")),
        P("-" * 60),
    )


def Page(*ele):
    return Div(Navbar(), *ele)


def blog_title(f):
    blog_name = stem(f)
    title = blog_file_to_title(blog_name)
    return Div(A(title, href=f"/post/{blog_name}"), id=stem(f))


@rt("/post/{blog_name}")
def get(blog_name: str):
    post = readlines(root / f"{blog_name}.md")
    md = "\n".join(post)
    title = blog_file_to_title(blog_name)
    return Titled("YYR", Page(H2(title), Div(md, cls="marked")))


def get_posts_for_page(posts: list, page: int, n_posts_per_page: int):
    return list(batchify(posts, batch_size=n_posts_per_page))[page]


@rt("/update_page/{page}")
def post(page: int):
    global current_page
    current_page = page
    current_posts = get_posts_for_page(posts, current_page, n_posts_per_page)
    return Ul(*current_posts, id="on-screen")


get_posts = post

current_page = 0
posts = [Li(blog_title(f)) for f in sorted(root.Glob("*.md"), reverse=True)] * 10
n_posts_per_page = 8
n_pages = len(posts) // n_posts_per_page
if len(posts) % n_posts_per_page != 0:
    n_pages += 1


@rt("/")
def get():
    btns = [
        Button(
            page,
            hx_post=f"/update_page/{page}",
            target_id="on-screen",
            hx_swap="outerHTML",
        )
        for page in range(n_pages)
    ]
    return Titled("YYR", Page(get_posts(current_page), *btns))


@rt("/page/{ix}")
def get(ix: int): ...


serve(reload=True)
