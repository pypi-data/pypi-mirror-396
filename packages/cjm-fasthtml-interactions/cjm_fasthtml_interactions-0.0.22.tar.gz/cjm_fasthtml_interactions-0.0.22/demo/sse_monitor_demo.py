"""SSEConnectionMonitor pattern demo - Server-Sent Events connection monitoring with auto-reconnect."""

import time
from demo import *

# Create APIRouter for SSE monitor routes
sse_monitor_ar = APIRouter(prefix="/sse_monitor")


@sse_monitor_ar
def index(request):
        """SSE connection monitor patterns demo page."""

        def sse_content():
            connection_id = "demo"

            # Create connection monitor with custom configuration
            config = SSEConnectionConfig(
                max_reconnect_attempts=5,
                reconnect_delay=1000,
                max_backoff_multiplier=3,
                log_to_console=True
            )

            status_container, monitor_script = SSEConnectionMonitor(
                connection_id=connection_id,
                status_size="sm",
                config=config
            )

            return Div(
                H1("SSE Connection Monitor Pattern",
                   cls=combine_classes(font_size._3xl, font_weight.bold, m.b(6), text_align.center)),

                P("The SSE Connection Monitor pattern provides visual status indicators and automatic reconnection for Server-Sent Events.",
                  cls=combine_classes(text_align.center, m.b(8), max_w._3xl, m.x.auto)),

                # Example 1: Live connection monitor
                Div(
                    H2("Example 1: Live Connection Monitor",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("This example shows a real SSE connection with live updates. The status indicator shows the connection state.",
                      cls=combine_classes(m.b(4))),

                    # Connection status card
                    Div(
                        Div(
                            Div(
                                H3("Connection Status", cls=combine_classes(font_weight.semibold, m.b(2))),
                                status_container,
                                cls=combine_classes(flex_display, items.center, justify.between)
                            ),
                            cls=combine_classes(card_body, m.b(4))
                        ),

                        # Live updates display
                        Div(
                            H3("Live Updates", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Div(
                                P("Waiting for updates...", cls=combine_classes(text_align.center, p(4))),
                                hx_ext="sse",
                                sse_connect=sse_monitor_ar.stream.to(),
                                sse_swap="update",
                                id=InteractionHtmlIds.sse_element(connection_id),
                                cls=str(combine_classes(card_body, bg_dui.base_200))
                            ),
                            cls=combine_classes(card_body)
                        ),

                        cls=combine_classes(card, bg_dui.base_100)
                    ),

                    cls=str(m.b(8))
                ),

                # Example 2: Features
                Div(
                    H2("Features",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    Div(
                        Div(
                            H3("Visual Status Indicators", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Ul(
                                Li("Live - Connected and receiving updates"),
                                Li("Disconnected - Connection lost, not reconnecting"),
                                Li("Error - Connection error occurred"),
                                Li("Reconnecting - Attempting to reconnect"),
                                cls=combine_classes(m.l(6))
                            ),
                            cls=combine_classes(card_body)
                        ),
                        Div(
                            H3("Automatic Reconnection", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Ul(
                                Li("Exponential backoff strategy"),
                                Li("Configurable retry attempts"),
                                Li("Configurable delay and backoff"),
                                Li("Graceful degradation"),
                                cls=combine_classes(m.l(6))
                            ),
                            cls=combine_classes(card_body)
                        ),
                        Div(
                            H3("Smart Behavior", cls=combine_classes(font_weight.semibold, m.b(2))),
                            Ul(
                                Li("Tab visibility awareness"),
                                Li("Server shutdown detection"),
                                Li("OOB swap detection"),
                                Li("Console logging (optional)"),
                                cls=combine_classes(m.l(6))
                            ),
                            cls=combine_classes(card_body)
                        ),
                        cls=combine_classes(grid_display, grid_cols._1, grid_cols._3.md, gap._4, m.b(6))
                    ),
                    cls=str(m.b(8))
                ),

                # Example 3: Configuration
                Div(
                    H2("Configuration Options",
                       cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    P("Customize the connection monitor behavior with SSEConnectionConfig:",
                      cls=combine_classes(m.b(4))),
                    Div(
                        Code("""config = SSEConnectionConfig(
    max_reconnect_attempts=5,    # Max retry attempts
    reconnect_delay=1000,         # Initial delay (ms)
    max_backoff_multiplier=3,     # Max backoff multiplier
    monitor_visibility=True,      # Monitor tab visibility
    log_to_console=True           # Enable logging
)""", cls=combine_classes(
                            "whitespace-pre",
                            "block",
                            p(4),
                            bg_dui.base_200,
                            "rounded"
                        )),
                        cls=combine_classes(card, card_body, bg_dui.base_100)
                    ),
                    cls=str(m.b(8))
                ),

                # Monitor script (required)
                monitor_script,

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
            sse_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )


@sse_monitor_ar
async def stream():
        """SSE endpoint for connection monitor demo."""
        import asyncio
        from starlette.responses import StreamingResponse

        async def event_generator():
            try:
                counter = 0
                while counter < 20:  # Stream 20 updates then stop
                    counter += 1
                    timestamp = time.strftime('%H:%M:%S')

                    # Generate update content
                    progress_value = min(counter * 5, 100)
                    update_content = Div(
                        H4(f"Update #{counter}", cls=combine_classes(font_weight.bold, m.b(2))),
                        P(f"Received at: {timestamp}", cls=str(m.b(1))),
                        P(f"Status: Streaming ({counter}/20 updates)", cls=str(m.b(2))),
                        Progress(
                            value=str(progress_value),
                            max="100",
                            cls=combine_classes(progress, progress_colors.primary, w.full)
                        ),
                        cls=combine_classes(p(4))
                    )

                    # Send SSE event
                    yield f"event: update\n"
                    yield f"data: {str(update_content)}\n\n"

                    # Wait before next update
                    await asyncio.sleep(2)

                # Final update
                final_content = Div(
                    H4("Stream Complete ✓", cls=combine_classes(font_weight.bold, m.b(2), text_align.center)),
                    P("All 20 updates delivered successfully.", cls=combine_classes(text_align.center, m.b(2))),
                    P("Refresh the page to see the stream again.", cls=combine_classes(text_align.center)),
                    cls=combine_classes(p(4), bg_dui.success, "text-success-content", "rounded")
                )
                yield f"event: update\n"
                yield f"data: {str(final_content)}\n\n"

            except asyncio.CancelledError:
                # Send close message before shutting down
                yield f"event: close\n"
                yield f"data: Server shutting down\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
