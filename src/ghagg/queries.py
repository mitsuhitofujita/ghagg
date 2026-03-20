SEARCH_PULL_REQUESTS = """
query($searchQuery: String!, $first: Int!, $after: String) {
  search(query: $searchQuery, type: ISSUE, first: $first, after: $after) {
    issueCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on PullRequest {
        id
        number
        title
        state
        createdAt
        updatedAt
        mergedAt
        closedAt
        additions
        deletions
        changedFiles
        author {
          login
        }
        mergedBy {
          login
        }
        baseRefName
        headRefName
        reviewDecision
        reviews(first: 100) {
          totalCount
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            author {
              login
            }
            state
            createdAt
            body
          }
        }
        comments(first: 100) {
          totalCount
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            author {
              login
            }
            createdAt
            body
          }
        }
        reviewThreads(first: 50) {
          totalCount
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            isResolved
            comments(first: 30) {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                author {
                  login
                }
                createdAt
                body
              }
            }
          }
        }
      }
    }
  }
}
"""

PR_REVIEWS = """
query($nodeId: ID!, $first: Int!, $after: String) {
  node(id: $nodeId) {
    ... on PullRequest {
      reviews(first: $first, after: $after) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          author {
            login
          }
          state
          createdAt
          body
        }
      }
    }
  }
}
"""

PR_COMMENTS = """
query($nodeId: ID!, $first: Int!, $after: String) {
  node(id: $nodeId) {
    ... on PullRequest {
      comments(first: $first, after: $after) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          author {
            login
          }
          createdAt
          body
        }
      }
    }
  }
}
"""

PR_REVIEW_THREADS = """
query($nodeId: ID!, $first: Int!, $after: String) {
  node(id: $nodeId) {
    ... on PullRequest {
      reviewThreads(first: $first, after: $after) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          comments(first: 30) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              id
              author {
                login
              }
              createdAt
              body
            }
          }
        }
      }
    }
  }
}
"""

REVIEW_THREAD_COMMENTS = """
query($nodeId: ID!, $first: Int!, $after: String) {
  node(id: $nodeId) {
    ... on ReviewThread {
      comments(first: $first, after: $after) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          author {
            login
          }
          createdAt
          body
        }
      }
    }
  }
}
"""
