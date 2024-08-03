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


def post_title(f):
    blog_name = stem(f)
    title = blog_file_to_title(blog_name)
    return Div(A(title, href=f"/post/{blog_name}"), id=stem(f))


@rt("/post/{blog_name}")
def get(blog_name: str):
    post = readlines(root / f"{blog_name}.md")
    md = "\n".join(post)
    title = blog_file_to_title(blog_name)
    return Page(H2(title), Div(md, cls="marked"))


def get_posts_for_page(posts: list, page: int, n_posts_per_page: int):
    return list(batchify(posts, batch_size=n_posts_per_page))[page]


@rt("/update_page/{page}")
def post(page: int):
    global current_page
    current_page = page
    current_posts = get_posts_for_page(posts, current_page, n_posts_per_page)
    btns = buttons(current_page)
    return Div(Ul(*current_posts), btns, id="on-screen")


get_posts = post  # fmt: ignore


def _make_buttons(pages, primary_page=None):
    return Div(
        *[
            (
                Button(
                    page + 1,
                    hx_post=f"/update_page/{page}",
                    target_id="on-screen",
                    hx_swap="outerHTML",
                    style="background-color: orange" if page == primary_page else None,
                )
                if isinstance(page, int)
                else "🦋"
            )
            for page in pages
        ]
    )


@rt("/show_buttons/{page}")
def buttons(page: int):
    global n_pages
    if n_pages < 5:
        return _make_buttons(pages=range(n_pages), primary_page=page)
    if page in list(range(3)):
        return _make_buttons(pages=[0, 1, 2, 3, None, n_pages - 1], primary_page=page)
    elif page in list(range(n_pages - 3, n_pages)):
        return _make_buttons(
            pages=[0, None, n_pages - 4, n_pages - 3, n_pages - 2, n_pages - 1],
            primary_page=page,
        )
    else:
        return _make_buttons(
            pages=[0, None, page - 1, page, page + 1, None, n_pages - 1],
            primary_page=page,
        )


blog_title = "BLOG"
current_page = 0
posts = [Li(post_title(f)) for f in sorted(root.Glob("*.md"), reverse=True)] * 1
n_posts_per_page = 8
n_pages = len(posts) // n_posts_per_page
if len(posts) % n_posts_per_page != 0:
    n_pages += 1


@rt("/")
def get():
    return Titled(blog_title, Page(get_posts(current_page)))


@rt("/page/{ix}")
def get(ix: int): ...


serve(reload=True)
