import logging

from ghagg.github_client import execute_graphql
from ghagg import queries

logger = logging.getLogger(__name__)


def _paginate_connection(node_id: str, query: str, connection_key: str, batch_size: int, existing_nodes: list, page_info: dict) -> list:
    all_nodes = list(existing_nodes)
    cursor = page_info["endCursor"]
    has_next = page_info["hasNextPage"]

    while has_next:
        logger.info("  Fetching more %s (cursor: %s)...", connection_key, cursor[:12] if cursor else "")
        variables = {"nodeId": node_id, "first": str(batch_size), "after": cursor}
        data = execute_graphql(query, variables)
        connection = data["data"]["node"][connection_key]
        all_nodes.extend(connection["nodes"])
        has_next = connection["pageInfo"]["hasNextPage"]
        cursor = connection["pageInfo"]["endCursor"]

    return all_nodes


def _resolve_overflow(pr: dict) -> dict:
    pr_id = pr["id"]
    pr_number = pr["number"]

    # Reviews
    reviews = pr["reviews"]
    if reviews["pageInfo"]["hasNextPage"]:
        logger.info("PR #%d: fetching remaining reviews...", pr_number)
        reviews["nodes"] = _paginate_connection(
            pr_id, queries.PR_REVIEWS, "reviews", 100, reviews["nodes"], reviews["pageInfo"]
        )

    # Comments
    comments = pr["comments"]
    if comments["pageInfo"]["hasNextPage"]:
        logger.info("PR #%d: fetching remaining comments...", pr_number)
        comments["nodes"] = _paginate_connection(
            pr_id, queries.PR_COMMENTS, "comments", 100, comments["nodes"], comments["pageInfo"]
        )

    # Review threads
    review_threads = pr["reviewThreads"]
    if review_threads["pageInfo"]["hasNextPage"]:
        logger.info("PR #%d: fetching remaining review threads...", pr_number)
        review_threads["nodes"] = _paginate_connection(
            pr_id, queries.PR_REVIEW_THREADS, "reviewThreads", 50, review_threads["nodes"], review_threads["pageInfo"]
        )

    # Review thread comments (check each thread)
    for thread in review_threads["nodes"]:
        thread_comments = thread["comments"]
        if thread_comments["pageInfo"]["hasNextPage"]:
            logger.info("PR #%d: fetching remaining thread comments (thread %s)...", pr_number, thread["id"][:12])
            thread_comments["nodes"] = _paginate_connection(
                thread["id"], queries.REVIEW_THREAD_COMMENTS, "comments", 30, thread_comments["nodes"], thread_comments["pageInfo"]
            )

    return pr


def fetch_pull_requests(repo: str, since: str, until: str) -> list[dict]:
    search_query = f"repo:{repo} is:pr created:{since}..{until}"
    all_prs = []
    cursor = None
    page = 0

    while True:
        page += 1
        variables = {"searchQuery": search_query, "first": "20"}
        if cursor:
            variables["after"] = cursor

        logger.info("Fetching PR list (page %d)...", page)
        data = execute_graphql(queries.SEARCH_PULL_REQUESTS, variables)
        search = data["data"]["search"]

        if page == 1:
            logger.info("Total PRs matching query: %d", search["issueCount"])

        for pr in search["nodes"]:
            if not pr:
                continue
            pr = _resolve_overflow(pr)
            all_prs.append(pr)

        if not search["pageInfo"]["hasNextPage"]:
            break
        cursor = search["pageInfo"]["endCursor"]

    logger.info("Fetched %d PRs total.", len(all_prs))
    return all_prs
