"""Admin namespace containing admin-related resources."""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...client import AddeparClient

from .audit import AuditResource
from .billable_portfolios import BillablePortfoliosResource
from .client_portal import ClientPortalResource
from .contacts import ContactsResource
from .files import FilesResource
from .import_tool import ImportToolResource
from .target_allocations import TargetAllocationsResource
from .reports import ReportsResource
from .roles import RolesResource
from .teams import TeamsResource
from .users import UsersResource
from .view_sets import ViewSetsResource


class AdminNamespace:
    """
    Namespace for admin-related API resources.

    Usage:
        client.admin.audit.query_login_attempts(...)
        client.admin.audit.query_attribute_changes(...)
        client.admin.billable_portfolios.create_billable_portfolio(...)
        client.admin.client_portal.publish_files(...)
        client.admin.contacts.get_contact(...)
        client.admin.contacts.list_contacts()
        client.admin.files.list_files(...)
        client.admin.files.upload_file(...)
        client.admin.import_tool.create_import(...)
        client.admin.import_tool.execute_import(...)
        client.admin.reports.list_reports(...)
        client.admin.reports.create_report_generation_job(...)
        client.admin.roles.get_role(...)
        client.admin.roles.list_roles()
        client.admin.target_allocations.list_allocation_models()
        client.admin.target_allocations.create_allocation_template(...)
        client.admin.teams.create_team(...)
        client.admin.teams.list_teams()
        client.admin.users.get_user(...)
        client.admin.users.list_users()
        client.admin.view_sets.get_view_set(...)
        client.admin.view_sets.list_view_sets()
    """

    def __init__(self, client: "AddeparClient") -> None:
        self._client = client
        self._audit: Optional[AuditResource] = None
        self._billable_portfolios: Optional[BillablePortfoliosResource] = None
        self._client_portal: Optional[ClientPortalResource] = None
        self._contacts: Optional[ContactsResource] = None
        self._files: Optional[FilesResource] = None
        self._import_tool: Optional[ImportToolResource] = None
        self._reports: Optional[ReportsResource] = None
        self._roles: Optional[RolesResource] = None
        self._target_allocations: Optional[TargetAllocationsResource] = None
        self._teams: Optional[TeamsResource] = None
        self._users: Optional[UsersResource] = None
        self._view_sets: Optional[ViewSetsResource] = None

    @property
    def audit(self) -> AuditResource:
        """Access audit resource."""
        if self._audit is None:
            self._audit = AuditResource(self._client)
        return self._audit

    @property
    def billable_portfolios(self) -> BillablePortfoliosResource:
        """Access billable portfolios resource."""
        if self._billable_portfolios is None:
            self._billable_portfolios = BillablePortfoliosResource(self._client)
        return self._billable_portfolios

    @property
    def client_portal(self) -> ClientPortalResource:
        """Access client portal resource."""
        if self._client_portal is None:
            self._client_portal = ClientPortalResource(self._client)
        return self._client_portal

    @property
    def contacts(self) -> ContactsResource:
        """Access contacts resource."""
        if self._contacts is None:
            self._contacts = ContactsResource(self._client)
        return self._contacts

    @property
    def files(self) -> FilesResource:
        """Access files resource."""
        if self._files is None:
            self._files = FilesResource(self._client)
        return self._files

    @property
    def import_tool(self) -> ImportToolResource:
        """Access import tool resource."""
        if self._import_tool is None:
            self._import_tool = ImportToolResource(self._client)
        return self._import_tool

    @property
    def reports(self) -> ReportsResource:
        """Access reports resource."""
        if self._reports is None:
            self._reports = ReportsResource(self._client)
        return self._reports

    @property
    def roles(self) -> RolesResource:
        """Access roles resource."""
        if self._roles is None:
            self._roles = RolesResource(self._client)
        return self._roles

    @property
    def target_allocations(self) -> TargetAllocationsResource:
        """Access target allocations resource."""
        if self._target_allocations is None:
            self._target_allocations = TargetAllocationsResource(self._client)
        return self._target_allocations

    @property
    def teams(self) -> TeamsResource:
        """Access teams resource."""
        if self._teams is None:
            self._teams = TeamsResource(self._client)
        return self._teams

    @property
    def users(self) -> UsersResource:
        """Access users resource."""
        if self._users is None:
            self._users = UsersResource(self._client)
        return self._users

    @property
    def view_sets(self) -> ViewSetsResource:
        """Access view sets resource."""
        if self._view_sets is None:
            self._view_sets = ViewSetsResource(self._client)
        return self._view_sets


__all__ = [
    "AdminNamespace",
    "AuditResource",
    "BillablePortfoliosResource",
    "ClientPortalResource",
    "ContactsResource",
    "FilesResource",
    "ImportToolResource",
    "ReportsResource",
    "RolesResource",
    "TargetAllocationsResource",
    "TeamsResource",
    "UsersResource",
    "ViewSetsResource",
]
