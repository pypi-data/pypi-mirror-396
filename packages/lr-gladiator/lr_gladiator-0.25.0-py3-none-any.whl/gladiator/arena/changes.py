from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Mapping, Optional, Sequence, TYPE_CHECKING

from ..config import LoginConfig
from .base import ArenaError, BaseArenaClient

if TYPE_CHECKING:
    import requests


class ChangeClient(BaseArenaClient):
    """Implements Change management helpers."""

    _VALID_EFFECTIVITY = {
        "PERMANENT_ON_APPROVAL",
        "PERMANENT_ON_DATE",
        "TEMPORARY",
    }

    def __init__(
        self,
        cfg: LoginConfig,
        *,
        session: Optional["requests.Session"] = None,
    ) -> None:
        super().__init__(cfg, session=session)
        self._workspace_lifecycle_phase_cache: Optional[Dict[str, dict]] = None

    # Example stub to demonstrate extension point
    def list_changes(self, *, workspace: Optional[str] = None) -> list[dict]:
        raise NotImplementedError("Change management APIs are not implemented yet.")

    @staticmethod
    def _normalize_datetime(value, field_name: str) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() or None
        if isinstance(value, datetime):
            dt = value
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")
        raise ArenaError(
            f"{field_name} must be an ISO-8601 string or datetime instance (got {type(value).__name__})."
        )

    def _api_list_change_categories(self) -> List[dict]:
        url = f"{self._api_base()}/settings/changes/categories"
        self._log(f"GET {url}")
        resp = self.session.get(url)
        resp.raise_for_status()
        data = self._ensure_json(resp)
        rows = data.get("results", data if isinstance(data, list) else [])
        return [row for row in rows if isinstance(row, dict)]

    def _api_resolve_change_guid(self, change_number: str) -> str:
        if not change_number or not change_number.strip():
            raise ArenaError("change_number is required to resolve a change")

        number = change_number.strip()
        url = f"{self._api_base()}/changes"
        params = {"number": number, "limit": 1, "responseview": "minimal"}
        self._log(f"GET {url} params={params}")
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        data = self._ensure_json(resp)
        results = data.get("results") if isinstance(data, dict) else data
        if not results:
            raise ArenaError(f'Change "{number}" not found.')

        record = results[0] if isinstance(results, list) else results
        guid = record.get("guid") or record.get("id")
        if not guid:
            raise ArenaError("API response missing change GUID")
        return str(guid)

    def resolve_change_category_guid(self, name: str) -> str:
        if not name or not name.strip():
            raise ArenaError("Change category name is required")
        needle = name.strip().casefold()
        for row in self._api_list_change_categories():
            label = str(row.get("name") or "").strip()
            if label and label.casefold() == needle:
                guid = row.get("guid")
                if guid:
                    return str(guid)
        raise ArenaError(f'Change category "{name}" not found.')

    def create_change(
        self,
        *,
        category_guid: str,
        title: str,
        description: Optional[str] = None,
        effectivity_type: str = "PERMANENT_ON_APPROVAL",
        planned_effectivity: Optional[object] = None,
        expiration_date: Optional[object] = None,
        approval_deadline: Optional[object] = None,
        enforce_approval_deadline: bool = False,
        additional_attributes: Optional[Mapping[str, object]] = None,
    ) -> dict:
        if not category_guid or not category_guid.strip():
            raise ArenaError("category_guid is required to create a change")
        if not title or not title.strip():
            raise ArenaError("title is required to create a change")

        eff_type = (effectivity_type or "").strip().upper() or "PERMANENT_ON_APPROVAL"
        if eff_type not in self._VALID_EFFECTIVITY:
            raise ArenaError(
                "effectivity_type must be one of PERMANENT_ON_APPROVAL, PERMANENT_ON_DATE, TEMPORARY"
            )

        payload: dict[str, object] = {
            "category": {"guid": category_guid.strip()},
            "title": title.strip(),
            "effectivityType": eff_type,
        }

        if description:
            payload["description"] = description

        approval_iso = self._normalize_datetime(approval_deadline, "approval_deadline")
        if approval_iso:
            payload["approvalDeadlineDateTime"] = approval_iso
        if enforce_approval_deadline:
            payload["enforceApprovalDeadline"] = True

        if additional_attributes:
            attrs = []
            for guid, value in additional_attributes.items():
                if not guid or not str(guid).strip():
                    continue
                attrs.append({"guid": str(guid).strip(), "value": value})
            if attrs:
                payload["additionalAttributes"] = attrs

        if eff_type == "PERMANENT_ON_DATE":
            planned_iso = self._normalize_datetime(
                planned_effectivity, "planned_effectivity"
            )
            if not planned_iso:
                raise ArenaError(
                    "planned_effectivity is required when effectivity_type is PERMANENT_ON_DATE"
                )
            payload["effectivityPlannedDateTime"] = planned_iso
            if expiration_date is not None:
                raise ArenaError(
                    "expiration_date is not applicable to PERMANENT_ON_DATE changes"
                )
        elif eff_type == "TEMPORARY":
            expiration_iso = self._normalize_datetime(
                expiration_date, "expiration_date"
            )
            if not expiration_iso:
                raise ArenaError(
                    "expiration_date is required when effectivity_type is TEMPORARY"
                )
            payload["expirationDateTime"] = expiration_iso
            if planned_effectivity is not None:
                raise ArenaError(
                    "planned_effectivity is not applicable to TEMPORARY changes"
                )
        else:
            if planned_effectivity is not None:
                raise ArenaError(
                    "planned_effectivity is only valid for PERMANENT_ON_DATE effectivity"
                )
            if expiration_date is not None:
                raise ArenaError(
                    "expiration_date is only valid for TEMPORARY effectivity"
                )

        url = f"{self._api_base()}/changes"
        self._log(f"POST {url}")
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        return self._ensure_json(resp)

    def add_item_to_change(
        self,
        *,
        change_number: str,
        item_number: str,
        new_revision: Optional[str] = None,
        lifecycle_phase: Optional[str] = None,
    ) -> dict:
        if not change_number or not change_number.strip():
            raise ArenaError("change_number is required to add an item to a change")
        if not item_number or not item_number.strip():
            raise ArenaError("item_number is required to add an item to a change")

        item_value = item_number.strip()

        change_guid = self._api_resolve_change_guid(change_number.strip())
        revision_info = self._resolve_item_revisions(item_value)
        working_guid = revision_info.get("WORKING")
        if not working_guid:
            raise ArenaError(f"Item {item_value} has no WORKING revision to add.")

        payload: Dict[str, object] = {
            "newItemRevision": {"guid": working_guid},
        }

        phase_map = revision_info.get("_phase_map")
        working_phase_name = (
            str(revision_info.get("_working_phase_name") or "").strip().casefold()
        )

        workspace_phases = self._get_workspace_lifecycle_phase_map()
        combined_phase_map: Dict[str, str] = {}
        choice_names: set[str] = set()

        for key, info in workspace_phases.items():
            guid = info.get("guid")
            if not guid:
                continue
            canonical = key
            combined_phase_map[canonical] = str(guid)
            name = info.get("name")
            if name:
                choice_names.add(str(name))
            for alias in info.get("aliases", []):
                if alias:
                    combined_phase_map[alias] = str(guid)

        if isinstance(phase_map, dict):
            for key, guid in phase_map.items():
                if not guid:
                    continue
                alias = str(key).casefold()
                combined_phase_map[alias] = str(guid)
                choice_names.add(str(key).title())

        phase_guid: Optional[str] = None
        if lifecycle_phase:
            key = lifecycle_phase.strip().casefold()
            if not key:
                raise ArenaError("lifecycle_phase must not be empty when provided")
            phase_guid = combined_phase_map.get(key)
            if not phase_guid:
                available_names = {
                    f"{info.get('name')}"
                    + (f" [{info.get('stage')}]" if info.get("stage") else "")
                    for info in workspace_phases.values()
                    if info.get("name")
                }
                available_names.update(choice_names)
                available = ", ".join(sorted(available_names))
                self._log(
                    "Available lifecycle phases for %s: %s"
                    % (item_value, available or "(none)")
                )
                raise ArenaError(
                    f'Lifecycle phase "{lifecycle_phase}" is not available. '
                    + (f"Choices: {available}" if available else "")
                )
        else:
            preferred_keys = [
                "in production",
                "production",
                "release to production",
                "released",
            ]
            for key in preferred_keys:
                guid = combined_phase_map.get(key)
                if guid and (not working_phase_name or key != working_phase_name):
                    phase_guid = guid
                    break
            if not phase_guid:
                for info in workspace_phases.values():
                    guid = info.get("guid")
                    name = info.get("name")
                    stage = (info.get("stage") or "").upper()
                    if (
                        guid
                        and stage == "PRODUCTION"
                        and name
                        and name.casefold() != working_phase_name
                    ):
                        phase_guid = str(guid)
                        break
            if not phase_guid and working_phase_name:
                fallback = combined_phase_map.get(working_phase_name)
                if fallback:
                    phase_guid = fallback

        if not phase_guid and choice_names:
            self._log(
                "Lifecycle phases available for %s: %s"
                % (item_value, ", ".join(sorted(choice_names)))
            )

        if phase_guid:
            payload["newLifecyclePhase"] = {"guid": phase_guid}

        new_revision_value = (new_revision or "").strip()
        if new_revision_value:
            payload["newRevisionNumber"] = new_revision_value

        url = f"{self._api_base()}/changes/{change_guid.strip()}/items"
        self._log(f"POST {url}")
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        data = self._try_json(resp)
        if data is not None:
            return data
        return {"status": resp.status_code}

    def submit_change(
        self,
        *,
        change_number: str,
        status: str = "SUBMITTED",
        comment: Optional[str] = None,
        administrators: Optional[Sequence[str]] = None,
    ) -> dict:
        if not change_number or not change_number.strip():
            raise ArenaError("change_number is required to submit a change")

        status_value = (status or "").strip().upper()
        if not status_value:
            raise ArenaError("status is required to submit a change")

        change_guid = self._api_resolve_change_guid(change_number.strip())

        payload: Dict[str, object] = {
            "change": {"guid": change_guid},
            "status": status_value,
        }

        if comment:
            payload["comment"] = comment

        if administrators:
            admins_payload = []
            for guid in administrators:
                if not guid:
                    continue
                guid_str = str(guid).strip()
                if not guid_str:
                    continue
                admins_payload.append({"guid": guid_str})
            if admins_payload:
                payload["administrators"] = admins_payload

        url = f"{self._api_base()}/changes/statuschanges"
        self._log(f"POST {url}")
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        data = self._try_json(resp)
        if data is not None:
            return data
        return {"status": resp.status_code}

    def _get_workspace_lifecycle_phase_map(self) -> Dict[str, dict]:
        cache = self._workspace_lifecycle_phase_cache
        if cache is not None:
            return cache

        url = f"{self._api_base()}/settings/items/lifecyclephases"
        self._log(f"GET {url}")
        resp = self.session.get(url)
        resp.raise_for_status()
        data = self._ensure_json(resp)
        rows = data.get("results", data if isinstance(data, list) else [])

        phase_map: Dict[str, dict] = {}
        display_names: set[str] = set()

        for row in rows:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").strip()
            guid = row.get("guid") or row.get("id")
            if not name or not guid:
                continue
            info = {
                "guid": str(guid),
                "name": name,
                "stage": row.get("stage"),
                "shortName": row.get("shortName"),
                "active": row.get("active"),
                "used": row.get("used"),
                "aliases": [],
            }
            canonical = name.casefold()
            phase_map[canonical] = info
            display_names.add(name)

            short_name = row.get("shortName")
            if short_name:
                alias_key = str(short_name).strip().casefold()
                if alias_key and alias_key != canonical:
                    info["aliases"].append(alias_key)

            alt = row.get("label") or row.get("title")
            if alt:
                alias_key = str(alt).strip().casefold()
                if (
                    alias_key
                    and alias_key != canonical
                    and alias_key not in info["aliases"]
                ):
                    info["aliases"].append(alias_key)

        if display_names:
            self._log(
                "Workspace lifecycle phases: %s" % ", ".join(sorted(display_names))
            )
        else:
            self._log("Workspace lifecycle phases: (none)")

        self._workspace_lifecycle_phase_cache = phase_map
        return phase_map

    def _resolve_item_revisions(self, item_number: str) -> Dict[str, Optional[str]]:
        url = f"{self._api_base()}/items/"
        params = {"number": item_number, "limit": 1, "responseview": "minimal"}
        self._log(f"GET {url} params={params}")
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        data = self._ensure_json(resp)
        results = data.get("results") if isinstance(data, dict) else data
        if not results:
            raise ArenaError(f"Item number {item_number} not found")

        record = results[0] if isinstance(results, list) else results
        item_guid = record.get("guid") or record.get("id")
        if not item_guid:
            raise ArenaError("API response missing item GUID")

        rev_url = f"{self._api_base()}/items/{item_guid}/revisions"
        self._log(f"GET {rev_url}")
        rev_resp = self.session.get(rev_url)
        rev_resp.raise_for_status()
        rev_data = self._ensure_json(rev_resp)
        revs = rev_data.get("results", rev_data if isinstance(rev_data, list) else [])

        working_guid: Optional[str] = None
        effective_candidates: List[dict] = []
        label_map: Dict[str, str] = {}
        phase_map: Dict[str, str] = {}
        working_phase_name: Optional[str] = None

        def _add_phase(entry: object) -> None:
            if isinstance(entry, list):
                for item in entry:
                    _add_phase(item)
                return
            if isinstance(entry, dict):
                name = entry.get("name") or entry.get("label") or entry.get("title")
                guid = entry.get("guid") or entry.get("value") or entry.get("id")
                if name and guid:
                    phase_map[str(name).casefold()] = str(guid)

        for rev in revs:
            guid = rev.get("guid") or rev.get("id")
            if not guid:
                continue
            guid = str(guid)
            status = (rev.get("revisionStatus") or "").upper()
            rv_code = rev.get("status")
            if status == "WORKING" or rv_code == 0:
                working_guid = guid
                _add_phase(rev.get("lifecyclePhase"))
                _add_phase(rev.get("availableLifecyclePhases"))
                _add_phase(rev.get("availableLifecyclePhaseOptions"))
                _add_phase(rev.get("nextLifecyclePhases"))
                _add_phase(rev.get("nextLifecyclePhase"))
                workflow = (
                    rev.get("workflow")
                    if isinstance(rev.get("workflow"), dict)
                    else None
                )
                if workflow:
                    _add_phase(workflow.get("phases"))
                if working_phase_name is None:
                    current_phase = rev.get("lifecyclePhase")
                    if isinstance(current_phase, dict):
                        phase_name = current_phase.get("name") or current_phase.get(
                            "label"
                        )
                        if phase_name:
                            working_phase_name = str(phase_name)
                    if not working_phase_name:
                        alt = rev.get("lifecyclePhaseName")
                        if alt:
                            working_phase_name = str(alt)
            if status == "EFFECTIVE" or rv_code == 1:
                effective_candidates.append(rev)
                _add_phase(rev.get("lifecyclePhase"))
            label = rev.get("number") or rev.get("name")
            if label:
                label_map[str(label).upper()] = guid

            phase_guid = rev.get("lifecyclePhaseGuid")
            phase_name = rev.get("lifecyclePhaseName")
            if phase_guid and phase_name:
                phase_map[str(phase_name).casefold()] = str(phase_guid)

        effective_guid: Optional[str] = None
        for rev in effective_candidates:
            if not rev.get("supersededDateTime"):
                effective_guid = str(rev.get("guid"))
                break
        if not effective_guid and effective_candidates:
            effective_guid = str(effective_candidates[-1].get("guid"))

        result: Dict[str, Optional[str]] = {
            "WORKING": working_guid,
            "EFFECTIVE": effective_guid,
            "_phase_map": phase_map,
        }
        if working_phase_name:
            result["_working_phase_name"] = working_phase_name
        for label, guid in label_map.items():
            if label not in result:
                result[label] = guid
        return result

    def get_change_items(self, *, change_number: str) -> dict:
        if not change_number or not change_number.strip():
            raise ArenaError("change_number is required to fetch change items")

        change_guid = self._api_resolve_change_guid(change_number.strip())
        url = f"{self._api_base()}/changes/{change_guid}/items"
        self._log(f"GET {url}")
        resp = self.session.get(url)
        resp.raise_for_status()
        return self._ensure_json(resp)


__all__ = ["ChangeClient"]
