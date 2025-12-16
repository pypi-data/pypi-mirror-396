"""Shared imports and utilities for interaction pattern demos."""

# FastHTML core
from fasthtml.common import *

# Library components
from cjm_fasthtml_interactions.patterns.step_flow import Step, StepFlow
from cjm_fasthtml_interactions.patterns.tabbed_interface import Tab, TabbedInterface
from cjm_fasthtml_interactions.patterns.master_detail import MasterDetail, DetailItem, DetailItemGroup
from cjm_fasthtml_interactions.patterns.async_loading import AsyncLoadingContainer, LoadingType
from cjm_fasthtml_interactions.patterns.modal_dialog import ModalDialog, ModalTriggerButton, ModalSize
from cjm_fasthtml_interactions.patterns.sse_connection_monitor import SSEConnectionMonitor, SSEConnectionConfig
from cjm_fasthtml_interactions.patterns.pagination import Pagination, PaginationStyle
from cjm_fasthtml_interactions.core.context import InteractionContext
from cjm_fasthtml_interactions.core.html_ids import InteractionHtmlIds
from cjm_fasthtml_app_core.core.html_ids import AppHtmlIds
from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
from cjm_fasthtml_app_core.core.layout import wrap_with_layout

# Utilities for styling
from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import container, max_w, w, h
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import grid_display, grid_cols, gap, flex_display, items, justify
from cjm_fasthtml_tailwind.core.base import combine_classes
from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes, btn_styles
from cjm_fasthtml_daisyui.components.data_display.card import card, card_body, card_title
from cjm_fasthtml_daisyui.components.data_display.badge import badge_colors
from cjm_fasthtml_daisyui.components.data_input.text_input import text_input
from cjm_fasthtml_daisyui.components.data_input.select import select
from cjm_fasthtml_daisyui.components.navigation.link import link, link_colors
from cjm_fasthtml_daisyui.components.feedback.progress import progress, progress_colors
from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui
