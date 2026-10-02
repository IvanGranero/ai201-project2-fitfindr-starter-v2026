# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I chose 4 of 5 rather than 5 of 5 because the search tool uses keyword matching and some user phrasings may not overlap well with the listing text. A successful end-to-end run should happen most of the time, but requiring perfection would be unrealistic given the search method.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because this branch depends only on checking whether search_listings() returned an empty list. There is no model call involved, so the behavior should be completely deterministic.

---

## 3. Something about state

For 5 of 5 matching queries, the item stored in
`session["selected_item"]` has the same `id` as the `new_item` received by
`suggest_outfit`.
 
**Why this target:**
 
I chose 5 of 5 because passing state correctly is a basic loop responsibility.
If the item changes between tools, outfit recommendations could be generated for
the wrong listing, making all later outputs unreliable.

---

## 4. Something about the fit card

In at least 4 of 5 generated fit cards, the caption mentions the selected
item's price and contains between 2 and 4 sentences.
 
**Why this target:**
 
I chose 4 of 5 because `create_fit_card()` uses a language model and exact
wording is not deterministic. The important requirement is that the caption
contains the key details and stays within the expected length rather than using
the same phrasing every time.

---

## 5. Your choice

For 5 of 5 searches where `max_price` is provided, every listing returned has a
price less than or equal to the specified maximum price.
 
**Why this target:**
 
I chose 5 of 5 because price filtering is a straightforward rule-based filter.
Unlike model output, there is no ambiguity in whether an item's price is above
or below the user's budget.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
