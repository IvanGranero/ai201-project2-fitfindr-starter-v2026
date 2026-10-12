"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

from itertools import count
import re
import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable
from trace import start_trace

from trace import step


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


def parse_query(query: str):
    size = None
    max_price = None

    size_match = re.search(r"\b(XXS|XS|S|M|L|XL|XXL)\b", query, re.I)
    if size_match:
        size = size_match.group(1).upper()

    price_match = re.search(r"under\s*\$?(\d+)", query, re.I)
    if price_match:
        max_price = float(price_match.group(1))

    description = query

    if size_match:
        description = description.replace(size_match.group(0), "")

    if price_match:
        description = description.replace(price_match.group(0), "")

    description = description.strip(" ,").lower()

    return description, size, max_price

# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    #1. Start a session with new_session().
    session = new_session(query, wardrobe)

    # 2. Count the times round the loop, and call trace.check_iterations(count)
    # on each one before you go again. It raises when the count passes
    # MAX_ITERATIONS in config.py — see trace.py.
    
    count = 1
    trace.check_iterations(count)

    trace.start_trace()



   
    description, size, max_price = parse_query(query)

    trace.step("parse_query", inputs={"query": query}, returned={"description": description, "size": size, "max_price": max_price})


    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # 4. Search

    results = call_tool("search_listings", {
        "description": description,
        "size": size,
        "max_price": max_price,
    })
    trace.step("search_listings (via MCP)", inputs={"description": description, "max_price": max_price}, returned=results)
    
    session["search_results"] = results

    # BRANCH
    if not results:
        session["error"] = (
            "No matching listings were found. "
            "Try changing the keywords, size, or price limit."
        )
        return session

    # 5. Select first result
    selected_item = results[0]
    session["selected_item"] = selected_item

    # 6. Outfit suggestion
    outfit = suggest_outfit(selected_item, wardrobe)
    session["outfit_suggestion"] = outfit
    trace.step("suggest_outfit", inputs={"selected_item": selected_item, "wardrobe": wardrobe}, returned=outfit)

    # 7. Fit card
    fit_card = create_fit_card(outfit, selected_item)
    session["fit_card"] = fit_card
    trace.step("create_fit_card", inputs={"outfit": outfit, "selected_item": selected_item}, returned=fit_card)

    
    # 8. Return completed session
    trace.get_trace()
    return session

    
    """
    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """



    # TODO: delete these two lines and build the loop.
    session["error"] = "The planning loop isn't built yet — see the TODO in agent.py."
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
