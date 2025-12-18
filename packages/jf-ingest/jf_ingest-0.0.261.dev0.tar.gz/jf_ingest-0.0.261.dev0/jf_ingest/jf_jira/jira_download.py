import json
import logging
from datetime import datetime
from typing import Generator, Optional

from jira import JIRA

from jf_ingest import logging_helper
from jf_ingest.config import (
    IngestionConfig,
    IngestionType,
    IssueDownloadingResult,
    JiraAuthMethod,
    JiraDownloadConfig,
    UserMetadata,
)
from jf_ingest.constants import Constants
from jf_ingest.file_operations import IngestIOHelper, SubDirectory
from jf_ingest.jf_jira import downloaders, pull_issues_wrapper
from jf_ingest.jf_jira.auth import get_jira_connection
from jf_ingest.jf_jira.exceptions import AtlassianConnectException
from jf_ingest.jf_jira.utils import (
    JiraFieldIdentifier,
    JiraObject,
    _construct_field_filters,
    expand_and_normalize_jira_fields,
    get_unique_users_from_issue,
    get_user_key,
)
from jf_ingest.telemetry import add_telemetry_fields, jelly_trace, record_span
from jf_ingest.utils import batch_iterable_by_bytes_size, get_object_bytes_size

logger = logging.getLogger(__name__)


class JiraDownloader:

    @jelly_trace()
    def __init__(self, ingest_config: IngestionConfig):
        logger.info('Initializing Jira Downloader')
        self.ingest_config = ingest_config

        # Setup Jira Config (this does some Data Normalization)
        self.jira_config = self.get_jira_config(
            ingest_config=ingest_config,
        )

        # Setup Ingest IO Helper
        self.ingest_io_helper = self.get_ingest_io_helper(ingest_config=ingest_config)

        # Setup Jira Connections
        (
            self.jira_connect_or_fallback_connection,
            self.jira_atlas_connect_connection,
            self.using_connect_as_primary_auth,
            self.use_jql_enhanced_search,
        ) = self.get_jira_connections(jira_config=self.jira_config)

        self.normalize_jira_config()

        # The following args are used for tracking counts across all of our objects
        self.object_counts: dict[JiraObject, Optional[int]] = {
            jira_object: None for jira_object in JiraObject
        }

        logger.info('Done initializing Jira Downloader')

    def _write_jira_data_to_local_or_s3(self, object_name: str, json_data):
        if isinstance(json_data, list):
            self.object_counts[JiraObject(object_name)] = len(json_data)

        self.ingest_io_helper.write_json_to_local_or_s3(
            object_name=object_name,
            json_data=json_data,
            subdirectory=SubDirectory.JIRA,
        )

    def log_jira_download_exit_message(
        self, task_name: str, affects_objects: Optional[list[JiraObject]] = None
    ):
        if affects_objects is None:
            affects_objects = [obj for obj in JiraObject]

        affects_objects.sort(key=lambda x: x.name)
        affect_objects_count = '\n'.join(
            f'\t{obj.name}: {self.object_counts[obj]}'
            for obj in affects_objects
            if self.object_counts[obj] is not None
        )
        output_message = (
            f'{task_name} process complete!\n'
            f'Objects downloaded count:\n'
            f'{affect_objects_count}'
        )
        logger.info(output_message)

    @jelly_trace()
    def get_ingest_io_helper(self, ingest_config: IngestionConfig) -> IngestIOHelper:
        ingest_io_helper = IngestIOHelper(ingest_config=ingest_config)

        S3_OR_JELLYFISH_LOG_STATEMENT = (
            's3' if ingest_config.ingest_type == IngestionType.DIRECT_CONNECT else 'jellyfish'
        )
        if ingest_config.save_locally:
            logger.info(f"Data will be saved locally to: {ingest_io_helper.local_file_path}")
        else:
            logger.info("Data will not be saved locally")
        if ingest_config.upload_to_s3:
            logger.info(f"Data will be submitted to {S3_OR_JELLYFISH_LOG_STATEMENT}")
        else:
            logger.info(f"Data will NOT be submitted to {S3_OR_JELLYFISH_LOG_STATEMENT}")

        return ingest_io_helper

    @jelly_trace()
    def get_jira_connections(
        self, jira_config: JiraDownloadConfig
    ) -> tuple[JIRA, Optional[JIRA], bool, bool]:

        # Test if JQL Enhanced Search is available
        use_jql_enhanced_search = downloaders.is_jql_enhanced_search_available(
            jira_config=jira_config,
            jql_enhanced_search_enabled=jira_config.feature_flags.get(
                Constants.JQL_ENHANCED_SEARCH_ENABLED, False
            ),
            force_legacy_api=jira_config.feature_flags.get(Constants.FORCE_LEGACY_API, False),
        )

        # Create final connections with appropriate API version
        jira_basic_connection = get_jira_connection(
            config=jira_config,
            auth_method=JiraAuthMethod.BasicAuth,
            use_jql_enhanced_search=use_jql_enhanced_search,
        )

        jira_atlas_connect_connection = (
            get_jira_connection(
                config=jira_config,
                auth_method=JiraAuthMethod.AtlassianConnect,
                use_jql_enhanced_search=use_jql_enhanced_search,
            )
            if JiraAuthMethod.AtlassianConnect in jira_config.available_auth_methods
            else None
        )
        # There is an ongoing effort to cut all things over to Atlassian Connect only,
        # but it is a piecewise migration for now.
        # OJ-29745
        jira_connect_or_fallback_connection = jira_basic_connection
        using_connect_as_primary_auth = False

        if jira_config.feature_flags.get("lusca-auth-always-use-connect-for-atlassian-apis-Q423"):
            logging_helper.send_to_agent_log_file("Will use connect for most API calls")

            if not isinstance(jira_atlas_connect_connection, JIRA):
                raise AtlassianConnectException(
                    'Atlassian Connect Connection is not a JIRA object, unable to proceed'
                )

            jira_connect_or_fallback_connection = jira_atlas_connect_connection
            using_connect_as_primary_auth = True
        else:
            logging_helper.send_to_agent_log_file("Will use basic auth for most API calls")

        return (
            jira_connect_or_fallback_connection,
            jira_atlas_connect_connection,
            using_connect_as_primary_auth,
            use_jql_enhanced_search,
        )

    @jelly_trace()
    def get_jira_config(
        self,
        ingest_config: IngestionConfig,
    ) -> JiraDownloadConfig:

        if not ingest_config.save_locally and not ingest_config.upload_to_s3:
            logger.error(
                f'Configuration error! Ingestion configuration must have either save_locally or upload_to_s3 set to True!'
            )
            raise Exception(
                'Save Locally and Upload to S3 are both set to False! Set one to true or no data will be saved!'
            )

        if not (jira_config := ingest_config.jira_config):
            raise Exception(
                f'load_and_push_to_s3 (Jira Download) was provided without a valid Jira Config!'
            )

        if jira_config.skip_issues and jira_config.only_issues:
            raise Exception(
                'skip_issues and only_issues have both been set to True! This is an invalid JF Ingest object'
            )

        logging_helper.send_to_agent_log_file(f"Feature flags: {jira_config.feature_flags}")
        return jira_config

    @jelly_trace()
    def normalize_jira_config(self):
        if not self.jira_connect_or_fallback_connection:
            self.jira_connect_or_fallback_connection, _, _, _ = self.get_jira_connections(
                jira_config=self.jira_config
            )
        ########################################################################
        # Normalize Jira Config to the Timezone that this Jira Instance exists
        # within
        ########################################################################
        instance_metadata = self.jira_connect_or_fallback_connection.myself()
        timezone_locale = instance_metadata.get('timeZone', '')
        logger.info(
            f'Jira Instance Timezone Locale detected as: {timezone_locale}. Datetimes will be normalized to this timezone locale'
        )
        try:
            self.jira_config.normalize_datetimes_to_timezone_locale(timezone_locale)
        except Exception as e:
            # No error should get raised, but just in case
            logger.warning(
                f'Failed to normalize datetimes to timezone locale: {timezone_locale}. Error: {e}'
            )

        ########################################################################
        # Simplify the config for later use
        ########################################################################
        self.ingest_type = self.ingest_config.ingest_type
        self.is_agent_run = self.ingest_type == IngestionType.AGENT

    @jelly_trace()
    def fetch_projects_and_versions(self) -> list[dict]:
        projects_and_versions: list[dict] = (
            downloaders.download_projects_and_versions_and_components(
                jira_connection=self.jira_connect_or_fallback_connection,
                is_agent_run=self.is_agent_run,
                jellyfish_project_ids_to_keys=self.jira_config.jellyfish_project_ids_to_keys,
                jellyfish_issue_metadata=self.jira_config.jellyfish_issue_metadata,
                include_projects=self.jira_config.include_projects,
                exclude_projects=self.jira_config.exclude_projects,
                include_categories=self.jira_config.include_project_categories,
                exclude_categories=self.jira_config.exclude_project_categories,
            )
        )

        return projects_and_versions

    @jelly_trace()
    def fetch_fields_data(self):
        jira_fields_data = downloaders.download_fields(
            self.jira_connect_or_fallback_connection,
        )
        normalized_include_fields = expand_and_normalize_jira_fields(
            jira_fields_data, self.jira_config.include_fields
        )
        normalized_exclude_fields = expand_and_normalize_jira_fields(
            jira_fields_data, self.jira_config.exclude_fields
        )

        return jira_fields_data, normalized_include_fields, normalized_exclude_fields

    @jelly_trace()
    def jira_download(self):

        logger.info(f'Starting full Jira Download process')
        log_sub_process_summaries = False  # Set this to False because each sub-process will log their own exit messages and it can be redundant
        projects_and_versions = self.jira_download_projects(
            log_download_exit_message=log_sub_process_summaries
        )
        normalized_include_fields, normalized_exclude_fields = self.jira_download_fields(
            log_download_exit_message=log_sub_process_summaries
        )

        if self.jira_config.only_issues:
            logger.info("Skipping full Jira Download because only_issues is set to True")
            self.jira_download_issues(
                projects_and_versions=projects_and_versions,
                normalized_include_fields=normalized_include_fields,
                normalized_exclude_fields=normalized_exclude_fields,
                log_download_exit_message=log_sub_process_summaries,
            )
        if self.jira_config.skip_issues:
            logger.info("Skipping full Jira Download because skip_issues is set to True")
            self.jira_download_refdata(log_download_exit_message=log_sub_process_summaries)
            self.jira_download_boards_and_sprints(
                log_download_exit_message=log_sub_process_summaries
            )
        else:
            self.jira_download_refdata(log_download_exit_message=log_sub_process_summaries)
            self.jira_download_boards_and_sprints(
                log_download_exit_message=log_sub_process_summaries
            )
            self.jira_download_issues(
                projects_and_versions=projects_and_versions,
                normalized_include_fields=normalized_include_fields,
                normalized_exclude_fields=normalized_exclude_fields,
                log_download_exit_message=log_sub_process_summaries,
            )

        download_metadata = {
            'company_slug': self.jira_config.company_slug,
            'ingest_type': self.ingest_type.value if self.ingest_type else None,
            'users_downloaded': not self.jira_config.skip_downloading_users,
            'boards_downloaded': self.jira_config.download_boards,
            'sprints_downloaded': self.jira_config.download_boards
            and self.jira_config.download_sprints,
            'issues_downloaded': not self.jira_config.skip_issues,
        }

        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraDownloadMetadata.value,
            json_data=download_metadata,
        )

        self.log_jira_download_exit_message(task_name='Jira Download')

    @jelly_trace()
    def jira_download_projects(self, log_download_exit_message: bool = True) -> list[dict]:
        projects_and_versions: list[dict] = self.fetch_projects_and_versions()

        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraProjectsAndVersions.value,
            json_data=projects_and_versions,
        )

        #######################################################################
        # Optionally Fetch Global Components
        #######################################################################
        if self.jira_config.download_global_components:
            global_components = downloaders.download_global_components(
                jira_connection=self.jira_connect_or_fallback_connection,
            )
            self._write_jira_data_to_local_or_s3(
                object_name=JiraObject.JiraGlobalComponents.value,
                json_data=global_components,
            )
        else:
            logger.info('Skipping download of global components')

        if log_download_exit_message:
            self.log_jira_download_exit_message(
                task_name='Jira Download Projects',
                affects_objects=[
                    JiraObject.JiraProjectsAndVersions,
                    JiraObject.JiraGlobalComponents,
                ],
            )
        return projects_and_versions

    @jelly_trace()
    def jira_download_fields(
        self, log_download_exit_message: bool = True
    ) -> tuple[list[JiraFieldIdentifier], list[JiraFieldIdentifier]]:

        #######################################################################
        # Jira Fields
        # NOTE: Here we need to download the fields from the fields endpoint
        # and then filter out fields based on the include/exclude list.
        # The tricky part here is that it's possible for customers to provide
        # us either a fields Unique Key (something like customfield_10008), or
        # the fields human readable name (something like "Sprint"). We must
        # support BOTH use cases!
        # To do so, grab all fields data from the API endpoint. Then, expand
        # and normalize the field exclude/include lists to contain both the
        # ID and the name. THEN filter out fields by their ID
        # Once fields have been normalized and expanded we must overwrite
        # the jira_config object to have the expanded list. That way we can
        # pass both the IDs and Keys to our issue downloading logic, which needs
        # both for IDs for grabbing fields AND names for filtering the changelog
        #######################################################################
        jira_fields_data, normalized_include_fields, normalized_exclude_fields = (
            self.fetch_fields_data()
        )

        filters = _construct_field_filters(
            include_field_ids=[f.jira_field_id for f in normalized_include_fields],
            exclude_field_ids=[f.jira_field_id for f in normalized_exclude_fields],
        )

        filtered_jira_fields = [
            field for field in jira_fields_data if all(filt(field) for filt in filters)
        ]

        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraFields.value,
            json_data=filtered_jira_fields,
        )

        if log_download_exit_message:
            self.log_jira_download_exit_message(
                task_name='Jira Download Fields', affects_objects=[JiraObject.JiraFields]
            )
        return normalized_include_fields, normalized_exclude_fields

    @jelly_trace()
    def jira_download_refdata(
        self,
        projects_and_versions_data: Optional[list[dict]] = None,
        log_download_exit_message: bool = True,
    ):

        if not projects_and_versions_data:
            projects_and_versions_data = self.fetch_projects_and_versions()

        project_ids = set(proj['id'] for proj in projects_and_versions_data)  # type: ignore

        ######################################################################
        # Jira Users
        #######################################################################
        users: list[dict] = []
        if (
            not self.jira_config.skip_downloading_users
            or not self.jira_config.user_keys_in_jellyfish
        ):
            users = downloaders.download_users(
                jira_basic_connection=self.jira_connect_or_fallback_connection,
                jira_atlas_connect_connection=(
                    self.jira_atlas_connect_connection
                    if self.jira_config.should_augment_emails
                    else None
                ),  # Use AtlasConnect for 'augment with email' subtask
                gdpr_active=self.jira_config.gdpr_active,
                search_users_by_letter_email_domain=self.jira_config.search_users_by_letter_email_domain,
                required_email_domains=self.jira_config.required_email_domains,
                is_email_required=self.jira_config.is_email_required,
                using_connect_as_primary_auth=self.using_connect_as_primary_auth,
            )
        # Upload users, even if there aren't any
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraUsers.value,
            json_data=users,
        )

        #######################################################################
        # Jira Resolutions
        #######################################################################
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraResolutions.value,
            json_data=downloaders.download_resolutions(self.jira_connect_or_fallback_connection),
        )

        #######################################################################
        # Jira Issue Types
        #######################################################################
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraIssueTypes.value,
            json_data=downloaders.download_issuetypes(
                self.jira_connect_or_fallback_connection, project_ids=list(project_ids)
            ),
        )

        #######################################################################
        # Jira Link Types
        #######################################################################
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraLinkTypes.value,
            json_data=downloaders.download_issuelinktypes(self.jira_connect_or_fallback_connection),
        )

        #######################################################################
        # Jira Priorities
        #######################################################################
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraPriorities.value,
            json_data=downloaders.download_priorities(self.jira_connect_or_fallback_connection),
        )

        #######################################################################
        # Jira Statuses
        #######################################################################
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraStatuses.value,
            json_data=downloaders.download_statuses(self.jira_connect_or_fallback_connection),
        )

        if log_download_exit_message:
            self.log_jira_download_exit_message(
                task_name='Jira Download Reference Data',
                affects_objects=[
                    JiraObject.JiraResolutions,
                    JiraObject.JiraIssueTypes,
                    JiraObject.JiraLinkTypes,
                    JiraObject.JiraPriorities,
                    JiraObject.JiraStatuses,
                ],
            )

    @jelly_trace
    def jira_download_boards_and_sprints(
        self, projects_data: Optional[list[dict]] = None, log_download_exit_message: bool = True
    ):

        projects_data = []
        if self.jira_config.filter_boards_by_projects:
            if not projects_data:
                projects_data = self.fetch_projects_and_versions()

        project_ids = set(proj['id'] for proj in projects_data)  # type: ignore

        #######################################################################
        # Jira Boards, Sprints, and Links
        #######################################################################
        if self.jira_config.download_boards:
            boards, sprints, links = downloaders.download_boards_and_sprints(
                self.jira_connect_or_fallback_connection,
                self.jira_config.download_sprints,
                self.jira_config.feature_flags.get(Constants.PULL_SPRINTS_BY_ID, False),
                self.jira_config.feature_flags.get(Constants.PULL_SPRINTS_BY_BOARD_MAX_WORKERS, 5),
                self.jira_config.feature_flags.get(Constants.PULL_SPRINTS_BY_ID_MAX_WORKERS, 5),
                self.jira_config.feature_flags.get(Constants.PULL_SPRINTS_SKIP_INACTIVE, False),
                filter_boards_by_projects=(
                    project_ids if self.jira_config.filter_boards_by_projects else None
                ),
            )
        else:
            boards, sprints, links = [], [], []
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraBoards.value,
            json_data=boards,
        )

        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraSprints.value,
            json_data=sprints,
        )

        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraBoardSprintLinks.value,
            json_data=links,
        )

        if log_download_exit_message:
            self.log_jira_download_exit_message(
                task_name='Jira Download Boards and Sprints',
                affects_objects=[
                    JiraObject.JiraBoards,
                    JiraObject.JiraSprints,
                    JiraObject.JiraBoardSprintLinks,
                ],
            )

    @jelly_trace()
    def jira_download_issues(
        self,
        projects_data: Optional[list[dict]] = None,
        normalized_include_fields: Optional[list[JiraFieldIdentifier]] = None,
        normalized_exclude_fields: Optional[list[JiraFieldIdentifier]] = None,
        log_download_exit_message: bool = True,
    ):
        api_type = "JQL Enhanced Search" if self.use_jql_enhanced_search else "Legacy"
        logger.info(f"Using {api_type} API for Jira operations")

        if not projects_data:
            projects_data = self.fetch_projects_and_versions()

        if normalized_include_fields == None or normalized_exclude_fields == None:
            _, normalized_include_fields, normalized_exclude_fields = self.fetch_fields_data()

        # For Jira Issue operations we need to determine the batch size that
        # the JIRA provider will limit us to
        jira_issues_batch_size = downloaders.get_jira_search_batch_size(
            jira_connection=self.jira_connect_or_fallback_connection,
            optimistic_batch_size=self.jira_config.issue_batch_size,
            use_jql_enhanced_search=self.use_jql_enhanced_search,
        )

        all_downloaded_issue_ids, all_deleted_issue_ids, users_found_across_all_issues = (
            pull_issues_wrapper(
                self.jira_connect_or_fallback_connection,
                jira_config=self.jira_config,
                projects_and_versions=projects_data,
                include_fields=normalized_include_fields,
                exclude_fields=normalized_exclude_fields,
                jira_issues_batch_size=jira_issues_batch_size,
                ingest_io_helper=self.ingest_io_helper,
                ingest_config=self.ingest_config,
                use_jql_enhanced_search=self.use_jql_enhanced_search,
            )
        )
        # Update object counts manually, because pull_issues_wrapper exists outside of this class
        self.object_counts[JiraObject.JiraIssues] = len(all_downloaded_issue_ids)
        self.object_counts[JiraObject.JiraIssuesIdsDeleted] = len(all_deleted_issue_ids)
        self.object_counts[JiraObject.JiraUsersFromIssues] = len(users_found_across_all_issues)

        logger.info(f'{len(all_deleted_issue_ids)} issues have been detected as being deleted')
        # Write issues that got deleted
        self._write_jira_data_to_local_or_s3(
            object_name=JiraObject.JiraIssuesIdsDeleted.value,
            json_data=list(all_deleted_issue_ids),
        )

        #######################################################################
        # Jira Work Logs
        #######################################################################
        if self.jira_config.download_worklogs:
            jira_worklogs_data = downloaders.download_worklogs(
                self.jira_connect_or_fallback_connection,
                all_downloaded_issue_ids,
                self.jira_config.work_logs_pull_from,
            )
            self._write_jira_data_to_local_or_s3(
                object_name=JiraObject.JiraWorklogs.value,
                json_data=jira_worklogs_data,
            )
            self.object_counts[JiraObject.JiraWorklogs] = len(jira_worklogs_data)

        if log_download_exit_message:
            self.log_jira_download_exit_message(
                task_name='Jira Download Issues',
                affects_objects=[
                    JiraObject.JiraIssues,
                    JiraObject.JiraWorklogs,
                    JiraObject.JiraIssuesIdsDeleted,
                ],
            )
