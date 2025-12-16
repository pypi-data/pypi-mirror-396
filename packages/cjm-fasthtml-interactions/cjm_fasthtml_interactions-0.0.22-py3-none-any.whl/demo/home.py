"""Homepage and features page for the demo app."""

from demo import *

# Create APIRouter for home routes
home_ar = APIRouter(prefix="")


@home_ar
def index(request):
    """Homepage with library overview."""
    # Import here to avoid circular imports
    from demo.step_flow_demo import step_flow_ar
    from demo.tabbed_interface_demo import tabbed_interface_ar
    from demo.master_detail_demo import master_detail_ar
    from demo.async_loading_demo import async_loading_ar
    from demo.modal_dialog_demo import modal_dialog_ar
    from demo.sse_monitor_demo import sse_monitor_ar
    from demo.pagination_demo import pagination_ar

    def home_content():
        return Div(
            H1("cjm-fasthtml-interactions Demo",
               cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

            P("Reusable user interaction patterns for FastHTML applications:",
              cls=combine_classes(font_size.lg, m.b(6))),

            # Feature list
            Div(
                Div(
                    H3("StepFlow Pattern", cls=combine_classes(font_weight.bold, m.b(2))),
                    Ul(
                        Li("Multi-step wizard workflows"),
                        Li("Visual progress indicators"),
                        Li("Form data collection"),
                        Li("State management and resumability"),
                        cls=combine_classes(m.l(6), m.b(4))
                    )
                ),
                Div(
                    H3("TabbedInterface Pattern", cls=combine_classes(font_weight.bold, m.b(2))),
                    Ul(
                        Li("DaisyUI radio-based tabs"),
                        Li("Automatic route generation"),
                        Li("On-demand content loading"),
                        Li("Multiple tab styles"),
                        cls=combine_classes(m.l(6), m.b(4))
                    )
                ),
                Div(
                    H3("MasterDetail Pattern", cls=combine_classes(font_weight.bold, m.b(2))),
                    Ul(
                        Li("Sidebar navigation with master list"),
                        Li("Hierarchical grouping with collapsible sections"),
                        Li("Badge indicators for status"),
                        Li("Active state management"),
                        cls=combine_classes(m.l(6), m.b(8))
                    )
                ),
                cls=combine_classes(text_align.left, m.b(8))
            ),

            # Navigation
            Div(
                # All patterns now use APIRouter with consistent HTMX navigation
                A(
                    "StepFlow Demo",
                    href=step_flow_ar.index.to(),
                    hx_get=step_flow_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.primary, btn_sizes.lg, m.r(2), m.b(2))
                ),
                A(
                    "Tabbed Interface Demo",
                    href=tabbed_interface_ar.index.to(),
                    hx_get=tabbed_interface_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.secondary, btn_sizes.lg, m.r(2), m.b(2))
                ),
                A(
                    "Master-Detail Demo",
                    href=master_detail_ar.index.to(),
                    hx_get=master_detail_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.success, btn_sizes.lg, m.r(2), m.b(2))
                ),
                A(
                    "Async Loading Demo",
                    href=async_loading_ar.index.to(),
                    hx_get=async_loading_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.info, btn_sizes.lg, m.r(2), m.b(2))
                ),
                A(
                    "Modal Dialog Demo",
                    href=modal_dialog_ar.index.to(),
                    hx_get=modal_dialog_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.warning, btn_sizes.lg, m.r(2), m.b(2))
                ),
                A(
                    "SSE Monitor Demo",
                    href=sse_monitor_ar.index.to(),
                    hx_get=sse_monitor_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.error, btn_sizes.lg, m.r(2), m.b(2))
                ),
                A(
                    "Pagination Demo",
                    href=pagination_ar.index.to(),
                    hx_get=pagination_ar.index.to(),
                    hx_target=f"#{AppHtmlIds.MAIN_CONTENT}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.success, btn_sizes.lg, m.r(2), m.b(2))
                ),
            ),

            cls=combine_classes(
                container,
                max_w._4xl,
                m.x.auto,
                p(8),
                text_align.center
            )
        )

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        home_content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )


