# SPDX-FileCopyrightText: 2025-present Christopher Soria <chrissoria@berkeley.edu>
#
# SPDX-License-Identifier: MIT

from llm_web_research.__about__ import __version__, __author__, __email__
from llm_web_research.search import web_research
from llm_web_research.precise_search import precise_web_research
from llm_web_research.tavily_search import tavily_search

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "web_research",
    "precise_web_research",
    "tavily_search",
]
