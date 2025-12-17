# Pysty

**Pysty** is a Python‑first UI component system for building modern web interfaces using **FastAPI**, **Pydantic**, **Dominate**, **TailwindCSS**, and optional **HTMX** — without writing JavaScript.

Pysty components are:

* Strongly typed (Pydantic models)
* Server‑rendered HTML
* HTMX‑ready by default
* Explicit and composable

This document shows how to **use Pysty**, **render components**, and **build a documentation site** using FastAPI.

---

## Installation

```bash
pip install pysty
```

or

```bash
uv add pysty
```

---

## Core Idea

Pysty components are **Python objects** that:

1. Accept configuration via typed fields
2. Compile into HTML using `render()`
3. Can optionally include HTMX attributes

No client‑side framework is required.

---

## Minimal Example

```python
import pysty as ps

card = ps.DefaultCard(
    title="Hello",
    content="This is a Pysty card",
)

html = card.render()
```

`render()` returns a **safe HTML string** that can be returned directly from FastAPI.

---

## Using Pysty with FastAPI

Below is a **complete example** showing how to build a small documentation site using Pysty.

### File: `fastapi_demo.py`

```python
"""Example FastAPI application Pysty components.

"""

from __future__ import annotations

import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pysty as ps

app = FastAPI()


def page(content: str) -> str:
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


def doc_section(title: str, description: str, preview: str, code: str) -> str:
    return f"""
    <section class="mb-24">
        <h2 class="text-3xl font-bold mb-2">{title}</h2>
        <p class="text-gray-600 mb-8 max-w-3xl">{description}</p>
        <div class="bg-white border border-gray-200 rounded-xl p-10 mb-8">
            {preview}
        </div>
        <pre class="bg-slate-900 text-slate-100 text-sm rounded-xl p-6 overflow-x-auto">{code}</pre>
    </section>
    """


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
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


# --------------------
# Cards Section
# --------------------

def cards_section() -> str:
    static_card = ps.DefaultCard(
        title="Static Card",
        content="A simple card with a title and description.",
    ).render()

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


@app.get("/card/refresh", response_class=HTMLResponse)
def refresh_card() -> str:
    return ps.DefaultCard(
        title="Updated!",
        content=f"Random value: {random.randint(1, 100)}",
        hx_get="/card/refresh",
        hx_trigger="click",
        hx_swap="outerHTML",
    ).render()


# --------------------
# Buttons Section
# --------------------

def button_section() -> str:
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
            variant="bg-gradient-to-r from-purple-500 to-pink-500 text-white",
        ).render()}
        {ps.DefaultButton(
            label="Outline",
            variant="bg-transparent border-2 border-blue-600 text-blue-600",
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
```

---

## HTMX Support (Optional)

Pysty does **not require HTMX**, but supports it natively.

You can pass any `hx_*` attribute directly to a component:

```python
ps.DefaultCard(
    title="Live",
    content="Click to refresh",
    hx_get="/refresh",
    hx_trigger="click",
    hx_swap="outerHTML",
)
```

Pysty treats HTMX attributes as first‑class configuration, not string hacks.

---

## Design Philosophy

* Python is the source of truth
* No client‑side state framework
* Explicit configuration over magic
* Tailwind classes stay visible
* Components are data, not templates

---

## Roadmap (Intentional)

* More base components (Table, Navbar, Modal)
* Theme abstraction layer
* JSON / schema export for tooling
* Optional state helpers

---


## Summary

If you know **FastAPI + Python**, you already know Pysty.

No JSX. No build step. No framework lock‑in.
