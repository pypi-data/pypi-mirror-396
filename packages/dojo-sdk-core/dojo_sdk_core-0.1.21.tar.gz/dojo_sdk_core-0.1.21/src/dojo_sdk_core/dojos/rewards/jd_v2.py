"""
Reward functions for JD (JingDong) e-commerce SPA tasks - V2 Architecture.

This version includes both frontend and backend validation with bundled reward functions.
Each task exports a bundle containing:
  - state_key: Dict defining backend queries (collection + filter)
  - validate_backend: Function (state_key, final_state) -> (float, str)
  - validate_frontend: Function (initial_state, final_state) -> (float, str)
"""

import logging
from typing import Any, Callable, Dict, List, Tuple, TypedDict

logger = logging.getLogger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

class StateKeyQuery(TypedDict):
    collection: str
    filter: Dict[str, Any]


StateKey = Dict[str, StateKeyQuery]
ValidatorFunc = Callable[[Dict[str, Any]], Tuple[float, str]]


class ValidateTask(TypedDict):
    state_key: StateKey
    validate_backend: ValidatorFunc
    validate_frontend: ValidatorFunc


# =============================================================================
# Helper Functions - Frontend State
# =============================================================================

def _check_page(final_state: Dict[str, Any], expected_page: str) -> Tuple[bool, str]:
    """Check if the current page matches the expected page."""
    page = final_state.get("page")
    if page != expected_page:
        return False, f"page='{page}' expected '{expected_page}'"
    return True, ""


def _check_search_query_contains(final_state: Dict[str, Any], expected_text: str) -> Tuple[bool, str]:
    """Check if the search query contains the expected text."""
    search_query = final_state.get("searchQuery", "")
    if expected_text not in search_query:
        return False, f"searchQuery='{search_query}' expected to contain '{expected_text}'"
    return True, ""


def _check_search_query_contains_any(final_state: Dict[str, Any], expected_texts: List[str]) -> Tuple[bool, str]:
    """Check if the search query contains any of the expected texts."""
    search_query = final_state.get("searchQuery", "")
    if not any(text in search_query for text in expected_texts):
        return False, f"searchQuery='{search_query}' expected to contain one of {expected_texts}"
    return True, ""


def _check_selected_product_id(final_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    """Check if the selected product ID matches."""
    selected_id = final_state.get("selectedProductId")
    if selected_id != expected_id:
        return False, f"selectedProductId='{selected_id}' expected '{expected_id}'"
    return True, ""


def _check_home_feed_category(final_state: Dict[str, Any], expected_category: str) -> Tuple[bool, str]:
    """Check if the home feed category matches."""
    category = final_state.get("homeFeedCategory")
    if category != expected_category:
        return False, f"homeFeedCategory='{category}' expected '{expected_category}'"
    return True, ""


# =============================================================================
# NAVIGATION TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: go-to-the-cart-page-from-the-homepage
# -----------------------------------------------------------------------------

def _validate_backend_go_to_the_cart_page_from_the_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_the_cart_page_from_the_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart page from homepage"


_validate_go_to_the_cart_page_from_the_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_the_cart_page_from_the_homepage,
    "validate_frontend": _validate_frontend_go_to_the_cart_page_from_the_homepage,
}


# -----------------------------------------------------------------------------
# Task: go-to-a-product-page-from-home
# -----------------------------------------------------------------------------

def _validate_backend_go_to_a_product_page_from_home(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_a_product_page_from_home(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product page from home"


_validate_go_to_a_product_page_from_home: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_a_product_page_from_home,
    "validate_frontend": _validate_frontend_go_to_a_product_page_from_home,
}


# -----------------------------------------------------------------------------
# Task: go-to-homepage-from-product-page
# -----------------------------------------------------------------------------

def _validate_backend_go_to_homepage_from_product_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_homepage_from_product_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to homepage from product page"


_validate_go_to_homepage_from_product_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_homepage_from_product_page,
    "validate_frontend": _validate_frontend_go_to_homepage_from_product_page,
}


# -----------------------------------------------------------------------------
# Task: go-to-cart-page-from-product-detail-page
# -----------------------------------------------------------------------------

def _validate_backend_go_to_cart_page_from_product_detail_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_cart_page_from_product_detail_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart page from product detail"


_validate_go_to_cart_page_from_product_detail_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_cart_page_from_product_detail_page,
    "validate_frontend": _validate_frontend_go_to_cart_page_from_product_detail_page,
}


# -----------------------------------------------------------------------------
# Task: go-to-product-detail-from-search
# -----------------------------------------------------------------------------

def _validate_backend_go_to_product_detail_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_go_to_product_detail_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product detail from search"


_validate_go_to_product_detail_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_go_to_product_detail_from_search,
    "validate_frontend": _validate_frontend_go_to_product_detail_from_search,
}


# -----------------------------------------------------------------------------
# Task: navigate-from-cart-back-to-homepage
# -----------------------------------------------------------------------------

def _validate_backend_navigate_from_cart_back_to_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_from_cart_back_to_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated from cart back to homepage"


_validate_navigate_from_cart_back_to_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_from_cart_back_to_homepage,
    "validate_frontend": _validate_frontend_navigate_from_cart_back_to_homepage,
}


# -----------------------------------------------------------------------------
# Task: navigate-from-search-to-homepage
# -----------------------------------------------------------------------------

def _validate_backend_navigate_from_search_to_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_from_search_to_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated from search to homepage"


_validate_navigate_from_search_to_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_from_search_to_homepage,
    "validate_frontend": _validate_frontend_navigate_from_search_to_homepage,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-cart-from-product-page-via-header
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_cart_from_product_page_via_header(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_cart_from_product_page_via_header(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart from product page via header"


_validate_navigate_to_cart_from_product_page_via_header: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_cart_from_product_page_via_header,
    "validate_frontend": _validate_frontend_navigate_to_cart_from_product_page_via_header,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-cart-from-search-page
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_cart_from_search_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_cart_from_search_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to cart from search page"


_validate_navigate_to_cart_from_search_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_cart_from_search_page,
    "validate_frontend": _validate_frontend_navigate_to_cart_from_search_page,
}


# -----------------------------------------------------------------------------
# Task: navigate-from-product-to-another-product
# -----------------------------------------------------------------------------

def _validate_backend_navigate_from_product_to_another_product(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_from_product_to_another_product(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-y7z8a9")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "华丰京觅")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated from product to another product"


_validate_navigate_from_product_to_another_product: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_from_product_to_another_product,
    "validate_frontend": _validate_frontend_navigate_from_product_to_another_product,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-product-from-homepage-section
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_product_from_homepage_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_product_from_homepage_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-a1b2c3")
    if not ok:
        return 0.0, error
    ok, error = _check_home_feed_category(final_state, "电脑数码")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product from homepage section"


_validate_navigate_to_product_from_homepage_section: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_product_from_homepage_section,
    "validate_frontend": _validate_frontend_navigate_to_product_from_homepage_section,
}


# -----------------------------------------------------------------------------
# Task: navigate-via-category-sidebar-appliances
# -----------------------------------------------------------------------------

def _validate_backend_navigate_via_category_sidebar_appliances(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_via_category_sidebar_appliances(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "家用电器")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated via category sidebar to appliances"


_validate_navigate_via_category_sidebar_appliances: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_via_category_sidebar_appliances,
    "validate_frontend": _validate_frontend_navigate_via_category_sidebar_appliances,
}


# -----------------------------------------------------------------------------
# Task: navigate-via-category-sidebar-electronics
# -----------------------------------------------------------------------------

def _validate_backend_navigate_via_category_sidebar_electronics(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_via_category_sidebar_electronics(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-a1b2c3")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated via category sidebar to Apple iPhone product"


_validate_navigate_via_category_sidebar_electronics: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_via_category_sidebar_electronics,
    "validate_frontend": _validate_frontend_navigate_via_category_sidebar_electronics,
}


# -----------------------------------------------------------------------------
# Task: multi-step-navigation-home-to-product-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_multi_step_navigation_home_to_product_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_multi_step_navigation_home_to_product_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    ok, error = _check_home_feed_category(final_state, "服饰鞋包")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully completed multi-step navigation"


_validate_multistep_navigation_home_to_product_to_cart: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_multi_step_navigation_home_to_product_to_cart,
    "validate_frontend": _validate_frontend_multi_step_navigation_home_to_product_to_cart,
}


# -----------------------------------------------------------------------------
# Task: navigate-to-store-page
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_store_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_store_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "store")
    if not ok:
        return 0.0, error
    selected_store_id = final_state.get("selectedStoreId")
    if not selected_store_id:
        return 0.0, "selectedStoreId is not set"
    return 1.0, "Successfully navigated to store page"


_validate_navigate_to_store_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_store_page,
    "validate_frontend": _validate_frontend_navigate_to_store_page,
}


# -----------------------------------------------------------------------------
# Task: filter-homepage-feed-by-category
# -----------------------------------------------------------------------------

def _validate_backend_filter_homepage_feed_by_category(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for feed filter"


def _validate_frontend_filter_homepage_feed_by_category(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    category = final_state.get("homeFeedCategory", "")
    valid_categories = ["服饰鞋包", "手机通讯", "电脑数码"]
    if category not in valid_categories:
        return 0.0, f"homeFeedCategory='{category}' expected one of {valid_categories}"
    return 1.0, f"Successfully filtered homepage feed by category '{category}'"


_validate_filter_homepage_feed_by_category: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_filter_homepage_feed_by_category,
    "validate_frontend": _validate_frontend_filter_homepage_feed_by_category,
}


# =============================================================================
# SEARCH TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: search-jeep-shirt
# -----------------------------------------------------------------------------

def _validate_backend_search_jeep_shirt(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_jeep_shirt(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_search_query_contains(final_state, "吉普衬衫")
    if not ok:
        return 0.0, error
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 吉普衬衫"


_validate_search_jeep_shirt: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_jeep_shirt,
    "validate_frontend": _validate_frontend_search_jeep_shirt,
}


# -----------------------------------------------------------------------------
# Task: find-a-product-using-search-from-homepage
# -----------------------------------------------------------------------------

def _validate_backend_find_a_product_using_search_from_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_find_a_product_using_search_from_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "吉普衬衫")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for product and navigated to detail page"


_validate_find_a_product_using_search_from_homepage: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_find_a_product_using_search_from_homepage,
    "validate_frontend": _validate_frontend_find_a_product_using_search_from_homepage,
}


# -----------------------------------------------------------------------------
# Task: search-a-product-from-another-product-page
# -----------------------------------------------------------------------------

def _validate_backend_search_a_product_from_another_product_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_a_product_from_another_product_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-y7z8a9")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for product and navigated to detail page"


_validate_search_a_product_from_another_product_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_a_product_from_another_product_page,
    "validate_frontend": _validate_frontend_search_a_product_from_another_product_page,
}


# -----------------------------------------------------------------------------
# Task: search-using-multi-term-query
# -----------------------------------------------------------------------------

def _validate_backend_search_using_multi_term_query(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_using_multi_term_query(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if "JEEP 衬衫 男" not in search_query and "JEEP" not in search_query:
        return 0.0, f"searchQuery='{search_query}' expected to contain 'JEEP 衬衫 男'"
    return 1.0, "Successfully searched with multi-term query"


_validate_search_using_multiterm_query: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_multi_term_query,
    "validate_frontend": _validate_frontend_search_using_multi_term_query,
}


# -----------------------------------------------------------------------------
# Task: search-from-search-history
# -----------------------------------------------------------------------------

def _validate_backend_search_from_search_history(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_from_search_history(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    history_items = ["漂亮的裙子", "历史记录", "京东品酒会"]
    if not any(item in search_query for item in history_items):
        return 0.0, f"searchQuery='{search_query}' expected from history {history_items}"
    return 1.0, "Successfully searched from search history"


_validate_search_from_search_history: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_from_search_history,
    "validate_frontend": _validate_frontend_search_from_search_history,
}


# -----------------------------------------------------------------------------
# Task: search-then-use-history-to-research
# -----------------------------------------------------------------------------

def _validate_backend_search_then_use_history_to_research(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    search_history_data = final_state.get("searchHistory")
    if not isinstance(search_history_data, list) or len(search_history_data) == 0:
        return 0.0, "searchHistory is missing or not a list in backend"
    
    # Check that "华为手机" is in the search history
    huawei_found = any(
        item.get("query") == "华为手机" for item in search_history_data
    )
    if not huawei_found:
        return 0.0, "searchHistory does not contain '华为手机'"
    
    return 1.0, "Backend: Successfully added '华为手机' to search history"


def _validate_frontend_search_then_use_history_to_research(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "华为手机")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched then re-searched using search history"


_validate_search_then_use_history_to_research: ValidateTask = {
    "state_key": {
        "searchHistory": {"collection": "searchHistory", "filter": {"query": "华为手机"}},
    },
    "validate_backend": _validate_backend_search_then_use_history_to_research,
    "validate_frontend": _validate_frontend_search_then_use_history_to_research,
}


# -----------------------------------------------------------------------------
# Task: search-using-suggestion-dropdown
# -----------------------------------------------------------------------------

def _validate_backend_search_using_suggestion_dropdown(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_using_suggestion_dropdown(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if "iPhone" not in search_query:
        return 0.0, f"searchQuery='{search_query}' expected to contain 'iPhone'"
    return 1.0, "Successfully searched using suggestion dropdown"


_validate_search_using_suggestion_dropdown: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_suggestion_dropdown,
    "validate_frontend": _validate_frontend_search_using_suggestion_dropdown,
}


# -----------------------------------------------------------------------------
# Task: search-for-apple-iphone
# -----------------------------------------------------------------------------

def _validate_backend_search_for_apple_iphone(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_apple_iphone(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["Apple", "iPhone"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for Apple iPhone"


_validate_search_for_apple_iphone: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_apple_iphone,
    "validate_frontend": _validate_frontend_search_for_apple_iphone,
}


# -----------------------------------------------------------------------------
# Task: search-for-huafeng-instant-noodles
# -----------------------------------------------------------------------------

def _validate_backend_search_for_huafeng_instant_noodles(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_huafeng_instant_noodles(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["华丰", "方便面"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 华丰方便面"


_validate_search_for_huafeng_instant_noodles: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_huafeng_instant_noodles,
    "validate_frontend": _validate_frontend_search_for_huafeng_instant_noodles,
}


# -----------------------------------------------------------------------------
# Task: search-for-aux-massage-chair
# -----------------------------------------------------------------------------

def _validate_backend_search_for_aux_massage_chair(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_aux_massage_chair(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["奥克斯", "按摩椅"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 奥克斯按摩椅"


_validate_search_for_aux_massage_chair: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_aux_massage_chair,
    "validate_frontend": _validate_frontend_search_for_aux_massage_chair,
}


# -----------------------------------------------------------------------------
# Task: search-for-asd-wok
# -----------------------------------------------------------------------------

def _validate_backend_search_for_asd_wok(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_asd_wok(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains_any(final_state, ["爱仕达", "炒锅"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for 爱仕达炒锅"


_validate_search_for_asd_wok: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_asd_wok,
    "validate_frontend": _validate_frontend_search_for_asd_wok,
}


# -----------------------------------------------------------------------------
# Task: search-for-huoli-28-laundry-detergent
# -----------------------------------------------------------------------------

def _validate_backend_search_for_huoli_28_laundry_detergent(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_for_huoli_28_laundry_detergent(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if "活力28" not in search_query and "洗衣液" not in search_query and "活力 28" not in search_query:
        return 0.0, f"searchQuery='{search_query}' expected to contain '活力28' or '洗衣液'"
    return 1.0, "Successfully searched for 活力28洗衣液"


_validate_search_for_huoli_28_laundry_detergent: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_huoli_28_laundry_detergent,
    "validate_frontend": _validate_frontend_search_for_huoli_28_laundry_detergent,
}


# -----------------------------------------------------------------------------
# Task: search-for-stores
# -----------------------------------------------------------------------------

def _validate_backend_search_for_stores(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for store search"


def _validate_frontend_search_for_stores(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_scope = final_state.get("searchScope", "")
    if search_scope != "店铺":
        return 0.0, f"searchScope='{search_scope}' expected '店铺'"
    ok, error = _check_search_query_contains_any(final_state, ["京东自营", "官方旗舰店"])
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched for stores"


_validate_search_for_stores: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_for_stores,
    "validate_frontend": _validate_frontend_search_for_stores,
}


# -----------------------------------------------------------------------------
# Task: search-clear-history
# -----------------------------------------------------------------------------

def _validate_backend_search_clear_history(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    search_history_data = final_state.get("searchHistory")
    if search_history_data is None:
        return 1.0, "Search history cleared (no data)"
    if isinstance(search_history_data, list) and len(search_history_data) == 0:
        return 1.0, "Search history cleared successfully"
    return 0.0, f"Search history not cleared, found {len(search_history_data) if isinstance(search_history_data, list) else 'invalid'} items"


def _validate_frontend_search_clear_history(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation passed (backend validates history clearing)"


_validate_search_clear_history: ValidateTask = {
    "state_key": {
        "searchHistory": {"collection": "searchHistory", "filter": {}},
    },
    "validate_backend": _validate_backend_search_clear_history,
    "validate_frontend": _validate_frontend_search_clear_history,
}


# -----------------------------------------------------------------------------
# Task: search-using-placeholder
# -----------------------------------------------------------------------------

PLACEHOLDER_SUGGESTIONS = [
    "电脑 显卡",
    "iPhone 15 Pro Max",
    "按摩椅",
    "方便面",
    "洗衣液",
    "炒锅",
    "紫苏酱",
    "男士衬衫",
    "JEEP衬衫",
    "活力28洗衣液",
]


def _validate_backend_search_using_placeholder(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for placeholder search"


def _validate_frontend_search_using_placeholder(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if search_query not in PLACEHOLDER_SUGGESTIONS:
        return 0.0, f"searchQuery='{search_query}' expected one of placeholder suggestions"
    return 1.0, "Successfully searched using placeholder suggestion"


_validate_search_using_placeholder: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_placeholder,
    "validate_frontend": _validate_frontend_search_using_placeholder,
}


# -----------------------------------------------------------------------------
# Task: search-using-arrow-keys
# -----------------------------------------------------------------------------

def _validate_backend_search_using_arrow_keys(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for arrow key search"


def _validate_frontend_search_using_arrow_keys(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "iPhone")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched using arrow key navigation"


_validate_search_using_arrow_keys: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_using_arrow_keys,
    "validate_frontend": _validate_frontend_search_using_arrow_keys,
}


# -----------------------------------------------------------------------------
# Task: search-from-hot-search-link
# -----------------------------------------------------------------------------

HOT_SEARCH_LINKS = [
    "桌面加湿器办公小型",
    "银饰",
    "羽绒服",
    "发热鼠标垫",
    "保暖内衣",
    "手套",
    "暖手宝",
    "围巾",
    "电动车挡风被加厚",
]


def _validate_backend_search_from_hot_search_link(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for hot search link"


def _validate_frontend_search_from_hot_search_link(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    search_query = final_state.get("searchQuery", "")
    if search_query not in HOT_SEARCH_LINKS:
        return 0.0, f"searchQuery='{search_query}' expected one of hot search links"
    return 1.0, "Successfully searched from hot search link"


_validate_search_from_hot_search_link: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_from_hot_search_link,
    "validate_frontend": _validate_frontend_search_from_hot_search_link,
}


# -----------------------------------------------------------------------------
# Task: search-refine-query
# -----------------------------------------------------------------------------

def _validate_backend_search_refine_query_from_results_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search refinement"


def _validate_frontend_search_refine_query_from_results_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "华为手机")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully refined search query"


_validate_search_refine_query_from_results_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_refine_query_from_results_page,
    "validate_frontend": _validate_frontend_search_refine_query_from_results_page,
}


# -----------------------------------------------------------------------------
# Task: search-and-navigate-to-product-detail
# -----------------------------------------------------------------------------

def _validate_backend_search_and_navigate_to_product_detail(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_and_navigate_to_product_detail(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    selected_id = final_state.get("selectedProductId", "")
    if selected_id not in ["prod-q7r8s9", "prod-y1z2a3b4"]:
        return 0.0, f"selectedProductId='{selected_id}' expected 'prod-q7r8s9' or 'prod-y1z2a3b4'"
    ok, error = _check_search_query_contains(final_state, "紫苏酱")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully searched and navigated to product detail"


_validate_search_and_navigate_to_product_detail: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_and_navigate_to_product_detail,
    "validate_frontend": _validate_frontend_search_and_navigate_to_product_detail,
}


# =============================================================================
# FILTER & SORT TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: apply-price-range-filter
# -----------------------------------------------------------------------------

def _validate_backend_apply_price_range_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_price_range_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    price_filter = final_state.get("searchPriceFilter")
    if price_filter is None:
        return 0.0, "searchPriceFilter is null, expected to be set"
    if "min" not in price_filter or "max" not in price_filter:
        return 0.0, f"searchPriceFilter={price_filter} missing 'min' or 'max'"
    
    # Validate the specific min and max values
    min_price = price_filter.get("min")
    max_price = price_filter.get("max")
    if min_price != 100:
        return 0.0, f"searchPriceFilter min={min_price}, expected 100"
    if max_price != 300:
        return 0.0, f"searchPriceFilter max={max_price}, expected 300"
    
    return 1.0, f"Successfully applied price range filter {price_filter}"


_validate_apply_price_range_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_price_range_filter,
    "validate_frontend": _validate_frontend_apply_price_range_filter,
}


# -----------------------------------------------------------------------------
# Task: apply-brand-filter-single-brand
# -----------------------------------------------------------------------------

def _validate_backend_apply_brand_filter_single_brand(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_brand_filter_single_brand(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    brand_filter = final_state.get("searchBrandFilter", [])
    if len(brand_filter) != 1:
        return 0.0, f"searchBrandFilter has {len(brand_filter)} brands, expected 1"
    if brand_filter[0] != "JEEP":
        return 0.0, f"searchBrandFilter={brand_filter} expected ['JEEP']"
    return 1.0, "Successfully applied single brand filter"


_validate_apply_brand_filter_single_brand: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_brand_filter_single_brand,
    "validate_frontend": _validate_frontend_apply_brand_filter_single_brand,
}


# -----------------------------------------------------------------------------
# Task: apply-brand-filter-multiple-brands
# -----------------------------------------------------------------------------

def _validate_backend_apply_brand_filter_multiple_brands(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_brand_filter_multiple_brands(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    brand_filter = final_state.get("searchBrandFilter", [])
    if len(brand_filter) < 2:
        return 0.0, f"searchBrandFilter has {len(brand_filter)} brands, expected at least 2"
    valid_combinations = [{"JEEP", "Apple"}, {"ASD", "AUX"}]
    brand_set = set(brand_filter)
    if not any(brand_set == combo for combo in valid_combinations):
        return 0.0, f"searchBrandFilter={brand_filter} expected ['JEEP', 'Apple'] or ['ASD', 'AUX']"
    return 1.0, f"Successfully applied multiple brand filter {brand_filter}"


_validate_apply_brand_filter_multiple_brands: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_brand_filter_multiple_brands,
    "validate_frontend": _validate_frontend_apply_brand_filter_multiple_brands,
}


# -----------------------------------------------------------------------------
# Task: apply-multiple-filters-price-and-brand
# -----------------------------------------------------------------------------

def _validate_backend_apply_multiple_filters_price_and_brand(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_apply_multiple_filters_price_and_brand(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    price_filter = final_state.get("searchPriceFilter")
    brand_filter = final_state.get("searchBrandFilter", [])
    if price_filter is None:
        return 0.0, "searchPriceFilter is null, expected to be set"
    
    # Validate the specific min and max values
    min_price = price_filter.get("min")
    max_price = price_filter.get("max")
    if min_price != 100:
        return 0.0, f"searchPriceFilter min={min_price}, expected 100"
    if max_price != 300:
        return 0.0, f"searchPriceFilter max={max_price}, expected 300"
    
    if len(brand_filter) == 0:
        return 0.0, "searchBrandFilter is empty, expected at least one brand"
    return 1.0, f"Successfully applied multiple filters (price: {price_filter}, brands: {brand_filter})"


_validate_apply_multiple_filters_price_and_brand: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_apply_multiple_filters_price_and_brand,
    "validate_frontend": _validate_frontend_apply_multiple_filters_price_and_brand,
}


# -----------------------------------------------------------------------------
# Task: clear-price-filter
# -----------------------------------------------------------------------------

def _validate_backend_clear_price_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_clear_price_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    price_filter = final_state.get("searchPriceFilter")
    if price_filter is not None:
        return 0.0, f"searchPriceFilter={price_filter} expected null"
    return 1.0, "Successfully cleared price filter"


_validate_clear_price_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_clear_price_filter,
    "validate_frontend": _validate_frontend_clear_price_filter,
}


# -----------------------------------------------------------------------------
# Task: clear-brand-filter
# -----------------------------------------------------------------------------

def _validate_backend_clear_brand_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for filter"


def _validate_frontend_clear_brand_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    brand_filter = final_state.get("searchBrandFilter", [])
    if len(brand_filter) != 0:
        return 0.0, f"searchBrandFilter={brand_filter} expected empty []"
    return 1.0, "Successfully cleared brand filter"


_validate_clear_brand_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_clear_brand_filter,
    "validate_frontend": _validate_frontend_clear_brand_filter,
}


# -----------------------------------------------------------------------------
# Task: filter-and-navigate-to-product
# -----------------------------------------------------------------------------

def _validate_backend_filter_and_navigate_to_product(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_filter_and_navigate_to_product(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    
    # Check selectedProductId is exactly prod-m4n5o6
    selected_id = final_state.get("selectedProductId")
    if selected_id != "prod-m4n5o6":
        return 0.0, f"selectedProductId is '{selected_id}', expected 'prod-m4n5o6'"
    
    # Check price filter is set with min=100 and max=300
    price_filter = final_state.get("searchPriceFilter")
    if price_filter is None:
        return 0.0, "searchPriceFilter is null, expected to be set with min: 100, max: 300"
    min_price = price_filter.get("min")
    max_price = price_filter.get("max")
    if min_price != 100:
        return 0.0, f"searchPriceFilter min={min_price}, expected 100"
    if max_price != 300:
        return 0.0, f"searchPriceFilter max={max_price}, expected 300"
    
    # Check brand filter contains JEEP
    brand_filter = final_state.get("searchBrandFilter", [])
    if "JEEP" not in brand_filter:
        return 0.0, f"searchBrandFilter is {brand_filter}, expected to contain 'JEEP'"
    
    return 1.0, f"Successfully filtered and navigated to product '{selected_id}' with price filter {price_filter} and brand filter {brand_filter}"


_validate_filter_and_navigate_to_product: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_filter_and_navigate_to_product,
    "validate_frontend": _validate_frontend_filter_and_navigate_to_product,
}


# -----------------------------------------------------------------------------
# Task: sort-by-price-ascending
# -----------------------------------------------------------------------------

def _validate_backend_sort_by_price_ascending(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for sort"


def _validate_frontend_sort_by_price_ascending(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    sort_type = final_state.get("searchSortType")
    if sort_type != "price":
        return 0.0, f"searchSortType='{sort_type}' expected 'price'"
    sort_order = final_state.get("searchSortOrder")
    if sort_order != "asc":
        return 0.0, f"searchSortOrder='{sort_order}' expected 'asc'"
    return 1.0, "Successfully sorted by price ascending"


_validate_sort_by_price_ascending: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_sort_by_price_ascending,
    "validate_frontend": _validate_frontend_sort_by_price_ascending,
}


# -----------------------------------------------------------------------------
# Task: sort-by-price-descending
# -----------------------------------------------------------------------------

def _validate_backend_sort_by_price_descending(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for sort"


def _validate_frontend_sort_by_price_descending(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    sort_type = final_state.get("searchSortType")
    if sort_type != "price":
        return 0.0, f"searchSortType='{sort_type}' expected 'price'"
    sort_order = final_state.get("searchSortOrder")
    if sort_order != "desc":
        return 0.0, f"searchSortOrder='{sort_order}' expected 'desc'"
    return 1.0, "Successfully sorted by price descending"


_validate_sort_by_price_descending: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_sort_by_price_descending,
    "validate_frontend": _validate_frontend_sort_by_price_descending,
}


# -----------------------------------------------------------------------------
# Task: sort-by-sales
# -----------------------------------------------------------------------------

def _validate_backend_sort_by_sales(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for sort"


def _validate_frontend_sort_by_sales(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "search")
    if not ok:
        return 0.0, error
    sort_type = final_state.get("searchSortType")
    if sort_type != "sales":
        return 0.0, f"searchSortType='{sort_type}' expected 'sales'"
    return 1.0, "Successfully sorted by sales"


_validate_sort_by_sales: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_sort_by_sales,
    "validate_frontend": _validate_frontend_sort_by_sales,
}


# =============================================================================
# CART TASKS (Backend validation)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: add-a-product-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_add_a_product_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    return 1.0, "Backend: Successfully added product to cart"


def _validate_frontend_add_a_product_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation skipped (cart data not in UI state)"


_validate_add_a_product_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_a_product_to_cart,
    "validate_frontend": _validate_frontend_add_a_product_to_cart,
}


# -----------------------------------------------------------------------------
# Task: add-a-product-from-search-result-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_add_a_product_from_search_result_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    return 1.0, "Backend: Successfully added product from search to cart"


def _validate_frontend_add_a_product_from_search_result_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    ok, error = _check_selected_product_id(final_state, "prod-m4n5o6")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to product detail page"


_validate_add_a_product_from_search_result_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_a_product_from_search_result_to_cart,
    "validate_frontend": _validate_frontend_add_a_product_from_search_result_to_cart,
}


# -----------------------------------------------------------------------------
# Task: add-an-item-from-the-homepage
# -----------------------------------------------------------------------------

def _validate_backend_add_an_item_from_the_homepage(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-q7r8s9' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    return 1.0, "Backend: Successfully added item from homepage to cart"


def _validate_frontend_add_an_item_from_the_homepage(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on homepage"


_validate_add_an_item_from_the_homepage: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-q7r8s9"}},
    },
    "validate_backend": _validate_backend_add_an_item_from_the_homepage,
    "validate_frontend": _validate_frontend_add_an_item_from_the_homepage,
}


# -----------------------------------------------------------------------------
# Task: add-an-item-with-3-quantity
# -----------------------------------------------------------------------------

def _validate_backend_add_an_item_with_3_quantity(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 3:
        return 0.0, f"Cart item qty={item.get('qty')} expected 3"
    return 1.0, "Backend: Successfully added item with qty 3"


def _validate_frontend_add_an_item_with_3_quantity(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on product page"


_validate_add_an_item_with_3_quantity: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_an_item_with_3_quantity,
    "validate_frontend": _validate_frontend_add_an_item_with_3_quantity,
}


# -----------------------------------------------------------------------------
# Task: add-product-with-specific-variant-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_add_product_with_specific_variant_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 1:
        return 0.0, f"Cart item qty={item.get('qty')} expected 1"
    variants = item.get("selectedVariants", {})
    if variants.get("颜色") != "深蓝" or variants.get("尺码") != "XL":
        return 0.0, f"selectedVariants={variants} expected {{'颜色': '深蓝', '尺码': 'XL'}}"
    return 1.0, "Backend: Successfully added product with specific variant"


def _validate_frontend_add_product_with_specific_variant_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on product page"


_validate_add_product_with_specific_variant_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_add_product_with_specific_variant_to_cart,
    "validate_frontend": _validate_frontend_add_product_with_specific_variant_to_cart,
}


# -----------------------------------------------------------------------------
# Task: select-variant-and-add-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_select_variant_and_add_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) < 2:
        return 0.0, f"Cart should have 2 entries, found {len(cart) if isinstance(cart, list) else 0}"
    
    matching_items = [item for item in cart if item.get("productId") == "prod-m4n5o6"]
    if len(matching_items) != 2:
        return 0.0, f"Expected 2 cart entries for prod-m4n5o6, found {len(matching_items)}"
    
    variant1_found = False
    variant2_found = False
    
    for item in matching_items:
        variants = item.get("selectedVariants", {})
        qty = item.get("qty")
        
        if variants.get("颜色") == "经典黑色" and variants.get("尺码") == "S" and qty == 1:
            variant1_found = True
        elif variants.get("颜色") == "卡其色" and variants.get("尺码") == "XL" and qty == 2:
            variant2_found = True
    
    if not variant1_found:
        return 0.0, "Missing cart entry: qty 1 with variants {颜色: 经典黑色, 尺码: S}"
    if not variant2_found:
        return 0.0, "Missing cart entry: qty 2 with variants {颜色: 卡其色, 尺码: XL}"
    
    return 1.0, "Backend: Successfully added multiple variants to cart"


def _validate_frontend_select_variant_and_add_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "product")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on product page"


_validate_select_variant_and_add_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_select_variant_and_add_to_cart,
    "validate_frontend": _validate_frontend_select_variant_and_add_to_cart,
}


# -----------------------------------------------------------------------------
# Task: remove-one-item-from-cart
# -----------------------------------------------------------------------------

def _validate_backend_remove_one_item_from_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    # Cart can be null or empty list when all items are removed
    if cart is None:
        return 1.0, "Backend: Successfully removed item from cart (cart is null)"
    if not isinstance(cart, list):
        return 0.0, "Cart is not a list or null"
    if len(cart) != 0:
        return 0.0, f"Cart has {len(cart)} items, expected 0"
    return 1.0, "Backend: Successfully removed item from cart"


def _validate_frontend_remove_one_item_from_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation skipped (cart data not in UI state)"


_validate_remove_one_item_from_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {}},
    },
    "validate_backend": _validate_backend_remove_one_item_from_cart,
    "validate_frontend": _validate_frontend_remove_one_item_from_cart,
}


# -----------------------------------------------------------------------------
# Task: remove-multiple-items-in-the-cart
# -----------------------------------------------------------------------------

def _validate_backend_remove_multiple_items_in_the_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    # Cart can be null or empty list when all items are removed
    if cart is None:
        return 1.0, "Backend: Successfully removed all items from cart (cart is null)"
    if not isinstance(cart, list):
        return 0.0, "Cart is not a list or null"
    if len(cart) != 0:
        return 0.0, f"Cart has {len(cart)} items, expected 0"
    return 1.0, "Backend: Successfully removed all items from cart"


def _validate_frontend_remove_multiple_items_in_the_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_remove_multiple_items_in_the_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {}},
    },
    "validate_backend": _validate_backend_remove_multiple_items_in_the_cart,
    "validate_frontend": _validate_frontend_remove_multiple_items_in_the_cart,
}


# -----------------------------------------------------------------------------
# Task: reduce-an-item-quantity-in-the-cart
# -----------------------------------------------------------------------------

def _validate_backend_reduce_an_item_quantity_in_the_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    item = cart[0]
    if item.get("qty") != 2:
        return 0.0, f"Cart item qty={item.get('qty')} expected 2"
    return 1.0, "Backend: Successfully reduced item quantity to 2"


def _validate_frontend_reduce_an_item_quantity_in_the_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "Frontend validation skipped (cart data not in UI state)"


_validate_reduce_an_item_quantity_in_the_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-m4n5o6"}},
    },
    "validate_backend": _validate_backend_reduce_an_item_quantity_in_the_cart,
    "validate_frontend": _validate_frontend_reduce_an_item_quantity_in_the_cart,
}


# -----------------------------------------------------------------------------
# Task: increase-an-item-and-reduce-another-item
# -----------------------------------------------------------------------------

def _validate_backend_increase_an_item_and_reduce_another_item(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    
    item1 = next((i for i in cart if i.get("productId") == "prod-m4n5o6"), None)
    if not item1:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    if item1.get("qty") != 4:
        return 0.0, f"Cart item prod-m4n5o6 qty={item1.get('qty')} expected 4"
    
    item2 = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item2:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    if item2.get("qty") != 1:
        return 0.0, f"Cart item prod-y7z8a9 qty={item2.get('qty')} expected 1"
    
    return 1.0, "Backend: Successfully increased one item and reduced another"


def _validate_frontend_increase_an_item_and_reduce_another_item(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_increase_an_item_and_reduce_another_item: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-m4n5o6", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_increase_an_item_and_reduce_another_item,
    "validate_frontend": _validate_frontend_increase_an_item_and_reduce_another_item,
}


# -----------------------------------------------------------------------------
# Task: search-and-add-two-items-to-cart
# -----------------------------------------------------------------------------

def _validate_backend_search_and_add_two_items_to_cart(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    if len(cart) < 2:
        return 0.0, f"Cart has {len(cart)} items, expected at least 2"
    
    item1 = next((i for i in cart if i.get("productId") == "prod-m4n5o6"), None)
    if not item1:
        return 0.0, "Cart item with productId 'prod-m4n5o6' not found in backend"
    if item1.get("qty") != 3:
        return 0.0, f"Cart item prod-m4n5o6 qty={item1.get('qty')} expected 3"
    
    item2 = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item2:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    if item2.get("qty") != 3:
        return 0.0, f"Cart item prod-y7z8a9 qty={item2.get('qty')} expected 3"
    
    return 1.0, "Backend: Successfully added two items with qty 3 each"


def _validate_frontend_search_and_add_two_items_to_cart(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_search_and_add_two_items_to_cart: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-m4n5o6", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_search_and_add_two_items_to_cart,
    "validate_frontend": _validate_frontend_search_and_add_two_items_to_cart,
}


# -----------------------------------------------------------------------------
# Task: search-and-add-item-to-cart-and-back-to-home
# -----------------------------------------------------------------------------

def _validate_backend_search_and_add_item_to_cart_and_back_to_home(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list) or len(cart) == 0:
        return 0.0, "Cart item with productId 'prod-q7r8s9' not found in backend"
    return 1.0, "Backend: Successfully added item to cart"


def _validate_frontend_search_and_add_item_to_cart_and_back_to_home(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "home")
    if not ok:
        return 0.0, error
    ok, error = _check_search_query_contains(final_state, "紫苏酱新")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on homepage with search query"


_validate_search_and_add_item_to_cart_and_back_to_home: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": "prod-q7r8s9"}},
    },
    "validate_backend": _validate_backend_search_and_add_item_to_cart_and_back_to_home,
    "validate_frontend": _validate_frontend_search_and_add_item_to_cart_and_back_to_home,
}


# -----------------------------------------------------------------------------
# Task: remove-item-from-cart-then-search-and-add-item
# -----------------------------------------------------------------------------

def _validate_backend_remove_item_from_cart_then_search_and_add_item(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    if len(cart) != 1:
        return 0.0, f"Cart has {len(cart)} items, expected 1"
    
    item = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    
    # Verify the old item is not in cart
    old_item = next((i for i in cart if i.get("productId") == "prod-m4n5o6"), None)
    if old_item:
        return 0.0, "Cart still contains prod-m4n5o6, expected it to be removed"
    
    return 1.0, "Backend: Successfully removed old item and added new item"


def _validate_frontend_remove_item_from_cart_then_search_and_add_item(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_remove_item_from_cart_then_search_and_add_item: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-m4n5o6", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_remove_item_from_cart_then_search_and_add_item,
    "validate_frontend": _validate_frontend_remove_item_from_cart_then_search_and_add_item,
}


# -----------------------------------------------------------------------------
# Task: use-homepage-to-navigate-and-add-items
# -----------------------------------------------------------------------------

def _validate_backend_use_homepage_to_navigate_and_add_items(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    cart = final_state.get("cart")
    if not isinstance(cart, list):
        return 0.0, "Cart array missing in backend state"
    if len(cart) < 2:
        return 0.0, f"Cart has {len(cart)} items, expected at least 2"
    
    item1 = next((i for i in cart if i.get("productId") == "prod-k1l2m3"), None)
    if not item1:
        return 0.0, "Cart item with productId 'prod-k1l2m3' not found in backend"
    
    item2 = next((i for i in cart if i.get("productId") == "prod-y7z8a9"), None)
    if not item2:
        return 0.0, "Cart item with productId 'prod-y7z8a9' not found in backend"
    
    return 1.0, "Backend: Successfully added two items from homepage"


def _validate_frontend_use_homepage_to_navigate_and_add_items(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_page(final_state, "cart")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully on cart page"


_validate_use_homepage_to_navigate_and_add_items: ValidateTask = {
    "state_key": {
        "cart": {"collection": "cart", "filter": {"productId": {"$in": ["prod-k1l2m3", "prod-y7z8a9"]}}},
    },
    "validate_backend": _validate_backend_use_homepage_to_navigate_and_add_items,
    "validate_frontend": _validate_frontend_use_homepage_to_navigate_and_add_items,
}


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================

REWARD_FUNCTIONS_JD_V2: Dict[str, ValidateTask] = {
    # Navigation Tasks
    "_validate_go_to_the_cart_page_from_the_homepage": _validate_go_to_the_cart_page_from_the_homepage,
    "_validate_go_to_a_product_page_from_home": _validate_go_to_a_product_page_from_home,
    "_validate_go_to_homepage_from_product_page": _validate_go_to_homepage_from_product_page,
    "_validate_go_to_cart_page_from_product_detail_page": _validate_go_to_cart_page_from_product_detail_page,
    "_validate_go_to_product_detail_from_search": _validate_go_to_product_detail_from_search,
    "_validate_navigate_from_cart_back_to_homepage": _validate_navigate_from_cart_back_to_homepage,
    "_validate_navigate_from_search_to_homepage": _validate_navigate_from_search_to_homepage,
    "_validate_navigate_to_cart_from_product_page_via_header": _validate_navigate_to_cart_from_product_page_via_header,
    "_validate_navigate_to_cart_from_search_page": _validate_navigate_to_cart_from_search_page,
    "_validate_navigate_from_product_to_another_product": _validate_navigate_from_product_to_another_product,
    "_validate_navigate_to_product_from_homepage_section": _validate_navigate_to_product_from_homepage_section,
    "_validate_navigate_via_category_sidebar_appliances": _validate_navigate_via_category_sidebar_appliances,
    "_validate_navigate_via_category_sidebar_electronics": _validate_navigate_via_category_sidebar_electronics,
    "_validate_multistep_navigation_home_to_product_to_cart": _validate_multistep_navigation_home_to_product_to_cart,
    "_validate_navigate_to_store_page": _validate_navigate_to_store_page,
    "_validate_filter_homepage_feed_by_category": _validate_filter_homepage_feed_by_category,
    # Search Tasks
    "_validate_search_jeep_shirt": _validate_search_jeep_shirt,
    "_validate_find_a_product_using_search_from_homepage": _validate_find_a_product_using_search_from_homepage,
    "_validate_search_a_product_from_another_product_page": _validate_search_a_product_from_another_product_page,
    "_validate_search_using_multiterm_query": _validate_search_using_multiterm_query,
    "_validate_search_from_search_history": _validate_search_from_search_history,
    "_validate_search_then_use_history_to_research": _validate_search_then_use_history_to_research,
    "_validate_search_using_suggestion_dropdown": _validate_search_using_suggestion_dropdown,
    "_validate_search_for_apple_iphone": _validate_search_for_apple_iphone,
    "_validate_search_for_huafeng_instant_noodles": _validate_search_for_huafeng_instant_noodles,
    "_validate_search_for_aux_massage_chair": _validate_search_for_aux_massage_chair,
    "_validate_search_for_asd_wok": _validate_search_for_asd_wok,
    "_validate_search_for_huoli_28_laundry_detergent": _validate_search_for_huoli_28_laundry_detergent,
    "_validate_search_for_stores": _validate_search_for_stores,
    "_validate_search_clear_history": _validate_search_clear_history,
    "_validate_search_using_placeholder": _validate_search_using_placeholder,
    "_validate_search_using_arrow_keys": _validate_search_using_arrow_keys,
    "_validate_search_from_hot_search_link": _validate_search_from_hot_search_link,
    "_validate_search_refine_query_from_results_page": _validate_search_refine_query_from_results_page,
    "_validate_search_and_navigate_to_product_detail": _validate_search_and_navigate_to_product_detail,
    # Filter & Sort Tasks
    "_validate_apply_price_range_filter": _validate_apply_price_range_filter,
    "_validate_apply_brand_filter_single_brand": _validate_apply_brand_filter_single_brand,
    "_validate_apply_brand_filter_multiple_brands": _validate_apply_brand_filter_multiple_brands,
    "_validate_apply_multiple_filters_price_and_brand": _validate_apply_multiple_filters_price_and_brand,
    "_validate_clear_price_filter": _validate_clear_price_filter,
    "_validate_clear_brand_filter": _validate_clear_brand_filter,
    "_validate_filter_and_navigate_to_product": _validate_filter_and_navigate_to_product,
    "_validate_sort_by_price_ascending": _validate_sort_by_price_ascending,
    "_validate_sort_by_price_descending": _validate_sort_by_price_descending,
    "_validate_sort_by_sales": _validate_sort_by_sales,
    # Cart Tasks
    "_validate_add_a_product_to_cart": _validate_add_a_product_to_cart,
    "_validate_add_a_product_from_search_result_to_cart": _validate_add_a_product_from_search_result_to_cart,
    "_validate_add_an_item_from_the_homepage": _validate_add_an_item_from_the_homepage,
    "_validate_add_an_item_with_3_quantity": _validate_add_an_item_with_3_quantity,
    "_validate_add_product_with_specific_variant_to_cart": _validate_add_product_with_specific_variant_to_cart,
    "_validate_select_variant_and_add_to_cart": _validate_select_variant_and_add_to_cart,
    "_validate_remove_one_item_from_cart": _validate_remove_one_item_from_cart,
    "_validate_remove_multiple_items_in_the_cart": _validate_remove_multiple_items_in_the_cart,
    "_validate_reduce_an_item_quantity_in_the_cart": _validate_reduce_an_item_quantity_in_the_cart,
    "_validate_increase_an_item_and_reduce_another_item": _validate_increase_an_item_and_reduce_another_item,
    "_validate_search_and_add_two_items_to_cart": _validate_search_and_add_two_items_to_cart,
    "_validate_search_and_add_item_to_cart_and_back_to_home": _validate_search_and_add_item_to_cart_and_back_to_home,
    "_validate_remove_item_from_cart_then_search_and_add_item": _validate_remove_item_from_cart_then_search_and_add_item,
    "_validate_use_homepage_to_navigate_and_add_items": _validate_use_homepage_to_navigate_and_add_items,
}


__all__ = [
    "REWARD_FUNCTIONS_JD_V2",
    "ValidateTask",
    "StateKey",
    "StateKeyQuery",
]

