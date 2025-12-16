# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["RepoListResponse", "RepoList", "PaginatedRepoList", "PaginatedRepoListRepo"]


class RepoList(BaseModel):
    """Repository list model"""

    repos: List[str]
    """List of repository names"""


class PaginatedRepoListRepo(BaseModel):
    """Repository item with metadata"""

    base_model: str
    """Base model identifier"""

    repo_name: str
    """Repository name"""


class PaginatedRepoList(BaseModel):
    """Paginated repository list with metadata"""

    has_more: bool
    """Whether more repositories are available"""

    limit: int
    """Page size"""

    offset: int
    """Starting offset"""

    repos: List[PaginatedRepoListRepo]
    """List of repositories with metadata"""

    total: Optional[int] = None
    """Total number of repositories (if available)"""


RepoListResponse: TypeAlias = Union[RepoList, PaginatedRepoList]
