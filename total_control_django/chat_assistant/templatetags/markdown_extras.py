import markdown
import bleach

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def markdownify(text):
    html = markdown.markdown(text, extensions=["nl2br"])
    cleaned = bleach.clean(
        html,
        tags=[
            "p",
            "strong",
            "em",
            "ul",
            "ol",
            "li",
            "a",
            "code",
            "pre",
            "blockquote",
            "br",
            "hr",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ],
        attributes={"a": ["href"]},
    )
    return mark_safe(cleaned)
