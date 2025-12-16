"""StepFlow pattern demo - Multi-step registration wizard."""

from typing import Dict, Any, Optional
from fasthtml.common import *
from demo import *


# Simple in-memory state store for the demo
class InMemoryStateStore:
    """In-memory workflow state store for demo purposes."""

    def __init__(self):
        self._current_steps: Dict[str, str] = {}
        self._states: Dict[str, Dict[str, Any]] = {}

    def _get_session_id(self, sess: Any) -> str:
        """Get or create a stable session identifier."""
        import uuid
        if "_demo_session_id" not in sess:
            sess["_demo_session_id"] = str(uuid.uuid4())
        return sess["_demo_session_id"]

    def _make_key(self, flow_id: str, sess: Any) -> str:
        return f"{flow_id}:{self._get_session_id(sess)}"

    def get_current_step(self, flow_id: str, sess: Any) -> Optional[str]:
        return self._current_steps.get(self._make_key(flow_id, sess))

    def set_current_step(self, flow_id: str, sess: Any, step_id: str) -> None:
        self._current_steps[self._make_key(flow_id, sess)] = step_id

    def get_state(self, flow_id: str, sess: Any) -> Dict[str, Any]:
        return self._states.get(self._make_key(flow_id, sess), {}).copy()

    def update_state(self, flow_id: str, sess: Any, updates: Dict[str, Any]) -> None:
        key = self._make_key(flow_id, sess)
        if key not in self._states:
            self._states[key] = {}
        self._states[key].update(updates)

    def clear_state(self, flow_id: str, sess: Any) -> None:
        key = self._make_key(flow_id, sess)
        self._current_steps.pop(key, None)
        self._states.pop(key, None)


# Create shared state store instance
demo_state_store = InMemoryStateStore()

# Create APIRouter for step flow demo
step_flow_ar = APIRouter(prefix="/step_flow")


# Define step render functions for registration workflow
def render_name_step(ctx: InteractionContext):
    """Render step 1 - collect name."""
    current_name = ctx.get("name", "")
    return Div(
        H2("Enter Your Name", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        Label("Full Name:", cls=combine_classes(font_weight.semibold, m.b(2))),
        Input(
            name="name",
            value=current_name,
            placeholder="John Doe",
            required=True,
            cls=combine_classes(text_input, w.full)
        ),
        cls=combine_classes(card_body)
    )


def render_email_step(ctx: InteractionContext):
    """Render step 2 - collect email."""
    name = ctx.get("name", "there")
    current_email = ctx.get("email", "")
    return Div(
        H2(f"Hi {name}! What's your email?",
           cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        Label("Email Address:", cls=combine_classes(font_weight.semibold, m.b(2))),
        Input(
            name="email",
            type="email",
            value=current_email,
            placeholder="john@example.com",
            required=True,
            cls=combine_classes(text_input, w.full)
        ),
        cls=combine_classes(card_body)
    )


def render_preferences_step(ctx: InteractionContext):
    """Render step 3 - collect preferences."""
    current_notifications = ctx.get("notifications", "")
    return Div(
        H2("Set Your Preferences",
           cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        Label("Notification Preferences:", cls=combine_classes(font_weight.semibold, m.b(2))),
        Select(
            Option("Daily updates", value="daily", selected=(current_notifications == "daily")),
            Option("Weekly digest", value="weekly", selected=(current_notifications == "weekly")),
            Option("Monthly summary", value="monthly", selected=(current_notifications == "monthly")),
            name="notifications",
            cls=combine_classes(select, w.full)
        ),
        cls=combine_classes(card_body)
    )


def render_confirm_step(ctx: InteractionContext):
    """Render step 4 - confirmation."""
    name = ctx.get("name", "")
    email = ctx.get("email", "")
    notifications = ctx.get("notifications", "")
    return Div(
        H2("Confirm Your Information",
           cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
        Div(
            P(Strong("Name: "), name, cls=str(m.b(2))),
            P(Strong("Email: "), email, cls=str(m.b(2))),
            P(Strong("Notifications: "), notifications.title(), cls=str(m.b(4))),
            P("Click 'Complete Registration' to finish.",
              cls=combine_classes(text_align.center, m.t(4))),
            cls=combine_classes(p(4))
        ),
        cls=combine_classes(card_body)
    )


# Define completion handler
def on_registration_complete(state: dict, request):
    """Handle registration completion."""
    name = state.get("name", "")
    email = state.get("email", "")
    return Div(
        Div(
            H2("Registration Complete! 🎉",
               cls=combine_classes(font_size._3xl, font_weight.bold, m.b(4), text_align.center)),
            P(f"Welcome, {name}!",
              cls=combine_classes(font_size.xl, m.b(2), text_align.center)),
            P(f"We've sent a confirmation email to {email}",
              cls=combine_classes(text_align.center, m.b(6))),
            Div(
                A(
                    "Start Another Registration",
                    href=step_flow_ar.start.to(),
                    hx_get=step_flow_ar.start.to(),
                    hx_target=f"#{InteractionHtmlIds.STEP_FLOW_CONTAINER}",
                    hx_push_url="true",
                    cls=combine_classes(btn, btn_colors.primary)
                ),
                cls=combine_classes(text_align.center)
            ),
            cls=combine_classes(card_body)
        ),
        cls=combine_classes(card, max_w.lg, m.x.auto, m.t(8))
    )


# Create registration step flow with progress indicator
registration_flow = StepFlow(
    flow_id="registration",
    steps=[
        Step(
            id="name",
            title="Name",
            render=render_name_step,
            data_keys=["name"]
        ),
        Step(
            id="email",
            title="Email",
            render=render_email_step,
            data_keys=["email"]
        ),
        Step(
            id="preferences",
            title="Preferences",
            render=render_preferences_step,
            data_keys=["notifications"]
        ),
        Step(
            id="confirm",
            title="Confirm",
            render=render_confirm_step,
            next_button_text="Complete Registration"
        )
    ],
    state_store=demo_state_store,  # Server-side state storage
    on_complete=on_registration_complete,
    show_progress=True  # Enable progress indicator
)

# Generate workflow router
registration_router = registration_flow.create_router(prefix="/workflow")


def render_registration_page(request, sess):
    """
    Render the complete registration page with header and workflow.

    Args:
        request: FastHTML request object
        sess: FastHTML session object

    Returns:
        Complete registration layout
    """
    return Div(
        # Header
        Div(
            H1("Registration Wizard",
               cls=combine_classes(font_size._3xl, font_weight.bold, m.b(2))),
            P("Complete the multi-step registration process using the StepFlow pattern.",
              cls=combine_classes(m.b(6))),
            cls=str(m.b(6))
        ),

        # StepFlow workflow
        registration_router.start(request, sess),

        cls=combine_classes(
            max_w._4xl,
            m.x.auto,
            p(6)
        )
    )


@step_flow_ar
def index(request, sess):
    """
    StepFlow demo index route.

    Handles both:
    - HTMX requests: Returns complete page content (header + workflow)
    - Full page requests: Returns complete page with navbar and layout
    """
    def content():
        return render_registration_page(request, sess)

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )


@step_flow_ar
def start(request, sess):
    """
    Route for starting/resuming the workflow.

    Handles both:
    - HTMX requests: Returns just the workflow content
    - Full page requests: Returns complete page with navbar and layout
    """
    from cjm_fasthtml_app_core.core.htmx import is_htmx_request

    # For HTMX requests, delegate to workflow router's start function
    if is_htmx_request(request):
        return registration_router.start(request, sess)

    # For full page requests, return complete page with navbar
    def content():
        return render_registration_page(request, sess)

    # Import navbar from demo_app to avoid circular import
    from demo_app import navbar
    return handle_htmx_request(
        request,
        content,
        wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
    )
