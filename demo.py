"""
demo.py

Interactive demonstration of the FitFindr agent showing all three tools in action
with narration at each step and visible state passing between tools.

Run with:
    python demo.py
"""

from agent import run_agent, _parse_query
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_step(step_num: int, title: str):
    """Print a formatted step header."""
    print(f"\n[STEP {step_num}] {title}")
    print("-" * 70)


def demo_complete_interaction(query: str, wardrobe: dict):
    """
    Demonstrate a complete multi-step interaction with narration
    and visible state passing between tools.
    """
    print_section("FitFindr Agent Demo — Complete Interaction")

    print(f"User Query: \"{query}\"")
    print(f"Wardrobe: {len(wardrobe['items'])} items")

    # ── STEP 1: Parse Query ───────────────────────────────────────────────────
    print_step(1, "Parse User Query")
    print("Agent is extracting search parameters from the natural language query...")
    parsed = _parse_query(query)
    print(f"\n✓ Parsed query:")
    print(f"  • Description: \"{parsed['description']}\"")
    print(f"  • Size: {parsed['size'] or '(not specified)'}")
    print(f"  • Max price: ${parsed['max_price'] if parsed['max_price'] else 'no limit'}")

    # ── STEP 2: Search Listings ───────────────────────────────────────────────
    print_step(2, "Search Listings Tool")
    print(f"Agent calling: search_listings(description=\"{parsed['description']}\", "
          f"size={parsed['size']}, max_price={parsed['max_price']})")
    print("\nSearching database for matching items...")

    search_results = search_listings(
        description=parsed["description"],
        size=parsed.get("size"),
        max_price=parsed.get("max_price"),
    )

    if not search_results:
        print("\n✗ No listings found! Agent would ask user to adjust criteria.")
        return

    print(f"\n✓ Found {len(search_results)} matching listing(s):")
    for i, item in enumerate(search_results, 1):
        print(f"\n  [{i}] {item['title']}")
        print(f"      Price: ${item['price']} | Size: {item['size']} | Condition: {item['condition']}")
        print(f"      Platform: {item['platform']} | Colors: {', '.join(item['colors'])}")

    # ── STEP 3: State Passing ─────────────────────────────────────────────────
    print_step(3, "State Passing: Select Item")
    selected_item = search_results[0]
    print(f"Agent selecting top result to style:")
    print(f"\n📦 STATE PASSED TO NEXT TOOL:")
    print(f"   selected_item = {selected_item['title']} (${selected_item['price']})")
    print(f"   This item is now the 'new_item' for suggest_outfit()")

    # ── STEP 4: Suggest Outfit ────────────────────────────────────────────────
    print_step(4, "Suggest Outfit Tool")
    print(f"Agent calling: suggest_outfit(new_item={selected_item['title']}, wardrobe=...)")
    print(f"\nWardrobe items available to match with:")
    for item in wardrobe['items'][:3]:
        print(f"  • {item['name']} ({item['category']})")
    print(f"  ... and {len(wardrobe['items'])-3} more items")

    print("\nCalling LLM to suggest outfit combinations...")
    outfit_suggestion = suggest_outfit(
        new_item=selected_item,
        wardrobe=wardrobe,
    )

    print(f"\n✓ Outfit suggestion generated:")
    print(f"\n{outfit_suggestion}")

    # ── STEP 5: State Passing ─────────────────────────────────────────────────
    print_step(5, "State Passing: Outfit to Caption")
    print(f"📦 STATE PASSED TO NEXT TOOL:")
    print(f"   outfit = (string from suggest_outfit)")
    print(f"   new_item = {selected_item['title']}")
    print(f"   These are now inputs to create_fit_card()")

    # ── STEP 6: Create Fit Card ───────────────────────────────────────────────
    print_step(6, "Create Fit Card Tool")
    print(f"Agent calling: create_fit_card(outfit=<suggestion>, new_item=<item>)")
    print(f"\nCalling LLM to write a casual Instagram caption...")

    fit_card = create_fit_card(
        outfit=outfit_suggestion,
        new_item=selected_item,
    )

    print(f"\n✓ Fit card caption generated:")
    print(f"\n{fit_card}")

    # ── FINAL OUTPUT ──────────────────────────────────────────────────────────
    print_section("Final Result")
    print(f"🛍️  Item: {selected_item['title']}")
    print(f"💰 Price: ${selected_item['price']}")
    print(f"📍 Platform: {selected_item['platform']}")
    print(f"\n👗 Outfit suggestion:\n{outfit_suggestion}")
    print(f"\n✨ Instagram caption:\n{fit_card}")
    print()


def demo_full_agent():
    """Demonstrate using the full run_agent() function."""
    print_section("FitFindr Agent Demo — Using Full run_agent()")

    query = "looking for a vintage graphic tee under $30, size M"
    wardrobe = get_example_wardrobe()

    session = run_agent(query, wardrobe)

    if session["error"]:
        print(f"❌ Error: {session['error']}")
        return

    print(f"✓ Agent completed successfully!")
    print(f"\nSession state:")
    print(f"  Query: {session['query']}")
    print(f"  Parsed: {session['parsed']}")
    print(f"  Search results: {len(session['search_results'])} items")
    print(f"  Selected item: {session['selected_item']['title']}")
    print(f"  Outfit suggestion: {len(session['outfit_suggestion'])} chars")
    print(f"  Fit card: {len(session['fit_card'])} chars")
    print()


if __name__ == "__main__":
    # Demo 1: Step-by-step breakdown with narration
    demo_complete_interaction(
        query="looking for a vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )

    # Demo 2: Full agent with state summary
    demo_full_agent()

    print("\n✨ Demo complete! Check app.py to try the interactive Gradio interface:\n"
          "   python app.py\n")
