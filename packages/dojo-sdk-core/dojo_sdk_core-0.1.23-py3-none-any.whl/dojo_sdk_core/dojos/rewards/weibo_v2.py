"""
Reward functions for Weibo SPA tasks - V2 Architecture.

This version includes both frontend and backend validation with bundled reward functions.
Each task exports a bundle containing:
  - state_key: Dict defining backend queries (collection + filter)
  - validate_backend: Function (state_key, final_state) -> (float, str)
  - validate_frontend: Function (initial_state, final_state) -> (float, str)
"""

import logging
import re
from typing import Any, Callable, Dict, Tuple, TypedDict

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

def _check_current_view(final_state: Dict[str, Any], expected_view: str) -> Tuple[bool, str]:
    """Check if the current view matches the expected view."""
    view = final_state.get("currentView")
    if view != expected_view:
        return False, f"currentView='{view}' expected '{expected_view}'"
    return True, ""


def _check_theme(final_state: Dict[str, Any], expected_theme: str) -> Tuple[bool, str]:
    """Check if the theme matches the expected theme."""
    theme = final_state.get("theme")
    if theme != expected_theme:
        return False, f"theme='{theme}' expected '{expected_theme}'"
    return True, ""


def _check_viewed_user_id(final_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    """Check if the viewed user ID matches."""
    viewed_id = final_state.get("viewedUserId")
    if viewed_id != expected_id:
        return False, f"viewedUserId='{viewed_id}' expected '{expected_id}'"
    return True, ""


def _check_viewed_post_id(final_state: Dict[str, Any], expected_id: str) -> Tuple[bool, str]:
    """Check if the viewed post ID matches."""
    viewed_id = final_state.get("viewedPostId")
    if viewed_id != expected_id:
        return False, f"viewedPostId='{viewed_id}' expected '{expected_id}'"
    return True, ""


def _check_search_category(final_state: Dict[str, Any], expected_category: str) -> Tuple[bool, str]:
    """Check if the search category matches."""
    category = final_state.get("searchCategory")
    if category != expected_category:
        return False, f"searchCategory='{category}' expected '{expected_category}'"
    return True, ""

def _check_search_query_equals(final_state: Dict[str, Any], expected_query: str) -> Tuple[bool, str]:
    """Check if the search query equals the expected value."""
    search_query = final_state.get("searchQuery", "")
    if search_query != expected_query:
        return False, f"searchQuery='{search_query}' expected '{expected_query}'"
    return True, ""


def _check_search_dropdown_open(final_state: Dict[str, Any], expected_open: bool) -> Tuple[bool, str]:
    """Check if the search dropdown is open."""
    dropdown_open = final_state.get("searchDropdownOpen", False)
    if dropdown_open != expected_open:
        return False, f"searchDropdownOpen={dropdown_open} expected {expected_open}"
    return True, ""


def _check_search_dropdown_results_empty(final_state: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if the search dropdown results are empty."""
    results = final_state.get("searchDropdownResults", {})
    suggestions = results.get("suggestions", [])
    users = results.get("users", [])
    if suggestions or users:
        return False, f"searchDropdownResults should be empty. suggestions={len(suggestions)}, users={len(users)}"
    return True, ""


def _check_search_dropdown_has_suggestions(final_state: Dict[str, Any], min_count: int = 1) -> Tuple[bool, str]:
    """Check if the search dropdown has suggestions."""
    results = final_state.get("searchDropdownResults", {})
    suggestions = results.get("suggestions", [])
    if len(suggestions) < min_count:
        return False, f"Expected at least {min_count} suggestion(s), got {len(suggestions)}"
    return True, ""


def _check_more_options_dropdown_open(final_state: Dict[str, Any], expected_open: bool) -> Tuple[bool, str]:
    """Check if the more options dropdown is open."""
    dropdown_open = final_state.get("moreOptionsDropdownOpen", False)
    if dropdown_open != expected_open:
        return False, f"moreOptionsDropdownOpen={dropdown_open} expected {expected_open}"
    return True, ""


def _check_feed_post_comments_open(final_state: Dict[str, Any], post_id: str) -> Tuple[bool, str]:
    """Check if a post's inline comments section is open in the feed."""
    displayed_posts = final_state.get("feedDisplayedPosts", [])
    for post in displayed_posts:
        if post.get("_id") == post_id:
            if post.get("isCommentsOpen") is True:
                return True, ""
            return False, f"Post '{post_id}' has isCommentsOpen={post.get('isCommentsOpen')}"
    return False, f"Post '{post_id}' not found in feedDisplayedPosts"


def _check_local_comment_like_override(
    final_state: Dict[str, Any], 
    comment_id: str, 
    expected_liked: bool
) -> Tuple[bool, str]:
    """Check if the comment like override matches the expected state."""
    overrides = final_state.get("localCommentLikeOverrides", {})
    comment_override = overrides.get(comment_id)
    if comment_override is None:
        return False, f"Comment '{comment_id}' not in localCommentLikeOverrides"
    is_liked = comment_override.get("isLiked")
    if is_liked != expected_liked:
        return False, f"Comment '{comment_id}' isLiked={is_liked} expected {expected_liked}"
    return True, ""


def _check_feed_comments_liked(
    final_state: Dict[str, Any], post_id: str, expected_comment_ids: list[str]
) -> Tuple[bool, str]:
    """Ensure specific comments on a feed post are liked (isLiked true).
    
    Checks localCommentLikeOverrides in dojo state (source of truth).
    """
    for comment_id in expected_comment_ids:
        ok, error = _check_local_comment_like_override(final_state, comment_id, True)
        if not ok:
            return False, error
    return True, ""


def _check_viewed_post_comments_liked(
    final_state: Dict[str, Any], expected_comment_ids: list[str]
) -> Tuple[bool, str]:
    """Ensure specific comments on the viewedPost are liked (isLiked true).
    
    Checks localCommentLikeOverrides in dojo state (source of truth).
    """
    for comment_id in expected_comment_ids:
        ok, error = _check_local_comment_like_override(final_state, comment_id, True)
        if not ok:
            return False, error
    return True, ""


def _check_local_post_like_override(
    final_state: Dict[str, Any], 
    post_id: str, 
    expected_liked: bool
) -> Tuple[bool, str]:
    """Check if the post like override matches the expected state."""
    overrides = final_state.get("localPostLikeOverrides", {})
    post_override = overrides.get(post_id)
    if post_override is None:
        return False, f"Post '{post_id}' not in localPostLikeOverrides"
    is_liked = post_override.get("isLiked")
    if is_liked != expected_liked:
        return False, f"Post '{post_id}' isLiked={is_liked} expected {expected_liked}"
    return True, ""

# =============================================================================
# NAVIGATION & SEARCH TASKS (Frontend-only)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: profile-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    # Check that we're viewing a user's profile
    viewed_user_id = final_state.get("viewedUserId")
    if not viewed_user_id:
        return 0.0, "viewedUserId is missing or null"
    
    return 1.0, f"Successfully navigated to profile from search (user: {viewed_user_id})"


_validate_profile_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_search,
    "validate_frontend": _validate_frontend_profile_from_search,
}


# -----------------------------------------------------------------------------
# Task: search-users-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_users(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_search_users(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to search users page"


_validate_search_users: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_users,
    "validate_frontend": _validate_frontend_search_users,
}


# -----------------------------------------------------------------------------
# Task: switch-theme-v2
# -----------------------------------------------------------------------------

def _validate_backend_switch_theme(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for theme change"


def _validate_frontend_switch_theme(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_theme(final_state, "dark")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully switched to dark theme"


_validate_switch_theme: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_switch_theme,
    "validate_frontend": _validate_frontend_switch_theme,
}


# -----------------------------------------------------------------------------
# Task: search-dropdown-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_dropdown_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_search_dropdown_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user13")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to user profile via search dropdown"


_validate_search_dropdown_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_search_dropdown_profile,
    "validate_frontend": _validate_frontend_search_dropdown_profile,
}


# -----------------------------------------------------------------------------
# Task: profile-from-sorted-comments-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_sorted_comments(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_sorted_comments(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user13")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from sorted comments"


_validate_profile_from_sorted_comments: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_sorted_comments,
    "validate_frontend": _validate_frontend_profile_from_sorted_comments,
}


# -----------------------------------------------------------------------------
# Task: view-full-comment-thread-v2
# -----------------------------------------------------------------------------

def _validate_backend_view_full_comment_thread(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for viewing comments"


def _validate_frontend_view_full_comment_thread(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:

    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "5")
    if not ok:
        return 0.0, error
    
    # Check that ViewAllRepliesModal is open (viewAllRepliesModalCommentId is not null)
    view_all_replies_modal_comment_id = final_state.get("viewAllRepliesModalCommentId")
    if view_all_replies_modal_comment_id is None:
        return 0.0, "ViewAllRepliesModal is not open (viewAllRepliesModalCommentId is null)"
    
    return 1.0, f"Successfully viewing full comment thread on post 5 (comment {view_all_replies_modal_comment_id})"


_validate_view_full_comment_thread: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_view_full_comment_thread,
    "validate_frontend": _validate_frontend_view_full_comment_thread,
}


# -----------------------------------------------------------------------------
# Task: video-post-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_video_post_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for viewing post"


def _validate_frontend_video_post_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "23")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to video post from profile"


_validate_video_post_from_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_video_post_from_profile,
    "validate_frontend": _validate_frontend_video_post_from_profile,
}


# -----------------------------------------------------------------------------
# Task: refresh-list-of-trending-topics-v2
# -----------------------------------------------------------------------------

def _validate_backend_refresh_list_of_trending_topics(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # hotSearch is frontend-only state
    return 1.0, "No backend validation required for trending topics refresh"


def _validate_frontend_refresh_list_of_trending_topics(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    init_topics = initial_state.get("mineTrendingTopics") or []
    final_topics = final_state.get("mineTrendingTopics") or []

    if not isinstance(init_topics, list) or not isinstance(final_topics, list):
        return 0.0, "mineTrendingTopics is not a list"

    def topic_ids(topics):
        ids = []
        for t in topics:
            if isinstance(t, dict):
                ids.append(t.get("_id") or t.get("text"))
        return ids

    init_ids = topic_ids(init_topics)
    final_ids = topic_ids(final_topics)

    if not final_ids:
        return 0.0, "mineTrendingTopics is empty after refresh"

    if init_ids and set(init_ids) == set(final_ids):
        return 0.0, "mineTrendingTopics did not change after refresh"

    return 1.0, "Successfully refreshed trending topics"

    

_validate_refresh_list_of_trending_topics: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_refresh_list_of_trending_topics,
    "validate_frontend": _validate_frontend_refresh_list_of_trending_topics,
}


# -----------------------------------------------------------------------------
# Task: refresh-list-of-suggested-users-v2
# -----------------------------------------------------------------------------

def _validate_backend_refresh_list_of_suggested_users(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Backend state doesn't change for suggested users refresh
    # The refresh is a frontend re-query of the same backend data
    suggested = final_state.get("suggestedUsers")
    if not isinstance(suggested, list):
        return 0.0, "suggestedUsers array missing in backend final state"
    
    if len(suggested) == 0:
        return 0.0, "suggestedUsers array is empty"
    
    return 1.0, "Backend: Suggested users data exists"


def _validate_frontend_refresh_list_of_suggested_users(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    init_users = initial_state.get("suggestedUsers") or []
    final_users = final_state.get("suggestedUsers") or []

    if not isinstance(init_users, list) or not isinstance(final_users, list):
        return 0.0, "suggestedUsers is not a list"

    def topic_ids(topics):
        ids = []
        for t in topics:
            if isinstance(t, dict):
                ids.append(t.get("_id") or t.get("name"))
        return ids

    init_ids = topic_ids(init_users)
    final_ids = topic_ids(final_users)

    if not final_ids:
        return 0.0, "suggestedUsers is empty after refresh"

    if init_ids and set(init_ids) == set(final_ids):
        return 0.0, "suggestedUsers did not change after refresh"

    return 1.0, "Successfully refreshed suggested users"


_validate_refresh_list_of_suggested_users: ValidateTask = {
    "state_key": {
        "suggestedUsers": {"collection": "suggestedUsers", "filter": {}},
    },
    "validate_backend": _validate_backend_refresh_list_of_suggested_users,
    "validate_frontend": _validate_frontend_refresh_list_of_suggested_users,
}


# =============================================================================
# LIKE/UNLIKE TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: unlike-single-post-from-feed-v2
# -----------------------------------------------------------------------------

def _validate_backend_unlike_single_post_from_feed(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 1 has isLiked=false
    posts = final_state.get("posts")
    if not isinstance(posts, list) or len(posts) == 0:
        return 0.0, "Post 1 not found in backend"
    
    post = posts[0]

    initialNumberOfLikes = 128

    if post.get("likeCount") == initialNumberOfLikes - 1:
        return 1.0, "Backend: Post unliked successfully"

    return 0.0, "Backend: Post like count did not decrease after unlike"

def _validate_frontend_unlike_single_post_from_feed(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_local_post_like_override(final_state, "1", False)
    if not ok:
        return 0.0, error
    return 1.0, "Successfully unliked post from feed"


_validate_unlike_single_post_from_feed: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_unlike_single_post_from_feed,
    "validate_frontend": _validate_frontend_unlike_single_post_from_feed,
}


# -----------------------------------------------------------------------------
# Task: unlike-all-posts-on-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_unlike_all_posts_on_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that all posts by user1 are not liked
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    # Iterate through all posts and check none have isLiked=True
    liked_posts = []
    for post in posts:
        if post.get("isLiked") is True:
            liked_posts.append(post.get("_id", "unknown"))
    
    if len(liked_posts) > 0:
        return 0.0, f"Backend: Found {len(liked_posts)} liked post(s) by user1: {liked_posts}"
    
    return 1.0, f"Backend: All {len(posts)} posts by user1 are unliked successfully"


def _validate_frontend_unlike_all_posts_on_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check localPostLikeOverrides - all posts should be unliked
    overrides = final_state.get("localPostLikeOverrides", {})
    
    # All overrides should have isLiked=False
    for post_id, override in overrides.items():
        if override.get("isLiked") is True:
            return 0.0, f"Post '{post_id}' should be unliked"
    
    return 1.0, "Successfully unliked all posts on profile"


_validate_unlike_all_posts_on_profile: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "user1"}},
    },
    "validate_backend": _validate_backend_unlike_all_posts_on_profile,
    "validate_frontend": _validate_frontend_unlike_all_posts_on_profile,
}


# =============================================================================
# FOLLOW/UNFOLLOW TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: unfollow-user-from-profile-page-v2
# -----------------------------------------------------------------------------

def _validate_backend_unfollow_user_from_profile_page(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user5 is not followed (expect empty array)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) > 0:
        return 0.0, f"Backend: User 'user5' is still followed"
    
    return 1.0, "Backend: User unfollowed successfully"


def _validate_frontend_unfollow_user_from_profile_page(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user5")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully unfollowed user from profile page"


_validate_unfollow_user_from_profile_page: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user5"}},
    },
    "validate_backend": _validate_backend_unfollow_user_from_profile_page,
    "validate_frontend": _validate_frontend_unfollow_user_from_profile_page,
}


# -----------------------------------------------------------------------------
# Task: search-follow-last-user-v2
# -----------------------------------------------------------------------------

def _validate_backend_search_follow_user(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user "8200663693" (当前用户) is followed in userFollows
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "User 8200663693 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId
    follow = user_follows[0]
    target_user_id = "8200663693"
    if follow.get("followedUserId") == target_user_id:
        return 1.0, f"Backend: User {target_user_id} successfully followed"
    
    return 0.0, f"Unexpected followedUserId: {follow.get('followedUserId')}"


def _validate_frontend_search_follow_user(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully searched and followed last user"


_validate_search_follow_user: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "8200663693"}},
    },
    "validate_backend": _validate_backend_search_follow_user,
    "validate_frontend": _validate_frontend_search_follow_user,
}


# =============================================================================
# GROUP MANAGEMENT TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: remove-user-from-single-group-v2
# -----------------------------------------------------------------------------

def _validate_backend_remove_user_from_single_group(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Get user1's follow entry (already filtered by followedUserId)
    user_follows_user1 = final_state.get("userFollows_user1")
    if not isinstance(user_follows_user1, list) or len(user_follows_user1) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows_user1[0]
    groups = follow.get("groups", [])
    
    # Check that user1 is NOT in "classmates" group
    if "classmates" in groups:
        return 0.0, "Backend: user1 is still in 'classmates' group"
    
    # Check that user1 is NOT in "colleagues" group
    # Just an extra award check to make sure the AI doesn't make multiple groups 
    if "colleagues" in groups:
        return 0.0, "Backend: user1 is still in 'colleagues' group"
    
    # Check that user1 is still in "celebrities" group
    if "celebrities" not in groups:
        return 0.0, "Backend: user1 is not in 'celebrities' group"
    
    return 1.0, "Backend: User removed from classmates group successfully"

def _validate_frontend_remove_user_from_single_group(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_viewed_user_id(final_state, "user1")
    
    if not ok:
        return 0.0, error

    return 1.0, "Successfully removed user from single group"


_validate_remove_user_from_single_group: ValidateTask = {
    "state_key": {
        "userFollows_user1": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_remove_user_from_single_group,
    "validate_frontend": _validate_frontend_remove_user_from_single_group,
}


# -----------------------------------------------------------------------------
# Task: reassign-user-to-different-group-v2
# -----------------------------------------------------------------------------

def _validate_backend_reassign_user_to_different_group(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Get user1's follow entry (already filtered by followedUserId)
    user_follows_user1 = final_state.get("userFollows_user1")
    if not isinstance(user_follows_user1, list) or len(user_follows_user1) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows_user1[0]
    groups = follow.get("groups", [])
    
    # Check that user1 is NOT in "classmates" group anymore
    if "classmates" in groups:
        return 0.0, "Backend: user1 is still in 'classmates' group"
    
    # Check that user1 is now in "colleagues" group
    if "colleagues" not in groups:
        return 0.0, "Backend: user1 is not in 'colleagues' group"
    
    return 1.0, "Backend: User reassigned from classmates to colleagues successfully"


def _validate_frontend_reassign_user_to_different_group(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully reassigned user to different group"


_validate_reassign_user_to_different_group: ValidateTask = {
    "state_key": {
        "userFollows_user1": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_reassign_user_to_different_group,
    "validate_frontend": _validate_frontend_reassign_user_to_different_group,
}


# -----------------------------------------------------------------------------
# Task: unassign-special-attention-and-groups-v2
# -----------------------------------------------------------------------------

def _validate_backend_unassign_special_attention_and_groups(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Get user1's follow entry (already filtered by followedUserId)
    user_follows_user1 = final_state.get("userFollows_user1")
    if not isinstance(user_follows_user1, list) or len(user_follows_user1) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows_user1[0]
    
    # Check that user1 has no groups assigned
    groups = follow.get("groups", [])
    if groups and len(groups) > 0:
        return 0.0, f"Backend: user1 still has groups assigned: {groups}"
    
    # Check that user1 has no special attention
    is_special = follow.get("isSpecialAttention", False)
    if is_special is True:
        return 0.0, "Backend: user1 still has special attention"
    
    return 1.0, "Backend: All groups and special attention removed successfully"


def _validate_frontend_unassign_special_attention_and_groups(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully unassigned special attention and groups"


_validate_unassign_special_attention_and_groups: ValidateTask = {
    "state_key": {
        "userFollows_user1": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_unassign_special_attention_and_groups,
    "validate_frontend": _validate_frontend_unassign_special_attention_and_groups,
}


# =============================================================================
# COMMENT TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: reply-to-comment-v2
# -----------------------------------------------------------------------------

def _validate_backend_reply_to_comment(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new reply was created on post 1 (already filtered by postId and user._id)
    replies = final_state.get("replies")
    if not isinstance(replies, list):
        return 0.0, "Replies array missing in backend final state"
    
    if len(replies) > 0:
        return 1.0, "Backend: Reply created successfully"
    
    return 0.0, "No new reply from current user found on post 1"


def _validate_frontend_reply_to_comment(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that comment section is open
    displayed_posts = final_state.get("feedDisplayedPosts", [])
    for post in displayed_posts:
        if post.get("_id") == "1":
            if post.get("isCommentsOpen") is True:
                return 1.0, "Successfully opened comments and replied"
    
    return 1.0, "Reply submitted (UI state may not track replies)"


_validate_reply_to_comment: ValidateTask = {
    "state_key": {
        "replies": {"collection": "replies", "filter": {"postId": "1", "user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_reply_to_comment,
    "validate_frontend": _validate_frontend_reply_to_comment,
}


# =============================================================================
# ADDITIONAL NAVIGATION TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: navigate-to-latest-feed-section-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_to_latest_feed_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_to_latest_feed_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "latest")
    if not ok:
        return 0.0, error
    return 1.0, "Successfully navigated to latest feed section"


_validate_navigate_to_latest_feed_section: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_to_latest_feed_section,
    "validate_frontend": _validate_frontend_navigate_to_latest_feed_section,
}


# -----------------------------------------------------------------------------
# Task: navigate-via-trending-topic-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_via_trending_topic(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_via_trending_topic(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "comprehensive")
    if not ok:
        return 0.0, error
    
    # Search query should be set to the trending topic
    search_query = final_state.get("searchQuery", "")
    if not search_query:
        return 0.0, "searchQuery is empty"
    
    return 1.0, f"Successfully navigated via trending topic: {search_query}"


_validate_navigate_via_trending_topic: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_via_trending_topic,
    "validate_frontend": _validate_frontend_navigate_via_trending_topic,
}


# -----------------------------------------------------------------------------
# Task: no-search-suggestions-v2
# -----------------------------------------------------------------------------

def _validate_backend_no_search_suggestions(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_no_search_suggestions(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_search_query_equals(final_state, "asdf")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_open(final_state, True)
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_results_empty(final_state)
    if not ok:
        return 0.0, error
    
    return 1.0, "Search dropdown shows no suggestions for obscure query"


_validate_no_search_suggestions: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_no_search_suggestions,
    "validate_frontend": _validate_frontend_no_search_suggestions,
}


# -----------------------------------------------------------------------------
# Task: open-inline-comments-section-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_inline_comments_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for opening comments"


def _validate_frontend_open_inline_comments_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_feed_post_comments_open(final_state, "1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully opened inline comments section"


_validate_open_inline_comments_section: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_inline_comments_section,
    "validate_frontend": _validate_frontend_open_inline_comments_section,
}


# -----------------------------------------------------------------------------
# Task: open-post-composer-more-dropdown-v2
# -----------------------------------------------------------------------------

def _validate_backend_open_post_composer_more_dropdown(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for opening dropdown"


def _validate_frontend_open_post_composer_more_dropdown(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_more_options_dropdown_open(final_state, True)
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully opened post composer more dropdown"


_validate_open_post_composer_more_dropdown: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_open_post_composer_more_dropdown,
    "validate_frontend": _validate_frontend_open_post_composer_more_dropdown,
}


# -----------------------------------------------------------------------------
# Task: partial-search-query-v2
# -----------------------------------------------------------------------------

def _validate_backend_partial_search_query(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_partial_search_query(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_search_query_equals(final_state, "电影")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_open(final_state, True)
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_dropdown_has_suggestions(final_state, 1)
    if not ok:
        return 0.0, error
    
    return 1.0, "Search dropdown shows suggestions for partial query"


_validate_partial_search_query: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_partial_search_query,
    "validate_frontend": _validate_frontend_partial_search_query,
}


# -----------------------------------------------------------------------------
# Task: post-and-view-hashtag-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_and_view_hashtag(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with #weibo# hashtag was created (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        if "#weibo#" in content:
            return 1.0, "Backend: Post with #weibo# hashtag created"
    
    return 0.0, "No post with #weibo# hashtag found"


def _validate_frontend_post_and_view_hashtag(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_query_equals(final_state, "#weibo#")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "comprehensive")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully posted and navigated to hashtag view"


_validate_post_and_view_hashtag: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_post_and_view_hashtag,
    "validate_frontend": _validate_frontend_post_and_view_hashtag,
}


# -----------------------------------------------------------------------------
# Task: post-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_post_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "dot-1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post from profile"


_validate_post_from_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_post_from_profile,
    "validate_frontend": _validate_frontend_post_from_profile,
}


# -----------------------------------------------------------------------------
# Task: post-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_post_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "35")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post from search"


_validate_post_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_post_from_search,
    "validate_frontend": _validate_frontend_post_from_search,
}


# -----------------------------------------------------------------------------
# Task: post-image-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_image(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with image media was created (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        media = post.get("media", [])
        for m in media:
            if m.get("type") == "image":
                return 1.0, "Backend: Post with image created"
    
    return 0.0, "No post with image media found"


def _validate_frontend_post_image(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully posted image"


_validate_post_image: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_post_image,
    "validate_frontend": _validate_frontend_post_image,
}


# -----------------------------------------------------------------------------
# Task: post-video-v2
# -----------------------------------------------------------------------------

def _validate_backend_post_video(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with video media was created (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        media = post.get("media", [])
        for m in media:
            if m.get("type") == "video":
                return 1.0, "Backend: Post with video created"
    
    return 0.0, "No post with video media found"


def _validate_frontend_post_video(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully posted video"


_validate_post_video: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_post_video,
    "validate_frontend": _validate_frontend_post_video,
}


# -----------------------------------------------------------------------------
# Task: profile-from-comments-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_comments(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_comments(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user9")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from comments"


_validate_profile_from_comments: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_comments,
    "validate_frontend": _validate_frontend_profile_from_comments,
}


# -----------------------------------------------------------------------------
# Task: profile-from-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user5")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from post"


_validate_profile_from_post: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_post,
    "validate_frontend": _validate_frontend_profile_from_post,
}


# -----------------------------------------------------------------------------
# Task: profile-from-reply-v2
# -----------------------------------------------------------------------------

def _validate_backend_profile_from_reply(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_profile_from_reply(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user4")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to profile from reply"


_validate_profile_from_reply: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_profile_from_reply,
    "validate_frontend": _validate_frontend_profile_from_reply,
}


# =============================================================================
# CUSTOM GROUP MANAGEMENT TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: delete-custom-group-v2
# -----------------------------------------------------------------------------

def _validate_backend_delete_custom_group(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that the custom group 'celebrities' is deleted (expect empty array)
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list):
        return 0.0, "customGroups array missing in backend final state"
    
    if len(custom_groups) > 0:
        return 0.0, "Backend: Custom group 'celebrities' still exists"
    
    return 1.0, "Backend: Custom group deleted successfully"


def _validate_frontend_delete_custom_group(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Frontend validation intentionally skipped; rely solely on backend/state_key
    return 1.0, "No frontend validation required"


_validate_delete_custom_group: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"_id": "celebrities"}},
    },
    "validate_backend": _validate_backend_delete_custom_group,
    "validate_frontend": _validate_frontend_delete_custom_group,
}


# -----------------------------------------------------------------------------
# Task: edit-custom-group-name-v2
# -----------------------------------------------------------------------------

def _validate_backend_edit_custom_group_name(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that the custom group was renamed
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group with new name '新分组名' not found"
    
    # Get the first (and only) item since we filtered by label
    group = custom_groups[0]
    if group.get("label") == "新分组名":
        return 1.0, "Backend: Custom group renamed successfully"
    
    return 0.0, f"Unexpected group label: {group.get('label')}"


def _validate_frontend_edit_custom_group_name(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Frontend validation intentionally skipped; rely solely on backend/state_key
    return 1.0, "No frontend validation required"


_validate_edit_custom_group_name: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "新分组名"}},
    },
    "validate_backend": _validate_backend_edit_custom_group_name,
    "validate_frontend": _validate_frontend_edit_custom_group_name,
}


# =============================================================================
# FOLLOW FLOW TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: follow-and-set-special-attention-flow-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_and_set_special_attention_flow(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that both user1 and user2 are followed (filtered by followedUserId $in)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) < 2:
        return 0.0, f"Expected 2 followed users (user1 and user2), got {len(user_follows)}"
    
    # Find user1 and user2 entries
    user1_found = False
    user2_found = False
    user2_has_special = False
    
    for entry in user_follows:
        followed_id = entry.get("followedUserId")
        if followed_id == "user1":
            user1_found = True
        elif followed_id == "user2":
            user2_found = True
            user2_has_special = entry.get("isSpecialAttention", False) is True
    
    if not user1_found:
        return 0.0, "user1 not followed"
    if not user2_found:
        return 0.0, "user2 not followed"
    if not user2_has_special:
        return 0.0, "user2 is followed but does not have special attention"
    
    return 1.0, "Backend: Both users followed, user2 has special attention"


def _validate_frontend_follow_and_set_special_attention_flow(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "special-follow")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to special follow feed"


_validate_follow_and_set_special_attention_flow: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": {"$in": ["user1", "user2"]}}},
    },
    "validate_backend": _validate_backend_follow_and_set_special_attention_flow,
    "validate_frontend": _validate_frontend_follow_and_set_special_attention_flow,
}


# -----------------------------------------------------------------------------
# Task: follow-and-unfollow-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_and_unfollow_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user2 (科技资讯) is NOT followed (was followed then unfollowed)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) > 0:
        return 0.0, f"Backend: User 'user2' is still followed"
    
    return 1.0, "Backend: User followed and then unfollowed successfully"


def _validate_frontend_follow_and_unfollow_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully on profile page after follow/unfollow"


_validate_follow_and_unfollow_from_profile: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user2"}},
    },
    "validate_backend": _validate_backend_follow_and_unfollow_from_profile,
    "validate_frontend": _validate_frontend_follow_and_unfollow_from_profile,
}


# -----------------------------------------------------------------------------
# Task: follow-assign-to-group-and-navigate-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_assign_to_group_and_navigate(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user1 is followed (already filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not followed"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows[0]
    groups = follow.get("groups", [])
    if "celebrities" in groups:
        return 1.0, "Backend: User followed and assigned to celebrities group successfully"
    
    return 0.0, f"user1 not in 'celebrities' group. Groups: {groups}"


def _validate_frontend_follow_assign_to_group_and_navigate(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that current view is custom-group-celebrities
    view = final_state.get("currentView")
    if view != "custom-group-celebrities":
        return 0.0, f"currentView='{view}' expected 'custom-group-celebrities'"
    
    return 1.0, "Successfully navigated to custom group feed"


_validate_follow_assign_to_group_and_navigate: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_follow_assign_to_group_and_navigate,
    "validate_frontend": _validate_frontend_follow_assign_to_group_and_navigate,
}


# -----------------------------------------------------------------------------
# Task: follow-create-group-and-assign-flow-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_create_group_and_assign_flow(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new custom group "test" was created (filtered by label)
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group 'test' not found"
    
    # Get the first (and only) item since we filtered by label "test"
    group = custom_groups[0]
    group_id = group.get("_id")
    if not group_id:
        return 0.0, "Custom group 'test' has no _id"
    
    # Check that user1 follows exist (filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not followed"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows[0]
    groups = follow.get("groups", [])
    if group_id in groups:
        return 1.0, "Backend: User followed, group created, and user assigned successfully"
    
    return 0.0, f"user1 not in group '{group_id}'. Groups: {groups}"


def _validate_frontend_follow_create_group_and_assign_flow(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    # Check that manage groups modal is closed
    if final_state.get("manageGroupsModalOpen", False):
        return 0.0, "manageGroupsModalOpen should be false"
    
    return 1.0, "Successfully created group and assigned user"


_validate_follow_create_group_and_assign_flow: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "test"}},
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_follow_create_group_and_assign_flow,
    "validate_frontend": _validate_frontend_follow_create_group_and_assign_flow,
}


# -----------------------------------------------------------------------------
# Task: follow-multiple-users-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_multiple_users_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that at least 2 users are followed (already filtered by userId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list):
        return 0.0, "userFollows array missing in backend final state"
    
    if len(user_follows) >= 2:
        return 1.0, f"Backend: {len(user_follows)} users followed successfully"
    else:
        return 0.0, f"Expected at least 2 users followed, found {len(user_follows)}"


def _validate_frontend_follow_multiple_users_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully followed multiple users from search"


_validate_follow_multiple_users_from_search: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"userId": "8200663693"}},
    },
    "validate_backend": _validate_backend_follow_multiple_users_from_search,
    "validate_frontend": _validate_frontend_follow_multiple_users_from_search,
}


# -----------------------------------------------------------------------------
# Task: follow-user-and-check-latest-feed-v2
# -----------------------------------------------------------------------------

def _validate_backend_follow_user_and_check_latest_feed(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that user1 (用户小王) is followed (already filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not followed"
    
    # Verify the first (and only) item is user1
    follow = user_follows[0]
    if follow.get("followedUserId") == "user1":
        return 1.0, "Backend: user1 followed successfully"
    
    return 0.0, f"Unexpected followedUserId: {follow.get('followedUserId')}"


def _validate_frontend_follow_user_and_check_latest_feed(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "latest")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to latest feed after following user"


_validate_follow_user_and_check_latest_feed: ValidateTask = {
    "state_key": {
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_follow_user_and_check_latest_feed,
    "validate_frontend": _validate_frontend_follow_user_and_check_latest_feed,
}


# =============================================================================
# NAVIGATION TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: home-from-search-v2
# -----------------------------------------------------------------------------

def _validate_backend_home_from_search(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_home_from_search(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated home from search"


_validate_home_from_search: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_home_from_search,
    "validate_frontend": _validate_frontend_home_from_search,
}


# -----------------------------------------------------------------------------
# Task: navigate-post-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_post(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_post(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "4")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post detail page"


_validate_navigate_post: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_post,
    "validate_frontend": _validate_frontend_navigate_post,
}


# -----------------------------------------------------------------------------
# Task: navigate-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_navigate_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for navigation"


def _validate_frontend_navigate_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to user profile"


_validate_navigate_profile: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_navigate_profile,
    "validate_frontend": _validate_frontend_navigate_profile,
}


# -----------------------------------------------------------------------------
# Task: load-more-posts-v2
# -----------------------------------------------------------------------------

def _validate_backend_load_more_posts(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for loading posts"


def _validate_frontend_load_more_posts(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    # Check that scrollPosition has increased (more posts loaded)
    initial_scroll = initial_state.get("feedScrollPosition", 0)
    final_scroll = final_state.get("feedScrollPosition", 0)
    
    if final_scroll <= initial_scroll:
        return 0.0, f"feedScrollPosition did not increase: {initial_scroll} -> {final_scroll}"
    
    return 1.0, f"Successfully loaded more posts (scrolled from {initial_scroll} to {final_scroll})"


_validate_load_more_posts: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_load_more_posts,
    "validate_frontend": _validate_frontend_load_more_posts,
}


# -----------------------------------------------------------------------------
# Task: load-many-posts-v2
# -----------------------------------------------------------------------------

def _validate_backend_load_many_posts(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for loading posts"


def _validate_frontend_load_many_posts(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "11")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully navigated to post from far down in feed"


_validate_load_many_posts: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_load_many_posts,
    "validate_frontend": _validate_frontend_load_many_posts,
}


# =============================================================================
# LIKE TASKS
# =============================================================================

# -----------------------------------------------------------------------------
# Task: like-post-from-main-feed-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_post_from_main_feed(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 1 has isLiked=true
    posts = final_state.get("posts")
    if not isinstance(posts, list) or len(posts) == 0:
        return 0.0, "Post 1 not found in backend"
    
    post = posts[0]
    # if post.get("isLiked") is True:
    #     return 1.0, "Backend: Post liked successfully"
    
    initialNumberOfLikes = 127 
    if post.get("likeCount") == initialNumberOfLikes + 1:
        return 1.0, "Backend: Post liked successfully"

    return 0.0, "Backend: Post like count did not increase after like"


def _validate_frontend_like_post_from_main_feed(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_local_post_like_override(final_state, "1", True)
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully liked post from main feed"


_validate_like_post_from_main_feed: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"_id": "1"}},
    },
    "validate_backend": _validate_backend_like_post_from_main_feed,
    "validate_frontend": _validate_frontend_like_post_from_main_feed,
}


# -----------------------------------------------------------------------------
# Task: like-comment-on-post-detail-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_comment_on_post_detail(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that comment p1-c1 has isLiked=true (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    for comment in comments:
        if comment.get("_id") == "p1-c1":
            if comment.get("isLiked") is True:
                return 1.0, "Backend: Comment liked successfully"
            else:
                return 0.0, "Comment p1-c1 is not liked in backend"
    
    return 0.0, "Comment p1-c1 not found in backend"


def _validate_frontend_like_comment_on_post_detail(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "1")
    if not ok:
        return 0.0, error

    ok, error = _check_viewed_post_comments_liked(final_state, ["p1-c1"])
    if not ok:
        return 0.0, error

    return 1.0, "Successfully liked comment on post detail page"


_validate_like_comment_on_post_detail: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "1"}},
    },
    "validate_backend": _validate_backend_like_comment_on_post_detail,
    "validate_frontend": _validate_frontend_like_comment_on_post_detail,
}


# -----------------------------------------------------------------------------
# Task: like-2-comments-v2
# -----------------------------------------------------------------------------

def _validate_backend_like_2_comments(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that comments p1-c1 and p1-c2 have isLiked=true (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    liked_count = 0
    for comment in comments:
        if comment.get("_id") in ["p1-c1", "p1-c2"]:
            if comment.get("isLiked") is True:
                liked_count += 1
    
    if liked_count >= 2:
        return 1.0, "Backend: Both comments liked successfully"
    elif liked_count == 1:
        return 0.0, "Only 1 comment liked, expected 2"
    else:
        return 0.0, "Neither comment is liked in backend"


def _validate_frontend_like_2_comments(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    # Check that the post's comments section is open
    ok, error = _check_feed_post_comments_open(final_state, "1")
    if not ok:
        return 0.0, error

    ok, error = _check_feed_comments_liked(final_state, "1", ["p1-c1", "p1-c2"])
    if not ok:
        return 0.0, error

    return 1.0, "Successfully liked 2 comments"


_validate_like_2_comments: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "1"}},
    },
    "validate_backend": _validate_backend_like_2_comments,
    "validate_frontend": _validate_frontend_like_2_comments,
}


# =============================================================================
# SEARCH & NAVIGATION TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: accept-search-suggestion-v2
# -----------------------------------------------------------------------------

def _validate_backend_accept_search_suggestion(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search"


def _validate_frontend_accept_search_suggestion(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_query_equals(final_state, "用户小王")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully accepted search suggestion"


_validate_accept_search_suggestion: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_accept_search_suggestion,
    "validate_frontend": _validate_frontend_accept_search_suggestion,
}


# -----------------------------------------------------------------------------
# Task: change-search-categories-v2
# -----------------------------------------------------------------------------

def _validate_backend_change_search_categories(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for search category change"


def _validate_frontend_change_search_categories(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_category(final_state, "users")
    if not ok:
        return 0.0, error
    
    ok, error = _check_search_query_equals(final_state, "用户小王")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully changed search category to users"


_validate_change_search_categories: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_change_search_categories,
    "validate_frontend": _validate_frontend_change_search_categories,
}


# -----------------------------------------------------------------------------
# Task: change-trending-tab-and-navigate-v2
# -----------------------------------------------------------------------------

def _validate_backend_change_trending_tab_and_navigate(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    return 1.0, "No backend validation required for trending tab navigation"


def _validate_frontend_change_trending_tab_and_navigate(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "search")
    if not ok:
        return 0.0, error
    
    # Check that hotSearchTab is "trending"
    hot_search_tab = final_state.get("hotSearchTab")
    if hot_search_tab != "trending":
        return 0.0, f"hotSearchTab='{hot_search_tab}' expected 'trending'"
    
    # Check that searchQuery is not empty (it should be the trending topic)
    search_query = final_state.get("searchQuery", "")
    if not search_query:
        return 0.0, "searchQuery is empty"
    
    return 1.0, f"Successfully changed trending tab and navigated to topic: {search_query}"


_validate_change_trending_tab_and_navigate: ValidateTask = {
    "state_key": {},
    "validate_backend": _validate_backend_change_trending_tab_and_navigate,
    "validate_frontend": _validate_frontend_change_trending_tab_and_navigate,
}


# =============================================================================
# GROUP & USER MANAGEMENT TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: add-user-to-new-custom-group-from-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_add_user_to_new_custom_group_from_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new custom group "兴趣爱好" exists (filtered by label)
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group '兴趣爱好' not found"
    
    # Get the first (and only) item since we filtered by label
    group = custom_groups[0]
    group_id = group.get("_id")
    if not group_id:
        return 0.0, "Custom group '兴趣爱好' has no _id"
    
    # Check that user1 follows exist (filtered by followedUserId)
    user_follows = final_state.get("userFollows")
    if not isinstance(user_follows, list) or len(user_follows) == 0:
        return 0.0, "user1 not found in userFollows"
    
    # Get the first (and only) item since we filtered by followedUserId "user1"
    follow = user_follows[0]
    groups = follow.get("groups", [])
    if group_id in groups:
        return 1.0, "Backend: New group created and user assigned"
    
    return 0.0, f"user1 not in group '{group_id}'. Groups: {groups}"


def _validate_frontend_add_user_to_new_custom_group_from_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully on profile page after adding user to new group"


_validate_add_user_to_new_custom_group_from_profile: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "兴趣爱好"}},
        "userFollows": {"collection": "userFollows", "filter": {"followedUserId": "user1"}},
    },
    "validate_backend": _validate_backend_add_user_to_new_custom_group_from_profile,
    "validate_frontend": _validate_frontend_add_user_to_new_custom_group_from_profile,
}


# -----------------------------------------------------------------------------
# Task: create-custom-group-and-navigate-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_custom_group_and_navigate(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a custom group "test" exists
    custom_groups = final_state.get("customGroups")
    if not isinstance(custom_groups, list) or len(custom_groups) == 0:
        return 0.0, "Custom group 'test' not found"
    
    # Get the first (and only) item since we filtered by label
    group = custom_groups[0]
    if group.get("label") == "test":
        return 1.0, "Backend: Custom group 'test' created"
    
    return 0.0, f"Unexpected group label: {group.get('label')}"


def _validate_frontend_create_custom_group_and_navigate(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that current view starts with "custom-group-"
    view = final_state.get("currentView", "")
    if not view.startswith("custom-group-"):
        return 0.0, f"currentView='{view}' expected to start with 'custom-group-'"
    
    return 1.0, f"Successfully navigated to custom group feed: {view}"


_validate_create_custom_group_and_navigate: ValidateTask = {
    "state_key": {
        "customGroups": {"collection": "customGroups", "filter": {"label": "test"}},
    },
    "validate_backend": _validate_backend_create_custom_group_and_navigate,
    "validate_frontend": _validate_frontend_create_custom_group_and_navigate,
}


# =============================================================================
# COMMENT TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: create-comment-with-expressions-on-detail-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_comment_with_expressions_on_detail(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 2 has a new comment with expression (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    # Look for a new comment from current user with expression content
    for comment in comments:
        if comment.get("user", {}).get("_id") == "8200663693":
            content = comment.get("content", "")
            # Check if it contains expression codes like [xxx]
            if "[" in content and "]" in content:
                return 1.0, "Backend: Comment with expression created successfully"
    
    return 0.0, "No new comment with expression found on post 2"


def _validate_frontend_create_comment_with_expressions_on_detail(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "post")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_post_id(final_state, "2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created comment with expressions on post detail"


_validate_create_comment_with_expressions_on_detail: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "2"}},
    },
    "validate_backend": _validate_backend_create_comment_with_expressions_on_detail,
    "validate_frontend": _validate_frontend_create_comment_with_expressions_on_detail,
}


# -----------------------------------------------------------------------------
# Task: create-comment-with-inline-section-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_comment_with_inline_section(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that post 2 has a new comment from current user (already filtered by postId)
    comments = final_state.get("comments")
    if not isinstance(comments, list):
        return 0.0, "Comments array missing in backend final state"
    
    for comment in comments:
        if comment.get("user", {}).get("_id") == "8200663693":
            return 1.0, "Backend: New comment created on post 2"
    
    return 0.0, "No new comment from current user found on post 2"


def _validate_frontend_create_comment_with_inline_section(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    ok, error = _check_feed_post_comments_open(final_state, "2")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created comment using inline section"


_validate_create_comment_with_inline_section: ValidateTask = {
    "state_key": {
        "comments": {"collection": "comments", "filter": {"postId": "2"}},
    },
    "validate_backend": _validate_backend_create_comment_with_inline_section,
    "validate_frontend": _validate_frontend_create_comment_with_inline_section,
}


# =============================================================================
# POST CREATION TASKS (NEW)
# =============================================================================

# -----------------------------------------------------------------------------
# Task: create-post-and-verify-in-profile-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_and_verify_in_profile(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post by current user exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        if "这是我的新微博" in content and "#日常生活#" in content:
            return 1.0, "Backend: New post created successfully"
    
    return 0.0, "No new post with expected content found"


def _validate_frontend_create_post_and_verify_in_profile(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "8200663693")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post and verified in profile"


_validate_create_post_and_verify_in_profile: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_and_verify_in_profile,
    "validate_frontend": _validate_frontend_create_post_and_verify_in_profile,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-emoji-expression-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_emoji_expression(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with [doge] exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "[doge]" in content and is_original is True:
            return 1.0, "Backend: Post with [doge] expression created"
    
    return 0.0, "No post with [doge] expression found"


def _validate_frontend_create_post_with_emoji_expression(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with emoji expression"


_validate_create_post_with_emoji_expression: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_emoji_expression,
    "validate_frontend": _validate_frontend_create_post_with_emoji_expression,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-hashtags-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_hashtags(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with hashtags exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "#生活分享#" in content and "#每日心情#" in content and is_original is True:
            return 1.0, "Backend: Post with hashtags created with isOriginal=true"
    
    return 0.0, "No post with both hashtags #生活分享# and #每日心情# found with isOriginal=true"


def _validate_frontend_create_post_with_hashtags(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with hashtags"


_validate_create_post_with_hashtags: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_hashtags,
    "validate_frontend": _validate_frontend_create_post_with_hashtags,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-three-expressions-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_three_expressions(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with 3 expressions exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        # Count expression codes [xxx]
        expressions = re.findall(r'\[[^\]]+\]', content)
        if len(expressions) >= 3:
            return 1.0, f"Backend: Post with {len(expressions)} expressions created"
    
    return 0.0, "No post with at least 3 expressions found"


def _validate_frontend_create_post_with_three_expressions(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with three expressions"


_validate_create_post_with_three_expressions: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_three_expressions,
    "validate_frontend": _validate_frontend_create_post_with_three_expressions,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-two-or-more-emojis-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_two_or_more_emojis(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with 2+ different emojis exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        # Count unique expression codes [xxx]
        expressions = set(re.findall(r'\[[^\]]+\]', content))
        is_original = post.get("isOriginal", False)
        if len(expressions) >= 2 and is_original is True:
            return 1.0, f"Backend: Post with {len(expressions)} different emojis created"
    
    return 0.0, "No post with at least 2 different emojis found"


def _validate_frontend_create_post_with_two_or_more_emojis(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with two or more emojis"


_validate_create_post_with_two_or_more_emojis: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_two_or_more_emojis,
    "validate_frontend": _validate_frontend_create_post_with_two_or_more_emojis,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-user-mention-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_user_mention(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with @mention exists (already filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "@科技资讯" in content and is_original is True:
            return 1.0, "Backend: Post with @mention created"
    
    return 0.0, "No post with @科技资讯 mention found with isOriginal=true"


def _validate_frontend_create_post_with_user_mention(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "feed")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with user mention"


_validate_create_post_with_user_mention: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_user_mention,
    "validate_frontend": _validate_frontend_create_post_with_user_mention,
}


# -----------------------------------------------------------------------------
# Task: create-post-with-mention-and-hashtag-v2
# -----------------------------------------------------------------------------

def _validate_backend_create_post_with_mention_and_hashtag(
    final_state: Dict[str, Any]
) -> Tuple[float, str]:
    # Check that a new post with both @mention and hashtag exists (filtered by user._id)
    posts = final_state.get("posts")
    if not isinstance(posts, list):
        return 0.0, "Posts array missing in backend final state"
    
    for post in posts:
        content = post.get("content", "")
        is_original = post.get("isOriginal", False)
        if "@用户小王" in content and "#weibo#" in content and is_original is True:
            return 1.0, "Backend: Post with mention and hashtag created"
    
    return 0.0, "No post with @用户小王 and #weibo# found with isOriginal=true"


def _validate_frontend_create_post_with_mention_and_hashtag(
    initial_state: Dict[str, Any], final_state: Dict[str, Any]
) -> Tuple[float, str]:
    ok, error = _check_current_view(final_state, "profile")
    if not ok:
        return 0.0, error
    
    ok, error = _check_viewed_user_id(final_state, "user1")
    if not ok:
        return 0.0, error
    
    return 1.0, "Successfully created post with mention and hashtag"


_validate_create_post_with_mention_and_hashtag: ValidateTask = {
    "state_key": {
        "posts": {"collection": "posts", "filter": {"user._id": "8200663693"}},
    },
    "validate_backend": _validate_backend_create_post_with_mention_and_hashtag,
    "validate_frontend": _validate_frontend_create_post_with_mention_and_hashtag,
}


# =============================================================================
# Registry of all V2 Reward Functions
# =============================================================================

REWARD_FUNCTIONS_WEIBO_V2: Dict[str, ValidateTask] = {
    # Navigation & Search Tasks
    "_validate_profile_from_search": _validate_profile_from_search,
    "_validate_search_users": _validate_search_users,
    "_validate_switch_theme": _validate_switch_theme,
    "_validate_search_dropdown_profile": _validate_search_dropdown_profile,
    "_validate_profile_from_sorted_comments": _validate_profile_from_sorted_comments,
    "_validate_view_full_comment_thread": _validate_view_full_comment_thread,
    "_validate_video_post_from_profile": _validate_video_post_from_profile,
    "_validate_refresh_list_of_trending_topics": _validate_refresh_list_of_trending_topics,
    "_validate_refresh_list_of_suggested_users": _validate_refresh_list_of_suggested_users,
    "_validate_navigate_to_latest_feed_section": _validate_navigate_to_latest_feed_section,
    "_validate_navigate_via_trending_topic": _validate_navigate_via_trending_topic,
    "_validate_no_search_suggestions": _validate_no_search_suggestions,
    "_validate_open_inline_comments_section": _validate_open_inline_comments_section,
    "_validate_open_post_composer_more_dropdown": _validate_open_post_composer_more_dropdown,
    "_validate_partial_search_query": _validate_partial_search_query,
    "_validate_post_from_profile": _validate_post_from_profile,
    "_validate_post_from_search": _validate_post_from_search,
    "_validate_profile_from_comments": _validate_profile_from_comments,
    "_validate_profile_from_post": _validate_profile_from_post,
    "_validate_profile_from_reply": _validate_profile_from_reply,
    "_validate_home_from_search": _validate_home_from_search,
    "_validate_navigate_post": _validate_navigate_post,
    "_validate_navigate_profile": _validate_navigate_profile,
    "_validate_load_more_posts": _validate_load_more_posts,
    "_validate_load_many_posts": _validate_load_many_posts,
    "_validate_accept_search_suggestion": _validate_accept_search_suggestion,
    "_validate_change_search_categories": _validate_change_search_categories,
    "_validate_change_trending_tab_and_navigate": _validate_change_trending_tab_and_navigate,
    # Like/Unlike Tasks
    "_validate_unlike_single_post_from_feed": _validate_unlike_single_post_from_feed,
    "_validate_unlike_all_posts_on_profile": _validate_unlike_all_posts_on_profile,
    "_validate_like_post_from_main_feed": _validate_like_post_from_main_feed,
    "_validate_like_comment_on_post_detail": _validate_like_comment_on_post_detail,
    "_validate_like_2_comments": _validate_like_2_comments,
    # Follow/Unfollow Tasks
    "_validate_unfollow_user_from_profile_page": _validate_unfollow_user_from_profile_page,
    "_validate_search_follow_user": _validate_search_follow_user,
    "_validate_follow_and_set_special_attention_flow": _validate_follow_and_set_special_attention_flow,
    "_validate_follow_and_unfollow_from_profile": _validate_follow_and_unfollow_from_profile,
    "_validate_follow_assign_to_group_and_navigate": _validate_follow_assign_to_group_and_navigate,
    "_validate_follow_create_group_and_assign_flow": _validate_follow_create_group_and_assign_flow,
    "_validate_follow_multiple_users_from_search": _validate_follow_multiple_users_from_search,
    "_validate_follow_user_and_check_latest_feed": _validate_follow_user_and_check_latest_feed,
    # Group Management Tasks
    "_validate_remove_user_from_single_group": _validate_remove_user_from_single_group,
    "_validate_reassign_user_to_different_group": _validate_reassign_user_to_different_group,
    "_validate_unassign_special_attention_and_groups": _validate_unassign_special_attention_and_groups,
    "_validate_delete_custom_group": _validate_delete_custom_group,
    "_validate_edit_custom_group_name": _validate_edit_custom_group_name,
    "_validate_add_user_to_new_custom_group_from_profile": _validate_add_user_to_new_custom_group_from_profile,
    "_validate_create_custom_group_and_navigate": _validate_create_custom_group_and_navigate,
    # Comment Tasks
    "_validate_reply_to_comment": _validate_reply_to_comment,
    "_validate_create_comment_with_expressions_on_detail": _validate_create_comment_with_expressions_on_detail,
    "_validate_create_comment_with_inline_section": _validate_create_comment_with_inline_section,
    # Post Creation Tasks
    "_validate_post_and_view_hashtag": _validate_post_and_view_hashtag,
    "_validate_post_image": _validate_post_image,
    "_validate_post_video": _validate_post_video,
    "_validate_create_post_and_verify_in_profile": _validate_create_post_and_verify_in_profile,
    "_validate_create_post_with_emoji_expression": _validate_create_post_with_emoji_expression,
    "_validate_create_post_with_hashtags": _validate_create_post_with_hashtags,
    "_validate_create_post_with_three_expressions": _validate_create_post_with_three_expressions,
    "_validate_create_post_with_two_or_more_emojis": _validate_create_post_with_two_or_more_emojis,
    "_validate_create_post_with_user_mention": _validate_create_post_with_user_mention,
    "_validate_create_post_with_mention_and_hashtag": _validate_create_post_with_mention_and_hashtag,
}


__all__ = [
    "REWARD_FUNCTIONS_WEIBO_V2",
    "ValidateTask",
    "StateKey",
    "StateKeyQuery",
]
