"""TabbedInterface pattern demo - Dashboard with multiple tabs."""

from fasthtml.common import *
from demo import *

# Create APIRouter for tabbed interface demo
tabbed_interface_ar = APIRouter(prefix="/tabbed_interface")


# Define tab render functions for dashboard
def render_overview_tab(ctx: InteractionContext):
    """Render overview tab."""
    stats = ctx.get_data("stats", {})
    return Div(
        H2("Dashboard Overview", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("This tab shows a dashboard overview with statistics.",
          cls=combine_classes(m.b(6))),
        Div(
            Div(
                H3("Total Items", cls=combine_classes(font_weight.semibold, m.b(2))),
                P(str(stats.get("total", 0)), cls=combine_classes(font_size._3xl, font_weight.bold)),
                cls=combine_classes(card_body)
            ),
            Div(
                H3("Active Items", cls=combine_classes(font_weight.semibold, m.b(2))),
                P(str(stats.get("active", 0)), cls=combine_classes(font_size._3xl, font_weight.bold)),
                cls=combine_classes(card_body)
            ),
            cls=combine_classes(grid_display, grid_cols._1, grid_cols._2.md, gap._4)
        ),
        cls=combine_classes(card_body)
    )


def render_settings_tab(ctx: InteractionContext):
    """Render settings tab."""
    return Div(
        H2("Settings", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("Configure your application preferences here.",
          cls=combine_classes(m.b(4))),
        Div(
            Label("Theme:", cls=combine_classes(font_weight.semibold, m.b(2))),
            Select(
                Option("Light", value="light"),
                Option("Dark", value="dark"),
                Option("Cupcake", value="cupcake"),
                cls=combine_classes(select, w.full, max_w.xs)
            ),
            cls=str(m.b(4))
        ),
        Div(
            Label("Language:", cls=combine_classes(font_weight.semibold, m.b(2))),
            Select(
                Option("English", value="en"),
                Option("Spanish", value="es"),
                Option("French", value="fr"),
                cls=combine_classes(select, w.full, max_w.xs)
            ),
            cls=str(m.b(4))
        ),
        cls=combine_classes(card_body)
    )


def render_help_tab(ctx: InteractionContext):
    """Render help tab."""
    return Div(
        H2("Help & Documentation", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("Find helpful resources and documentation here.",
          cls=combine_classes(m.b(4))),
        Div(
            H3("Quick Links", cls=combine_classes(font_weight.semibold, m.b(3))),
            Ul(
                Li(A("Getting Started Guide", href="#", cls=combine_classes(link, link_colors.primary))),
                Li(A("API Reference", href="#", cls=combine_classes(link, link_colors.primary))),
                Li(A("Common Issues", href="#", cls=combine_classes(link, link_colors.primary))),
                Li(A("Contact Support", href="#", cls=combine_classes(link, link_colors.primary))),
                cls=combine_classes(m.l(6))
            )
        ),
        cls=combine_classes(card_body)
    )


def render_about_tab(ctx: InteractionContext):
    """Render about tab."""
    return Div(
        H2("About", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("This demo showcases the TabbedInterface pattern from cjm-fasthtml-interactions.",
          cls=combine_classes(m.b(4))),
        Div(
            H3("Features", cls=combine_classes(font_weight.semibold, m.b(3))),
            Ul(
                Li("DaisyUI radio-based tab navigation"),
                Li("Automatic route generation"),
                Li("On-demand content loading"),
                Li("Direct URL navigation support"),
                Li("Multiple tab styles (lift, bordered, boxed)"),
                cls=combine_classes(m.l(6), m.b(4))
            )
        ),
        Div(
            H3("Version", cls=combine_classes(font_weight.semibold, m.b(2))),
            P("cjm-fasthtml-interactions v0.1.0", cls=str(m.b(4)))
        ),
        cls=combine_classes(card_body)
    )


# Optional data loader for overview tab
def load_dashboard_stats(request):
    """Load statistics for overview tab."""
    return {
        "stats": {
            "total": 156,
            "active": 42
        }
    }


# Create tabbed interface with lift style
dashboard_tabs = TabbedInterface(
    interface_id="dashboard",
    tabs_list=[
        Tab(
            id="overview",
            label="Overview",
            title="Dashboard Overview",
            render=render_overview_tab,
            data_loader=load_dashboard_stats
        ),
        Tab(
            id="settings",
            label="Settings",
            title="Configuration Settings",
            render=render_settings_tab
        ),
        Tab(
            id="help",
            label="Help",
            title="Help & Documentation",
            render=render_help_tab
        ),
        Tab(
            id="about",
            label="About",
            title="About This Demo",
            render=render_about_tab
        )
    ],
    tab_style="lift"  # Use DaisyUI lift style
)

# Generate dashboard router
dashboard_router = dashboard_tabs.create_router(prefix="/tabs")


def render_dashboard_page(request, sess, current_tab: str = "overview"):
    """
    Render the complete dashboard page with header and tabs.

    Args:
        request: FastHTML request object
        sess: FastHTML session object
        current_tab: Currently active tab ID

    Returns:
        Complete dashboard layout
    """
    return Div(
        # Header
        Div(
            H1("Interactive Dashboard",
               cls=combine_classes(font_size._3xl, font_weight.bold, m.b(2))),
            P("Explore the TabbedInterface pattern with this interactive dashboard example.",
              cls=combine_classes(m.b(6))),
            cls=str(m.b(6))
        ),

        # Tabbed interface (tabs + content)
        dashboard_tabs.render_full_interface(
            current_tab_id=current_tab,
            tab_route_func=lambda tid: tabbed_interface_ar.tab.to(tab_id=tid),
            request=request,
            sess=sess
        ),

        cls=combine_classes(
            max_w._6xl,
            m.x.auto,
            p(6)
        )
    )


@tabbed_interface_ar
def index(request, sess):
    """
    TabbedInterface demo index route.

    Handles both:
    - HTMX requests: Returns complete page content (header + dashboard)
    - Full page requests: Returns complete page with navbar and layout
    """
    def content():
        return render_dashboard_page(request, sess)

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )


@tabbed_interface_ar
def tab(request, sess, tab_id: str = "overview"):
    """
    Route for loading individual tab content.

    Handles both:
    - HTMX requests: Returns just the tab content
    - Full page requests: Returns complete dashboard with tabs and page layout
    """
    from cjm_fasthtml_app_core.core.htmx import is_htmx_request

    # For HTMX requests, delegate to dashboard router's tab function
    if is_htmx_request(request):
        return dashboard_router.tab(request, sess, tab_id=tab_id)

    # For full page requests, return complete dashboard page with navbar
    def content():
        return render_dashboard_page(request, sess, current_tab=tab_id)

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )
