"""Tool and field descriptions for defining AI agent tools."""

# Tool Descriptions
FETCH_TOOL_DESCRIPTION = (
    "Fetch a web page and analyze its content using AI. Provide a URL and a "
    "prompt describing what information you want to extract or how to analyze "
    "the content. The raw HTML is NOT returned - only the AI's analysis based "
    "on your prompt."
)

SEARCH_TOOL_DESCRIPTION = (
    "Search the web and get an AI-synthesized answer with citations. The "
    "response includes the answer and source URLs that can be fetched for "
    "further investigation. Optionally filter by allowed or blocked domains."
)

# Fetch Field Descriptions
FETCH_URL_DESCRIPTION = "The URL to fetch and analyze"

FETCH_PROMPT_DESCRIPTION = (
    "Instructions for how to analyze the page content. Be specific about what "
    "information you want to extract"
)

# Search Field Descriptions
SEARCH_QUERY_DESCRIPTION = "The search query to find information about. Be specific"

SEARCH_ALLOWED_DOMAINS_DESCRIPTION = (
    "Only include results from these domains (e.g., ['*.edu', '*.gov'])"
)

SEARCH_BLOCKED_DOMAINS_DESCRIPTION = (
    "Exclude results from these domains (e.g., ['*.xyz', '*.spam'])"
)
