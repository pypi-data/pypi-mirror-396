"""Contacts resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class ContactsResource(BaseResource):
    """
    Resource for Addepar Contacts API.

    Contacts are individuals who can access the Client Portal.

    Tier 1 (CRUD):
        - get_contact() - Get a single contact
        - list_contacts() - List all contacts (paginated)
        - create_contact() - Create a new contact
        - update_contact() - Update a contact
        - delete_contact() - Delete a contact

    Entity Affiliation Methods:
        - get_entity_affiliations() - Get contact's entity affiliations
        - add_entity_affiliations() - Add entity affiliations
        - replace_entity_affiliations() - Replace all entity affiliations
        - remove_entity_affiliations() - Remove entity affiliations

    Group Affiliation Methods:
        - get_group_affiliations() - Get contact's group affiliations
        - add_group_affiliations() - Add group affiliations
        - replace_group_affiliations() - Replace all group affiliations
        - remove_group_affiliations() - Remove group affiliations

    View Set Methods:
        - get_default_view_set() - Get contact's default view set
        - set_default_view_set() - Set contact's default view set
        - remove_default_view_set() - Remove contact's default view set

    Team Methods:
        - get_team() - Get contact's team
        - replace_team() - Replace contact's team
        - remove_team() - Remove contact from team

    Portal Access Methods:
        - invite_to_portal() - Send Client Portal invite
        - restore_portal_access() - Restore revoked portal access
        - revoke_portal_access() - Revoke portal access

    Two-Factor Authentication Methods:
        - exempt_from_2fa() - Make 2FA optional for contact
        - require_2fa() - Require 2FA for contact

    Single Sign-On (SSO) Methods:
        - enable_sso() - Enable SSO for contact
        - disable_sso() - Disable SSO for contact
    """

    # =========================================================================
    # Tier 1: CRUD Methods
    # =========================================================================

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get a single contact by ID.

        Args:
            contact_id: The ID of the contact to retrieve.

        Returns:
            The contact resource object containing id, type, attributes,
            and relationships.
        """
        response = self._get(f"/contacts/{contact_id}")
        data = response.json()
        contact = data.get("data", {})
        logger.debug(f"Retrieved contact {contact_id}")
        return contact

    def list_contacts(self, *, page_limit: int = DEFAULT_PAGE_LIMIT) -> List[Dict[str, Any]]:
        """
        List all contacts with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of contact resource objects.
        """
        contacts = list(self._paginate("/contacts", page_limit=page_limit))
        logger.debug(f"Listed {len(contacts)} contacts")
        return contacts

    def create_contact(
        self,
        first_name: str,
        last_name: str,
        *,
        title: Optional[str] = None,
        suffix: Optional[str] = None,
        login_email: Optional[str] = None,
        external_user_id: Optional[str] = None,
        birthday: Optional[str] = None,
        employer: Optional[str] = None,
        occupation: Optional[str] = None,
        ssn: Optional[str] = None,
        mailing_addresses: Optional[List[Dict[str, Any]]] = None,
        emails: Optional[List[Dict[str, Any]]] = None,
        phone_numbers: Optional[List[Dict[str, Any]]] = None,
        family_members: Optional[List[Dict[str, Any]]] = None,
        default_affiliation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new contact.

        Args:
            first_name: Contact's first name. Required. Max 40 characters.
            last_name: Contact's last name. Required. Max 80 characters.
            title: Contact's title (e.g., "Mr."). Max 10 characters.
            suffix: Contact's suffix (e.g., "Jr."). Max 10 characters.
            login_email: Email for Client Portal sign-in.
            external_user_id: Firm's unique ID for the contact. Max 31 characters.
            birthday: Contact's birthday in YYYY-MM-DD format.
            employer: Contact's employer. Max 80 characters.
            occupation: Contact's occupation. Max 80 characters.
            ssn: Contact's Social Security number. Max 9 characters.
            mailing_addresses: List of mailing address objects with keys:
                street (required), street2, city (required), state (required),
                zip (required), country, address_type.
            emails: List of email objects with keys:
                email (required), email_type (required: PERSONAL, WORK, FAMILY, OTHER).
            phone_numbers: List of phone number objects with keys:
                number (required), phone_type (required: HOME, WORK, CELL, FAX, OTHER).
            family_members: List of family member objects with keys:
                first_name (required), last_name (required), relationship (required).
            default_affiliation: Default entity or group affiliation with keys:
                entity_id or group_id (one must be non-null if the other is null).

        Returns:
            The created contact resource object.

        Raises:
            ValidationError: If required fields are missing or invalid.
            ConflictError: If external_user_id or login_email is a duplicate.
        """
        attributes: Dict[str, Any] = {
            "first_name": first_name,
            "last_name": last_name,
        }

        if title is not None:
            attributes["title"] = title
        if suffix is not None:
            attributes["suffix"] = suffix
        if login_email is not None:
            attributes["login_email"] = login_email
        if external_user_id is not None:
            attributes["external_user_id"] = external_user_id
        if birthday is not None:
            attributes["birthday"] = birthday
        if employer is not None:
            attributes["employer"] = employer
        if occupation is not None:
            attributes["occupation"] = occupation
        if ssn is not None:
            attributes["ssn"] = ssn
        if mailing_addresses is not None:
            attributes["mailing_addresses"] = mailing_addresses
        if emails is not None:
            attributes["emails"] = emails
        if phone_numbers is not None:
            attributes["phone_numbers"] = phone_numbers
        if family_members is not None:
            attributes["family_members"] = family_members
        if default_affiliation is not None:
            attributes["default_affiliation"] = default_affiliation

        payload = {
            "data": {
                "type": "contacts",
                "attributes": attributes,
            }
        }

        response = self._post("/contacts", json=payload)
        data = response.json()
        contact = data.get("data", {})
        logger.info(f"Created contact: {contact.get('id')}")
        return contact

    def update_contact(
        self,
        contact_id: str,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        title: Optional[str] = None,
        suffix: Optional[str] = None,
        login_email: Optional[str] = None,
        external_user_id: Optional[str] = None,
        birthday: Optional[str] = None,
        employer: Optional[str] = None,
        occupation: Optional[str] = None,
        ssn: Optional[str] = None,
        mailing_addresses: Optional[List[Dict[str, Any]]] = None,
        emails: Optional[List[Dict[str, Any]]] = None,
        phone_numbers: Optional[List[Dict[str, Any]]] = None,
        family_members: Optional[List[Dict[str, Any]]] = None,
        default_affiliation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a contact.

        Args:
            contact_id: The ID of the contact to update.
            first_name: Contact's first name. Max 40 characters.
            last_name: Contact's last name. Max 80 characters.
            title: Contact's title. Max 10 characters.
            suffix: Contact's suffix. Max 10 characters.
            login_email: Email for Client Portal sign-in. Cannot be deleted.
            external_user_id: Firm's unique ID for the contact. Max 31 characters.
            birthday: Contact's birthday in YYYY-MM-DD format.
            employer: Contact's employer. Max 80 characters.
            occupation: Contact's occupation. Max 80 characters.
            ssn: Contact's Social Security number. Max 9 characters.
            mailing_addresses: List of mailing address objects.
            emails: List of email objects.
            phone_numbers: List of phone number objects.
            family_members: List of family member objects.
            default_affiliation: Default entity or group affiliation.

        Returns:
            The updated contact resource object.

        Note:
            Cannot update: portal_access, is_exempt_from_two_factor_requirement,
            saml_settings, view_set_overrides (read-only fields).

        Raises:
            ConflictError: If external_user_id or login_email is a duplicate.
        """
        attributes: Dict[str, Any] = {}

        if first_name is not None:
            attributes["first_name"] = first_name
        if last_name is not None:
            attributes["last_name"] = last_name
        if title is not None:
            attributes["title"] = title
        if suffix is not None:
            attributes["suffix"] = suffix
        if login_email is not None:
            attributes["login_email"] = login_email
        if external_user_id is not None:
            attributes["external_user_id"] = external_user_id
        if birthday is not None:
            attributes["birthday"] = birthday
        if employer is not None:
            attributes["employer"] = employer
        if occupation is not None:
            attributes["occupation"] = occupation
        if ssn is not None:
            attributes["ssn"] = ssn
        if mailing_addresses is not None:
            attributes["mailing_addresses"] = mailing_addresses
        if emails is not None:
            attributes["emails"] = emails
        if phone_numbers is not None:
            attributes["phone_numbers"] = phone_numbers
        if family_members is not None:
            attributes["family_members"] = family_members
        if default_affiliation is not None:
            attributes["default_affiliation"] = default_affiliation

        payload = {
            "data": {
                "type": "contacts",
                "id": contact_id,
                "attributes": attributes,
            }
        }

        response = self._patch(f"/contacts/{contact_id}", json=payload)
        data = response.json()
        contact = data.get("data", {})
        logger.info(f"Updated contact: {contact_id}")
        return contact

    def delete_contact(self, contact_id: str) -> None:
        """
        Delete a contact.

        Args:
            contact_id: The ID of the contact to delete.
        """
        self._delete(f"/contacts/{contact_id}")
        logger.info(f"Deleted contact: {contact_id}")

    # =========================================================================
    # Entity Affiliation Methods
    # =========================================================================

    def get_entity_affiliations(self, contact_id: str) -> List[Dict[str, Any]]:
        """
        Get a contact's entity affiliations.

        Args:
            contact_id: The ID of the contact.

        Returns:
            List of entity relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/contacts/{contact_id}/relationships/entity_affiliations")
        data = response.json()
        entities = data.get("data", [])
        logger.debug(f"Retrieved {len(entities)} entity affiliations for contact {contact_id}")
        return entities

    def add_entity_affiliations(self, contact_id: str, entity_ids: List[str]) -> None:
        """
        Add entity affiliations to a contact.

        Args:
            contact_id: The ID of the contact.
            entity_ids: List of entity IDs to affiliate with the contact.
        """
        payload = {
            "data": [
                {"id": entity_id, "type": "entities"}
                for entity_id in entity_ids
            ]
        }

        self._post(f"/contacts/{contact_id}/relationships/entity_affiliations", json=payload)
        logger.info(f"Added {len(entity_ids)} entity affiliations for contact {contact_id}")

    def replace_entity_affiliations(self, contact_id: str, entity_ids: List[str]) -> None:
        """
        Replace all entity affiliations for a contact.

        Args:
            contact_id: The ID of the contact.
            entity_ids: List of entity IDs to replace current affiliations.
        """
        payload = {
            "data": [
                {"id": entity_id, "type": "entities"}
                for entity_id in entity_ids
            ]
        }

        self._patch(f"/contacts/{contact_id}/relationships/entity_affiliations", json=payload)
        logger.info(f"Replaced entity affiliations for contact {contact_id} with {len(entity_ids)} entities")

    def remove_entity_affiliations(self, contact_id: str, entity_ids: List[str]) -> None:
        """
        Remove entity affiliations from a contact.

        Args:
            contact_id: The ID of the contact.
            entity_ids: List of entity IDs to remove from affiliations.
        """
        payload = {
            "data": [
                {"id": entity_id, "type": "entities"}
                for entity_id in entity_ids
            ]
        }

        self._delete(f"/contacts/{contact_id}/relationships/entity_affiliations", json=payload)
        logger.info(f"Removed {len(entity_ids)} entity affiliations for contact {contact_id}")

    # =========================================================================
    # Group Affiliation Methods
    # =========================================================================

    def get_group_affiliations(self, contact_id: str) -> List[Dict[str, Any]]:
        """
        Get a contact's group affiliations.

        Args:
            contact_id: The ID of the contact.

        Returns:
            List of group relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/contacts/{contact_id}/relationships/group_affiliations")
        data = response.json()
        groups = data.get("data", [])
        logger.debug(f"Retrieved {len(groups)} group affiliations for contact {contact_id}")
        return groups

    def add_group_affiliations(self, contact_id: str, group_ids: List[str]) -> None:
        """
        Add group affiliations to a contact.

        Args:
            contact_id: The ID of the contact.
            group_ids: List of group IDs to affiliate with the contact.
        """
        payload = {
            "data": [
                {"id": group_id, "type": "groups"}
                for group_id in group_ids
            ]
        }

        self._post(f"/contacts/{contact_id}/relationships/group_affiliations", json=payload)
        logger.info(f"Added {len(group_ids)} group affiliations for contact {contact_id}")

    def replace_group_affiliations(self, contact_id: str, group_ids: List[str]) -> None:
        """
        Replace all group affiliations for a contact.

        Args:
            contact_id: The ID of the contact.
            group_ids: List of group IDs to replace current affiliations.
        """
        payload = {
            "data": [
                {"id": group_id, "type": "groups"}
                for group_id in group_ids
            ]
        }

        self._patch(f"/contacts/{contact_id}/relationships/group_affiliations", json=payload)
        logger.info(f"Replaced group affiliations for contact {contact_id} with {len(group_ids)} groups")

    def remove_group_affiliations(self, contact_id: str, group_ids: List[str]) -> None:
        """
        Remove group affiliations from a contact.

        Args:
            contact_id: The ID of the contact.
            group_ids: List of group IDs to remove from affiliations.
        """
        payload = {
            "data": [
                {"id": group_id, "type": "groups"}
                for group_id in group_ids
            ]
        }

        self._delete(f"/contacts/{contact_id}/relationships/group_affiliations", json=payload)
        logger.info(f"Removed {len(group_ids)} group affiliations for contact {contact_id}")

    # =========================================================================
    # View Set Methods
    # =========================================================================

    def get_default_view_set(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a contact's default view set.

        Args:
            contact_id: The ID of the contact.

        Returns:
            The view set relationship data, or None if no view set is assigned.
            Returns dict with 'id' and 'type' keys when a view set is assigned.
        """
        response = self._get(f"/contacts/{contact_id}/relationships/default_view_set")
        data = response.json()
        view_set = data.get("data")
        logger.debug(f"Retrieved default view set for contact {contact_id}")
        return view_set

    def set_default_view_set(self, contact_id: str, view_set_id: str) -> None:
        """
        Set the default view set for a contact.

        Args:
            contact_id: The ID of the contact.
            view_set_id: The ID of the view set to assign.
        """
        payload = {
            "data": {
                "id": view_set_id,
                "type": "view_sets",
            }
        }

        self._post(f"/contacts/{contact_id}/relationships/default_view_set", json=payload)
        logger.info(f"Set default view set {view_set_id} for contact {contact_id}")

    def remove_default_view_set(self, contact_id: str) -> None:
        """
        Remove the default view set from a contact.

        Args:
            contact_id: The ID of the contact.
        """
        self._delete(f"/contacts/{contact_id}/relationships/default_view_set")
        logger.info(f"Removed default view set for contact {contact_id}")

    # =========================================================================
    # Team Methods
    # =========================================================================

    def get_team(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a contact's team.

        Args:
            contact_id: The ID of the contact.

        Returns:
            The team relationship data, or None if no team is assigned.
            Returns dict with 'id' and 'type' keys when a team is assigned.
        """
        response = self._get(f"/contacts/{contact_id}/relationships/team")
        data = response.json()
        team = data.get("data")
        logger.debug(f"Retrieved team for contact {contact_id}")
        return team

    def replace_team(self, contact_id: str, team_id: str) -> None:
        """
        Replace a contact's team.

        Args:
            contact_id: The ID of the contact.
            team_id: The ID of the team to assign.
        """
        payload = {
            "data": {
                "id": team_id,
                "type": "teams",
            }
        }

        self._patch(f"/contacts/{contact_id}/relationships/team", json=payload)
        logger.info(f"Replaced team for contact {contact_id} with team {team_id}")

    def remove_team(self, contact_id: str) -> None:
        """
        Remove a contact from their team.

        Args:
            contact_id: The ID of the contact.
        """
        self._delete(f"/contacts/{contact_id}/relationships/team")
        logger.info(f"Removed team for contact {contact_id}")

    # =========================================================================
    # Portal Access Methods
    # =========================================================================

    def invite_to_portal(self, contact_id: str) -> None:
        """
        Send or resend a Client Portal invite to a contact.

        The invite is sent to the contact's login email address.

        Args:
            contact_id: The ID of the contact to invite.

        Raises:
            ValidationError: If login email is missing or invalid.
            ConflictError: If contact is already activated or revoked.
        """
        self._post(f"/contacts/{contact_id}/invite")
        logger.info(f"Sent portal invite to contact {contact_id}")

    def restore_portal_access(self, contact_id: str) -> None:
        """
        Restore a contact's Client Portal access.

        Allows a client to sign into the Client Portal again.
        Can only restore access for clients whose access is currently revoked.

        Args:
            contact_id: The ID of the contact.

        Raises:
            ValidationError: If contact is not activated or revoked.
        """
        self._patch(f"/contacts/{contact_id}/restore")
        logger.info(f"Restored portal access for contact {contact_id}")

    def revoke_portal_access(self, contact_id: str) -> None:
        """
        Revoke a contact's Client Portal access.

        Prevents a client from signing into the Client Portal.
        Can only revoke access for clients whose access is currently activated.

        Args:
            contact_id: The ID of the contact.

        Raises:
            ValidationError: If contact is not activated.
        """
        self._patch(f"/contacts/{contact_id}/revoke")
        logger.info(f"Revoked portal access for contact {contact_id}")

    # =========================================================================
    # Two-Factor Authentication Methods
    # =========================================================================

    def exempt_from_2fa(self, contact_id: str) -> None:
        """
        Exempt a contact from the firm's 2FA Client Portal login requirement.

        Can only make 2FA optional for active contacts when the firm requires
        2FA in Firm Administration > System security.

        Args:
            contact_id: The ID of the contact.

        Raises:
            ValidationError: If contact is not activated, has SSO enabled,
                or firm doesn't require 2FA for portal contacts.
        """
        self._patch(f"/contacts/{contact_id}/exempt_two_factor_authentication")
        logger.info(f"Exempted contact {contact_id} from 2FA requirement")

    def require_2fa(self, contact_id: str) -> None:
        """
        Require a contact to use two-factor authentication.

        Requires an exempted contact to follow the firm's 2FA Client Portal
        login requirement. Can only require active contacts to use 2FA when
        the firm requires it in Firm Administration > System security.

        Args:
            contact_id: The ID of the contact.

        Raises:
            ValidationError: If contact is not activated, has SSO enabled,
                or firm doesn't require 2FA for portal contacts.
        """
        self._patch(f"/contacts/{contact_id}/require_two_factor_authentication")
        logger.info(f"Required 2FA for contact {contact_id}")

    # =========================================================================
    # Single Sign-On (SSO) Methods
    # =========================================================================

    def enable_sso(self, contact_id: str, saml_user_id: str) -> None:
        """
        Enable single sign-on (SSO) for a contact.

        Enables SAML settings to require the contact to use SSO.
        Can only enable SSO if the contact's portal access isn't revoked
        and if SAML is set up for the firm.

        Args:
            contact_id: The ID of the contact.
            saml_user_id: The contact's SAML user ID for SSO. Max 80 characters.

        Raises:
            ValidationError: If contact is missing login email, is revoked,
                or saml_user_id is invalid.
            ForbiddenError: If SAML is not enabled for the firm.
            ConflictError: If saml_user_id is a duplicate.
        """
        payload = {
            "data": {
                "id": contact_id,
                "type": "saml_settings",
                "attributes": {
                    "saml_user_id": saml_user_id,
                },
            }
        }

        self._patch(f"/contacts/{contact_id}/enable_saml", json=payload)
        logger.info(f"Enabled SSO for contact {contact_id}")

    def disable_sso(self, contact_id: str) -> None:
        """
        Disable single sign-on (SSO) for a contact.

        Disables SAML settings to prevent the contact from using SSO.
        Can only disable SSO if the contact's portal access isn't revoked
        and if SAML is set up for the firm.

        Args:
            contact_id: The ID of the contact.

        Raises:
            ValidationError: If contact is missing login email or is revoked.
            ForbiddenError: If SAML is not enabled for the firm.
        """
        self._patch(f"/contacts/{contact_id}/disable_saml")
        logger.info(f"Disabled SSO for contact {contact_id}")
