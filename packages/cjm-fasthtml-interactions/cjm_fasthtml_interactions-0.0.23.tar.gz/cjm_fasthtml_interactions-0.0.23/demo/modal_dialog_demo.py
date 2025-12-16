"""ModalDialog pattern demo - Various modal dialog examples with different sizes and content."""

import time
from demo import *

# Create APIRouter for modal dialog routes
modal_dialog_ar = APIRouter(prefix="/modal_dialogs")


@modal_dialog_ar
def index(request):
        """Modal dialog patterns demo page."""

        def modal_content():
            # Create modals for different examples

            # Example 1: Simple info modal
            simple_modal = ModalDialog(
                modal_id="info",
                content=Div(
                    H2("Information", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("This is a simple informational modal with default settings.", cls=str(m.b(4))),
                    P("Click the X button or the backdrop to close.", cls=combine_classes(text_align.center)),
                    cls=combine_classes(card_body)
                ),
                size=ModalSize.SMALL
            )

            # Example 2: Large modal with async content
            loading_modal = ModalDialog(
                modal_id="settings",
                content=AsyncLoadingContainer(
                    container_id="settings-form",
                    load_url=modal_dialog_ar.content_settings.to(),
                    loading_message="Loading settings..."
                ),
                size=ModalSize.LARGE
            )

            # Example 3: Full-screen modal
            fullscreen_modal = ModalDialog(
                modal_id="media",
                content=Div(
                    H2("Full Screen Modal", cls=combine_classes(font_size._3xl, font_weight.bold, m.b(4), text_align.center)),
                    Div(
                        P("This modal takes up most of the screen (11/12 width and height).", cls=combine_classes(m.b(4))),
                        P("Perfect for displaying media, galleries, or detailed content.", cls=combine_classes(m.b(4))),
                        Div(
                            Div(cls=combine_classes(card, bg_dui.base_200, p(16))),
                            cls=combine_classes(grid_display, grid_cols._2, gap._4)
                        ),
                        cls=combine_classes(flex_display, items.center, justify.center, h.full)
                    ),
                    cls=combine_classes(card_body)
                ),
                size=ModalSize.FULL
            )

            # Example 4: Custom size modal with auto-show
            welcome_modal = ModalDialog(
                modal_id="welcome",
                content=Div(
                    H2("Welcome! 👋", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4), text_align.center)),
                    P("This modal appeared automatically when the page loaded.", cls=combine_classes(text_align.center, m.b(2))),
                    P("Close it and refresh the page to see it again!", cls=combine_classes(text_align.center)),
                    cls=combine_classes(card_body)
                ),
                size=ModalSize.CUSTOM,
                custom_width=str(w("96")),
                custom_height=str(h("48")),
                auto_show=True
            )

            # Example 5: Modal with HTMX form
            form_modal = ModalDialog(
                modal_id="contact",
                content=Div(
                    H2("Contact Form", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    Form(
                        Div(
                            Label("Name:", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Input(
                                name="name",
                                placeholder="Your name",
                                required=True,
                                cls=combine_classes(text_input, w.full, m.b(4))
                            )
                        ),
                        Div(
                            Label("Email:", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Input(
                                name="email",
                                type="email",
                                placeholder="your@email.com",
                                required=True,
                                cls=combine_classes(text_input, w.full, m.b(4))
                            )
                        ),
                        Div(
                            Label("Message:", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Textarea(
                                name="message",
                                placeholder="Your message",
                                required=True,
                                rows=4,
                                cls=combine_classes(text_input, w.full, m.b(4))
                            )
                        ),
                        Div(
                            Button(
                                "Send Message",
                                type="submit",
                                cls=combine_classes(btn, btn_colors.primary, m.r(2))
                            ),
                            Button(
                                "Cancel",
                                type="button",
                                onclick=f"document.getElementById('{InteractionHtmlIds.modal_dialog('contact')}').close()",
                                cls=combine_classes(btn, btn_styles.ghost)
                            ),
                            cls=combine_classes(text_align.right)
                        ),
                        hx_post=modal_dialog_ar.submit_contact.to(),
                        hx_target=f"#{InteractionHtmlIds.modal_dialog_content('contact')}",
                        hx_swap="innerHTML"
                    ),
                    id=InteractionHtmlIds.modal_dialog_content("contact"),
                    cls=combine_classes(card_body)
                ),
                size=ModalSize.MEDIUM
            )

            return Div(
                H1("Modal Dialog Pattern",
                   cls=combine_classes(font_size._3xl, font_weight.bold, m.b(6), text_align.center)),

                P("The ModalDialog pattern provides reusable modal dialogs with DaisyUI styling.",
                  cls=combine_classes(text_align.center, m.b(8), max_w._3xl, m.x.auto)),

                # Example 1: Simple modal
                Div(
                    H2("Example 1: Simple Info Modal",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("Basic modal with default settings (small size)",
                      cls=combine_classes(m.b(4))),
                    ModalTriggerButton(
                        modal_id="info",
                        label="Show Info Modal",
                        button_cls=str(btn_colors.info)
                    ),
                    cls=str(m.b(8))
                ),

                # Example 2: Large modal with async content
                Div(
                    H2("Example 2: Large Modal with Async Content",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("Modal that loads content asynchronously using AsyncLoadingContainer",
                      cls=combine_classes(m.b(4))),
                    ModalTriggerButton(
                        modal_id="settings",
                        label="Open Settings",
                        button_cls=str(btn_colors.primary)
                    ),
                    cls=str(m.b(8))
                ),

                # Example 3: Full-screen modal
                Div(
                    H2("Example 3: Full-Screen Modal",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("Modal that takes up most of the screen (11/12 width and height)",
                      cls=combine_classes(m.b(4))),
                    ModalTriggerButton(
                        modal_id="media",
                        label="View Full Screen",
                        button_cls=str(btn_colors.secondary)
                    ),
                    cls=str(m.b(8))
                ),

                # Example 4: Auto-show modal (welcome)
                Div(
                    H2("Example 4: Auto-Show Modal",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("This modal appeared automatically when you loaded this page. Refresh to see it again!",
                      cls=combine_classes(m.b(4))),
                    P("(Custom size with auto_show=True parameter)",
                      cls=combine_classes(m.b(4))),
                    cls=str(m.b(8))
                ),

                # Example 5: Modal with form
                Div(
                    H2("Example 5: Modal with Form",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("Modal containing a form that submits via HTMX",
                      cls=combine_classes(m.b(4))),
                    ModalTriggerButton(
                        modal_id="contact",
                        label="Contact Us",
                        button_cls=str(btn_colors.success)
                    ),
                    cls=str(m.b(8))
                ),

                # Render all modals
                simple_modal,
                loading_modal,
                fullscreen_modal,
                welcome_modal,
                form_modal,

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
            modal_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )


@modal_dialog_ar
def content_settings():
        """Return settings form content after delay."""
        time.sleep(1)
        return Div(
            H2("Settings Configuration", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
            P("Configure your application preferences:", cls=combine_classes(m.b(4))),

            Div(
                Label("Theme:", cls=combine_classes(font_weight.semibold, m.b(2))),
                Select(
                    Option("Light", value="light"),
                    Option("Dark", value="dark"),
                    Option("Cupcake", value="cupcake"),
                    Option("Forest", value="forest"),
                    cls=combine_classes(select, w.full)
                ),
                cls=str(m.b(4))
            ),

            Div(
                Label("Notifications:", cls=combine_classes(font_weight.semibold, m.b(2))),
                Select(
                    Option("All", value="all"),
                    Option("Important only", value="important"),
                    Option("None", value="none"),
                    cls=combine_classes(select, w.full)
                ),
                cls=str(m.b(4))
            ),

            Div(
                Button("Save Settings", cls=combine_classes(btn, btn_colors.primary, m.r(2))),
                Button("Cancel", onclick=f"document.getElementById('{InteractionHtmlIds.modal_dialog('settings')}').close()",
                       cls=combine_classes(btn, btn_styles.ghost)),
                cls=combine_classes(text_align.right)
            ),

            id="settings-form"
        )


@modal_dialog_ar
def submit_contact(name: str, email: str, message: str):
        """Handle contact form submission."""
        time.sleep(0.5)
        return Div(
            H2("Message Sent! ✓", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4), text_align.center)),
            P(f"Thank you, {name}!", cls=combine_classes(text_align.center, m.b(2))),
            P(f"We've received your message and will respond to {email} soon.",
              cls=combine_classes(text_align.center, m.b(4))),
            Div(
                Button(
                    "Close",
                    onclick=f"document.getElementById('{InteractionHtmlIds.modal_dialog('contact')}').close()",
                    cls=combine_classes(btn, btn_colors.primary)
                ),
                cls=combine_classes(text_align.center)
            ),
            id=InteractionHtmlIds.modal_dialog_content("contact")
        )
