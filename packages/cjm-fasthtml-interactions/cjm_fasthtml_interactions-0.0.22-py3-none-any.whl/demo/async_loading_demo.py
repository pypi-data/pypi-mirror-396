"""AsyncLoadingContainer pattern demo - Async content loading with various loading indicators."""

import time
from demo import *

# Create APIRouter for async loading routes
async_loading_ar = APIRouter(prefix="/async_loading")


@async_loading_ar
def index(request):
    """Async loading patterns demo page."""

    def async_content():
        return Div(
            H1("Async Loading Container Pattern",
               cls=combine_classes(font_size._3xl, font_weight.bold, m.b(6), text_align.center)),

            P("The AsyncLoadingContainer pattern enables asynchronous content loading with customizable loading indicators.",
              cls=combine_classes(text_align.center, m.b(8), max_w._3xl, m.x.auto)),

            # Example 1: Spinner loader
            Div(
                H2("Example 1: Spinner Loader",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Simple spinner with loading message",
                  cls=combine_classes(m.b(4))),
                AsyncLoadingContainer(
                    container_id="spinner-demo",
                    load_url=async_loading_ar.content_spinner.to(),
                    loading_message="Loading content...",
                    container_cls=str(combine_classes(card, bg_dui.base_100))
                ),
                cls=str(m.b(8))
            ),

            # Example 2: Different loading styles
            Div(
                H2("Example 2: Different Loading Styles",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Various loading indicator styles from DaisyUI",
                  cls=combine_classes(m.b(4))),
                Div(
                    Div(
                        H3("Dots", cls=combine_classes(font_weight.semibold, m.b(2))),
                        AsyncLoadingContainer(
                            container_id="dots-demo",
                            load_url=async_loading_ar.content_dots.to(),
                            loading_type=LoadingType.DOTS,
                            loading_size="md",
                            container_cls=str(combine_classes(card, bg_dui.base_100))
                        )
                    ),
                    Div(
                        H3("Ring", cls=combine_classes(font_weight.semibold, m.b(2))),
                        AsyncLoadingContainer(
                            container_id="ring-demo",
                            load_url=async_loading_ar.content_ring.to(),
                            loading_type=LoadingType.RING,
                            loading_size="md",
                            container_cls=str(combine_classes(card, bg_dui.base_100))
                        )
                    ),
                    Div(
                        H3("Ball", cls=combine_classes(font_weight.semibold, m.b(2))),
                        AsyncLoadingContainer(
                            container_id="ball-demo",
                            load_url=async_loading_ar.content_ball.to(),
                            loading_type=LoadingType.BALL,
                            loading_size="md",
                            container_cls=str(combine_classes(card, bg_dui.base_100))
                        )
                    ),
                    cls=combine_classes(grid_display, grid_cols._1, grid_cols._3.md, gap._4, m.b(8))
                ),
                cls=str(m.b(8))
            ),

            # Example 3: innerHTML swap
            Div(
                H2("Example 3: Inner Content Swap",
                   cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                P("Container persists, only inner content is swapped",
                  cls=combine_classes(m.b(4))),
                AsyncLoadingContainer(
                    container_id="inner-swap-demo",
                    load_url=async_loading_ar.content_inner.to(),
                    swap="innerHTML",
                    loading_type=LoadingType.SPINNER,
                    container_cls=str(combine_classes(card, card_body, bg_dui.base_200, p(8)))
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
        async_content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )


@async_loading_ar
def content_spinner():
    """Return loaded content after delay (spinner example)."""
    time.sleep(1.5)
    return Div(
        H3("Content Loaded!", cls=combine_classes(font_size.xl, font_weight.bold, m.b(2))),
        P("This content was loaded asynchronously using HTMX after a 1.5 second delay."),
        P(f"Loaded at: {time.strftime('%H:%M:%S')}"),
        id="spinner-demo",
        cls=combine_classes(card, card_body, bg_dui.base_100)
    )


@async_loading_ar
def content_dots():
    """Return loaded content for dots example."""
    time.sleep(1)
    return Div(
        P("Dots loader", cls=combine_classes(font_weight.semibold, m.b(1))),
        P("Loaded successfully!"),
        id="dots-demo",
        cls=combine_classes(card, card_body, bg_dui.base_100)
    )


@async_loading_ar
def content_ring():
    """Return loaded content for ring example."""
    time.sleep(1.2)
    return Div(
        P("Ring loader", cls=combine_classes(font_weight.semibold, m.b(1))),
        P("Loaded successfully!"),
        id="ring-demo",
        cls=combine_classes(card, card_body, bg_dui.base_100)
    )


@async_loading_ar
def content_ball():
    """Return loaded content for ball example."""
    time.sleep(0.8)
    return Div(
        P("Ball loader", cls=combine_classes(font_weight.semibold, m.b(1))),
        P("Loaded successfully!"),
        id="ball-demo",
        cls=combine_classes(card, card_body, bg_dui.base_100)
    )


@async_loading_ar
def content_inner():
    """Return loaded content for innerHTML swap example."""
    time.sleep(1)
    # Note: No ID needed since we're swapping innerHTML
    return Div(
        H3("Inner Content", cls=combine_classes(font_size.xl, font_weight.bold, m.b(2))),
        P("This content replaced only the inner HTML of the container."),
        P("The container div with its styling and ID persisted."),
        P(f"Loaded at: {time.strftime('%H:%M:%S')}")
    )
