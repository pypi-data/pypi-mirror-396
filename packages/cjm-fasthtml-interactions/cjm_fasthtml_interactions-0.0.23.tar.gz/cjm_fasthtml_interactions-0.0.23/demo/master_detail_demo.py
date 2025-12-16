"""MasterDetail pattern demo - File browser with sidebar navigation."""

from fasthtml.common import *
from demo import *

# Create APIRouter for master detail demo
master_detail_ar = APIRouter(prefix="/master_detail")


# Define detail render functions for file browser
def render_file_detail(ctx: InteractionContext):
    """Render file detail view."""
    file_data = ctx.get_data("file", {})
    return Div(
        H2(f"📄 {file_data.get('name', 'Unknown File')}",
           cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("File details and metadata:",
          cls=combine_classes(m.b(4))),
        Div(
            Div(
                H3("File Information", cls=combine_classes(font_weight.semibold, m.b(2))),
                P(Strong("Size: "), f"{file_data.get('size', 0)} bytes", cls=str(m.b(2))),
                P(Strong("Type: "), file_data.get('type', 'N/A'), cls=str(m.b(2))),
                P(Strong("Modified: "), file_data.get('modified', 'N/A'), cls=str(m.b(2))),
                P(Strong("Path: "), file_data.get('path', 'N/A'), cls=str(m.b(4))),
                cls=combine_classes(card_body, m.b(4))
            ),
            Div(
                H3("Actions", cls=combine_classes(font_weight.semibold, m.b(2))),
                Div(
                    Button("Download", cls=combine_classes(btn, btn_colors.primary, btn_sizes.sm, m.r(2))),
                    Button("Share", cls=combine_classes(btn, btn_colors.secondary, btn_sizes.sm, m.r(2))),
                    Button("Delete", cls=combine_classes(btn, btn_colors.error, btn_sizes.sm)),
                ),
                cls=combine_classes(card_body)
            ),
            cls=str(m.t(4))
        ),
        cls=combine_classes(card_body)
    )


def render_folder_detail(ctx: InteractionContext):
    """Render folder detail view."""
    folder_data = ctx.get_data("folder", {})
    return Div(
        H2(f"📁 {folder_data.get('name', 'Unknown Folder')}",
           cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("Folder contents and statistics:",
          cls=combine_classes(m.b(4))),
        Div(
            Div(
                H3("Folder Statistics", cls=combine_classes(font_weight.semibold, m.b(2))),
                P(Strong("Total Items: "), str(folder_data.get('item_count', 0)), cls=str(m.b(2))),
                P(Strong("Files: "), str(folder_data.get('file_count', 0)), cls=str(m.b(2))),
                P(Strong("Folders: "), str(folder_data.get('folder_count', 0)), cls=str(m.b(4))),
                cls=combine_classes(card_body, m.b(4))
            ),
            Div(
                H3("Contents", cls=combine_classes(font_weight.semibold, m.b(2))),
                Ul(
                    *[Li(item, cls=str(m.b(1))) for item in folder_data.get('items', [])],
                    cls=combine_classes(m.l(6))
                ),
                cls=combine_classes(card_body)
            ),
            cls=str(m.t(4))
        ),
        cls=combine_classes(card_body)
    )


def render_overview_detail(ctx: InteractionContext):
    """Render storage overview."""
    overview_data = ctx.get_data("overview", {})
    return Div(
        H2("💾 Storage Overview",
           cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        P("Your file storage at a glance:",
          cls=combine_classes(m.b(4))),
        Div(
            Div(
                H3("Storage Summary", cls=combine_classes(font_weight.semibold, m.b(2))),
                P(Strong("Total Files: "), str(overview_data.get('total_files', 0)), cls=str(m.b(2))),
                P(Strong("Total Size: "), overview_data.get('total_size', 'N/A'), cls=str(m.b(2))),
                P(Strong("Available Space: "), overview_data.get('available_space', 'N/A'), cls=str(m.b(4))),
                cls=combine_classes(card_body, m.b(4))
            ),
            Div(
                H3("Quick Stats", cls=combine_classes(font_weight.semibold, m.b(3))),
                Div(
                    Div(
                        P("Documents", cls=combine_classes(font_weight.semibold)),
                        P(str(overview_data.get('documents_count', 0)),
                          cls=combine_classes(font_size._2xl, font_weight.bold)),
                        cls=combine_classes(card_body)
                    ),
                    Div(
                        P("Images", cls=combine_classes(font_weight.semibold)),
                        P(str(overview_data.get('images_count', 0)),
                          cls=combine_classes(font_size._2xl, font_weight.bold)),
                        cls=combine_classes(card_body)
                    ),
                    Div(
                        P("Videos", cls=combine_classes(font_weight.semibold)),
                        P(str(overview_data.get('videos_count', 0)),
                          cls=combine_classes(font_size._2xl, font_weight.bold)),
                        cls=combine_classes(card_body)
                    ),
                    cls=combine_classes(grid_display, grid_cols._1, grid_cols._3.md, gap._4)
                ),
                cls=combine_classes(card_body)
            ),
            cls=str(m.t(4))
        ),
        cls=combine_classes(card_body)
    )


# Data loaders for master-detail items
def load_report_data(request):
    """Load annual report file metadata."""
    return {
        "file": {
            "name": "annual-report.pdf",
            "size": 3145728,  # 3 MB
            "type": "PDF Document",
            "modified": "2025-01-15 09:30",
            "path": "/documents/annual-report.pdf"
        }
    }


def load_presentation_data(request):
    """Load presentation file metadata."""
    return {
        "file": {
            "name": "presentation.pdf",
            "size": 2097152,  # 2 MB
            "type": "PDF Document",
            "modified": "2025-01-20 14:30",
            "path": "/documents/presentation.pdf"
        }
    }


def load_vacation_photo_data(request):
    """Load vacation photo metadata."""
    return {
        "file": {
            "name": "vacation-photo.jpg",
            "size": 524288,  # 512 KB
            "type": "JPEG Image",
            "modified": "2024-12-25 16:45",
            "path": "/media/vacation-photo.jpg"
        }
    }


def load_demo_video_data(request):
    """Load demo video metadata."""
    return {
        "file": {
            "name": "demo-video.mp4",
            "size": 8388608,  # 8 MB
            "type": "MP4 Video",
            "modified": "2025-01-18 11:20",
            "path": "/media/demo-video.mp4"
        }
    }


def load_folder_data(request):
    """Load folder metadata."""
    return {
        "folder": {
            "name": "Work Projects",
            "item_count": 12,
            "file_count": 8,
            "folder_count": 4,
            "items": ["project-plan.docx", "budget.xlsx", "team-photo.jpg", "meeting-notes.txt"]
        }
    }


def load_overview_data(request):
    """Load storage overview data."""
    return {
        "overview": {
            "total_files": 1247,
            "total_size": "8.4 GB",
            "available_space": "41.6 GB",
            "documents_count": 342,
            "images_count": 856,
            "videos_count": 49
        }
    }


# Create master-detail file browser interface
file_browser = MasterDetail(
    interface_id="file_browser",
    master_title="File Browser",
    items=[
        DetailItem(
            id="overview",
            label="Storage Overview",
            render=render_overview_detail,
            data_loader=load_overview_data,
            badge_text="1.2K files",
            badge_color=badge_colors.info
        ),
        DetailItemGroup(
            id="documents",
            title="Documents",
            items=[
                DetailItem(
                    id="doc-report",
                    label="annual-report.pdf",
                    render=render_file_detail,
                    data_loader=load_report_data,
                    badge_text="3 MB",
                    badge_color=badge_colors.info
                ),
                DetailItem(
                    id="doc-presentation",
                    label="presentation.pdf",
                    render=render_file_detail,
                    data_loader=load_presentation_data,
                    badge_text="2 MB",
                    badge_color=badge_colors.info
                ),
                DetailItem(
                    id="folder-work",
                    label="Work Projects",
                    render=render_folder_detail,
                    data_loader=load_folder_data,
                    badge_text="12 items",
                    badge_color=badge_colors.success
                )
            ],
            badge_text="3 items",
            default_open=True
        ),
        DetailItemGroup(
            id="media",
            title="Media Files",
            items=[
                DetailItem(
                    id="img-vacation",
                    label="vacation-photo.jpg",
                    render=render_file_detail,
                    data_loader=load_vacation_photo_data,
                    badge_text="512 KB",
                    badge_color=badge_colors.warning
                ),
                DetailItem(
                    id="video-demo",
                    label="demo-video.mp4",
                    render=render_file_detail,
                    data_loader=load_demo_video_data,
                    badge_text="8 MB",
                    badge_color=badge_colors.error
                )
            ],
            badge_text="2 items",
            default_open=False
        )
    ]
)

# Generate browser router
browser_router = file_browser.create_router(prefix="/browser")


def render_file_browser_page(request, sess, active_item: str = "overview"):
    """
    Render the complete file browser page with header and master-detail interface.

    Args:
        request: FastHTML request object
        sess: FastHTML session object
        active_item: Currently active item ID

    Returns:
        Complete file browser layout
    """
    return Div(
        # Header
        Div(
            H1("File Browser",
               cls=combine_classes(font_size._3xl, font_weight.bold, m.b(2))),
            P("Explore the MasterDetail pattern with this file browser example featuring hierarchical navigation.",
              cls=combine_classes(m.b(6))),
            cls=str(m.b(6))
        ),

        # Master-Detail interface (sidebar + detail content)
        file_browser.render_full_interface(
            active_item_id=active_item,
            item_route_func=lambda iid: master_detail_ar.detail.to(item_id=iid),
            request=request,
            sess=sess
        ),

        cls=combine_classes(
            max_w._7xl,
            m.x.auto,
            p(6)
        )
    )


@master_detail_ar
def index(request, sess):
    """
    MasterDetail demo index route.

    Handles both:
    - HTMX requests: Returns complete page content (header + file browser)
    - Full page requests: Returns complete page with navbar and layout
    """
    def content():
        return render_file_browser_page(request, sess)

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )


@master_detail_ar
def detail(request, sess, item_id: str = "overview"):
    """
    Route for loading individual item detail content.

    Handles both:
    - HTMX requests: Returns just the detail content (and updated master list)
    - Full page requests: Returns complete file browser with page layout
    """
    from cjm_fasthtml_app_core.core.htmx import is_htmx_request

    # For HTMX requests, delegate to browser router's detail function
    if is_htmx_request(request):
        return browser_router.detail(request, sess, item_id=item_id)

    # For full page requests, return complete file browser page with navbar
    def content():
        return render_file_browser_page(request, sess, active_item=item_id)

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )
