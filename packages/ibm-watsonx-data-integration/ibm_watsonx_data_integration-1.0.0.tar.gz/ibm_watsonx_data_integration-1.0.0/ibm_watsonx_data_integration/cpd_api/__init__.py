# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module contains API clients for apps common for all services across CPD."""

from ibm_watsonx_data_integration.cpd_api.access_groups_api import AccessGroupsApiClient
from ibm_watsonx_data_integration.cpd_api.access_groups_api_on_prem import AccessGroupsApiClientOnPrem
from ibm_watsonx_data_integration.cpd_api.account_api import AccountAPIClient
from ibm_watsonx_data_integration.cpd_api.broker_api import BrokerApiClient
from ibm_watsonx_data_integration.cpd_api.connections_api import ConnectionsApiClient
from ibm_watsonx_data_integration.cpd_api.global_catalog_api import GlobalCatalogApiClient
from ibm_watsonx_data_integration.cpd_api.global_search_api import GlobalSearchApiClient
from ibm_watsonx_data_integration.cpd_api.job_api import JobApiClient
from ibm_watsonx_data_integration.cpd_api.metering_api import MeteringApiClient
from ibm_watsonx_data_integration.cpd_api.parameter_set_api import ParameterSetApiClient
from ibm_watsonx_data_integration.cpd_api.project_api import ProjectApiClient
from ibm_watsonx_data_integration.cpd_api.resource_controller_api import ResourceControllerApiClient
from ibm_watsonx_data_integration.cpd_api.role_api import RoleApiClient
from ibm_watsonx_data_integration.cpd_api.role_api_on_prem import RoleApiClientOnPrem
from ibm_watsonx_data_integration.cpd_api.service_id_api import ServiceIDApiClient
from ibm_watsonx_data_integration.cpd_api.trusted_profile_api import TrustedProfileApiClient
from ibm_watsonx_data_integration.cpd_api.user_api import UserAPIClient
from ibm_watsonx_data_integration.cpd_api.user_api_on_prem import UserAPIClientOnPrem

__all__ = [
    "AccountAPIClient",
    "BrokerApiClient",
    "GlobalCatalogApiClient",
    "GlobalSearchApiClient",
    "JobApiClient",
    "MeteringApiClient",
    "ParameterSetApiClient",
    "ProjectApiClient",
    "ProjectApiClient",
    "ResourceControllerApiClient",
    "UserAPIClient",
    "UserAPIClientOnPrem",
    "AccessGroupsApiClientOnPrem",
    "RoleApiClientOnPrem",
    "RoleApiClient",
    "AccessGroupsApiClient",
    "ConnectionsApiClient",
    "ServiceIDApiClient",
    "TrustedProfileApiClient",
]
