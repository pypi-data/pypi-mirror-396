"""Pagination pattern demo - Navigation between pages with automatic route generation."""

from demo import *

# Sample data for demonstration
TOTAL_ITEMS = 100

def load_demo_items(request):
    """Load all items - filtered by example parameter."""
    example = request.query_params.get("example", "1") if request else "1"
    # For demo, generate 100 items for each example
    return [f"Item {i}" for i in range(1, TOTAL_ITEMS + 1)]


def render_example1_items(items, page, request):
    """Render items for Example 1 (grid view)."""
    total_items = TOTAL_ITEMS
    items_per_page = 10
    start_idx = (page - 1) * items_per_page + 1
    end_idx = start_idx + len(items) - 1

    return Div(
        # Header
        Div(
            H3("Item List", cls=combine_classes(font_weight.semibold, m.b(2))),
            P(f"Showing items {start_idx}-{end_idx} of {total_items}",
              cls=combine_classes(m.b(4))),
            cls=combine_classes(card_body, bg_dui.base_200)
        ),

        # Items grid
        Div(
            *[
                Div(
                    Div(
                        H4(f"Item #{start_idx + idx}", cls=combine_classes(font_weight.bold, m.b(2))),
                        P(f"This is item number {start_idx + idx} in the list.", cls=combine_classes(m.b(2))),
                        P(f"Page {page}", cls=combine_classes(font_size.sm)),
                        cls=combine_classes(card_body)
                    ),
                    cls=combine_classes(card, bg_dui.base_100)
                )
                for idx, item in enumerate(items)
            ],
            cls=combine_classes(grid_display, grid_cols._1, grid_cols._2.md, grid_cols._3.lg, gap._4)
        )
    )


def render_example2_items(items, page, request):
    """Render items for Example 2 (compact pagination)."""
    return Div(
        H3("Results List", cls=combine_classes(font_weight.semibold, m.b(4))),
        Ul(
            *[Li(f"{item} (Page {page})", cls=str(m.b(2))) for item in items[:5]],
            cls=combine_classes(m.l(6))
        ),
        cls=combine_classes(card_body)
    )


def render_example3_items(items, page, request):
    """Render items for Example 3 (custom styling)."""
    return Div(
        H3("Search Results", cls=combine_classes(font_weight.semibold, m.b(2))),
        P(f"Custom button text and smaller size (Page {page})", cls=combine_classes(m.b(4))),
        cls=combine_classes(card_body)
    )


def render_example4_items(items, page, request):
    """Render items for Example 4 (with First/Last buttons)."""
    total_items = TOTAL_ITEMS
    items_per_page = 10
    start_idx = (page - 1) * items_per_page + 1
    end_idx = start_idx + len(items) - 1

    return Div(
        H3("Large Dataset", cls=combine_classes(font_weight.semibold, m.b(2))),
        P(f"Showing items {start_idx}-{end_idx} of {total_items}", cls=combine_classes(m.b(4))),
        P("With First/Last buttons for quick navigation", cls=combine_classes(m.b(4))),
        Ul(
            *[Li(f"{item} (Page {page})", cls=str(m.b(2))) for item in items[:5]],
            cls=combine_classes(m.l(6))
        ),
        cls=combine_classes(card_body)
    )


# Create pagination instances for each example
example1_pagination = Pagination(
    pagination_id="example1",
    data_loader=load_demo_items,
    render_items=render_example1_items,
    items_per_page=10,
    preserve_params=["example"],
    push_url=False
)

example2_pagination = Pagination(
    pagination_id="example2",
    data_loader=load_demo_items,
    render_items=render_example2_items,
    items_per_page=10,
    style=PaginationStyle.COMPACT,
    preserve_params=["example"],
    push_url=False
)

example3_pagination = Pagination(
    pagination_id="example3",
    data_loader=load_demo_items,
    render_items=render_example3_items,
    items_per_page=10,
    prev_text="← Back",
    next_text="Forward →",
    button_size=str(btn_sizes.sm),
    page_info_format="{current}/{total}",
    preserve_params=["example"],
    push_url=False
)

example4_pagination = Pagination(
    pagination_id="example4",
    data_loader=load_demo_items,
    render_items=render_example4_items,
    items_per_page=10,
    show_endpoints=True,
    preserve_params=["example"],
    push_url=False
)

# Create routers for each example
example1_router = example1_pagination.create_router(prefix="/pagination_demo/example1")
example2_router = example2_pagination.create_router(prefix="/pagination_demo/example2")
example3_router = example3_pagination.create_router(prefix="/pagination_demo/example3")
example4_router = example4_pagination.create_router(prefix="/pagination_demo/example4")

# Create APIRouter for main demo page
pagination_ar = APIRouter(prefix="/pagination_demo")


@pagination_ar
def index(request):
    """Pagination pattern demo page."""

    def pagination_content():
        return Div(
            H1("Pagination Pattern",
               cls=combine_classes(font_size._3xl, font_weight.bold, m.b(6), text_align.center)),

            P("The Pagination pattern provides automatic route generation and state management for paginated content.",
              cls=combine_classes(text_align.center, m.b(8), max_w._3xl, m.x.auto)),

            # Example 1: Simple pagination with paginated content
            Div(
                H2("Example 1: Simple Pagination",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Default pagination style with page info display",
                  cls=combine_classes(m.b(4))),

                # Content container that gets updated
                Div(
                    # Placeholder - will be replaced by HTMX
                    Div(
                        P("Loading...", cls=combine_classes(text_align.center, p(4))),
                        cls=combine_classes(card, bg_dui.base_100, p(6))
                    ),
                    hx_get=example1_router.content.to(page=1, example="1"),
                    hx_trigger="load",
                    hx_target="this",
                    hx_swap="outerHTML",
                    id=example1_pagination.content_id
                ),
                cls=str(m.b(8))
            ),

            # Example 2: Compact pagination
            Div(
                H2("Example 2: Compact Pagination",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Compact style without page info (Previous/Next only)",
                  cls=combine_classes(m.b(4))),

                Div(
                    # Placeholder - will be replaced by HTMX
                    Div(
                        P("Loading...", cls=combine_classes(text_align.center, p(4))),
                        cls=combine_classes(card, bg_dui.base_100, p(6))
                    ),
                    hx_get=example2_router.content.to(page=1, example="2"),
                    hx_trigger="load",
                    hx_target="this",
                    hx_swap="outerHTML",
                    id=example2_pagination.content_id
                ),
                cls=str(m.b(8))
            ),

            # Example 3: Custom styling
            Div(
                H2("Example 3: Custom Styling",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Pagination with custom button text and size",
                  cls=combine_classes(m.b(4))),

                Div(
                    # Placeholder - will be replaced by HTMX
                    Div(
                        P("Loading...", cls=combine_classes(text_align.center, p(4))),
                        cls=combine_classes(card, bg_dui.base_100, p(6))
                    ),
                    hx_get=example3_router.content.to(page=1, example="3"),
                    hx_trigger="load",
                    hx_target="this",
                    hx_swap="outerHTML",
                    id=example3_pagination.content_id
                ),
                cls=str(m.b(8))
            ),

            # Example 4: First/Last buttons
            Div(
                H2("Example 4: First/Last Buttons",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Pagination with First/Last buttons for quick navigation to endpoints",
                  cls=combine_classes(m.b(4))),

                Div(
                    # Placeholder - will be replaced by HTMX
                    Div(
                        P("Loading...", cls=combine_classes(text_align.center, p(4))),
                        cls=combine_classes(card, bg_dui.base_100, p(6))
                    ),
                    hx_get=example4_router.content.to(page=1, example="4"),
                    hx_trigger="load",
                    hx_target="this",
                    hx_swap="outerHTML",
                    id=example4_pagination.content_id
                ),
                cls=str(m.b(8))
            ),

            # Example 5: Features overview
            Div(
                H2("Features",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                Div(
                    Div(
                        H3("Automatic", cls=combine_classes(font_weight.semibold, m.b(2))),
                        Ul(
                            Li("Route generation"),
                            Li("Pagination math"),
                            Li("State preservation"),
                            Li("HTMX integration"),
                            cls=combine_classes(m.l(6))
                        ),
                        cls=combine_classes(card_body)
                    ),
                    Div(
                        H3("Customization", cls=combine_classes(font_weight.semibold, m.b(2))),
                        Ul(
                            Li("Custom button text"),
                            Li("Page info format"),
                            Li("Button sizes"),
                            Li("Multiple styles"),
                            cls=combine_classes(m.l(6))
                        ),
                        cls=combine_classes(card_body)
                    ),
                    Div(
                        H3("Integration", cls=combine_classes(font_weight.semibold, m.b(2))),
                        Ul(
                            Li("Declarative API"),
                            Li("Query param preservation"),
                            Li("Flexible data loading"),
                            Li("Custom rendering"),
                            cls=combine_classes(m.l(6))
                        ),
                        cls=combine_classes(card_body)
                    ),
                    cls=combine_classes(grid_display, grid_cols._1, grid_cols._3.md, gap._4, m.b(6))
                ),
                cls=str(m.b(8))
            ),

            cls=combine_classes(
                container,
                max_w._6xl,
                m.x.auto,
                p(8)
            )
        )

    from demo_app import navbar
    return handle_htmx_request(
        request,
        pagination_content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )
