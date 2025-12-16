"""
Reward functions for Xiaohongshu (Little Red Book) app tasks - V2 Architecture.

This version includes both frontend and backend validation with bundled reward functions.
Each task exports a bundle containing:
  - state_key: Dict defining backend queries (collection + filter)
  - validate_backend: Function (state_key, final_state) -> (float, str)
  - validate_frontend: Function (initial_state, final_state) -> (float, str)
"""

import logging
import re
from typing import Any, Callable, Dict, Optional, Tuple, TypedDict

logger = logging.getLogger(__name__)

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


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
# BATCH 1: Navigation & UI State Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: access-creative-center-page-v2
# -----------------------------------------------------------------------------

def _validate_backend_access_creative_center_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # No backend state changes for this navigation task
    return 1.0, "No backend validation required for creative center navigation"


def _validate_frontend_access_creative_center_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    return 1.0, "Creative center opened via publish entry point"


_validate_access_creative_center_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_access_creative_center_page,
    "validate_frontend": _validate_frontend_access_creative_center_page,
}


# -----------------------------------------------------------------------------
# Task: album-view-v2
# -----------------------------------------------------------------------------

def _validate_backend_album_view(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # No backend state changes for this navigation task
    return 1.0, "No backend validation required for album view navigation"


def _validate_frontend_album_view(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    for field, expected in (("page", "profile"), ("previousPage", "explore"), ("profileView", "bookmarks")):
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Profile bookmarks view is visible from album grid"


_validate_album_view: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_album_view,
    "validate_frontend": _validate_frontend_album_view,
}


# -----------------------------------------------------------------------------
# Task: back-page-v2
# -----------------------------------------------------------------------------

def _validate_backend_back_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for back page navigation"


def _validate_frontend_back_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "album":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'album'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Returned to profile from album view using back navigation"


_validate_back_page: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_back_page,
    "validate_frontend": _validate_frontend_back_page,
}


# -----------------------------------------------------------------------------
# Task: bookmarks-view-v2
# -----------------------------------------------------------------------------

def _validate_backend_bookmarks_view(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for bookmarks view navigation"


def _validate_frontend_bookmarks_view(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("profileView") != "bookmarks":
        return 0.0, f"profileView={final_state.get('profileView')} expected 'bookmarks'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Viewing current user's bookmarks"


_validate_bookmarks_view: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_bookmarks_view,
    "validate_frontend": _validate_frontend_bookmarks_view,
}


# -----------------------------------------------------------------------------
# Task: business-hover-v2
# -----------------------------------------------------------------------------

def _validate_backend_business_hover(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for hover state"


def _validate_frontend_business_hover(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    hover_state = final_state.get("navbarHoverState")
    if not isinstance(hover_state, dict):
        return 0.0, "navbarHoverState missing or not an object"
    if hover_state.get("business") is not True:
        return 0.0, "navbarHoverState.business is not true"
    return 1.0, "Business dropdown is open via hover"


_validate_business_hover: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_business_hover,
    "validate_frontend": _validate_frontend_business_hover,
}


# -----------------------------------------------------------------------------
# Task: creative-center-hover-v2
# -----------------------------------------------------------------------------

def _validate_backend_creative_center_hover(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for hover state"


def _validate_frontend_creative_center_hover(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    hover_state = final_state.get("navbarHoverState")
    if not isinstance(hover_state, dict):
        return 0.0, "navbarHoverState missing or not an object"
    if hover_state.get("creative") is not True:
        return 0.0, "navbarHoverState.creative is not true"
    return 1.0, "Creative center hover modal is visible"


_validate_creative_center_hover: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_creative_center_hover,
    "validate_frontend": _validate_frontend_creative_center_hover,
}


# -----------------------------------------------------------------------------
# Task: creative-dashboard-v2
# -----------------------------------------------------------------------------

def _validate_backend_creative_dashboard(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for creative dashboard navigation"


def _validate_frontend_creative_dashboard(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("creativeSidebarNav") != "home":
        return 0.0, f"creativeSidebarNav={final_state.get('creativeSidebarNav')} expected 'home'"
    if final_state.get("creativeView") != "home":
        return 0.0, f"creativeView={final_state.get('creativeView')} expected 'home'"
    return 1.0, "Creative dashboard is visible with the Home tab selected"


_validate_creative_dashboard: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_creative_dashboard,
    "validate_frontend": _validate_frontend_creative_dashboard,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-v2
# -----------------------------------------------------------------------------

def _validate_backend_dark_mode(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_dark_mode(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"
    return 1.0, "Theme set to dark mode"


_validate_dark_mode: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_dark_mode,
    "validate_frontend": _validate_frontend_dark_mode,
}


# -----------------------------------------------------------------------------
# Task: light-mode-v2
# -----------------------------------------------------------------------------

def _validate_backend_light_mode(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_light_mode(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("themeMode") != "light":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'light'"
    return 1.0, "Theme set to light mode"


_validate_light_mode: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_light_mode,
    "validate_frontend": _validate_frontend_light_mode,
}


# -----------------------------------------------------------------------------
# Task: system-theme-v2
# -----------------------------------------------------------------------------

def _validate_backend_system_theme(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_system_theme(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("themeMode") != "system":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'system'"
    return 1.0, "Theme set to follow system setting"


_validate_system_theme: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_system_theme,
    "validate_frontend": _validate_frontend_system_theme,
}


# -----------------------------------------------------------------------------
# Task: likes-view-v2
# -----------------------------------------------------------------------------

def _validate_backend_likes_view(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for likes view navigation"


def _validate_frontend_likes_view(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("profileView") != "likes":
        return 0.0, f"profileView={final_state.get('profileView')} expected 'likes'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Viewing current user's liked posts"


_validate_likes_view: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_likes_view,
    "validate_frontend": _validate_frontend_likes_view,
}


# -----------------------------------------------------------------------------
# Task: navigate-own-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_own_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for profile navigation"


def _validate_frontend_navigate_own_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page is {final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "0":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '0'"
    return 1.0, "Navigated to current user's profile"


_validate_navigate_own_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_own_profile,
    "validate_frontend": _validate_frontend_navigate_own_profile,
}


# -----------------------------------------------------------------------------
# Task: open-an-album-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_an_album(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for album navigation"


def _validate_frontend_open_an_album(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "album":
        return 0.0, f"page={final_state.get('page')} expected 'album'"
    if final_state.get("previousPage") != "profile":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'profile'"
    if final_state.get("activeAlbumId") != "1764819999139-kaqa0ell41o":
        return 0.0, f"activeAlbumId={final_state.get('activeAlbumId')} expected '1764819999139-kaqa0ell41o'"
    return 1.0, "Opened an album from the profile grid"


_validate_open_an_album: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_an_album,
    "validate_frontend": _validate_frontend_open_an_album,
}


# -----------------------------------------------------------------------------
# Task: open-post-modal-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_post_modal(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for modal opening"


def _validate_frontend_open_post_modal(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if not final_state.get("activePostId"):
        return 0.0, "activePostId is missing or null"
    if final_state.get("isVideoPaused") is True:
        return 0.0, "isVideoPaused is True; expected False while modal open"
    return 1.0, "Opened a post modal with video playing"


_validate_open_post_modal: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_post_modal,
    "validate_frontend": _validate_frontend_open_post_modal,
}


# -----------------------------------------------------------------------------
# Task: open-video-pause-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_video_pause(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for video pause"


def _validate_frontend_open_video_pause(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("activePostId") != "2":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '2'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused after opening post 2"
    return 1.0, "Opened post 2 video and paused it"


_validate_open_video_pause: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_video_pause,
    "validate_frontend": _validate_frontend_open_video_pause,
}


# -----------------------------------------------------------------------------
# Task: search-input-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_input(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search input"


def _validate_frontend_search_input(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("searchQuery") != "hello":
        return 0.0, f"searchQuery={final_state.get('searchQuery')} expected 'hello'"
    return 1.0, "Updated search input to 'hello'"


_validate_search_input: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_input,
    "validate_frontend": _validate_frontend_search_input,
}


# -----------------------------------------------------------------------------
# Task: search-filter-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search filter"


def _validate_frontend_search_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("searchQuery") != "oo":
        return 0.0, f"searchQuery={final_state.get('searchQuery')} expected 'oo'"
    filters = final_state.get("searchAdvancedFilters")
    if not isinstance(filters, dict):
        return 0.0, "searchAdvancedFilters missing or not an object"
    expected = {
        "sortBy": "latest",
        "noteType": "image",
        "publishTime": "year",
        "searchScope": "unseen",
        "location": "any",
    }
    for key, value in expected.items():
        if filters.get(key) != value:
            return 0.0, f"searchAdvancedFilters.{key}={filters.get(key)} expected '{value}'"
    return 1.0, "Search query and filters updated to requested values"


_validate_search_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_filter,
    "validate_frontend": _validate_frontend_search_filter,
}


# -----------------------------------------------------------------------------
# Task: set-filter-v2
# -----------------------------------------------------------------------------

def _validate_backend_set_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for feed filter"


def _validate_frontend_set_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("feedFilter") != "OOTD":
        return 0.0, f"feedFilter={final_state.get('feedFilter')} expected 'OOTD'"
    return 1.0, "Feed filter set to OOTD"


_validate_set_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_set_filter,
    "validate_frontend": _validate_frontend_set_filter,
}


# -----------------------------------------------------------------------------
# Task: share-v2
# -----------------------------------------------------------------------------

def _validate_backend_share(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for share popover"


def _validate_frontend_share(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("sharePopoverPostId") != "1":
        return 0.0, f"sharePopoverPostId={final_state.get('sharePopoverPostId')} expected '1'"
    return 1.0, "Share popover open for post 1"


_validate_share: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_share,
    "validate_frontend": _validate_frontend_share,
}


# -----------------------------------------------------------------------------
# Task: watch-full-video-v2
# -----------------------------------------------------------------------------

def _validate_backend_watch_full_video(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for video watching"


def _validate_frontend_watch_full_video(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("activePostId") != "2":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '2'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused at completion"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching video"
    return 1.0, "Watched post 2 video through completion"


_validate_watch_full_video: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_watch_full_video,
    "validate_frontend": _validate_frontend_watch_full_video,
}


# -----------------------------------------------------------------------------
# Task: find-mention-v2
# -----------------------------------------------------------------------------

def _validate_backend_find_mention(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for finding mention"


def _validate_frontend_find_mention(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "notifications" or final_state.get("previousPage") != "explore":
        return 0.0, (
            f"page={final_state.get('page')} previousPage={final_state.get('previousPage')} expected notifications/explore"
        )
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("highlightCommentId") != "c1":
        return 0.0, f"highlightCommentId={final_state.get('highlightCommentId')} expected 'c1'"
    return 1.0, "Navigated to notifications and opened the mention thread"


_validate_find_mention: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_find_mention,
    "validate_frontend": _validate_frontend_find_mention,
}


# =============================================================================
# BATCH 2: Like/Bookmark/Interaction Tasks (with backend validation)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: like-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"
    
    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user = user_1[0]
    if user.get("likeCount") != 1:
        return 0.0, f"Backend: User 1 likeCount={user.get('likeCount')} expected 1"
    
    return 1.0, "Backend: Post 1 liked successfully"


def _validate_frontend_like_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    return 1.0, "Post 1 modal was opened"


_validate_like_post: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_like_post,
    "validate_frontend": _validate_frontend_like_post,
}


# -----------------------------------------------------------------------------
# Task: unlike-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_unlike_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_10 = final_state.get("post_10")
    if not isinstance(post_10, list) or len(post_10) == 0:
        return 0.0, "Post 10 not found in backend"
    post = post_10[0]
    if post.get("likes") != 0:
        return 0.0, f"Backend: Post 10 likes={post.get('likes')} expected 0"
    
    return 1.0, "Backend: Post 10 unliked successfully"


def _validate_frontend_unlike_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("activePostId") != "3":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '3'"
    return 1.0, "Post 3 modal was opened for unliking"


_validate_unlike_post: ValidateTask = {
    "state_key": {
        "post_10": {"collection": "posts", "filter": {"_id": "10"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_unlike_post,
    "validate_frontend": _validate_frontend_unlike_post,
}


# -----------------------------------------------------------------------------
# Task: bookmark-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_bookmark_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("bookmarks") != 1:
        return 0.0, f"Backend: Post 1 bookmarks={post.get('bookmarks')} expected 1"
    
    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user = user_1[0]
    if user.get("bookmarkedCount") != 1:
        return 0.0, f"Backend: User 1 bookmarkedCount={user.get('bookmarkedCount')} expected 1"
    
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    bookmarks = current_user[0].get("bookmarks")
    if not isinstance(bookmarks, list) or "1" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks={bookmarks} expected to include '1'"
    
    return 1.0, "Backend: Post 1 bookmarked successfully"


def _validate_frontend_bookmark_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Bookmarked post 1 while remaining on explore feed"

_validate_bookmark_post: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_post,
    "validate_frontend": _validate_frontend_bookmark_post,
}


# -----------------------------------------------------------------------------
# Task: like-and-bookmark-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_and_bookmark(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post = post_2[0]
    if post.get("likes") != 1 or post.get("bookmarks") != 1:
        return 0.0, f"Backend: Post 2 likes={post.get('likes')} bookmarks={post.get('bookmarks')} expected 1/1"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    if "2" not in current_user[0].get("likedPosts", []):
        return 0.0, f"Backend: currentUser.likedPosts should contain '2'"
    if "2" not in current_user[0].get("bookmarks", []):
        return 0.0, f"Backend: currentUser.bookmarks should contain '2'"
    
    return 1.0, "Backend: Liked and bookmarked post 2 successfully"


def _validate_frontend_like_and_bookmark(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Frontend validation skipped - data not in UI state
    return 1.0, "Frontend validation skipped (data not in UI state)"

_validate_like_and_bookmark: ValidateTask = {
    "state_key": {
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
        "user_2": {"collection": "users", "filter": {"_id": "2"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_like_and_bookmark,
    "validate_frontend": _validate_frontend_like_and_bookmark,
}


# -----------------------------------------------------------------------------
# Task: like-3-sequential-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_3_sequential(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"
    
    # Check that we have all 3 posts
    if len(posts) < 3:
        return 0.0, f"Expected 3 posts, got {len(posts)}"
    
    for post in posts:
        pid = post.get("_id")
        if post.get("likes") != 1:
            return 0.0, f"Backend: Post {pid} likes={post.get('likes')} expected 1"

    users = final_state.get("users")
    if not isinstance(users, list):
        return 0.0, "Users array missing in backend"
    
    # Check users 1 and 3 (user 2 is the author of post 2, doesn't need validation per original logic)
    for user in users:
        uid = user.get("_id")
        if uid in ("1", "3"):
            if user.get("likeCount") != 1:
                return 0.0, f"Backend: User {uid} likeCount={user.get('likeCount')} expected 1"

    return 1.0, "Backend: Sequentially liked posts 1, 2, and 3"


def _validate_frontend_like_3_sequential(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Sequential likes performed from explore feed"

_validate_like_3_sequential: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["1", "2", "3"]}}},
        "users": {"collection": "users", "filter": {"_id": {"$in": ["1", "2", "3"]}}},
    },
    "validate_backend": _validate_backend_like_3_sequential,
    "validate_frontend": _validate_frontend_like_3_sequential,
}


# -----------------------------------------------------------------------------
# Task: bookmark-and-like-v2
# -----------------------------------------------------------------------------

def _validate_backend_bookmark_and_like(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1 or post.get("bookmarks") != 1:
        return 0.0, (
            f"Backend: Post 1 likes/bookmarks mismatch. likes={post.get('likes')} bookmarks={post.get('bookmarks')} expected 1/1"
        )

    return 1.0, "Backend: Bookmarked and liked post 1"


def _validate_frontend_bookmark_and_like(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    requirements = (
        ("page", "profile"),
        ("previousPage", "explore"),
        ("profileView", "bookmarks"),
        ("profileUserId", "0"),
    )
    for field, expected in requirements:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    return 1.0, "Viewing own bookmark tab while interacting with post 1"

_validate_bookmark_and_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_and_like,
    "validate_frontend": _validate_frontend_bookmark_and_like,
}


# -----------------------------------------------------------------------------
# Task: bookmark-album-v2
# -----------------------------------------------------------------------------

def _validate_backend_bookmark_album(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check posts 8 and 9 have bookmarks
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"

    if len(posts) < 2:
        return 0.0, f"Expected 2 posts (8 and 9), got {len(posts)}"

    for post in posts:
        pid = post.get("_id")
        if post.get("bookmarks") != 1:
            return 0.0, f"Backend: Post {pid} bookmarks={post.get('bookmarks')} expected 1"

    # Check current user has both posts in bookmarks and album "yoo" with post 9
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    user = current_user[0]

    bookmarks = user.get("bookmarks", [])
    if "8" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks should contain '8'"
    if "9" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks should contain '9'"

    # Check for album named "yoo" with post 9 in it
    albums = user.get("albums", [])
    yoo_album = next((a for a in albums if a.get("name") == "yoo"), None)
    if not yoo_album:
        return 0.0, "Backend: currentUser should have an album named 'yoo'"
    if "9" not in yoo_album.get("postIds", []):
        return 0.0, f"Backend: Album 'yoo' should contain post '9'"

    return 1.0, "Backend: Bookmarked posts 8 and 9, album 'yoo' created with post 9"


def _validate_frontend_bookmark_album(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Bookmarked posts from explore feed"

_validate_bookmark_album: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["8", "9"]}}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_album,
    "validate_frontend": _validate_frontend_bookmark_album,
}


# =============================================================================
# BATCH 3: Follow/Unfollow Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: follow-user-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_user(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user1 = user_1[0]
    followers = user1.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 1 followers={followers} expected to include '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list) or "1" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '1'"

    return 1.0, "Backend: Successfully followed user 1"


def _validate_frontend_follow_user(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("profileUserId") != "1":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '1'"
    return 1.0, "Viewing user 1 profile before following"

_validate_follow_user: ValidateTask = {
    "state_key": {
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_follow_user,
    "validate_frontend": _validate_frontend_follow_user,
}


# -----------------------------------------------------------------------------
# Task: unfollow-user-v2
# -----------------------------------------------------------------------------

def _validate_backend_unfollow_user(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user1 = user_1[0]
    followers = user1.get("followers", [])
    if "0" in followers:
        return 0.0, f"Backend: User 1 followers={followers} should not contain '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following", [])
    if "1" in following:
        return 0.0, f"Backend: currentUser.following={following} should not contain '1'"

    return 1.0, "Backend: Successfully unfollowed user 1"


def _validate_frontend_unfollow_user(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("profileUserId", "1"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "On user 1's profile page after unfollowing"

_validate_unfollow_user: ValidateTask = {
    "state_key": {
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_unfollow_user,
    "validate_frontend": _validate_frontend_unfollow_user,
}


# -----------------------------------------------------------------------------
# Task: follow-new-follower-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_new_follower(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    user_15 = final_state.get("user_15")
    if not isinstance(user_15, list) or len(user_15) == 0:
        return 0.0, "User 15 not found in backend"
    new_user = user_15[0]
    followers = new_user.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 15 followers={followers} expected to include '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list) or "15" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '15'"

    return 1.0, "Backend: Followed the new follower"


def _validate_frontend_follow_new_follower(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "notifications" or final_state.get("previousPage") != "explore":
        return 0.0, (
            f"page={final_state.get('page')} previousPage={final_state.get('previousPage')} expected notifications/explore"
        )
    return 1.0, "Following action performed from notifications view"

_validate_follow_new_follower: ValidateTask = {
    "state_key": {
        "user_15": {"collection": "users", "filter": {"_id": "15"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_follow_new_follower,
    "validate_frontend": _validate_frontend_follow_new_follower,
}


# -----------------------------------------------------------------------------
# Task: search-and-follow-all-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_and_follow_all(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    users = final_state.get("users")
    if not isinstance(users, list):
        return 0.0, "Users array missing in backend"
    
    if len(users) < 5:
        return 0.0, f"Expected 5 users, got {len(users)}"
    
    for user in users:
        uid = user.get("_id")
        followers = user.get("followers")
        if not isinstance(followers, list) or "0" not in followers:
            return 0.0, f"Backend: User {uid} followers={followers} expected to include '0'"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list):
        return 0.0, "Backend: currentUser.following is not a list"
    for uid in ("1", "2", "3", "4", "5"):
        if uid not in following:
            return 0.0, f"Backend: currentUser.following={following} expected to include '{uid}'"

    return 1.0, "Backend: Followed all users 1-5"


def _validate_frontend_search_and_follow_all(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Returned to explore page after following all users"

_validate_search_and_follow_all: ValidateTask = {
    "state_key": {
        "users": {"collection": "users", "filter": {"_id": {"$in": ["1", "2", "3", "4", "5"]}}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_and_follow_all,
    "validate_frontend": _validate_frontend_search_and_follow_all,
}


# =============================================================================
# BATCH 4: Comment Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: comment-on-video-v2
# -----------------------------------------------------------------------------

def _validate_backend_comment_on_video(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_4 = final_state.get("post_4")
    if not isinstance(post_4, list) or len(post_4) == 0:
        return 0.0, "Post 4 not found in backend"
    post = post_4[0]
    comments = post.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Backend: Post 4 comments array missing"
    
    # Look for comment with content containing "this cat so cute!"
    found = False
    for comment in comments:
        content = comment.get("content", "")
        if "this cat so cute!" in content.lower():
            found = True
            break
    if not found:
        return 0.0, "Backend: Comment 'this cat so cute!' not found on post 4"

    return 1.0, "Backend: Comment added to post 4"


def _validate_frontend_comment_on_video(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Commented on post 4 from explore feed"

_validate_comment_on_video: ValidateTask = {
    "state_key": {
        "post_4": {"collection": "posts", "filter": {"_id": "4"}},
    },
    "validate_backend": _validate_backend_comment_on_video,
    "validate_frontend": _validate_frontend_comment_on_video,
}


# -----------------------------------------------------------------------------
# Task: comment-on-two-separate-posts-v2
# -----------------------------------------------------------------------------

def _validate_backend_comment_on_two_separate_posts(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post1 = post_1[0]
    comments1 = post1.get("comments", [])
    found1 = any("nice song!" in c.get("content", "").lower() for c in comments1)
    if not found1:
        return 0.0, "Backend: Comment 'nice song!' not found on post 1"

    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post2 = post_2[0]
    comments2 = post2.get("comments", [])
    found2 = any("what the dog doing?" in c.get("content", "").lower() for c in comments2)
    if not found2:
        return 0.0, "Backend: Comment 'what the dog doing?' not found on post 2"

    return 1.0, "Backend: Comments added to posts 1 and 2"


def _validate_frontend_comment_on_two_separate_posts(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Comments added while staying on explore feed"

_validate_comment_on_two_separate_posts: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
    },
    "validate_backend": _validate_backend_comment_on_two_separate_posts,
    "validate_frontend": _validate_frontend_comment_on_two_separate_posts,
}


# -----------------------------------------------------------------------------
# Task: reply-chain-v2
# -----------------------------------------------------------------------------

def _validate_backend_reply_chain(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    comments = post.get("comments", [])
    
    # Should have at least 3 comments including the new reply
    has_nested_reply = any(
        isinstance(c.get("content"), str)
        and c["content"].strip().lower() == "nice"
        and c.get("parentId") == "c1-1"
        for c in comments
    )
    if not has_nested_reply:
        return 0.0, "Backend: Reply with content 'nice' to comment c1-1 not found"

    return 1.0, "Backend: Nested reply added to comment chain"


def _validate_frontend_reply_chain(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    return 1.0, "Reply chain interaction completed on post 1"

_validate_reply_chain: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_reply_chain,
    "validate_frontend": _validate_frontend_reply_chain,
}


# -----------------------------------------------------------------------------
# Task: comment-interaction-series-v2
# -----------------------------------------------------------------------------

def _validate_backend_comment_interaction_series(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    def _get_post(key: str) -> Tuple[Optional[Dict[str, Any]], str]:
        data = final_state.get(key)
        if not isinstance(data, list) or not data:
            return None, f"{key} not found in backend"
        return data[0], ""

    def _require_comment_liked(post: Dict[str, Any], comment_id: str, label: str) -> Tuple[bool, str]:
        comment = next((c for c in post.get("comments", []) if c.get("_id") == comment_id), None)
        if not comment:
            return False, f"{label}: comment {comment_id} not found"
        liked = comment.get("likedBy")
        if not isinstance(liked, list) or "0" not in liked:
            return False, f"{label}: comment {comment_id} likedBy={liked} expected to include '0'"
        return True, ""

    def _require_reply(
        post: Dict[str, Any], *, expected_parent: str, expected_content: str
    ) -> Tuple[bool, str]:
        replies = [
            c
            for c in post.get("comments", [])
            if isinstance(c.get("content"), str)
            and c["content"].strip().lower() == expected_content
            and c.get("parentId") == expected_parent
            and c.get("authorId") == "0"
        ]
        if not replies:
            return False, (
                f"Reply '{expected_content}' to {expected_parent} not found on post {post.get('_id')}"
            )
        return True, ""

    post1, error = _get_post("post_1")
    if not post1:
        return 0.0, error
    ok, error = _require_comment_liked(post1, "c1", "Post 1")
    if not ok:
        return 0.0, error
    ok, error = _require_comment_liked(post1, "seed-1", "Post 1")
    if not ok:
        return 0.0, error
    ok, error = _require_reply(post1, expected_parent="seed-1", expected_content="nice")
    if not ok:
        return 0.0, error

    post2, error = _get_post("post_2")
    if not post2:
        return 0.0, error
    ok, error = _require_comment_liked(post2, "c2", "Post 2")
    if not ok:
        return 0.0, error
    ok, error = _require_reply(post2, expected_parent="c2", expected_content="nice2")
    if not ok:
        return 0.0, error

    post3, error = _get_post("post_3")
    if not post3:
        return 0.0, error
    ok, error = _require_comment_liked(post3, "c3", "Post 3")
    if not ok:
        return 0.0, error
    ok, error = _require_reply(post3, expected_parent="c3", expected_content="nice3")
    if not ok:
        return 0.0, error

    return 1.0, "Backend: Comment interaction series completed"


def _validate_backend_comment_interaction_series_unused(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check post 1: comments c1, c1-1 liked and reply to c1-1
    post1 = final_state.get("post_1")
    if not post1:
        return 0.0, "post_1 not found in final_state"
    comments1 = post1.get("comments", [])
    for cid in ("c1", "c1-1"):
        comment = next((c for c in comments1 if c.get("_id") == cid), None)
        if not comment:
            return 0.0, f"Comment {cid} not found on post 1"
        liked = comment.get("likedBy")
        if not isinstance(liked, list) or "0" not in liked:
            return 0.0, f"Backend: Comment {cid} likedBy={liked} expected to include '0'"

    # Check post 2: comment c2 liked and reply
    post2 = final_state.get("post_2")
    if not post2:
        return 0.0, "post_2 not found in final_state"
    comments2 = post2.get("comments", [])
    comment = next((c for c in comments2 if c.get("_id") == "c2"), None)
    if not comment:
        return 0.0, "Comment c2 not found on post 2"
    liked = comment.get("likedBy")
    if not isinstance(liked, list) or "0" not in liked:
        return 0.0, f"Backend: Comment c2 likedBy={liked} expected to include '0'"

    # Check post 3: comment c3 liked and reply
    post3 = final_state.get("post_3")
    if not post3:
        return 0.0, "post_3 not found in final_state"
    comments3 = post3.get("comments", [])
    comment = next((c for c in comments3 if c.get("_id") == "c3"), None)
    if not comment:
        return 0.0, "Comment c3 not found on post 3"
    liked = comment.get("likedBy")
    if not isinstance(liked, list) or "0" not in liked:
        return 0.0, f"Backend: Comment c3 likedBy={liked} expected to include '0'"

    return 1.0, "Backend: Comment interaction series completed"


def _validate_frontend_comment_interaction_series(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null"
    return 1.0, "Completed comment interactions while returning to explore feed"

_validate_comment_interaction_series: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
        "post_3": {"collection": "posts", "filter": {"_id": "3"}},
    },
    "validate_backend": _validate_backend_comment_interaction_series,
    "validate_frontend": _validate_frontend_comment_interaction_series,
}


# -----------------------------------------------------------------------------
# Task: bookmark-album-comment-reply-v2
# -----------------------------------------------------------------------------

def _validate_backend_bookmark_album_comment_reply(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check current user has bookmark
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    if "8" not in current_user[0].get("bookmarks", []):
        return 0.0, "Backend: currentUser.bookmarks should contain '8'"

    # Check post 8 has the comments with reply chain
    post_8 = final_state.get("post_8")
    if not isinstance(post_8, list) or len(post_8) == 0:
        return 0.0, "Post 8 not found in backend"
    post = post_8[0]

    comments = post.get("comments", [])
    nice_comments = [
        c for c in comments
        if isinstance(c.get("content"), str) and c["content"].strip().lower() == "nice"
    ]
    if len(nice_comments) < 2:
        return 0.0, f"Backend: Post 8 has {len(nice_comments)} 'nice' comments, expected 2"

    # Check that one comment has parentId pointing to another (reply chain)
    nice_comment_ids = {c.get("_id") for c in nice_comments}
    has_reply = any(
        c.get("parentId") and c.get("parentId") in nice_comment_ids
        for c in nice_comments
    )
    if not has_reply:
        return 0.0, "Backend: No reply found - one 'nice' comment should have parentId pointing to the other"

    return 1.0, "Backend: Post 8 bookmarked with comment reply chain"


def _validate_frontend_bookmark_album_comment_reply(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    page_requirements = (
        ("page", "album"),
        ("previousPage", "profile"),
        ("profileView", "bookmarks"),
        ("albumOwnerId", "0"),
    )
    for field, expected in page_requirements:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if not final_state.get("activeAlbumId"):
        return 0.0, "activeAlbumId missing while viewing bookmarks"
    if final_state.get("activePostId") != "8":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '8'"

    return 1.0, "Album bookmarks UI state validated for post 8"

_validate_bookmark_album_comment_reply: ValidateTask = {
    "state_key": {
        "post_8": {"collection": "posts", "filter": {"_id": "8"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_bookmark_album_comment_reply,
    "validate_frontend": _validate_frontend_bookmark_album_comment_reply,
}


# =============================================================================
# BATCH 5: Album & Complex Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: create-album-add-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_album_add(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"
    
    if len(posts) < 2:
        return 0.0, f"Expected 2 posts, got {len(posts)}"
    
    for post in posts:
        pid = post.get("_id")
        if post.get("bookmarks") != 1:
            return 0.0, f"Backend: Post {pid} bookmarks={post.get('bookmarks')} expected 1"

    return 1.0, "Backend: Posts 1 and 2 bookmarked"


def _validate_frontend_create_album_add(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    return 1.0, "Created album while browsing explore feed"

_validate_create_album_add: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["1", "2"]}}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_create_album_add,
    "validate_frontend": _validate_frontend_create_album_add,
}


# -----------------------------------------------------------------------------
# Task: open-album-watch-video-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_album_watch_video(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for video watching"


def _validate_frontend_open_album_watch_video(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "album":
        return 0.0, f"page={final_state.get('page')} expected 'album'"
    if final_state.get("previousPage") != "profile":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'profile'"
    if final_state.get("activeAlbumId") != "1764819999139-kaqa0ell41o":
        return 0.0, f"activeAlbumId={final_state.get('activeAlbumId')} expected '1764819999139-kaqa0ell41o'"
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("isVideoPaused") is not True:
        return 0.0, "Video is not paused after watching album video"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching album video"
    return 1.0, "Opened an album, played post 1, and watched it to completion"


_validate_open_album_watch_video: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_album_watch_video,
    "validate_frontend": _validate_frontend_open_album_watch_video,
}


# -----------------------------------------------------------------------------
# Task: remove-bookmarks-in-album-v2
# -----------------------------------------------------------------------------

def _validate_backend_remove_bookmarks_in_album(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"

    bookmarks = current_user[0].get("bookmarks", [])
    for bid in ["4", "7", "8", "9", "12"]:
        if bid in bookmarks:
            return 0.0, f"Backend: Bookmark {bid} should have been removed"
    return 1.0, "Backend: Bookmarks removed"


def _validate_frontend_remove_bookmarks_in_album(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "album":
        return 0.0, f"page={final_state.get('page')} expected 'album'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null (modal closed)"
    return 1.0, "Album page with modal closed after unbookmarking"

_validate_remove_bookmarks_in_album: ValidateTask = {
    "state_key": {
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_remove_bookmarks_in_album,
    "validate_frontend": _validate_frontend_remove_bookmarks_in_album,
}


# -----------------------------------------------------------------------------
# Task: edit-album-collection-v2
# -----------------------------------------------------------------------------

ALBUM_EDIT_TARGET_ID = "album-0"
ALBUM_EDIT_TARGET_NAME = "私密收藏"
ALBUM_EDIT_TARGET_DESCRIPTION = "这是我的私密专辑"


def _validate_backend_edit_album_collection(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    albums = current_user[0].get("albums", [])
    album = next((a for a in albums or [] if a.get("_id") == ALBUM_EDIT_TARGET_ID), None)
    if not album:
        return 0.0, f"Backend: Album '{ALBUM_EDIT_TARGET_ID}' not found for current user"
    if album.get("name") != ALBUM_EDIT_TARGET_NAME:
        return 0.0, f"Backend: Album name='{album.get('name')}' expected '{ALBUM_EDIT_TARGET_NAME}'"
    if album.get("description") != ALBUM_EDIT_TARGET_DESCRIPTION:
        return 0.0, (
            f"Backend: Album description='{album.get('description')}' "
            f"expected '{ALBUM_EDIT_TARGET_DESCRIPTION}'"
        )
    if album.get("isPublic") is not False:
        return 0.0, f"Backend: Album isPublic={album.get('isPublic')} expected False"
    return 1.0, "Backend: Album renamed, updated description, and set to private"


def _validate_frontend_edit_album_collection(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    requirements = (
        ("page", "album"),
        ("previousPage", "profile"),
        ("profileView", "bookmarks"),
        ("profileUserId", "0"),
        ("albumOwnerId", "0"),
    )
    for field, expected in requirements:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if final_state.get("activeAlbumId") not in (ALBUM_EDIT_TARGET_ID, "album-0"):
        return 0.0, f"activeAlbumId={final_state.get('activeAlbumId')} expected '{ALBUM_EDIT_TARGET_ID}'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null"
    return 1.0, "Album editor open for the current user's bookmarks collection"


_validate_edit_album_collection: ValidateTask = {
    "state_key": {
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_edit_album_collection,
    "validate_frontend": _validate_frontend_edit_album_collection,
}


# -----------------------------------------------------------------------------
# Task: draft-article-v2
# -----------------------------------------------------------------------------

def _validate_backend_draft_article(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    drafts = final_state.get("drafts")
    if not isinstance(drafts, list):
        return 0.0, "Backend: drafts array missing"
    
    for draft in drafts:
        if draft.get("title") == "Hi" and draft.get("content") == "wow" and draft.get("type") == "article":
            return 1.0, "Backend: Article draft 'Hi' with content 'wow' saved"
    
    return 0.0, "Backend: No article draft with title 'Hi' and content 'wow' found"


def _validate_frontend_draft_article(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("creativePublishTab") != "article":
        return 0.0, f"creativePublishTab={final_state.get('creativePublishTab')} expected 'article'"
    if final_state.get("creativeView") not in ("text-editor", "dashboard"):
        return 0.0, f"creativeView={final_state.get('creativeView')} expected 'text-editor' or 'dashboard'"

    return 1.0, "Article editor UI state validated"


_validate_draft_article: ValidateTask = {
    "state_key": {
        "drafts": {"collection": "drafts", "filter": {"userId": "0"}},
    },
    "validate_backend": _validate_backend_draft_article,
    "validate_frontend": _validate_frontend_draft_article,
}


# -----------------------------------------------------------------------------
# Task: edit-draft-v2
# -----------------------------------------------------------------------------

def _validate_backend_edit_draft(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    drafts = final_state.get("drafts")
    if not isinstance(drafts, list):
        return 0.0, "Backend: drafts array missing"

    for draft in drafts:
        if not isinstance(draft, dict):
            continue
        title = (draft.get("title") or "").strip()
        content = (draft.get("content") or "").strip()
        if (
            draft.get("type") == "article"
            and draft.get("userId") == "0"
            and title.lower() == "new draft"
            and content.lower() == "new body"
        ):
            return 1.0, "Backend: Article draft updated to 'new draft'"

    return 0.0, "Backend: Edited article draft with title 'new draft' not found"


def _validate_frontend_edit_draft(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("pageDisplayState") != "creative":
        return 0.0, f"pageDisplayState={final_state.get('pageDisplayState')} expected 'creative'"
    if final_state.get("creativePublishTab") != "article":
        return 0.0, f"creativePublishTab={final_state.get('creativePublishTab')} expected 'article'"
    if final_state.get("creativeView") != "dashboard":
        return 0.0, f"creativeView={final_state.get('creativeView')} expected 'dashboard'"
    return 1.0, "Edited draft saved while viewing the creative dashboard"


_validate_edit_draft: ValidateTask = {
    "state_key": {
        "drafts": {"collection": "drafts", "filter": {"userId": "0"}},
    },
    "validate_backend": _validate_backend_edit_draft,
    "validate_frontend": _validate_frontend_edit_draft,
}


# =============================================================================
# BATCH 6: Search & Multi-Action Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: clear-search-history-v2
# -----------------------------------------------------------------------------

def _validate_backend_clear_search_history(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    history = final_state.get("searchHistory")
    if history is None:
        return 1.0, "Backend: Search history cleared"
    if not isinstance(history, list):
        return 0.0, "Backend: searchHistory is not a list"
    if history:
        return 0.0, f"Backend: searchHistory still has {len(history)} entries"
    return 1.0, "Backend: Search history cleared"


def _validate_frontend_clear_search_history(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    if final_state.get("previousPage") != "search":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'search'"
    if final_state.get("searchQuery"):
        return 0.0, f"searchQuery='{final_state.get('searchQuery')}' expected empty string"
    return 1.0, "Cleared search history while remaining on explore feed"


_validate_clear_search_history: ValidateTask = {
    "state_key": {
        "searchHistory": {"collection": "searchHistory", "filter": {"userId": "0"}},
    },
    "validate_backend": _validate_backend_clear_search_history,
    "validate_frontend": _validate_frontend_clear_search_history,
}


# -----------------------------------------------------------------------------
# Task: search-and-like-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_and_like(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    user_1 = final_state.get("user_1")
    if not isinstance(user_1, list) or len(user_1) == 0:
        return 0.0, "User 1 not found in backend"
    user1 = user_1[0]
    if user1.get("likeCount") != 1:
        return 0.0, f"Backend: User 1 likeCount={user1.get('likeCount')} expected 1"

    return 1.0, "Backend: Searched and liked post 1"


def _validate_frontend_search_and_like(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    search_query = final_state.get("searchQuery")
    active_post = final_state.get("activePostId")
    if search_query != "手势舞一枚" and active_post != "1":
        return 0.0, f"searchQuery={search_query} or activePostId={active_post} expected search '手势舞一枚' or post '1' opened"
    return 1.0, "Searched and liked post 1"

_validate_search_and_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_search_and_like,
    "validate_frontend": _validate_frontend_search_and_like,
}


# -----------------------------------------------------------------------------
# Task: search-user-and-like-all-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_user_and_like_all(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check user 2 (妹妹宝) has likeCount == 3
    user_2 = final_state.get("user_2")
    if not isinstance(user_2, list) or len(user_2) == 0:
        return 0.0, "User 2 not found in backend"
    user = user_2[0]
    if user.get("likeCount") != 3:
        return 0.0, f"Backend: User 2 likeCount={user.get('likeCount')} expected 3"
    
    # Check current user has liked posts 12, 23, 24
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    liked_posts = current_user[0].get("likedPosts", [])
    expected_likes = {"12", "23", "24"}
    if not expected_likes.issubset(set(liked_posts)):
        return 0.0, f"Backend: currentUser.likedPosts={liked_posts} should contain ['12', '23', '24']"
    
    # Check that posts 12, 23, 24 each have 1 like
    posts_to_check = [("post_12", "12"), ("post_23", "23"), ("post_24", "24")]
    for post_key, post_id in posts_to_check:
        post_data = final_state.get(post_key)
        if isinstance(post_data, list) and len(post_data) > 0:
            if post_data[0].get("likes") != 1:
                return 0.0, f"Backend: Post {post_id} likes={post_data[0].get('likes')} expected 1"
    
    return 1.0, "Backend: Searched user 2 and liked all their posts"


def _validate_frontend_search_user_and_like_all(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user navigated to user 2's (妹妹宝) profile page
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "2":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '2' (妹妹宝's profile)"
    # After closing all modals, activePostId should be null
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null (all modals closed)"
    return 1.0, "On user 2's profile page with all modals closed after liking posts"

_validate_search_user_and_like_all: ValidateTask = {
    "state_key": {
        "post_12": {"collection": "posts", "filter": {"_id": "12"}},
        "post_23": {"collection": "posts", "filter": {"_id": "23"}},
        "post_24": {"collection": "posts", "filter": {"_id": "24"}},
        "user_2": {"collection": "users", "filter": {"_id": "2"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_user_and_like_all,
    "validate_frontend": _validate_frontend_search_user_and_like_all,
}


# -----------------------------------------------------------------------------
# Task: search-like-unbookmark-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_like_unbookmark(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 1 has 1 like
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    if post_1[0].get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post_1[0].get('likes')} expected 1"
    
    # Check that current user has unbookmarked the post (not in bookmarks)
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    bookmarks = current_user[0].get("bookmarks", [])
    if "1" in bookmarks:
        return 0.0, f"Backend: Post 1 still in currentUser.bookmarks={bookmarks}, should be removed"
    
    return 1.0, "Backend: Post 1 has 1 like and is unbookmarked"


def _validate_frontend_search_like_unbookmark(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("previousPage", "search"),
        ("profileView", "bookmarks"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null (modal closed)"
    return 1.0, "Profile bookmarks view with modal closed after unbookmarking"

_validate_search_like_unbookmark: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_like_unbookmark,
    "validate_frontend": _validate_frontend_search_like_unbookmark,
}


# -----------------------------------------------------------------------------
# Task: search-history-like-v2
# -----------------------------------------------------------------------------

SEARCH_HISTORY_QUERY = "🍂秋天落叶拍照姿势"


def _validate_backend_search_history_like(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_data = final_state.get("post_3")
    if not isinstance(post_data, list) or len(post_data) == 0:
        return 0.0, "Post 3 not found in backend"
    post = post_data[0]
    if post.get("likes", 0) < 1:
        return 0.0, f"Backend: Post 3 likes={post.get('likes')} expected at least 1"
    if post.get("bookmarks", 0) < 1:
        return 0.0, f"Backend: Post 3 bookmarks={post.get('bookmarks')} expected at least 1"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    user = current_user[0]
    liked_posts = user.get("likedPosts", [])
    if "3" not in liked_posts:
        return 0.0, f"Backend: currentUser.likedPosts={liked_posts} expected to include '3'"
    bookmarks = user.get("bookmarks", [])
    if "3" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks={bookmarks} expected to include '3'"

    return 1.0, "Backend: Liked post 3 from search history"


def _validate_frontend_search_history_like(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "search":
        return 0.0, f"page={final_state.get('page')} expected 'search'"
    if final_state.get("previousPage") != "explore":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'explore'"
    if final_state.get("searchQuery") != SEARCH_HISTORY_QUERY:
        return 0.0, f"searchQuery='{final_state.get('searchQuery')}' expected '{SEARCH_HISTORY_QUERY}'"
    if final_state.get("activePostId") != "3":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '3'"
    return 1.0, "Liked bookmarked post 3 while searching via history entry"


_validate_search_history_like: ValidateTask = {
    "state_key": {
        "post_3": {"collection": "posts", "filter": {"_id": "3"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_search_history_like,
    "validate_frontend": _validate_frontend_search_history_like,
}


# -----------------------------------------------------------------------------
# Task: advanced-filter-search-follow-v2
# -----------------------------------------------------------------------------

ADVANCED_SEARCH_QUERY = "咖啡"
ADVANCED_FILTERS_EXPECTED = {
    "sortBy": "mostLikes",
    "noteType": "image",
    "publishTime": "week",
    "searchScope": "following",
    "location": "any",
}
ADVANCED_TARGET_USER_ID = "18"


def _validate_backend_advanced_filter_search_follow(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following", [])
    if not isinstance(following, list) or ADVANCED_TARGET_USER_ID not in following:
        return 0.0, (
            f"Backend: currentUser.following={following} expected to include '{ADVANCED_TARGET_USER_ID}'"
        )

    user_18 = final_state.get("user_18")
    if not isinstance(user_18, list) or len(user_18) == 0:
        return 0.0, "User 18 not found in backend"
    followers = user_18[0].get("followers", [])
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 18 followers={followers} expected to include '0'"

    return 1.0, "Backend: Followed user 18 after applying advanced filters"


def _validate_frontend_advanced_filter_search_follow(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    filters = final_state.get("searchAdvancedFilters")
    if not isinstance(filters, dict):
        return 0.0, "searchAdvancedFilters missing from UI state"
    for key, expected in ADVANCED_FILTERS_EXPECTED.items():
        value = filters.get(key)
        if value != expected:
            return 0.0, f"searchAdvancedFilters.{key}={value} expected '{expected}'"

    page = final_state.get("page")
    if page == "search":
        expectations = (
            ("previousPage", "explore"),
            ("searchQuery", ADVANCED_SEARCH_QUERY),
            ("searchType", "user"),
        )
        for field, expected in expectations:
            value = final_state.get(field)
            if value != expected:
                return 0.0, f"{field}={value} expected '{expected}'"
        return 1.0, "Remained on search page with filters applied while following the user"

    if page == "profile":
        if final_state.get("profileUserId") != ADVANCED_TARGET_USER_ID:
            return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '{ADVANCED_TARGET_USER_ID}'"
        if final_state.get("previousPage") != "search":
            return 0.0, f"previousPage={final_state.get('previousPage')} expected 'search'"
        return 1.0, "Viewing followed user's profile after advanced search follow"

    return 0.0, f"page={page} expected 'search' or 'profile' after advanced search follow"


_validate_advanced_filter_search_follow: ValidateTask = {
    "state_key": {
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
        "user_18": {"collection": "users", "filter": {"_id": ADVANCED_TARGET_USER_ID}},
    },
    "validate_backend": _validate_backend_advanced_filter_search_follow,
    "validate_frontend": _validate_frontend_advanced_filter_search_follow,
}


# -----------------------------------------------------------------------------
# Task: search-own-profile-reply-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_own_profile_reply(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post = post_2[0]
    comments = post.get("comments", [])
    has_reply = any(
        isinstance(c.get("content"), str)
        and c["content"].strip().lower() == "nice"
        and c.get("parentId") == "c2"
        for c in comments
    )
    if not has_reply:
        return 0.0, "Backend: Post 2 is missing reply 'nice' to comment c2"

    return 1.0, "Backend: Reply added to post 2"


def _validate_frontend_search_own_profile_reply(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("previousPage", "search"),
        ("activePostId", "2"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Own profile page with post 2 modal opened for reply"

_validate_search_own_profile_reply: ValidateTask = {
    "state_key": {
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
    },
    "validate_backend": _validate_backend_search_own_profile_reply,
    "validate_frontend": _validate_frontend_search_own_profile_reply,
}


# =============================================================================
# BATCH 7: Dark Mode Combination Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: dark-mode-filter-v2
# -----------------------------------------------------------------------------

def _validate_backend_dark_mode_filter(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for dark mode filter"


def _validate_frontend_dark_mode_filter(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"
    if final_state.get("feedFilter") != "校园日常":
        return 0.0, f"feedFilter={final_state.get('feedFilter')} expected '校园日常'"
    return 1.0, "Dark mode enabled and feed filter set to 校园日常"


_validate_dark_mode_filter: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_dark_mode_filter,
    "validate_frontend": _validate_frontend_dark_mode_filter,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-like-v2
# -----------------------------------------------------------------------------

def _validate_backend_dark_mode_like(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    return 1.0, "Backend: Post 1 liked"


def _validate_frontend_dark_mode_like(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    expectations = (
        ("page", "explore"),
        ("previousPage", "explore"),
        ("themeMode", "dark"),
    )
    for field, expected in expectations:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Dark mode stays enabled while liking post 1 on explore"

_validate_dark_mode_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_dark_mode_like,
    "validate_frontend": _validate_frontend_dark_mode_like,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-notif-like-v2
# -----------------------------------------------------------------------------

def _validate_backend_dark_mode_notif_like(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    comments = post.get("comments", [])
    comment = next((c for c in comments if c.get("_id") == "c1"), None)
    if not comment:
        return 0.0, "Comment c1 not found on post 1"
    liked = comment.get("likedBy")
    if not isinstance(liked, list) or "0" not in liked:
        return 0.0, f"Backend: Comment c1 likedBy={liked} expected to include '0'"

    return 1.0, "Backend: Comment c1 liked"


def _validate_frontend_dark_mode_notif_like(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"
    if final_state.get("page") != "explore" or final_state.get("previousPage") != "notifications":
        return 0.0, (
            f"page={final_state.get('page')} previousPage={final_state.get('previousPage')} expected explore/notifications"
        )
    return 1.0, "Handled notification and returned to explore with dark mode on"

_validate_dark_mode_notif_like: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_dark_mode_notif_like,
    "validate_frontend": _validate_frontend_dark_mode_notif_like,
}


# -----------------------------------------------------------------------------
# Task: dark-mode-search-watch-v2
# -----------------------------------------------------------------------------

def _validate_backend_dark_mode_search_watch(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search and watch"


def _validate_frontend_dark_mode_search_watch(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("themeMode") != "dark":
        return 0.0, f"themeMode={final_state.get('themeMode')} expected 'dark'"

    expected = (("page", "search"), ("previousPage", "explore"), ("searchQuery", "oo"))
    for field, value in expected:
        current = final_state.get(field)
        if current != value:
            return 0.0, f"{field}={current} expected '{value}'"
    if final_state.get("activePostId") != "1":
        return 0.0, f"activePostId={final_state.get('activePostId')} expected '1'"
    if final_state.get("isVideoEnded") is not True:
        return 0.0, "isVideoEnded is not True after watching search result video"
    return 1.0, "Searched for 'oo', switched to dark mode, and watched post 1"


_validate_dark_mode_search_watch: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_dark_mode_search_watch,
    "validate_frontend": _validate_frontend_dark_mode_search_watch,
}


# -----------------------------------------------------------------------------
# Task: filter-comment-profile-dark-v2
# -----------------------------------------------------------------------------

def _validate_backend_filter_comment_profile_dark(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_2 = final_state.get("post_2")
    if not isinstance(post_2, list) or len(post_2) == 0:
        return 0.0, "Post 2 not found in backend"
    post = post_2[0]
    comments = post.get("comments", [])
    found = any("nice" in c.get("content", "").lower() for c in comments)
    if not found:
        return 0.0, "Backend: Comment 'nice' not found on post 2"

    return 1.0, "Backend: Comment added to post 2"


def _validate_frontend_filter_comment_profile_dark(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    expectations = (
        ("page", "profile"),
        ("previousPage", "explore"),
        ("feedFilter", "萌宠日常"),
        ("profileUserId", "0"),
        ("themeMode", "dark"),
    )
    for field, expected in expectations:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Profile view reflects 萌宠日常 filter in dark mode"

_validate_filter_comment_profile_dark: ValidateTask = {
    "state_key": {
        "post_2": {"collection": "posts", "filter": {"_id": "2"}},
    },
    "validate_backend": _validate_backend_filter_comment_profile_dark,
    "validate_frontend": _validate_frontend_filter_comment_profile_dark,
}


# -----------------------------------------------------------------------------
# Task: like-search-follow-dark-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_search_follow_dark(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") != 1:
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 1"

    user_2 = final_state.get("user_2")
    if not isinstance(user_2, list) or len(user_2) == 0:
        return 0.0, "User 2 not found in backend"
    user2 = user_2[0]
    followers = user2.get("followers")
    if not isinstance(followers, list) or followers != ["0"]:
        return 0.0, f"Backend: User 2 followers={followers} expected ['0']"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    following = current_user[0].get("following")
    if not isinstance(following, list) or "2" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '2'"

    return 1.0, "Backend: Liked post 1 and followed user 2"


def _validate_frontend_like_search_follow_dark(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "search"),
        ("previousPage", "explore"),
        ("searchQuery", "妹妹宝"),
        ("searchType", "user"),
        ("themeMode", "dark"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "Liked, searched, followed user, and set dark theme"

_validate_like_search_follow_dark: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "user_2": {"collection": "users", "filter": {"_id": "2"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_like_search_follow_dark,
    "validate_frontend": _validate_frontend_like_search_follow_dark,
}


# =============================================================================
# BATCH 8: Complex Multi-Action Tasks
# =============================================================================

# -----------------------------------------------------------------------------
# Task: comprehensive-user-interaction-v2
# -----------------------------------------------------------------------------

def _validate_backend_comprehensive_user_interaction(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    def _get_entry(key: str, label: str) -> Tuple[Optional[Dict[str, Any]], str]:
        data = final_state.get(key)
        if not isinstance(data, list) or len(data) == 0:
            return None, f"{label} not found in backend"
        return data[0], ""

    post1, error = _get_entry("post_1", "Post 1")
    if not post1:
        return 0.0, error
    if post1.get("likes", 0) < 1:
        return 0.0, f"Backend: Post 1 likes={post1.get('likes')} expected at least 1"
    comments = post1.get("comments", [])
    new_comment = next(
        (
            c
            for c in comments
            if isinstance(c.get("content"), str)
            and c["content"].strip().lower() == "nice"
            and c.get("authorId") == "0"
        ),
        None,
    )
    if not new_comment:
        return 0.0, "Backend: Comment 'nice' from current user not found on post 1"

    post3, error = _get_entry("post_3", "Post 3")
    if not post3:
        return 0.0, error
    if post3.get("likes", 0) < 1:
        return 0.0, f"Backend: Post 3 likes={post3.get('likes')} expected at least 1"
    if post3.get("bookmarks", 0) < 1:
        return 0.0, f"Backend: Post 3 bookmarks={post3.get('bookmarks')} expected at least 1"

    current_user, error = _get_entry("current_user", "Current user")
    if not current_user:
        return 0.0, error
    liked_posts = current_user.get("likedPosts", [])
    if not isinstance(liked_posts, list) or not all(pid in liked_posts for pid in ("1", "3")):
        return 0.0, f"Backend: currentUser.likedPosts={liked_posts} expected to include '1' and '3'"
    bookmarks = current_user.get("bookmarks", [])
    if not isinstance(bookmarks, list) or "3" not in bookmarks:
        return 0.0, f"Backend: currentUser.bookmarks={bookmarks} expected to include '3'"
    following = current_user.get("following", [])
    if not isinstance(following, list) or "1" not in following:
        return 0.0, f"Backend: currentUser.following={following} expected to include '1'"

    user1, error = _get_entry("user_1", "User 1")
    if not user1:
        return 0.0, error
    followers = user1.get("followers", [])
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 1 followers={followers} expected to include '0'"

    return 1.0, "Backend: Comprehensive user interaction completed"


def _validate_frontend_comprehensive_user_interaction(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "explore":
        return 0.0, f"page={final_state.get('page')} expected 'explore'"
    if final_state.get("previousPage") != "profile":
        return 0.0, f"previousPage={final_state.get('previousPage')} expected 'profile'"
    if final_state.get("activePostId") is not None:
        return 0.0, f"activePostId={final_state.get('activePostId')} expected null"
    return 1.0, "Returned to explore after completing comprehensive interactions"

_validate_comprehensive_user_interaction: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "post_3": {"collection": "posts", "filter": {"_id": "3"}},
        "user_1": {"collection": "users", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_comprehensive_user_interaction,
    "validate_frontend": _validate_frontend_comprehensive_user_interaction,
}


# -----------------------------------------------------------------------------
# Task: cross-user-engagement-v2
# -----------------------------------------------------------------------------

def _validate_backend_cross_user_engagement(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_expectations = {
        "1": {"likes": 1},
        "2": {"likes": 1, "bookmarks": 1},
        "3": {"likes": 1},
        "4": {"likes": 1, "bookmarks": 1},
        "5": {"likes": 1},
    }

    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend"
    
    if len(posts) < 5:
        return 0.0, f"Expected 5 posts, got {len(posts)}"
    
    for post in posts:
        pid = post.get("_id")
        if pid in post_expectations:
            expectations = post_expectations[pid]
            for field, expected_value in expectations.items():
                if post.get(field) != expected_value:
                    return 0.0, f"Backend: Post {pid} {field}={post.get(field)} expected {expected_value}"

    user_5 = final_state.get("user_5")
    if not isinstance(user_5, list) or len(user_5) == 0:
        return 0.0, "User 5 not found in backend"
    user5 = user_5[0]
    followers = user5.get("followers")
    if not isinstance(followers, list) or "0" not in followers:
        return 0.0, f"Backend: User 5 followers={followers} expected to include '0'"

    return 1.0, "Backend: Cross-user engagement completed"


def _validate_frontend_cross_user_engagement(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    if final_state.get("page") != "profile":
        return 0.0, f"page={final_state.get('page')} expected 'profile'"
    if final_state.get("profileUserId") != "5":
        return 0.0, f"profileUserId={final_state.get('profileUserId')} expected '5'"
    return 1.0, "Viewing user 5 profile after cross-user engagement"

_validate_cross_user_engagement: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": {"$in": ["1", "2", "3", "4", "5"]}}},
        "user_5": {"collection": "users", "filter": {"_id": "5"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_cross_user_engagement,
    "validate_frontend": _validate_frontend_cross_user_engagement,
}


# -----------------------------------------------------------------------------
# Task: unlike-currentuser-likes-v2
# -----------------------------------------------------------------------------

def _validate_backend_unlike_currentuser_likes(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    post_1 = final_state.get("post_1")
    if not isinstance(post_1, list) or len(post_1) == 0:
        return 0.0, "Post 1 not found in backend"
    post = post_1[0]
    if post.get("likes") not in (0, None):
        return 0.0, f"Backend: Post 1 likes={post.get('likes')} expected 0"

    current_user = final_state.get("current_user")
    if not isinstance(current_user, list) or len(current_user) == 0:
        return 0.0, "Current user not found in backend"
    liked = current_user[0].get("likedPosts")
    if not isinstance(liked, list) or liked:
        return 0.0, f"Backend: currentUser.likedPosts={liked} expected empty list"

    return 1.0, "Backend: Unliked post 1"


def _validate_frontend_unlike_currentuser_likes(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    checks = [
        ("page", "profile"),
        ("profileView", "likes"),
    ]
    for field, expected in checks:
        value = final_state.get(field)
        if value != expected:
            return 0.0, f"{field}={value} expected '{expected}'"
    return 1.0, "On profile likes view after unliking post"

_validate_unlike_currentuser_likes: ValidateTask = {
    "state_key": {
        "post_1": {"collection": "posts", "filter": {"_id": "1"}},
        "current_user": {"collection": "users", "filter": {"_id": "0"}},
    },
    "validate_backend": _validate_backend_unlike_currentuser_likes,
    "validate_frontend": _validate_frontend_unlike_currentuser_likes,
}


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================

REWARD_FUNCTIONS_XIAOHONGSHU_V2: Dict[str, ValidateTask] = {
    # Navigation & UI State Tasks
    "_validate_access_creative_center_page": _validate_access_creative_center_page,
    "_validate_album_view": _validate_album_view,
    "_validate_back_page": _validate_back_page,
    "_validate_bookmarks_view": _validate_bookmarks_view,
    "_validate_business_hover": _validate_business_hover,
    "_validate_creative_center_hover": _validate_creative_center_hover,
    "_validate_creative_dashboard": _validate_creative_dashboard,
    "_validate_dark_mode": _validate_dark_mode,
    "_validate_light_mode": _validate_light_mode,
    "_validate_system_theme": _validate_system_theme,
    "_validate_likes_view": _validate_likes_view,
    "_validate_navigate_own_profile": _validate_navigate_own_profile,
    "_validate_open_an_album": _validate_open_an_album,
    "_validate_open_post_modal": _validate_open_post_modal,
    "_validate_open_video_pause": _validate_open_video_pause,
    "_validate_search_input": _validate_search_input,
    "_validate_search_filter": _validate_search_filter,
    "_validate_set_filter": _validate_set_filter,
    "_validate_share": _validate_share,
    "_validate_watch_full_video": _validate_watch_full_video,
    "_validate_find_mention": _validate_find_mention,
    # Like/Bookmark Tasks
    "_validate_like_post": _validate_like_post,
    "_validate_unlike_post": _validate_unlike_post,
    "_validate_bookmark_post": _validate_bookmark_post,
    "_validate_like_and_bookmark": _validate_like_and_bookmark,
    "_validate_like_3_sequential": _validate_like_3_sequential,
    "_validate_bookmark_and_like": _validate_bookmark_and_like,
    "_validate_bookmark_album": _validate_bookmark_album,
    # Follow/Unfollow Tasks
    "_validate_follow_user": _validate_follow_user,
    "_validate_unfollow_user": _validate_unfollow_user,
    "_validate_follow_new_follower": _validate_follow_new_follower,
    "_validate_search_and_follow_all": _validate_search_and_follow_all,
    # Comment Tasks
    "_validate_comment_on_video": _validate_comment_on_video,
    "_validate_comment_on_two_separate_posts": _validate_comment_on_two_separate_posts,
    "_validate_reply_chain": _validate_reply_chain,
    "_validate_comment_interaction_series": _validate_comment_interaction_series,
    "_validate_bookmark_album_comment_reply": _validate_bookmark_album_comment_reply,
    # Album & Complex Tasks
    "_validate_create_album_add": _validate_create_album_add,
    "_validate_open_album_watch_video": _validate_open_album_watch_video,
    "_validate_remove_bookmarks_in_album": _validate_remove_bookmarks_in_album,
    "_validate_edit_album_collection": _validate_edit_album_collection,
    "_validate_draft_article": _validate_draft_article,
    "_validate_edit_draft": _validate_edit_draft,
    # Search & Multi-Action Tasks
    "_validate_clear_search_history": _validate_clear_search_history,
    "_validate_search_and_like": _validate_search_and_like,
    "_validate_search_user_and_like_all": _validate_search_user_and_like_all,
    "_validate_search_like_unbookmark": _validate_search_like_unbookmark,
    "_validate_search_own_profile_reply": _validate_search_own_profile_reply,
    "_validate_search_history_like": _validate_search_history_like,
    "_validate_advanced_filter_search_follow": _validate_advanced_filter_search_follow,
    # Dark Mode Combination Tasks
    "_validate_dark_mode_filter": _validate_dark_mode_filter,
    "_validate_dark_mode_like": _validate_dark_mode_like,
    "_validate_dark_mode_notif_like": _validate_dark_mode_notif_like,
    "_validate_dark_mode_search_watch": _validate_dark_mode_search_watch,
    "_validate_filter_comment_profile_dark": _validate_filter_comment_profile_dark,
    "_validate_like_search_follow_dark": _validate_like_search_follow_dark,
    # Complex Multi-Action Tasks
    "_validate_comprehensive_user_interaction": _validate_comprehensive_user_interaction,
    "_validate_cross_user_engagement": _validate_cross_user_engagement,
    "_validate_unlike_currentuser_likes": _validate_unlike_currentuser_likes,
    # Aliases for task files that use names without underscores
    "_validate_creativ_edashboard": _validate_creative_dashboard,
    "_validate_clear_search_history": _validate_clear_search_history,
    "_validate_search_history_like": _validate_search_history_like,
    "_validate_edit_draft": _validate_edit_draft,
}
