import asyncio
import fnmatch
import functools
import logging
import queue
import traceback
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from logging.handlers import QueueHandler, QueueListener
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Union,
)

from requests.exceptions import HTTPError
from tqdm import tqdm

from jf_ingest import diagnostics, logging_helper
from jf_ingest.config import (
    GitConfig,
    GitProvider,
    GitProviderInJellyfishRepo,
    IngestionConfig,
)
from jf_ingest.constants import Constants
from jf_ingest.events.models import GitIngestEvent, IngestType
from jf_ingest.file_operations import IngestIOHelper, SubDirectory
from jf_ingest.jf_git.exceptions import (
    GitAuthorizationException,
    GitProviderUnavailable,
)
from jf_ingest.jf_git.standardized_models import (
    BackpopulationWindow,
    StandardizedBranch,
    StandardizedCommit,
    StandardizedJFAPIPullRequest,
    StandardizedObject,
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedPullRequestAuthor,
    StandardizedPullRequestMetadata,
    StandardizedPullRequestReviewAuthor,
    StandardizedRepository,
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.telemetry import add_telemetry_fields, jelly_trace, record_span
from jf_ingest.utils import (
    ThreadPoolExecutorWithLogging,
    batch_iterable,
    batch_iterable_by_bytes_size,
    get_jellyfish_company_slug,
    get_object_bytes_size,
    init_jf_ingest_run,
    tqdm_to_logger,
)

logger = logging.getLogger(__name__)

'''

    Constants

'''
# NOTE: ONLY GITHUB IS CURRENTLY SUPPORTED!!!!
BBS_PROVIDER = 'bitbucket_server'
BBC_PROVIDER = 'bitbucket_cloud'
GH_PROVIDER = 'github'
GL_PROVIDER = 'gitlab'
PROVIDERS = [GL_PROVIDER, GH_PROVIDER, BBS_PROVIDER, BBC_PROVIDER]


class JFIngestGitProviderException(Exception):
    pass


class GitObject(Enum):
    GitOrganizations = "git_data_organizations"
    GitUsers = "git_data_users"
    GitTeams = "git_data_teams"
    GitRepositories = "git_data_repos"
    GitBranches = "git_data_branches"
    GitCommits = "git_data_commits"
    GitPullRequests = "git_data_prs"
    GitPullRequestAuthors = "git_data_pr_authors"
    GitPullRequestReviewAuthors = "git_data_pr_review_authors"


def _generate_git_ingest_event(event_name: str, git_config: GitConfig) -> GitIngestEvent:
    return GitIngestEvent(
        company_slug=get_jellyfish_company_slug(),
        ingest_type=IngestType.GIT,
        event_name=event_name,
        git_instance=git_config.instance_slug,
        git_provider=git_config.git_provider.value,
    )


class GitAdapter(ABC):
    config: GitConfig
    PULL_REQUEST_BATCH_SIZE_IN_BYTES = (
        50 * Constants.MB_SIZE_IN_BYTES
    )  # PRs can be huge and of variable size. We need to limit them by batch size in bytes
    NUMBER_OF_COMMITS_PER_BATCH = (
        30000  # Commits are generally uniform in size. This is ~50 MBs per commit batch
    )

    @staticmethod
    def generate_unknown_emoji_code(emoji_code: str) -> str:
        return f'UNKNOWN ({emoji_code})'

    def _transform_data_objects_before_saving(
        self,
        dataclass_objects: (
            List[StandardizedObject]
            | List[StandardizedBranch]
            | List[StandardizedCommit]
            | List[StandardizedOrganization]
            | List[StandardizedPullRequest]
            | List[StandardizedRepository]
            | List[StandardizedTeam]
            | List[StandardizedUser]
            | List[StandardizedPullRequestAuthor]
            | List[StandardizedPullRequestReviewAuthor]
        ),
    ) -> List[Dict]:
        """Helper function for taking a list of objects that inherit from Dataclass and
        transforming them to a list of dictionary objects

        Args:
            dataclass_objects (List[DataclassInstance]): A list of Dataclass Instances

        Returns:
            List[Dict]: A list of dictionaries
        """

        def _transform(obj: StandardizedObject):
            if self.config.git_redact_names_and_urls:
                obj.redact_names_and_urls()
            if self.config.git_strip_text_content:
                obj.strip_text_content()
            return asdict(obj)

        return [_transform(dc_object) for dc_object in dataclass_objects]

    @staticmethod
    def get_git_adapter(config: GitConfig) -> "GitAdapter":
        """Static function for generating a GitAdapter from a provided GitConfig object

        Args:
            config (GitConfig): A git configuration data object. The specific GitAdapter
                is returned based on the git_provider field in this object

        Raises:
            GitProviderUnavailable: If the supplied git config has an unknown git provider, this error will be thrown

        Returns:
            GitAdapter: A specific subclass of the GitAdapter, based on what git_provider we need
        """
        from jf_ingest.jf_git.adapters.azure_devops import AzureDevopsAdapter
        from jf_ingest.jf_git.adapters.github import GithubAdapter
        from jf_ingest.jf_git.adapters.gitlab import GitlabAdapter

        if config.git_provider in [GitProviderInJellyfishRepo.GITHUB, GitProvider.GITHUB]:
            return GithubAdapter(config)
        elif config.git_provider in [GitProviderInJellyfishRepo.ADO, GitProvider.ADO]:
            return AzureDevopsAdapter(config)
        elif config.git_provider in [GitProviderInJellyfishRepo.GITLAB, GitProvider.GITLAB]:
            return GitlabAdapter(config)
        else:
            raise GitProviderUnavailable(
                f'Git provider {config.git_provider} is not currently supported'
            )

    @abstractmethod
    def get_api_scopes(self) -> str:
        """Return the list of API Scopes. This is useful for Validation

        Returns:
            str: A string of API scopes we have, given the adapters credentials
        """
        pass

    @abstractmethod
    def get_organizations(self) -> List[StandardizedOrganization]:
        """Get the list of organizations the adapter has access to

        Returns:
            List[StandardizedOrganization]: A list of standardized organizations within this Git Instance
        """
        pass

    @abstractmethod
    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedUser, None, None]:
        """Get the list of users in a given Git Organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object

        Returns:
            List[StandardizedUser]: A standardized User Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedTeam, None, None]:
        """Get the list of teams in a given Git Organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object

        Returns:
            List[StandardizedUser]: A standardized Team Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_repos(
        self,
        standardized_organization: StandardizedOrganization,
        limit: Optional[int] = None,
        only_private: bool = False,
    ) -> Generator[StandardizedRepository, None, None]:
        """Get a list of standardized repositories within a given organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized organization
            limit (int, optional): When provided, the number of items returned is limited.
            only_private (bool): When True, only private repositories will be returned. Defaults to False

        Returns:
            List[StandardizedRepository]: A list of standardized Repositories
        """
        pass

    @abstractmethod
    def get_repos_count(
        self, standardized_organization: StandardizedOrganization, only_private: bool = False
    ) -> int:
        """Get the count of repositories within a given organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized organization
            only_private (bool): When True, only private repositories will be counted. Defaults to False

        Returns:
            int: The count of repositories
        """
        pass

    @abstractmethod
    def get_commits_for_default_branch(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the Default Branch.

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            limit (int): limit the number of commit objects we will yield
            pull_since (datetime): filter commits to be newer than this date
            pull_until (datetime): filter commits to be older than this date

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        pass

    @abstractmethod
    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_branches: Optional[bool] = False,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedBranch, None, None]:
        """Function for pulling branches for a repository. By default, pull_branches will run as False,
        so we will only process the default branch. If pull_branches is true, than we will pull all
        branches in this repository

        Args:
            standardized_repo (StandardizedRepository): A standardized repo, which hold info about the default branch.
            pull_branches (bool): A boolean flag. If True, pull all branches available on Repo. If false, only process the default branch. Defaults to False.
            limit (int, optional): When provided, the number of items returned is limited.

        Yields:
            StandardizedBranch: A Standardized Branch Object
        """
        pass

    @abstractmethod
    def get_commits_for_branches(
        self,
        standardized_repo: StandardizedRepository,
        branches: List[StandardizedBranch],
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the included branches.
        Included branches are found by crawling across the branches pulled/available
        from get_filtered_branches

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            branches (List[StandardizedBranch]): A list of branches to pull commits for
            pull_since (datetime): A date to pull from
            pull_until (datetime): A date to pull up to
            limit (Optional[int]): limit the number of commit objects we will yield

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        pass

    @abstractmethod
    def get_pr_metadata(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pr_pull_from_date: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        """Get all PRs, but only included the bare necesaties

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
            pr_pull_from_date: This is currently only used by the GithubAdapter. It is useful because
                the GithubAdapter caches Repository metadata, including when the Repo's most recent
                PR was updated. We can determine if we need to pull any PR data in memory, before seeing
                that value via the API

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        pass

    @abstractmethod
    def git_provider_pr_endpoint_supports_date_filtering(self) -> bool:
        """Returns a boolean on if this PR supports time window filtering.
        So far, Github DOES NOT support this (it's adapter will return False)
        but ADO does support this (it's adapter will return True)

        Returns:
            bool: A boolean on if the adapter supports time filtering when searching for PRs
        """
        return False

    @abstractmethod
    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: Optional[int] = None,
        start_cursor: Optional[Any] = None,
        start_window: Optional[datetime] = None,
        end_window: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequest, None, None]:
        """Get the list of standardized Pull Requests for a Standardized Repository.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            pull_files_for_pr (bool): When provided, we will pull file metadata for all PRs
            hash_files_for_prs (bool): When provided, all file metadata will be hashed for PRs
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        pass

    @abstractmethod
    def get_pr_authors(
        self, pr_list: list[StandardizedJFAPIPullRequest]
    ) -> list[StandardizedPullRequestAuthor]:
        """Get the authors of a list of PRs

        This is currently only implemented for GitHub instances
        """
        pass

    @abstractmethod
    def get_pr_review_authors(
        self, pr_list: list[StandardizedJFAPIPullRequest]
    ) -> list[StandardizedPullRequestReviewAuthor]:
        """Get the review authors of a list of PRs

        This is currently only implemented for GitHub instances
        """
        pass

    @abstractmethod
    def get_user(
        self, user_identifier: str, standardize: bool = False, org_login: Optional[str] = None
    ) -> dict | StandardizedUser:
        """Get a single user by their unique identifier (username, email, or id)

        Args:
            user_identifier (str): The unique identifier for the user
            standardize (bool): When True, return a StandardizedUser object. When False, return the raw API dict. Defaults to False.
            org_login (Optional[str]): The organization login, if needed by the adapter to fetch the user. So far only ADO needs this

        Returns:
            dict | StandardizedUser: The user data as a dictionary or StandardizedUser object
        """
        pass

    @abstractmethod
    def get_repo(
        self, login: str, repo_id: str, standardize: bool = False
    ) -> dict | StandardizedRepository:
        """Get a single repo by it's ID. You must know the organization login and repo ID (or Repo Name).
        NOTE: The Github Provider does not uniquely idenify repos by repo ID so you must provide Repo Name instead!

        Args:
            login (str): The organization login
            repo_id (str): The unique identifier for the repo (or Repo Name for Github)
            standardize (bool): When True, return a StandardizedRepository object. When False, return the raw API dict. Defaults to False.
        Returns:
            dict | StandardizedRepository: The repo data as a dictionary or StandardizedRepository object
        """
        pass

    @abstractmethod
    def get_commit(
        self, login: str, repo_id: str, commit_hash: str, standardize: bool = False
    ) -> dict | StandardizedCommit:
        """Get a single commit by it's hash. You must know the organization login and repo ID as well.
        If you are missing one of these values you could try to get the repo first via get_repo and then
        reference the values from the StandardizedRepository object.
        NOTE: The Github Provider does not uniquely idenify repos by repo ID so you must provide Repo Name instead!

        Args:
            login (str): The organization login
            repo_id (str): The unique identifier for the repo (or Repo Name for Github)
            commit_hash (str): The commit hash
            standardize (bool): When True, return a StandardizedCommit object. When False, return the raw API dict. Defaults to False.
        Returns:
            dict | StandardizedCommit: The commit data as a dictionary or StandardizedCommit object
        """
        pass

    @abstractmethod
    def get_pr(
        self, login: str, repo_id: str, pr_number: str, standardize: bool = False
    ) -> dict | StandardizedPullRequest:
        """Get a PR by it's number. You must know the organization login and repo ID as well.
        NOTE: The Github Provider does not uniquely idenify repos by repo ID so you must provide Repo Name instead!

        Args:
            login (str): The organization login
            repo_id (str): The unique identifier for the repo (or Repo Name for Github)
            pr_number (str): The PR number
            standardize (bool): When True, return a StandardizedPullRequest object. When False, return the raw API dict. Defaults to False.
        Returns:
            dict | StandardizedPullRequest: The PR data as a dictionary or StandardizedPullRequest object
        """
        pass

    def help(self, func_name: Optional[str] = None):
        """Helper function to print out available methods on the GitAdapter class.
        Args:
            func_name (Optional[str], optional): The function name to get help for. If not provided, a list of available methods will be printed. Defaults to None.
        """

        def _available_methods():
            getter_functions = filter(lambda func_name: func_name.startswith('get_'), dir(self))
            getter_functions_string_block = '\n\t'.join(getter_functions)
            return f"\n\nAvailable methods:\n\t{getter_functions_string_block}\n"

        def _print_help_message():
            logger.info(
                'This is a helper function inside the GitAdapter base class to help you remember methods available for debugging'
            )
            logger.info(_available_methods())
            logger.info(
                'You can call this function with a specific method name to get more details on that method. Example: _adapter._help("get_repos")'
            )

        if not func_name:
            _print_help_message()
            return
        else:
            func = getattr(self, func_name, None)
            if not func:
                logger.error(f'Function {func_name} not found on adapter {self.__class__.__name__}')
                logger.info(_available_methods())
                return

            logger.info(
                f'\nHelp for function {func_name} on adapter {self.__class__.__name__}:\n\n\t{func.__doc__}\n'
            )

    def get_commits_for_repo(
        self, standardized_repo: StandardizedRepository, branches: List[StandardizedBranch]
    ) -> Generator[StandardizedCommit, None, None]:
        """This is a function that wraps the get_commits_for_branches function and applies the Repo
        backpopulation logic, if we need it to

        Args:
            standardized_repo (StandardizedRepository): A standardized Repository object
            branches (List[StandardizedBranches]): A list of branches to pull commits for

        Yields:
            Generator[StandardizedCommit, None, None]: A stream of commits. Potentially terminating early if we hit the pull from date
        """
        pull_from_for_commits = self.config.get_pull_from_for_commits()
        backpopulation_window = determine_commit_backpopulation_window(
            config=self.config, repo=standardized_repo
        )
        pull_until_for_commits = None

        # If backpopulating, set
        if backpopulation_window:
            backpopulation_start, backpopulation_end = backpopulation_window
            pull_from_for_commits = backpopulation_start
            pull_until_for_commits = backpopulation_end
            logging_helper.send_to_agent_log_file(
                f'Backpopulation was determeined as necessary for {standardized_repo.name}. Backpopulation will run from [{pull_from_for_commits}, {pull_until_for_commits}]',
                level=logging.DEBUG,
            )
        else:
            logging_helper.send_to_agent_log_file(
                f'Backpopulation was not determined as necessary for {standardized_repo.name}. Commits will be pulled from {pull_from_for_commits}',
                level=logging.DEBUG,
            )

        commit_count = 0
        commit = None
        for j, commit in enumerate(
            self.get_commits_for_branches(
                standardized_repo=standardized_repo,
                branches=branches,
                pull_since=pull_from_for_commits,
                pull_until=pull_until_for_commits,
            ),
            start=1,
        ):
            with logging_helper.log_loop_iters('branch commit inside repo', j, 100):
                # If we crawl across commits and find that we already have commits this old, stop processing
                # NOTE: THis is technically redundant, because the get_commits calls should have a pull_from/pull_until
                # scheme that should limit how many commits we pull
                if commit.commit_date and commit.commit_date < pull_from_for_commits:
                    break
                yield commit
                commit_count += 1
        if backpopulation_window:
            commits_backpopulated_to = None
            if commit:
                commits_backpopulated_to = max(
                    min(pull_from_for_commits, commit.commit_date), self.config.pull_from
                )
            else:
                commits_backpopulated_to = max(pull_from_for_commits, self.config.pull_from)
            standardized_repo.commits_backpopulated_to = commits_backpopulated_to
            logging_helper.send_to_agent_log_file(
                f'Setting commits_backpopulated_to for repo {standardized_repo.name} to {commits_backpopulated_to}',
                level=logging.DEBUG,
            )
        logging_helper.send_to_agent_log_file(f'Found {commit_count} commits', level=logging.DEBUG)

    def get_prs_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool,
        hash_files_for_prs: bool,
    ) -> Generator[StandardizedPullRequest, None, None]:
        """This is a function that wraps the get_commits_for_branches function and applies the Repo
        backpopulation logic, if we need it to

        Args:
            standardized_repo (StandardizedRepository): A standardized Repository object

        Yields:
            Generator[StandardizedCommit, None, None]: A stream of commits. Potentially terminating early if we hit the pull from date
        """
        start_time = datetime.now()
        prs_start_cursor = None
        backpopulation_window = determine_pr_backpopulation_window(
            config=self.config, repo=standardized_repo
        )
        if backpopulation_window:
            pull_from_for_prs, pull_up_to_for_prs = backpopulation_window
            logging_helper.send_to_agent_log_file(
                f'Backpopulation was determined as necessary for Repo {standardized_repo.name} (ID: {standardized_repo.id}). '
                f'Backpop window: [{pull_from_for_prs}, {pull_up_to_for_prs}]',
                level=logging.DEBUG,
            )
        else:
            pull_from_for_prs = self.config.get_pull_from_for_prs(standardized_repo.id)
            pull_up_to_for_prs = datetime.now().astimezone(timezone.utc) + timedelta(days=1)
            logging_helper.send_to_agent_log_file(
                f'Backpopulation was NOT determined as necessary for Repo {standardized_repo.name} (ID: {standardized_repo.id}). '
                f'PR Pull Window: [{pull_from_for_prs}, {pull_up_to_for_prs}]',
                level=logging.DEBUG,
            )
        # If we are backpopulating and our Adapter DOES NOT support filtering for PRs with
        # datetime bounds, we need to find the starting mark of where to start
        # pulling PRs. To do this, we leverage the get_pr_metadata function, which should be
        # a light-weight alternative (in terms of API calls) to the get_prs function.
        # For an adapter that uses GQL, this alternative can be VERY light. For a non-GQL
        # adapter, this can be slightly lighter but likely not by much
        # NOTE: If a provider supports PR time filtering (like ADO), then this can be skipped!
        # It is faster to have the API do the filtering for us
        if backpopulation_window and not self.git_provider_pr_endpoint_supports_date_filtering():
            logging_helper.send_to_agent_log_file(
                f'Backpopulation window detected for PRs in {standardized_repo.name}, attempting to walk back on all PRs to find backpopulation window end date',
                level=logging.DEBUG,
            )

            backpopulation_start, backpopulation_end = backpopulation_window
            pull_from_for_prs = backpopulation_start
            prs_found = False
            for api_pr_metadata in self.get_pr_metadata(
                standardized_repo=standardized_repo, pr_pull_from_date=pull_from_for_prs
            ):
                if api_pr_metadata.updated_at > backpopulation_end:
                    logging_helper.send_to_agent_log_file(
                        f'Backpopulation flow -- skipping PR (ID: {api_pr_metadata.id}) from {api_pr_metadata.updated_at} '
                        f'because backpopulation_end is {backpopulation_end.isoformat()} (Repo: {standardized_repo.name})',
                        level=logging.DEBUG,
                    )
                    # This is the START cursor, so it is NON-INCLUSIVE. We want it to be trailing by 1 index
                    prs_start_cursor = api_pr_metadata.api_index
                    continue
                else:
                    if api_pr_metadata.updated_at <= self.config.pull_from:
                        logging_helper.send_to_agent_log_file(
                            f'Exiting backpopulation walkback loop and NOT ingesting this PR, because PR {api_pr_metadata.id} was last updated at {api_pr_metadata.updated_at} which is less than our base pull from date: {self.config.pull_from}',
                            level=logging.DEBUG,
                        )
                        standardized_repo.prs_backpopulated_to = self.config.pull_from
                        return
                    elif api_pr_metadata.updated_at <= backpopulation_start:
                        # We want to ingest this one PR in this case, because it will greatly fast forward our backpopulation dates
                        logging_helper.send_to_agent_log_file(
                            f'Exiting backpopulation walkback loop, because PR {api_pr_metadata.id} was last updated at {api_pr_metadata.updated_at} which is less than our backpopulation start time ({backpopulation_start}). We WILL ingest this PR',
                            level=logging.DEBUG,
                        )
                        prs_found = True
                        break
                    else:
                        logging_helper.send_to_agent_log_file(
                            f'Exiting backpopulation walkback loop, because PR {api_pr_metadata.id} was last updated at {api_pr_metadata.updated_at} which is within our backpopulation window ([{backpopulation_start}, {backpopulation_end}]). We will ingest this PR and all other PRs up until {backpopulation_start}',
                            level=logging.DEBUG,
                        )
                        prs_found = True
                        break

            if not prs_found:
                logging_helper.send_to_agent_log_file(
                    f'No PRs found when looking in and beyond our backpopulation window, setting PRs backpopulated to to the pull from date for this git instance {self.config.pull_from}',
                    level=logging.DEBUG,
                )
                standardized_repo.prs_backpopulated_to = self.config.pull_from
                return

        pr = None
        pr_count_for_repo = 0
        get_pr_runs = 0
        repo_time_limit_emitted = False
        repo_time_limit_in_minutes = 10
        for i, pr in enumerate(
            self.get_prs(
                standardized_repo=standardized_repo,
                pull_files_for_pr=pull_files_for_pr,
                hash_files_for_prs=hash_files_for_prs,
                start_cursor=prs_start_cursor,
                start_window=pull_from_for_prs,
                end_window=pull_up_to_for_prs,
            ),
            start=1,
        ):
            get_pr_runs += 1
            with logging_helper.log_loop_iters('pr inside repo', i, 10):
                # If we crawl across prs and find that we already have PR this old, stop processing
                if (
                    not self.git_provider_pr_endpoint_supports_date_filtering()
                    and pr.updated_at
                    and pr.updated_at <= pull_from_for_prs
                ):
                    logging_helper.send_to_agent_log_file(
                        f'Stopping PR crawl for repo {standardized_repo.name} because PR {pr.id} as been identified as being older than the pull from date ({pr.updated_at} <= {pull_from_for_prs}).',
                        level=logging.DEBUG,
                    )
                    # If we're backpopulating, this PR represents the next oldest PR. If we ingest it, we can speed up
                    # the backpopulation window to be as old as this PR. Only ingest it if it's within the parent 'pull_from' window, though
                    if backpopulation_window and pr.updated_at >= self.config.pull_from:
                        logging_helper.send_to_agent_log_file(
                            f'This PR ({pr.id}) will be ingest by Jellyfish, because are backpopulating this repo ({standardized_repo.name})',
                            level=logging.DEBUG,
                        )
                        yield pr
                        pr_count_for_repo += 1
                    break
                yield pr
                pr_count_for_repo += 1

            time_elapsed_in_minutes = (datetime.now() - start_time).total_seconds() / 60
            if (
                time_elapsed_in_minutes >= repo_time_limit_in_minutes
                and not repo_time_limit_emitted
            ):
                logging_helper.send_to_agent_log_file(
                    f'Repo {standardized_repo.name} has been processing PRs for over {repo_time_limit_in_minutes} minutes. '
                    f'It has processed {pr_count_for_repo} PRs so far. '
                    f'It {"is" if backpopulation_window else "is not"} backpopulating. {f"{backpopulation_window}" if backpopulation_window else ""} '
                    f'Total time elapsed so far for {standardized_repo.name}: {timedelta(minutes=time_elapsed_in_minutes)}. '
                    'Continuing processing, but logging this for visibility.',
                    level=logging.INFO,
                )
                repo_time_limit_emitted = True
        add_telemetry_fields({'get_pr_runs': get_pr_runs})
        # If we're backpopulating, update the prs_back_populated_to variable
        if backpopulation_window:
            prs_back_populated_to = None
            if pr:
                prs_back_populated_to = max(
                    min(pull_from_for_prs, pr.updated_at), self.config.pull_from
                )
            else:
                prs_back_populated_to = max(pull_from_for_prs, self.config.pull_from)
            standardized_repo.prs_backpopulated_to = prs_back_populated_to
            logging_helper.send_to_agent_log_file(
                f'Setting prs_backpopulated_to for repo {standardized_repo.name} to {prs_back_populated_to}',
                level=logging.DEBUG,
            )

        total_time_elapsed_in_minutes = (datetime.now() - start_time).total_seconds() / 60
        logging_helper.send_to_agent_log_file(
            f'Done Processing PRs for repo {standardized_repo.name}. '
            f'Found {pr_count_for_repo} PRs. '
            f'Total time elapsed: {timedelta(minutes=total_time_elapsed_in_minutes)}.',
            level=logging.INFO if repo_time_limit_emitted else logging.DEBUG,
        )

    def get_filtered_branches(
        self, repo: StandardizedRepository, branches: List[StandardizedBranch]
    ) -> set[str]:
        """Return branches for which we should pull commits, specified by customer in git config.
            The repo's default branch will always be included in the returned list.

        Args:
            repo (StandardizedRepository): A standardized repository

        Returns:
            set[str]: A set of branch names (as strings)
        """

        # Helper function
        def get_matching_branches(
            included_branch_patterns: List[str], repo_branch_names: List[Optional[str]]
        ) -> List[str]:
            # Given a list of patterns, either literal branch names or names with wildcards (*) meant to match a set of branches in a repo,
            # return the list of branches from repo_branches that match any of the branch name patterns.
            # fnmatch is used over regex to support wildcards but avoid complicating the requirements on branch naming in a user's config.
            matching_branches = []
            for repo_branch_name in repo_branch_names:
                if not repo_branch_name:
                    continue
                elif self.config.pull_all_commits_and_branches:
                    matching_branches.append(repo_branch_name)
                elif any(
                    fnmatch.fnmatch(repo_branch_name, pattern)
                    for pattern in included_branch_patterns
                ):
                    matching_branches.append(repo_branch_name)
            return matching_branches

        # Always process the default branch
        branches_to_process = [repo.default_branch_name] if repo.default_branch_name else []
        # Agent use case: check for the included_branches values
        additional_branches_for_repo: List[str] = self.config.included_branches_by_repo.get(
            repo.name, []
        )

        # Extend and potentially filter branches to process
        repo_branch_names = [b.name for b in branches if b]
        branches_to_process.extend(
            get_matching_branches(additional_branches_for_repo, repo_branch_names)
        )
        return set(branches_to_process)

    def discover_new_orgs(self) -> List[StandardizedOrganization]:
        """Helper function for discovering new Git organizations. Currently
        not implemented because only Github has been implement as a GitAdapter
        subclass, and Github DOES NOT support discovering new orgs. Orgs must
        be entered manually

        Raises:
            NotImplementedError: Error stating that this function is net yet to use yet

        Returns:
            List[StandardizedOrganization]: A list of standardized Org Objects
        """
        raise NotImplementedError('Discover New Orgs is not yet implemented')

    def load_and_dump_git(self, git_config: GitConfig, ingest_config: IngestionConfig):
        """This is a shared class function that can get called by
        the different types of GitAdapters that extend this class.
        This function handles fetching all the necessary data from
        Git, transforming it, and saving it to local disk and/or S3

        Args:
            ingest_config (IngestionConfig): A valid Ingestion Config
        """
        init_jf_ingest_run(ingestion_config=ingest_config)
        self._run_load_and_dump_git(git_config=git_config, ingest_config=ingest_config)

    class CommitOrPR(Enum):
        COMMIT = 'commit'
        PR = 'pr'

        def __str__(self) -> str:
            return self.value

    def _pull_commits_or_prs_for_repos_helper(
        self,
        commit_or_pr: CommitOrPR,
        repos_to_process: List[StandardizedRepository],
        repo_to_branches: Dict[str, List[StandardizedBranch]],  # Used only for commits
        use_async: bool,
        upload_function: Callable,
    ) -> int:
        """
        Helper function to reduce the amount of duplicated code between pulling commits and PRs

        Args:
            commit_or_pr (CommitOrPR): An enum value indicating whether to pull commits or PRs
            repos_to_process (List[StandardizedRepository]): A list of standardized repositories to process
            repo_to_branches (Dict[str, List[StandardizedBranch]]): A mapping of repo IDs to branches to process (only used for commits)
            use_async (bool): Whether to use asynchronous processing
            upload_function (Callable): The function to call to upload processed data

        Returns:
            int: The total number of objects processed/uploaded
        """

        # Define Helper Function for Processing and Uploading Commits or PRs, which is repeated for
        # repos needing backpopulation and those that do not need it
        total_objects_processed = 0
        object_name = (
            GitObject.GitCommits.value
            if commit_or_pr == self.CommitOrPR.COMMIT
            else GitObject.GitPullRequests.value
        )

        def _process_and_upload_objects(
            desc: str, repos_to_process: List[StandardizedRepository]
        ) -> int:
            objects_processed = 0

            # For each repo, create a generator of commits or PRs
            # that live within that repo.
            # If use_async is true than we will asynchronously query
            # across repos
            list_of_object_generators = [
                (
                    self.get_commits_for_repo(repo, branches=repo_to_branches[repo.id])
                    if commit_or_pr
                    == self.CommitOrPR.COMMIT  # Conditionally call the right function
                    else self.get_prs_for_repo(
                        repo,
                        pull_files_for_pr=self.config.pull_files_for_prs,
                        hash_files_for_prs=self.config.hash_files_for_prs,
                    )
                )
                for repo in repos_to_process
            ]

            with tqdm_to_logger(
                desc=f"{desc}{' (async)' if use_async else ''}",
                unit=f' Repos',
                total=len(repos_to_process),
                use_async=use_async,
            ) as repos_progress_bar:
                if use_async:
                    objects_async_wrapper = self.async_process_iterator(
                        aiterable=self.async_batch_cast_iterables(
                            list_of_object_generators, progress_bar=repos_progress_bar
                        ),
                        write_function=upload_function,
                        object_name=object_name,
                        limiter_function=(
                            len if commit_or_pr == self.CommitOrPR.COMMIT else get_object_bytes_size
                        ),
                        limiter_max=(
                            self.NUMBER_OF_COMMITS_PER_BATCH
                            if commit_or_pr == self.CommitOrPR.COMMIT
                            else self.PULL_REQUEST_BATCH_SIZE_IN_BYTES
                        ),
                    )
                    objects_processed += asyncio.run(objects_async_wrapper)
                else:
                    # Wrap the iterable to update the progress bar
                    def _process_iterable_with_progress_bar(
                        generators: List[Generator[Any, None, None]]
                    ) -> Generator[Generator, None, None]:
                        for generator in generators:
                            yield from generator
                            repos_progress_bar.update(1)

                    objects_generator_with_pbar = _process_iterable_with_progress_bar(
                        list_of_object_generators
                    )

                    # Pass the wrapped iterable to the appropriate batcher function
                    batcher_function = (
                        batch_iterable(
                            objects_generator_with_pbar, batch_size=self.NUMBER_OF_COMMITS_PER_BATCH
                        )
                        if commit_or_pr == self.CommitOrPR.COMMIT
                        else batch_iterable_by_bytes_size(
                            objects_generator_with_pbar,
                            batch_byte_size=self.PULL_REQUEST_BATCH_SIZE_IN_BYTES,
                        )
                    )

                    # Upload in batches
                    for batch_num, object_batch in enumerate(batcher_function):
                        objects_processed += len(object_batch)
                        object_batch_as_dict = self._transform_data_objects_before_saving(
                            object_batch
                        )
                        upload_function(
                            object_name=object_name,
                            json_data=object_batch_as_dict,
                            batch_number=batch_num,
                        )

            return objects_processed

        #
        # Segement Repos between those needing and not needing backpopulation
        #
        repos_needing_backpopulation = [
            repo
            for repo in repos_to_process
            if (
                repo.commit_backpopulation_window
                if commit_or_pr == self.CommitOrPR.COMMIT
                else repo.pr_backpopulation_window
            )
        ]
        repos_not_needing_backpopulation = [
            repo
            for repo in repos_to_process
            if not (
                repo.commit_backpopulation_window
                if commit_or_pr == self.CommitOrPR.COMMIT
                else repo.pr_backpopulation_window
            )
        ]

        #
        # Run backpopulation object fetching
        #
        with record_span(f'process_backpopulation_{commit_or_pr}s'):
            total_objects_processed += _process_and_upload_objects(
                desc=f'Processing {commit_or_pr}s for Repos Needing Backpopulation across {len(repos_needing_backpopulation)} repos',
                repos_to_process=repos_needing_backpopulation,
            )

        #
        # Run non-backpopulation object fetching
        #
        with record_span(f'process_non_backpopulation_{commit_or_pr}s'):
            total_objects_processed += _process_and_upload_objects(
                desc=f'Processing {commit_or_pr}s for Repos Not Needing Backpopulation across {len(repos_not_needing_backpopulation)} repos',
                repos_to_process=repos_not_needing_backpopulation,
            )

        # Done
        if not total_objects_processed:
            upload_function(object_name=object_name, json_data=[])

        logger.info(
            f'Successfully processed {total_objects_processed} total {commit_or_pr}s across {len(repos_to_process)} repos.'
        )
        add_telemetry_fields({f'git_{commit_or_pr}_count': total_objects_processed})
        return total_objects_processed

    def _run_load_and_dump_git(self, git_config: GitConfig, ingest_config: IngestionConfig):
        #######################################################################
        # Init IO Helper
        #######################################################################
        ingest_io_helper = IngestIOHelper(ingest_config=ingest_config)

        # Wrapper function for writing to the IngestIOHelper
        def _write_to_s3_or_local(
            object_name: str, json_data: list[dict], batch_number: Optional[Union[int, str]] = 0
        ):
            ingest_io_helper.write_json_to_local_or_s3(
                object_name=object_name,
                json_data=json_data,
                subdirectory=SubDirectory.GIT,
                save_locally=ingest_config.save_locally,
                upload_to_s3=ingest_config.upload_to_s3,
                git_instance_key=self.config.instance_file_key,
                batch_number=batch_number,
            )

        use_async = self.config.jf_options.get('git_pull_use_async', False)
        if use_async:
            # Set up async logging. Without this, many of our logs would block the main thread or be swallowed.
            async_log_queue: queue.Queue = queue.Queue()
            async_log_listener = QueueListener(async_log_queue, logging.StreamHandler())
            async_log_handler = QueueHandler(async_log_queue)
            logger.addHandler(async_log_handler)
            async_log_listener.start()

            logger.info(
                'Asynchronous pull enabled. Fetch calls are made asynchronously where possible.'
            )

        #######################################################################
        # ORGANIZATION DATA
        #######################################################################
        with record_span('get_organizations'):
            logger.info('Fetching Git Organization Data...')
            try:
                standardized_organizations: List[StandardizedOrganization] = (
                    self.get_organizations()
                )
            except HTTPError as e:
                resp = getattr(e, 'response', None)
                if resp and resp.status_code in [401, 403, 404]:
                    raise GitAuthorizationException(
                        f'Unable to fetch organizations for {git_config.git_provider} {git_config.instance_slug}: {e}'
                    )
                raise
            logger.info(
                f'Successfully pulled Git Organizations data for {len(standardized_organizations)} Organizations.'
            )
            add_telemetry_fields({'git_organization_count': len(standardized_organizations)})
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitOrganizations.value,
            json_data=self._transform_data_objects_before_saving(standardized_organizations),
        )

        #######################################################################
        # USER DATA
        #######################################################################
        if not git_config.skip_pulling_users:
            logger.info('Fetching Git User Data...')
            with tqdm_to_logger(
                desc='Processing Users across Organizations',
                unit=' Organizations',
                total=len(standardized_organizations),
                use_async=use_async,
            ) as orgs_pbar:

                def _get_users_with_progress_bar(
                    org: StandardizedOrganization,
                ) -> Generator[StandardizedUser, None, None]:
                    users = self.get_users(org)
                    orgs_pbar.update(1)
                    yield from users

                with record_span('get_users'):
                    if use_async:
                        get_users_funcs: List[Callable] = []
                        for org in standardized_organizations:
                            get_users_funcs.append(
                                functools.partial(_get_users_with_progress_bar, org)
                            )
                        standardized_users = asyncio.run(
                            self.call_async(get_users_funcs, force_eval=True)
                        )
                    else:
                        standardized_users = [
                            user
                            for org in standardized_organizations
                            for user in _get_users_with_progress_bar(org)
                        ]
                    add_telemetry_fields({'git_user_count': len(standardized_users)})
            logger.info(f'Successfully found {len(standardized_users)} users.')
            # Upload Data
            _write_to_s3_or_local(
                object_name=GitObject.GitUsers.value,
                json_data=self._transform_data_objects_before_saving(standardized_users),
            )
        else:
            _write_to_s3_or_local(
                object_name=GitObject.GitUsers.value,
                json_data=[],
            )
            logger.info(
                f'Not pulling users because \'skip_pulling_users\' is set to: {git_config.skip_pulling_users}.'
            )

        #######################################################################
        # REPO DATA, NOTE THAT WE UPLOAD LATER BECAUSE WE NEED TO SET
        # THE BACKPOPULATD DATES BELOW AFTER WE PULL PRS AND COMMITS
        #######################################################################
        if not git_config.skip_pulling_repos:
            with record_span('get_repos'):
                logger.info('Fetching Git Repo Data...')

                # Gitlab orgs can share repos. To prevent duplicates, track the ids seen.
                repo_ids_seen: Set[str] = set()
                standardized_repos: List[StandardizedRepository] = []

                with tqdm_to_logger(
                    desc='Pulling all available Repositories across all Organizations (async)',
                    unit=' Organizations',
                    total=len(standardized_organizations),
                    use_async=use_async,
                ) as pbar:

                    def _get_repo_with_progress_bar(
                        org: StandardizedOrganization,
                    ) -> Generator[StandardizedRepository, None, None]:
                        repos = self.get_repos(standardized_organization=org)
                        pbar.update(1)
                        yield from repos

                    if use_async:
                        get_repos_funcs: List[Callable] = []
                        for org in standardized_organizations:
                            get_repos_funcs.append(
                                functools.partial(_get_repo_with_progress_bar, org=org)
                            )
                        repos_results = asyncio.run(
                            self.call_async(get_repos_funcs, force_eval=True)
                        )
                        for repo in repos_results:
                            repo_id = repo.id
                            if repo_id in repo_ids_seen:
                                continue
                            standardized_repos.append(repo)
                            repo_ids_seen.add(repo_id)
                    else:
                        for org in standardized_organizations:
                            with record_span(
                                'get_repos_for_org',
                                {'org_name': str(org.name), 'org_login': str(org.login)},
                            ):
                                for repo in _get_repo_with_progress_bar(org):
                                    repo_id = repo.id
                                    if repo_id in repo_ids_seen:
                                        continue
                                    standardized_repos.append(repo)
                                    repo_ids_seen.add(repo_id)

                logger.info(
                    f'Successfully pulled Git Repo Data for {len(standardized_repos)} Repos.'
                )
                add_telemetry_fields({'git_repo_count': len(standardized_repos)})
        else:
            logger.info(
                f'Not pulling new repo data because \'skip_pulling_repos\' is set to {git_config.skip_pulling_repos}. '
                f'We will pull data for the {len(git_config.repos_in_jellyfish)} repos that already exist in Jellyfish'
            )
            standardized_repos = git_config.repos_in_jellyfish

        repos_to_process = [
            repo for repo in standardized_repos if repo.id not in git_config.quiescent_repos
        ]

        filters = []
        if self.config.included_repos:
            logger.info(f'Filtering repos to only include {self.config.included_repos}')

            def check_included_repo(repo_to_check: StandardizedRepository) -> bool:
                for repo_to_include in self.config.included_repos:
                    if repo_to_check.name.lower() == str(repo_to_include).lower() or str(
                        repo_to_check.id
                    ) == str(repo_to_include):
                        return True
                return False

            filters.append(check_included_repo)
        if self.config.excluded_repos:
            logger.info(f'Filtering repos to exclude {self.config.excluded_repos}')

            def check_excluded_repo(repo_to_check: StandardizedRepository) -> bool:
                for repo_to_exclude in self.config.excluded_repos:
                    if repo_to_check.name.lower() == str(repo_to_exclude).lower() or str(
                        repo_to_check.id
                    ) == str(repo_to_exclude):
                        return False
                return True

            filters.append(check_excluded_repo)

        repos_to_process = [
            repo for repo in repos_to_process if all(filt(repo) for filt in filters)
        ]

        repo_count = len(repos_to_process)

        # Generate Backpopulation windows for repos
        repos_to_process = _hydrate_backpopulation_windows_for_repos(
            config=self.config, repos=repos_to_process
        )

        logging_helper.send_to_agent_log_file(
            f'Processing {len(repos_to_process)}. {len(git_config.quiescent_repos)} were marked as being quiescent'
        )

        #######################################################################
        # BRANCH DATA
        # NOTE: Branches are optionally processed, depending on GitConfiguration.
        # For Direct Connect it is likely we only process the default branch,
        # for agent we process all branches
        #######################################################################
        repo_to_branches: dict[str, List[StandardizedBranch]] = {}
        all_branches = []
        get_branches_funcs: dict[str, Callable] = {}
        with tqdm_to_logger(
            desc='Processing Branches for each Repo',
            unit=' Repos',
            total=len(repos_to_process),
            use_async=use_async,
        ) as pbar:

            def _get_branches_with_tqdm(
                repo: StandardizedRepository, pull_all: bool
            ) -> Generator[StandardizedBranch, None, None]:
                branches = self.get_branches_for_repo(repo, pull_all)
                yield from branches
                pbar.update(1)

            with record_span('get_branches_for_repos'):
                for repo in repos_to_process:
                    pull_branches = (
                        git_config.pull_all_commits_and_branches
                        or git_config.repo_id_to_pull_all_commits_and_branches.get(repo.id, False)
                    )
                    # If we're using async, use this to build all of our calls. They'll be run after we collect them.
                    if use_async:
                        get_branches_funcs[repo.id] = functools.partial(
                            _get_branches_with_tqdm, repo, pull_branches
                        )
                    else:
                        branch_batch = []
                        # Iterate across branches and update the progress bar so we can see
                        # counts and rates of branch processing
                        for branch in _get_branches_with_tqdm(repo, pull_branches):
                            branch_batch.append(branch)

                        repo_to_branches[repo.id] = branch_batch
                        all_branches.extend(branch_batch)
                if use_async:
                    wrapped_branch_funcs = []

                    def get_repo_branch_wrapper(repository_id, branch_func):
                        results = [b for b in branch_func()]
                        # Return a tuple here for relating back to the repo. Must be a list for call_async.
                        return [(repository_id, results)]

                    for r_id, b_func in get_branches_funcs.items():
                        wrapped_branch_funcs.append(
                            functools.partial(get_repo_branch_wrapper, r_id, b_func)
                        )
                    branches_results = asyncio.run(
                        self.call_async(wrapped_branch_funcs, force_eval=False)
                    )
                    # We can use the repo id on the branch to relate them back to the repo for later use.
                    for b_result in branches_results:
                        repo_to_branches[b_result[0]] = b_result[1]
                        all_branches.extend(b_result[1])
                add_telemetry_fields({'git_branch_count': len(all_branches)})

        _write_to_s3_or_local(
            object_name=GitObject.GitBranches.value,
            json_data=self._transform_data_objects_before_saving(all_branches),
        )

        #######################################################################
        # COMMIT DATA
        #
        # NOTE: Commit data can be quite large, so for better memory handling
        # we will create a chain of generators (get_commits_for_branches returns a generator)
        # and process our way through those generators, uploading data ~50 MBs at a time
        # NOTE: Commit data is pretty uniform in size (each commit is ~2KB), so we'll upload
        # in batches of 30k commits (roughly 50 MB in data)
        #
        #######################################################################
        logger.info(f'Fetching Git Commit Data for {repo_count} Repos...')
        with record_span('get_commits_for_repos'):
            total_commits = self._pull_commits_or_prs_for_repos_helper(
                commit_or_pr=self.CommitOrPR.COMMIT,
                repos_to_process=repos_to_process,
                repo_to_branches=repo_to_branches,
                use_async=use_async,
                upload_function=_write_to_s3_or_local,
            )
            # total_commits is tracked inside the helper function and added to telemetry there

        #######################################################################
        # PULL REQUEST DATA
        #
        # NOTE: Pull Request data can be quite large, so for better memory handling
        # we will create a chain of generators (get_prs returns a generator)
        # and process our way through those generators, uploading data ~50 MBs at a time
        #
        #######################################################################
        logger.info(f'Fetching Git Pull Request Data for {repo_count} Repos...')
        with record_span('get_prs_for_repos'):
            # NOTE: Need to filter out repos that should skip pulling PRs for
            repos_to_process_prs_for = []
            skipped_repo_strings = []  # List of strings for logging purposes only
            for _repo in repos_to_process:
                if self.config.repos_to_skip_pull_prs_for.get(_repo.id, False):
                    skipped_repo_strings.append(f'{_repo.name} (ID: {_repo.id})')
                else:
                    repos_to_process_prs_for.append(_repo)

            if skipped_repo_strings:
                logger.info(
                    f'The following repos will skip pulling PRs because \'avoid_pulling_prs\' is set to True: {", ".join(skipped_repo_strings)}'
                )

            total_prs = self._pull_commits_or_prs_for_repos_helper(
                commit_or_pr=self.CommitOrPR.PR,
                repos_to_process=repos_to_process_prs_for,
                repo_to_branches=repo_to_branches,
                use_async=use_async,
                upload_function=_write_to_s3_or_local,
            )

        # Upload Repo Data at the very end
        _write_to_s3_or_local(
            object_name=GitObject.GitRepositories.value,
            json_data=(
                self._transform_data_objects_before_saving(repos_to_process)
                if repos_to_process
                else []
            ),
        )

        if use_async:
            logger.removeHandler(async_log_handler)
            async_log_listener.stop()

        summary_message = (
            'The folliwing counts of Git data were pulled:',
            f'\tTotal Organizations: {len(standardized_organizations)},',
            f'\tTotal Repositories: {len(repos_to_process)}, ',
            f'\tTotal Users (from the API, not from Pull Requests): {len(standardized_users) if not git_config.skip_pulling_users else 0}, ',
            f'\tTotal Branches (from the API, not from Pull Requests): {len(all_branches)}, ',
            f'\tTotal Commits (from the API, not from Pull Requests): {total_commits}, ',
            f'\tTotal Pull Requests: {total_prs}',
            f'\tNOTE: Users, Branches, and Commits associated with Pull Requests are not included in these counts.',
            '',
        )

        logger.info('\n'.join(summary_message))
        logger.info(f'Done processing Git Data!')

    @logging_helper.log_entry_exit()
    def validate_instance_authorization(self) -> None:
        """
        Validate our authorization to the Git instance is sufficient for collecting
        the necessary data.

        Raises:
            GitAuthorizationException: Raised when unable to access a required resource
        """
        if self.config.git_provider == GitProviderInJellyfishRepo.GITHUB_ENTERPRISE_CLOUD:
            logger.info('Skipping authorization check for Github Enterprise Cloud instance')
            return None

        logger.info(
            f'Verifying authorization to {self.config.company_slug} {self.config.git_provider.name} instance...'
        )

        # If discover orgs is set to false, we'll track instances where we can successfully make requests with
        # the authentication provided, but are unable to receive any results
        discover_orgs = self.config.discover_organizations
        logger.info(f'Discover organizations set to {discover_orgs}')

        # Some Github instances are only used for copilot - in this case, it's expected that we won't be able to
        # pull any data. In the future, we'll have a flag to denote whether the instance is *only* used for copilot,
        # but for now, we'll just check if the instance has it enabled
        copilot_enabled = self.config.copilot_enabled
        logger.info(f'Copilot enabled set to {copilot_enabled}')

        # Providing a pull since datetime is required for Github when pulling commits. Setting it to an old date to
        # account for old repositories that may have been inactive for some time
        pull_since_date = datetime(1970, 1, 1, tzinfo=timezone.utc)

        if discover_orgs:
            try:
                orgs = self.get_organizations()
                logger.info(f'Discovered {len(orgs)} accessible organizations')
            except Exception as e:
                raise GitAuthorizationException(
                    f'Unable to access organizations for {self.config.git_provider}: {e}'
                )
        else:
            logger.info(
                f'Using {len(self.config.git_organizations)} provided organizations from JF DB'
            )
            orgs = [
                StandardizedOrganization(id=org, name=None, login=org, url=None)
                for org in self.config.git_organizations
            ]

        # Keep track of auth errors rather than raising immediately to capture all potential issues
        auth_errors: dict[str, list[str]] = {}

        # Some Gitlab instances can have thousands of orgs (aka groups), which will make the auth validator
        # take a long time to run. To prevent this, we'll break the look if 10 orgs have been successfully checked
        is_gitlab_provider = bool(self.config.git_provider == GitProviderInJellyfishRepo.GITLAB)
        successful_org_auth_count = 0

        for idx, org in enumerate(orgs, start=1):
            if org.login in self.config.excluded_organizations:
                logger.info(f'Skipping authorization check for excluded org {org.login}')
                continue

            logger.info(f'Verifying authorization to org {org.login} ({idx}/{len(orgs)})')
            any_resource_accessed = False
            resource_accessed_types: list[str] = []
            org_auth_errors: list[str] = []

            if not self.config.skip_pulling_users:
                if _validate_resource_access(
                    resource_name='users',
                    fetch_func=self.get_users,
                    fetch_kwargs={'standardized_organization': org, 'limit': 10},
                    org_auth_errors=org_auth_errors,
                    discover_orgs=discover_orgs,
                    record_empty=True,
                ):
                    any_resource_accessed = True
                    resource_accessed_types.append('users')

            # Gitlab does not have the concept of teams other than groups, which we classify as orgs
            if (
                not self.config.git_provider == GitProviderInJellyfishRepo.GITLAB
                and self.config.pull_teams
            ):
                if _validate_resource_access(
                    resource_name='teams',
                    fetch_func=self.get_teams,
                    fetch_kwargs={'standardized_organization': org, 'limit': 10},
                    org_auth_errors=org_auth_errors,
                    discover_orgs=discover_orgs,
                    record_empty=True,
                ):
                    any_resource_accessed = True
                    resource_accessed_types.append('teams')

            if not self.config.skip_pulling_repos:
                repos, get_repos_err = self._get_repos_for_auth_check(org)
                repo_data_access = False

                # If we encountered an error while trying to access repositories, the returned list of repos will
                # be empty, and this block will be skipped
                if repos:
                    branch_access = False
                    commit_access = False
                    pr_access = False

                    for repo_idx, repo in enumerate(repos, start=1):
                        logger.info(
                            f'Attempting auth validation on repo {repo.name} (attempt {repo_idx}/{len(repos)})'
                        )

                        if branches := _validate_resource_access(
                            resource_name='branches',
                            fetch_func=self.get_branches_for_repo,
                            fetch_kwargs={
                                'standardized_repo': repo,
                                'pull_branches': True,
                                'limit': 10,
                            },
                            org_auth_errors=org_auth_errors,
                            discover_orgs=discover_orgs,
                            record_empty=False,
                        ):
                            branch_access = True
                            resource_accessed_types.append('branches')

                            if _validate_resource_access(
                                resource_name='commits',
                                fetch_func=self.get_commits_for_branches,
                                fetch_kwargs={
                                    'standardized_repo': repo,
                                    'branches': branches,
                                    'pull_since': pull_since_date,
                                    'limit': 1,
                                },
                                org_auth_errors=org_auth_errors,
                                discover_orgs=discover_orgs,
                                record_empty=False,
                            ):
                                commit_access = True
                                resource_accessed_types.append('commits')

                        if _validate_resource_access(
                            resource_name='prs',
                            fetch_func=self.get_prs,
                            fetch_kwargs={
                                'standardized_repo': repo,
                                'pull_files_for_pr': True,
                                'hash_files_for_prs': False,
                                'limit': 1,
                            },
                            org_auth_errors=org_auth_errors,
                            discover_orgs=discover_orgs,
                            record_empty=False,
                        ):
                            pr_access = True
                            resource_accessed_types.append('prs')

                        if any([branch_access, commit_access, pr_access]):
                            any_resource_accessed = True
                            repo_data_access = True

                        # Only break if we've accessed all types of repository resources
                        if all([branch_access, commit_access, pr_access]):
                            break
                elif copilot_enabled and not get_repos_err:
                    logger.info(
                        f'No repositories found, but copilot is enabled - skipping repo auth check for org {org.login}'
                    )
                    continue
                else:
                    org_auth_errors.append('Unable to access any organization repositories')

                if not get_repos_err and repos:
                    if not repo_data_access and not discover_orgs:
                        org_auth_errors.append(
                            f'Unable to access branches, commits or PRs from any of the first {len(repos)} accessible repos'
                        )
                    else:
                        # If we have discover_orgs set to True, only check that we didn't raise any exceptions
                        logger.info(f'Authorization validated for repo data in {org.login}')
                elif get_repos_err:
                    org_auth_errors.append(get_repos_err)

            if org_auth_errors:
                msg_prefix = (
                    f'Found {len(org_auth_errors)} authorization error(s) in org {org.login}'
                )
                exc_raised = any('raised' in err for err in org_auth_errors)

                if any_resource_accessed and not exc_raised:
                    logger.warning(f'{msg_prefix}, but accessed: {resource_accessed_types}')

                    # If any resources were accessed and no exception was raised, we can count that as
                    # the authorization check passing
                    successful_org_auth_count += 1
                elif not exc_raised:
                    resource_err_msg = (
                        'All resource types were accessible, but returned zero results'
                    )
                    logger.error(f'{msg_prefix}, {resource_err_msg}')
                    auth_errors[org.login] = [resource_err_msg]
                else:
                    logger.error(f'{msg_prefix}, including a raised exception')
                    auth_errors[org.login] = org_auth_errors
            else:
                logger.info(
                    f'Completed authorization validation for all resources in org {org.login}'
                )
                successful_org_auth_count += 1

            if successful_org_auth_count >= 10 and is_gitlab_provider:
                logger.info(
                    'Reached 10 successfully authorized organizations, stopping authorization check on Gitlab instance'
                )
                break

        if auth_errors:
            error_message = (
                f'Found {len(auth_errors)}/{len(orgs)} organizations with authorization errors:\n'
            )

            for org_name, org_auth_errors in auth_errors.items():
                error_message += f'Organization: {org_name}\n'
                for error in org_auth_errors:
                    error_message += f' - {error}\n'

            raise GitAuthorizationException(error_message)
        else:
            logger.info(
                f'Successfully authorized access to all necessary resources in {self.config.git_provider.value} instance for {self.config.company_slug}'
            )

    def _get_repos_for_auth_check(
        self, org: StandardizedOrganization, limit: int = 10
    ) -> tuple[list[StandardizedRepository], Optional[str]]:
        """
        Get repositories for authorization check. If the number of private repositories is fewer than the limit,
        we will supplement the list with public repositories in an attempt to reach the limit. If an exception
        is raised while trying to access repositories, the exception message will be returned.

        Args:
            org (StandardizedOrganization): The organization to get repositories for
            limit (int, optional): The maximum number of repositories to return. Defaults to 10.

        Returns:
            tuple[list[StandardizedRepository], bool]: A tuple containing a list of repositories and a string
                                                       if an exception was raised, None otherwise
        """
        repos: List[StandardizedRepository] = []
        exception_raised: Optional[str] = None

        try:
            # Check if the org has any private repositories. If the provider is ADO, we don't need to
            # check for private (aka hidden) repos, since we don't normally pull this data
            private_repo_count = (
                bool(self.get_repos_count(org, only_private=True))
                if self.config.git_provider != GitProvider.ADO
                else False
            )

            if private_repo_count:
                logger.info(f'Attempting to access private repos for org {org.login}')
                priv_repos = [
                    r
                    for r in self.get_repos(org, limit=limit, only_private=True)
                    if r.id not in self.config.excluded_repos
                ]
                repos.extend(priv_repos)
            else:
                logger.warning('No private repositories found')

            if len(repos) < limit:
                logger.warning(
                    f'{len(repos)} private repos found, attempting to access public repos for org {org.login}'
                )
                public_repos = [
                    r
                    for r in self.get_repos(org, limit=limit - len(repos), only_private=False)
                    if r.id not in self.config.excluded_repos
                ]
                repos.extend(public_repos)
        except Exception as e:
            exception_raised = f'Unable to access repositories in org {org.login}: {str(e)}'
            logger.error(exception_raised)

        if not exception_raised:
            logger.info(f'Found {len(repos)} repositories for org {org.login}')

        return repos, exception_raised

    def force_evaluate(self, fn: Callable, *args, progress_bar: tqdm = None, **kwargs):
        """
        Helper function for when we want to fully evaluate a generator within the adapter. This is particularly useful
        for our async wrappers, since evaluating generators is blocking unless threaded or done with an async generator.

        Args:
            fn (Callable): The function that should be called that returns a generator. The args and kwargs will be
                passed along to it.
            progress_bar (Optional[tqdm], optional): A progress bar used to update how many of an object was pulled.

        Returns:
            List[Any]: A list from the evaluated generator.
        """
        results = [result for result in fn(*args, **kwargs)]
        if progress_bar is not None:
            progress_bar.update(len(results))
        return results

    async def call_async(
        self,
        tasks: List[Any],
        force_eval: bool = True,
        max_workers: Optional[int] = None,
        progress_bar: Optional[tqdm] = None,
    ) -> List[Any]:
        """
        Helper function to call a list of callables in a threaded pool.

        Args:
            tasks (List[Any]): A list of callables (undefined since we allow partials and other callables).
                Use functools.partial to pass along args and kwargs.
            force_eval (bool, optional): Whether to force the evaluation of the function return value if it's a generator.
                This is applied to each called task. Defaults to True.
            max_workers (Optional[int], optional): The maximum number of threads to use. Defaults to None.
            progress_bar (Optional[tqdm], optional): The progress bar to use, only passed to force_eval if True. Defaults to None.
        Returns:
            List[Any]: A list from the evaluated generator.
        """
        results = []
        tasks_to_fetch = []
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutorWithLogging(max_workers=max_workers) as executor:
            for task in tasks:
                if force_eval:
                    t = functools.partial(self.force_evaluate, task, progress_bar=progress_bar)
                    tasks_to_fetch.append(loop.run_in_executor(executor, t))
                else:
                    tasks_to_fetch.append(loop.run_in_executor(executor, task))
            task_results = await asyncio.gather(*tasks_to_fetch)
            for task_result in task_results:
                results.extend(task_result)
        return results

    async def async_process_iterator(
        self,
        aiterable: AsyncGenerator,
        write_function: Callable,
        object_name: str,
        progress_bar: Optional[tqdm] = None,
        limiter_function: Optional[Callable] = None,
        limiter_max: Optional[Any] = None,
    ) -> int:
        """
        Asynchronously handle processing and batching of a list of generators.
        This is useful if we need to write to file across multiple generators and when we care about memory usage or file size.
        Returned items will be passed to _transform_data_objects_before_saving before writing.

        It's preferable to use call_async if batching is not required. This makes use of more resources to run asynchronously.

        Args:
            aiterable (AsyncIterable): An async iterable to return and batch from.
            progress_bar (tqdm): The progress bar to use to track progress.
            write_function (Callable): A callable that accepts arguments passed to IngestIOHelper.write_json_to_local_or_s3.
                object_name, json_data, and batch_number are used.
            object_name (str): Name of the object to pass to write_function.
            limiter_function (Optional[Callable]): A callable to check batches of items against.
                Not called if limiter_max is None.
            limiter_max (Optional[Any]): The maximum number of items to write in batches.
                Not used if limiter_function is None.
        Returns:
            int: The number of items processed.
        """
        total = 0
        batch_number = 0
        batch = []

        async for aitem in aiterable:
            total += 1

            if progress_bar:
                progress_bar.update(1)
            batch.append(aitem)

            if limiter_function is not None:
                if limiter_max and limiter_function(batch) >= limiter_max:
                    logging_helper.send_to_agent_log_file(
                        f'Writing {object_name} batch {batch_number}', level=logging.DEBUG
                    )

                    batch_as_dict = self._transform_data_objects_before_saving(batch)
                    write_function(
                        object_name=object_name,
                        json_data=batch_as_dict,
                        batch_number=batch_number,
                    )

                    # Clear batch once written to s3
                    batch = []
                    batch_number += 1

        # Catch whatever didn't hit our threshold during processing.
        if len(batch):
            logging_helper.send_to_agent_log_file(
                f'Writing {object_name} batch {batch_number}', level=logging.DEBUG
            )
            batch_as_dict = self._transform_data_objects_before_saving(batch)
            write_function(
                object_name=object_name,
                json_data=batch_as_dict,
                batch_number=batch_number,
            )
        return total

    async def async_batch_cast_iterables(
        self,
        iterables: Sequence[Sequence | Generator],
        progress_bar: Optional[tqdm] = None,
        max_workers: Optional[int] = None,
        max_queue_size: int = 10000,
    ) -> AsyncGenerator:
        """
        Helper function that takes a list of synchronous generators and returns a single asynchronous generator.
        This makes use of an asyncio queue shared across multiple concurrent asyncio tasks.

        Args:
            iterables (List[Iterable]): A list of iterables to return from.
            progress_bar (Optional[tqdm]): The progress bar to use to track progress.
            max_workers (Optional[int], optional): The maximum number of threads to use. Defaults to None.
            max_queue_size(int): The maximum number of items allowed in the queue before it blocks puts.
                Defaults to 10000.

        Returns:
            AsyncGenerator: An asynchronous generator returning from the provided synchronous iterables.
        """
        logging_helper.send_to_agent_log_file(
            'Starting async iterable pooling.', level=logging.DEBUG
        )

        # Use an asyncio queue to handle processing since we can asynchronously process it.
        batch_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutorWithLogging(max_workers=max_workers) as executor:
            awaitables = []

            # Create awaitable futures to run in our executor.
            def _queue_items(sync_iterator: Iterable):
                for item in sync_iterator:
                    # Run on the main event loop
                    future = asyncio.run_coroutine_threadsafe(batch_queue.put(item), loop)
                    # Wait for queuing to finish before continuing iteration.
                    future.result()
                progress_bar.update(1) if progress_bar else None

            for i in iterables:
                awaitables.append(loop.run_in_executor(executor, _queue_items, i))

            futures = set()
            pending_futures = set()
            if awaitables:
                # Use FIRST_COMPLETED here and in the loop since futures will not update until await is called on them.
                futures, pending_futures = await asyncio.wait(
                    awaitables, return_when=asyncio.FIRST_COMPLETED
                )

            logging_helper.send_to_agent_log_file(
                f'Queued {len(futures) + len(pending_futures)} iterable futures.',
                level=logging.DEBUG,
            )

            # Yields from queue while tasks are running.
            while len(pending_futures):
                # Raise any exceptions we've come across.
                for f in futures:
                    if f.done() and f.exception():
                        logger.error(f'Iterable future failed: {f.exception()}')
                        raise f.exception()
                while not batch_queue.empty():
                    yield await batch_queue.get()

                futures, pending_futures = await asyncio.wait(
                    pending_futures, return_when=asyncio.FIRST_COMPLETED
                )

            # Catch any exceptions we missed in our pending loop.
            for f in futures:
                if f.done() and f.exception():
                    logger.error(f'Iterable future failed: {f.exception()}')
                    raise f.exception()

            logging_helper.send_to_agent_log_file(
                'Iterable futures completed, draining remaining results from async queue.',
                level=logging.DEBUG,
            )

            # We may have data in the queue after futures have completed.
            while not batch_queue.empty():
                yield await batch_queue.get()

            logging_helper.send_to_agent_log_file('Async queue drained.', level=logging.DEBUG)


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def load_and_push_git_to_s3(ingest_config: IngestionConfig) -> list[Exception]:
    """Handler function for the end to end processing of Git Data.
    This function is responsible for taking in an ingest config,
    creating a git adapter, and then running the Git Adapter function
    for uploading data to S3 (or saving it locally). The function for
    handling that logic is part of the GitAdapter class (see load_and_dump_git)

    Args:
        ingest_config (IngestionConfig): A fully formed IngestionConfig class, with
        valid Git Configuration in it.
    """
    exceptions: list[Exception] = []

    for git_config in ingest_config.git_configs:
        try:
            add_telemetry_fields({'company_slug': ingest_config.company_slug})
            git_adapter: GitAdapter = GitAdapter.get_git_adapter(git_config)
            with record_span('load_and_dump_git'):
                add_telemetry_fields(
                    {
                        'git_provider': git_config.git_provider.value,
                        'instance_slug': git_config.instance_slug,
                    }
                )
                git_adapter.load_and_dump_git(git_config=git_config, ingest_config=ingest_config)
        except GitProviderUnavailable:
            logger.warning(
                f'Git Config for provider {git_config.git_provider} is currently NOT supported!'
            )
            exceptions.append(JFIngestGitProviderException(git_config.git_provider))
            continue
        except Exception as e:
            logger.error(f'Error processing Git Data for {git_config.instance_slug}')
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)
            exceptions.append(e)

    return exceptions


def determine_commit_backpopulation_window(
    config: GitConfig, repo: StandardizedRepository
) -> Optional[BackpopulationWindow]:
    """Get the backpopulation window for Commits

    Args:
        config (GitConfig): A valid Git Config
        repo (StandardizedRepository): A valid standardized repository

    Returns:
        BackpopulationWindow: A Backpopulation window object
    """
    commits_backpopulated_to = config.get_backpopulated_date_for_commits(repo.id)
    return _get_backpopulation_helper(
        repo=repo,
        pull_from=config.pull_from,
        objects_back_populated_to=commits_backpopulated_to,
        object_name='commits',
        force_full_backpopulation_pull=config.force_full_backpopulation_pull,
        backpopulation_window_days=config.backpopulation_window_days,
    )


def determine_pr_backpopulation_window(
    config: GitConfig, repo: StandardizedRepository
) -> Optional[BackpopulationWindow]:
    """Get the backpopulation window for PRs

    Args:
        config (GitConfig): A valid Git Config
        repo (StandardizedRepository): A valid standardized repository

    Returns:
        BackpopulationWindow: A Backpopulation window object
    """
    prs_backpopulated_to = config.get_backpopulated_date_for_prs(repo.id)
    return _get_backpopulation_helper(
        repo=repo,
        pull_from=config.pull_from,
        objects_back_populated_to=prs_backpopulated_to,
        object_name='PRs',
        force_full_backpopulation_pull=config.force_full_backpopulation_pull,
        backpopulation_window_days=config.backpopulation_window_days,
    )


def _hydrate_backpopulation_windows_for_repos(
    config: GitConfig,
    repos: list[StandardizedRepository],
) -> list[StandardizedRepository]:
    """Hydrate the backpopulation windows for commits and PRs for a given list of repositories

    Args:
        config (GitConfig): A valid Git Config
        repos (list[StandardizedRepository]): A list of valid standardized repositories
    Returns:
        list[StandardizedRepository]: The repositories with backpopulation windows set
    """
    hydrated_repos: list[StandardizedRepository] = []
    repos_needing_commit_backpopulation_count = 0
    repos_needing_pr_backpopulation_count = 0
    repo_names_needing_backpopulation = set()
    for repo in repos:
        repo.commit_backpopulation_window = determine_commit_backpopulation_window(config, repo)
        repo.pr_backpopulation_window = determine_pr_backpopulation_window(config, repo)

        if repo.commit_backpopulation_window:
            repos_needing_commit_backpopulation_count += 1
            repo_names_needing_backpopulation.add(repo.name)
        if repo.pr_backpopulation_window:
            repos_needing_pr_backpopulation_count += 1
            repo_names_needing_backpopulation.add(repo.name)

        hydrated_repos.append(repo)

    repo_names_needing_backpopulation_list = list(repo_names_needing_backpopulation)
    repo_names_sample = None
    if repo_names_needing_backpopulation_list:
        repo_names_sample = repo_names_needing_backpopulation_list[
            : min(30, len(repo_names_needing_backpopulation_list))
        ]

    helper_message = (
        'Backpopulation Information:',
        f'\tBackpopulation window size is {config.backpopulation_window_days} days',
        f'\tPull from date is {config.pull_from}',
        f'\t{repos_needing_commit_backpopulation_count}/{len(repos)} repos need commit backpopulation',
        f'\t{repos_needing_pr_backpopulation_count}/{len(repos)} repos need PR backpopulation',
        f'\tSample of repos needing backpopulation: {repo_names_sample if repo_names_sample else "N/A"}'
        '',
    )
    logger.info('\n'.join(helper_message))
    return hydrated_repos


def _get_backpopulation_helper(
    repo: StandardizedRepository,
    pull_from: datetime,
    objects_back_populated_to: Optional[datetime],
    object_name: str,
    force_full_backpopulation_pull: bool = False,
    backpopulation_window_days: int = 30,
) -> Optional[BackpopulationWindow]:
    if objects_back_populated_to and objects_back_populated_to <= pull_from:
        # No backpopulation necessary
        return None
    # We're backpopulating objects for this repo

    if objects_back_populated_to:
        base_date = objects_back_populated_to
    else:
        base_date = datetime.now().astimezone(timezone.utc) + timedelta(days=1)

    backpopulation_window_start = (
        pull_from
        if force_full_backpopulation_pull
        else max(pull_from, base_date - timedelta(days=backpopulation_window_days))
    )
    backpopulation_window_end = base_date

    logging_helper.send_to_agent_log_file(
        f'Backpopulation window found for {object_name} for repo {repo.name} (ID: {repo.id}). Window spans from {backpopulation_window_start} to {backpopulation_window_end} ({object_name} backpopulated to {objects_back_populated_to}, pull_from: {pull_from})',
        level=logging.DEBUG,
    )
    return BackpopulationWindow(backpopulation_window_start, backpopulation_window_end)


def _validate_resource_access(
    resource_name: str,
    fetch_func: Callable[..., Iterable[Any]],
    fetch_kwargs: dict[str, Any],
    org_auth_errors: list[str],
    discover_orgs: bool,
    record_empty: bool,
) -> list[Any]:
    results: list[Any] = []

    try:
        results = [i for i in fetch_func(**fetch_kwargs)]

        if results:
            logger.info(f"Successfully accessed {resource_name}")
        else:
            empty_msg = f"No {resource_name} found"
            logger.warning(empty_msg)

            if not discover_orgs and record_empty:
                org_auth_errors.append(empty_msg)
    except Exception as e:
        error_msg = f"Exception raised when attempting to access {resource_name}: {e}"
        logger.error(error_msg)
        org_auth_errors.append(error_msg)

    return results
