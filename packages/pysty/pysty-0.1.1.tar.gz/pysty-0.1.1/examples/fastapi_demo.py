"""Example FastAPI application documenting Pysty components.

This application demonstrates how to build a documentation site using
Pysty components. It uses the ``DefaultCard`` and ``DefaultButton``
components defined in the ``pysty`` package. Sections are composed
dynamically and rendered into a simple HTML shell.

Run this app with ``uvicorn fastapi_demo:app --reload`` and visit
``http://localhost:8000/`` to view the documentation.
"""

from __future__ import annotations

import random
from typing import Callable

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pysty as ps

# Create FastAPI app
app = FastAPI()


# --------------------------------------------------------------------
# Page wrapper
# --------------------------------------------------------------------
def page(content: str) -> str:
    """Wrap the given content in a basic HTML layout.

    The page includes TailwindCSS and HTMX via CDN. Content is
    inserted inside a centered container with some padding.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Pysty Demo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    </head>
    <body class="bg-gray-50 text-gray-900">
        <div class="max-w-6xl mx-auto px-6 py-16">
            {content}
        </div>
    </body>
    </html>
    """


# --------------------------------------------------------------------
# Documentation section helper
# --------------------------------------------------------------------
def doc_section(title: str, description: str, preview: str, code: str) -> str:
    """Render a documentation section.

    Each section consists of a heading, a description, a preview of the
    rendered component(s), and the source code used to create the preview.
    """
    return f"""
    <section class="mb-24">
        <h2 class="text-3xl font-bold mb-2">{title}</h2>
        <p class="text-gray-600 mb-8 max-w-3xl">{description}</p>
        <div class="bg-white border border-gray-200 rounded-xl p-10 mb-8">
            {preview}
        </div>
        <pre class="bg-slate-900 text-slate-100 text-sm rounded-xl p-6 overflow-x-auto">
{code}
        </pre>
    </section>
    """


# --------------------------------------------------------------------
# Home route
# --------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Render the home page with documentation sections."""
    content = (
        """
        <h1 class="text-4xl font-bold text-center mb-3">Pysty Components</h1>
        <p class="text-gray-600 text-center mb-20 max-w-2xl mx-auto">
            A Python-first UI component system built around explicit configuration,
            strong typing, and composable server-driven interaction.
        </p>
        """
        + cards_section()
        + button_section()
    )
    return HTMLResponse(page(content))


# --------------------------------------------------------------------
# Section: Cards
# --------------------------------------------------------------------
def cards_section() -> str:
    """Demonstrate static and interactive cards."""
    # Static card
    static_card = ps.DefaultCard(
        title="Static Card",
        content="A simple card with a title and description.",
    ).render()

    # Interactive card that refreshes on click
    interactive_card = ps.DefaultCard(
        title="Interactive Card",
        content="Click this card to refresh.",
        hx_get="/card/refresh",
        hx_trigger="click",
        hx_swap="outerHTML",
    ).render()

    preview = f"""
    <div class="flex flex-wrap gap-6">
        {static_card}
        {interactive_card}
    </div>
    """

    code = """ps.DefaultCard(
    title="Interactive Card",
    content="Click this card to refresh.",
    hx_get="/card/refresh",
    hx_trigger="click",
    hx_swap="outerHTML",
)
"""

    return doc_section(
        "Cards",
        "Cards can be static or interactive without changing their API.",
        preview,
        code,
    )


# Endpoint to refresh the interactive card
@app.get("/card/refresh", response_class=HTMLResponse)
def refresh_card() -> str:
    """Return a card with a random value to demonstrate interactivity."""
    return ps.DefaultCard(
        title="Updated!",
        content=f"Random value: {random.randint(1, 100)}",
        hx_get="/card/refresh",
        hx_trigger="click",
        hx_swap="outerHTML",
    ).render()


# --------------------------------------------------------------------
# Section: Buttons
# --------------------------------------------------------------------
def button_section() -> str:
    """Showcase buttons with preset variants and custom classes."""
    preview = f"""
    <div class="flex flex-wrap gap-3 mb-6">
        {ps.DefaultButton(label="Default").render()}
        {ps.DefaultButton(label="Success", variant="success").render()}
        {ps.DefaultButton(label="Warning", variant="warning").render()}

        {ps.DefaultButton(label="Danger", variant="danger").render()}
        {ps.DefaultButton(label="Ghost", variant="ghost").render()}
    </div>
    <div class="flex flex-wrap gap-3">
        {ps.DefaultButton(
            label="Gradient",
            variant="bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:opacity-90",
        ).render()}
        {ps.DefaultButton(
            label="Outline",
            variant="bg-transparent border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white",
        ).render()}
    </div>
    """

    code = """ps.DefaultButton(label="Success", variant="success")

ps.DefaultButton(
    label="Gradient",
    variant="bg-gradient-to-r from-purple-500 to-pink-500 text-white",
)
"""

    return doc_section(
        "Buttons",
        "Buttons support semantic presets or fully custom Tailwind classes.",
        preview,
        code,
    )
