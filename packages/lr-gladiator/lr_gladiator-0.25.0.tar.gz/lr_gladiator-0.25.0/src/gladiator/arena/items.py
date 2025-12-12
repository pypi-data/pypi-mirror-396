from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, FrozenSet, List, Mapping, Optional

import requests

from ..checksums import sha256_file
from ..config import LoginConfig
from .base import ArenaError, BaseArenaClient


class ItemClient(BaseArenaClient):
    """Implements Arena item, BOM, and file operations."""

    def __init__(
        self,
        cfg: LoginConfig,
        *,
        session: Optional[requests.Session] = None,
    ) -> None:
        super().__init__(cfg, session=session)

    @staticmethod
    def _arena_payload_has_code(payload: object, code: int) -> bool:
        if not isinstance(payload, dict):
            return False
        if payload.get("code") == code:
            return True
        errs = payload.get("errors")
        if isinstance(errs, list):
            for err in errs:
                if isinstance(err, dict) and err.get("code") == code:
                    return True
        return False

    # --- version picking helpers ---
    @staticmethod
    def _logical_key(f: Dict) -> str:
        # Prefer any group-level id; fall back to normalized filename
        return (
            f.get("attachmentGroupGuid")
            or f.get("attachmentGroupId")
            or f.get("attachmentGuid")
            or (f.get("name") or f.get("filename") or "").lower()
        )

    @staticmethod
    def _version_of(f: Dict) -> int:
        for k in ("version", "fileVersion", "versionNumber", "rev", "revision"):
            v = f.get(k)
            if v is None:
                continue
            try:
                return int(v)
            except Exception:
                if isinstance(v, str) and len(v) == 1 and v.isalpha():
                    return ord(v.upper()) - 64  # A->1
        return -1

    @staticmethod
    def _timestamp_of(f: Dict):
        from datetime import datetime
        from email.utils import parsedate_to_datetime

        for k in (
            "modifiedAt",
            "updatedAt",
            "lastModified",
            "lastModifiedDate",
            "effectiveDate",
            "createdAt",
        ):
            s = f.get(k)
            if not s:
                continue
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                try:
                    return parsedate_to_datetime(s)
                except Exception:
                    continue
        return None

    @staticmethod
    def _item_payload_dict(payload) -> Dict:
        """Coerce API payloads into a simple item dict."""
        if isinstance(payload, dict):
            item = payload.get("item")
            if isinstance(item, dict):
                return item
            return payload
        return {}

    @staticmethod
    def _string_from(
        value: object, keys: tuple[str, ...] = ("name", "number", "label")
    ) -> Optional[str]:
        if isinstance(value, dict):
            for key in keys:
                text = value.get(key)
                if text not in (None, ""):
                    return str(text)
            return None
        if value is None:
            return None
        return str(value)

    def _latest_files(self, files: List[Dict]) -> List[Dict]:
        best: Dict[str, Dict] = {}
        for f in files:
            key = self._logical_key(f)
            if not key:
                continue
            score = (self._version_of(f), self._timestamp_of(f) or 0)
            prev = best.get(key)
            if not prev:
                f["_score"] = score
                best[key] = f
                continue
            if score > prev.get("_score", (-1, 0)):
                f["_score"] = score
                best[key] = f
        out = []
        for v in best.values():
            v.pop("_score", None)
            out.append(v)
        return out

    # ---------- Public high-level methods ----------
    def get_latest_approved_revision(self, item_number: str) -> str:
        return self._api_get_latest_approved(item_number)

    def list_files(
        self, item_number: str, revision: Optional[str] = None
    ) -> List[Dict]:
        target_guid = self._api_resolve_revision_guid(
            item_number, revision or "EFFECTIVE"
        )
        raw = self._api_list_files_by_item_guid(target_guid)
        return self._latest_files(raw)

    def download_files(
        self,
        item_number: str,
        revision: Optional[str] = None,
        out_dir: Path = Path("."),
    ) -> List[Path]:
        files = self.list_files(item_number, revision)
        out_dir.mkdir(parents=True, exist_ok=True)
        downloaded: List[Path] = []
        for f in files:
            # Skip associations with no blob
            if not f.get("haveContent", True):
                self._log(
                    f"Skip {item_number}: file {f.get('filename')} has no content"
                )
                continue

            url = f.get("downloadUrl") or f.get("url")
            filename = f.get("filename") or f.get("name")
            if not url or not filename:
                continue

            p = out_dir / filename
            try:
                with self.session.get(
                    url,
                    stream=True,
                    headers={"arena_session_id": self.cfg.arena_session_id or ""},
                ) as r:
                    # If the blob is missing/forbidden, don’t abort the whole command
                    if r.status_code in (400, 403, 404):
                        self._log(
                            f"Skip {item_number}: {filename} content unavailable "
                            f"(HTTP {r.status_code})"
                        )
                        continue
                    r.raise_for_status()
                    with open(p, "wb") as fh:
                        for chunk in r.iter_content(128 * 1024):
                            fh.write(chunk)
                downloaded.append(p)
            except requests.HTTPError as exc:
                # Be resilient: log and continue
                self._log(f"Download failed for {filename}: {exc}")
                continue
        return downloaded

    def download_files_recursive(
        self,
        item_number: str,
        revision: Optional[str] = None,
        out_dir: Path = Path("."),
        *,
        max_depth: Optional[int] = None,
    ) -> List[Path]:
        """
        Download files for `item_number` AND, recursively, for all subassemblies
        discovered via the BOM. Each child item is placed under a subdirectory:
            <out_dir>/<child_item_number>/
        Root files go directly in <out_dir>/.

        Depth semantics match `get_bom(..., recursive=True, max_depth=...)`.
        """
        # Ensure the root directory exists
        out_dir.mkdir(parents=True, exist_ok=True)

        downloaded: List[Path] = []
        bom_cache: Dict[str, List[Dict]] = {}

        def fetch_children(item: str) -> List[Dict]:
            if item not in bom_cache:
                bom_cache[item] = self.get_bom(
                    item,
                    revision,
                    recursive=False,
                    max_depth=None,
                )
            return bom_cache[item]

        def walk(
            current_item: str,
            dest: Path,
            depth: int,
            ancestors: FrozenSet[str],
        ) -> None:
            if current_item in ancestors:
                self._log(
                    "Detected BOM cycle involving "
                    f"{current_item} (ancestors: {', '.join(sorted(ancestors))})"
                )
                return

            next_ancestors = ancestors | {current_item}

            dest.mkdir(parents=True, exist_ok=True)
            downloaded.extend(self.download_files(current_item, revision, out_dir=dest))

            if max_depth is not None and depth >= max_depth:
                return

            children = fetch_children(current_item)
            seen_children: set[str] = set()
            for child in children:
                if not child:
                    continue
                child_num = child.get("itemNumber")
                if not child_num:
                    continue
                if child_num == current_item:
                    continue
                if child_num in seen_children:
                    continue
                if child_num in next_ancestors:
                    self._log(
                        "Detected BOM cycle involving "
                        f"{child_num} (ancestors: {', '.join(sorted(next_ancestors))})"
                    )
                    continue
                seen_children.add(child_num)

                child_dir = dest / child_num
                walk(child_num, child_dir, depth + 1, next_ancestors)

        walk(item_number, out_dir, depth=0, ancestors=frozenset())
        return downloaded

    def get_item_summary(
        self, item_number: str, revision: Optional[str] = None
    ) -> Dict:
        """Return normalized metadata for a specific item revision."""
        selector = (revision or "EFFECTIVE").strip() or "EFFECTIVE"
        target_guid = self._api_resolve_revision_guid(item_number, selector)
        url = f"{self._api_base()}/items/{target_guid}"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        payload = self._ensure_json(r)
        item_data = self._item_payload_dict(payload)

        category_field = item_data.get("category") or payload.get("category")
        category_name = self._string_from(
            category_field, ("name", "number", "label", "displayName")
        )

        revision_label = (
            item_data.get("revisionNumber")
            or item_data.get("revision")
            or payload.get("revisionNumber")
            or payload.get("revision")
            or selector
        )

        lifecycle_field = (
            item_data.get("lifecyclePhase")
            or payload.get("lifecyclePhase")
            or item_data.get("lifecyclePhaseName")
            or payload.get("lifecyclePhaseName")
        )
        lifecycle_phase = self._string_from(
            lifecycle_field,
            ("name", "phase", "label", "displayName", "number"),
        )

        url_field = item_data.get("url") or payload.get("url")
        app_url = None
        api_url = None
        if isinstance(url_field, dict):
            app_url = url_field.get("app") or url_field.get("appUrl")
            api_url = url_field.get("api") or url_field.get("apiUrl")
        if not app_url:
            app_url = payload.get("appUrl") or item_data.get("appUrl")

        summary = {
            "number": item_data.get("number") or payload.get("number") or item_number,
            "revision": revision_label,
            "name": item_data.get("name") or payload.get("name"),
            "description": item_data.get("description") or payload.get("description"),
            "category": category_name,
            "lifecyclePhase": lifecycle_phase,
            "revisionStatus": item_data.get("revisionStatus")
            or payload.get("revisionStatus"),
            "selector": selector,
            "revisionGuid": target_guid,
            "appUrl": app_url,
            "apiUrl": api_url,
        }
        return summary

    def download_item_picture(
        self,
        item_number: str,
        revision: Optional[str] = None,
        *,
        dest_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """Download the item's picture to dest_dir/<item_number>.<ext> if present."""
        selector = (revision or "EFFECTIVE").strip() or "EFFECTIVE"
        target_guid = self._api_resolve_revision_guid(item_number, selector)
        endpoints = ("image/content", "image")
        base = f"{self._api_base()}/items/{target_guid}"
        headers = {"Accept": "*/*"}

        for idx, suffix in enumerate(endpoints):
            url = f"{base}/{suffix}"
            self._log(f"GET {url} (image)")
            resp = self.session.get(url, stream=True, headers=headers)
            try:
                retry_with_next = resp.status_code == 405 and idx + 1 < len(endpoints)
                if retry_with_next:
                    continue

                if resp.status_code == 404:
                    return None

                if resp.status_code == 400:
                    payload = self._try_json(resp)
                    if self._arena_payload_has_code(
                        payload, 3011
                    ) or self._arena_payload_has_code(payload, 3017):
                        return None

                resp.raise_for_status()

                content_type = (resp.headers.get("Content-Type") or "").lower()
                extension = ".png"
                if "jpeg" in content_type or "jpg" in content_type:
                    extension = ".jpg"
                elif "gif" in content_type:
                    extension = ".gif"
                elif "bmp" in content_type:
                    extension = ".bmp"
                elif "image/" in content_type:
                    subtype = content_type.split("/", 1)[1]
                    subtype = subtype.split(";", 1)[0].strip()
                    if subtype:
                        extension = f".{subtype}"

                target_dir = Path(dest_dir) if dest_dir is not None else Path(".")
                target_dir.mkdir(parents=True, exist_ok=True)
                out_path = target_dir / f"{item_number}{extension}"

                with open(out_path, "wb") as fh:
                    for chunk in resp.iter_content(64 * 1024):
                        if not chunk:
                            continue
                        fh.write(chunk)
                return out_path
            finally:
                resp.close()
        return None

    def upload_file_to_working(
        self,
        item_number: str,
        file_path: Path,
        reference: Optional[str] = None,
        *,
        title: Optional[str] = None,
        category_name: str = "CAD Data",
        file_format: Optional[str] = None,
        description: Optional[str] = None,
        primary: bool = True,
        latest_edition_association: bool = True,
        edition: str = None,
    ) -> Dict:
        """
        Update-if-exists-else-create semantics:
          1) Resolve EFFECTIVE GUID from item number
          2) Resolve WORKING revision GUID (fail if none)
          3) Find existing file by title orexact filename (WORKING first, then EFFECTIVE)
             - If found: POST /files/{fileGuid}/content (multipart)
             - Else:     POST /items/{workingGuid}/files (multipart) with file.edition
        """
        return self._api_upload_or_update_file(
            item_number=item_number,
            file_path=file_path,
            reference=reference,
            title=title,
            category_name=category_name,
            file_format=file_format,
            description=description,
            primary=primary,
            latest_edition_association=latest_edition_association,
            edition=edition,
        )

    def get_bom(
        self,
        item_number: str,
        revision: Optional[str] = None,
        *,
        recursive: bool = False,
        max_depth: Optional[int] = None,
    ) -> List[Dict]:
        """
        Return a normalized list of BOM lines for the given item.

        By default this fetches the EFFECTIVE (approved) revision's BOM.
        Use revision="WORKING" or a specific label (e.g., "B2") to override.

        If recursive=True, expand subassemblies depth-first. max_depth limits the recursion
        depth (1 = only direct children). If omitted, recursion is unlimited.
        """
        selector = (revision or "EFFECTIVE").strip()
        out: List[Dict] = []
        self._bom_expand(
            root_item=item_number,
            selector=selector,
            out=out,
            recursive=recursive,
            max_depth=max_depth,
            _level=0,
            _seen=set(),
        )
        return out

    # === Internal: single fetch + normalization ===

    def _normalize_bom_rows(self, rows: List[Dict]) -> List[Dict]:
        norm: List[Dict] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            itm = row.get("item", {}) if isinstance(row, dict) else {}
            norm.append(
                {
                    # association/line
                    "guid": row.get("guid"),
                    "lineNumber": row.get("lineNumber"),
                    "notes": row.get("notes"),
                    "quantity": row.get("quantity"),
                    "refDes": row.get("refDes")
                    or row.get("referenceDesignators")
                    or "",
                    # child item
                    "itemGuid": itm.get("guid") or itm.get("id"),
                    "itemNumber": itm.get("number"),
                    "itemName": itm.get("name"),
                    "itemRevision": itm.get("revisionNumber"),
                    "itemRevisionStatus": itm.get("revisionStatus"),
                    "itemUrl": (itm.get("url") or {}).get("api"),
                    "itemAppUrl": (itm.get("url") or {}).get("app"),
                }
            )
        return norm

    def _api_get_bom_lines_by_revision_guid(self, revision_guid: str) -> List[Dict]:
        url = f"{self._api_base()}/items/{revision_guid}/bom"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        return self._normalize_bom_rows(rows)

    def _fetch_bom_normalized(self, item_number: str, selector: str) -> List[Dict]:
        """
        Fetch and normalize the BOM for item_number with the given revision selector.
        Falls back WORKING -> EFFECTIVE if selector is WORKING and no WORKING exists.
        """
        # 1) Resolve the exact revision GUID we want the BOM for
        try:
            target_guid = self._api_resolve_revision_guid(item_number, selector)
        except ArenaError:
            if selector.strip().upper() == "WORKING":
                # fallback: try EFFECTIVE for children that don't have a WORKING revision
                target_guid = self._api_resolve_revision_guid(item_number, "EFFECTIVE")
            else:
                raise

        # 2) GET /items/{guid}/bom
        url = f"{self._api_base()}/items/{target_guid}/bom"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)

        rows = data.get("results", data if isinstance(data, list) else [])
        return self._normalize_bom_rows(rows)

    def add_or_update_bom_line(
        self,
        *,
        parent_item_number: str,
        child_item_number: str,
        parent_revision: str = "WORKING",
        child_revision: Optional[str] = None,
        quantity: Optional[float] = None,
        ref_des: Optional[str] = None,
        notes: Optional[str] = None,
        additional_attributes: Optional[Mapping[str, object]] = None,
    ) -> Dict:
        if not parent_item_number or not parent_item_number.strip():
            raise ArenaError("parent_item_number is required")
        if not child_item_number or not child_item_number.strip():
            raise ArenaError("child_item_number is required")

        parent_number = parent_item_number.strip()
        child_number = child_item_number.strip()

        parent_selector = (parent_revision or "WORKING").strip() or "WORKING"
        parent_guid = self._api_resolve_revision_guid(parent_number, parent_selector)

        child_selector = (child_revision or "WORKING").strip() or "WORKING"
        try:
            child_guid = self._api_resolve_revision_guid(child_number, child_selector)
            resolved_child_selector = child_selector
        except ArenaError:
            if child_selector.upper() == "WORKING":
                child_guid = self._api_resolve_revision_guid(child_number, "EFFECTIVE")
                resolved_child_selector = "EFFECTIVE"
            else:
                raise

        qty_value: Optional[float] = None
        if quantity is not None:
            try:
                qty_value = float(quantity)
            except (TypeError, ValueError):
                raise ArenaError("quantity must be a number") from None
            if qty_value <= 0:
                raise ArenaError("quantity must be greater than zero")

        ref_des_value: Optional[str] = None
        if ref_des is not None:
            ref_des_value = str(ref_des).strip()

        notes_value: Optional[str] = None
        if notes is not None:
            notes_value = str(notes)

        attrs_payload: List[Dict[str, object]] = []
        if additional_attributes:
            for guid, value in additional_attributes.items():
                guid_str = str(guid).strip()
                if not guid_str:
                    continue
                attrs_payload.append({"guid": guid_str, "value": value})

        existing_lines = self._api_get_bom_lines_by_revision_guid(parent_guid)
        child_key = child_number.casefold()
        existing_line = None
        for line in existing_lines:
            num = str(line.get("itemNumber") or "").strip()
            if num and num.casefold() == child_key:
                existing_line = line
                break

        base_meta = {
            "parentRevisionGuid": parent_guid,
            "childRevisionGuid": child_guid,
            "childRevisionSelector": resolved_child_selector.upper(),
        }

        if existing_line is None:
            payload: Dict[str, object] = {
                "item": {"guid": child_guid},
                "quantity": qty_value if qty_value is not None else 1.0,
            }
            if ref_des is not None:
                payload["refDes"] = ref_des_value or ""
            if notes is not None:
                payload["notes"] = notes_value or ""
            if attrs_payload:
                payload["additionalAttributes"] = attrs_payload

            url = f"{self._api_base()}/items/{parent_guid}/bom"
            self._log(f"POST {url}")
            resp = self.session.post(url, json=payload)
            resp.raise_for_status()
            data = self._ensure_json(resp)
            return {
                **base_meta,
                "action": "created",
                "line": data,
            }

        line_guid = existing_line.get("guid")
        if not line_guid:
            raise ArenaError("Existing BOM line is missing a guid; cannot update.")

        payload = {}
        if qty_value is not None:
            payload["quantity"] = qty_value
        if ref_des is not None:
            payload["refDes"] = ref_des_value or ""
        if notes is not None:
            payload["notes"] = notes_value or ""
        if attrs_payload:
            payload["additionalAttributes"] = attrs_payload

        if not payload:
            raise ArenaError("No changes provided for existing BOM line.")

        url = f"{self._api_base()}/items/{parent_guid}/bom/{line_guid}"
        self._log(f"PUT {url}")
        resp = self.session.put(url, json=payload)
        resp.raise_for_status()
        data = self._ensure_json(resp)
        return {
            **base_meta,
            "action": "updated",
            "line": data,
            "bomLineGuid": line_guid,
        }

    # === Internal: recursive expansion ===

    def _bom_expand(
        self,
        *,
        root_item: str,
        selector: str,
        out: List[Dict],
        recursive: bool,
        max_depth: Optional[int],
        _level: int,
        _seen: set,
    ) -> None:
        # avoid cycles
        if root_item in _seen:
            return
        _seen.add(root_item)

        rows = self._fetch_bom_normalized(root_item, selector)

        # attach level and parentNumber (useful in JSON + for debugging)
        for r in rows:
            r["level"] = _level
            r["parentNumber"] = root_item
            out.append(r)

        if not recursive:
            return

        # depth check: if max_depth=1, only expand children once (level 0 -> level 1)
        if max_depth is not None and _level >= max_depth:
            return

        # expand each child that looks like an assembly (if it has a BOM; empty BOM is okay)
        for r in rows:
            child_num = r.get("itemNumber")
            if not child_num:
                continue
            try:
                # Recurse; keep same selector, with WORKING->EFFECTIVE fallback handled in _fetch_bom_normalized
                self._bom_expand(
                    root_item=child_num,
                    selector=selector,
                    out=out,
                    recursive=True,
                    max_depth=max_depth,
                    _level=_level + 1,
                    _seen=_seen,
                )
            except ArenaError:
                # Child might not have a BOM; skip silently
                continue

    def _api_get_latest_approved(self, item_number: str) -> str:
        item_guid = self._api_resolve_item_guid(item_number)
        url = f"{self._api_base()}/items/{item_guid}/revisions"
        self._log(f"GET {url}")
        r = self.session.get(url)
        if r.status_code == 404:
            raise ArenaError(f"Item {item_number} not found")
        r.raise_for_status()
        data = self._ensure_json(r)
        revs = data.get("results", data if isinstance(data, list) else [])
        if not isinstance(revs, list):
            raise ArenaError(f"Unexpected revisions payload for item {item_number}")

        # Arena marks the currently effective (approved) revision as:
        #   - revisionStatus == "EFFECTIVE"   (string)
        #   - OR status == 1                  (numeric)
        effective = [
            rv
            for rv in revs
            if (str(rv.get("revisionStatus") or "").upper() == "EFFECTIVE")
            or (rv.get("status") == 1)
        ]
        if not effective:
            raise ArenaError(f"No approved/released revisions for item {item_number}")

        # Prefer the one that is not superseded; otherwise fall back to the most recently superseded.
        current = next(
            (rv for rv in effective if not rv.get("supersededDateTime")), None
        )
        if not current:
            # sort by supersededDateTime (None last) then by number/name as a stable tie-breaker
            def _sd(rv):
                dt = rv.get("supersededDateTime")
                return dt or "0000-00-00T00:00:00Z"

            effective.sort(key=_sd)
            current = effective[-1]

        # The human-visible revision is under "number" (e.g., "B3"); fall back defensively.
        rev_label = (
            current.get("number") or current.get("name") or current.get("revision")
        )
        if not rev_label:
            raise ArenaError(
                f"Could not determine revision label for item {item_number}"
            )
        return rev_label

    def _api_list_files(self, item_number: str) -> List[Dict]:
        item_guid = self._api_resolve_item_guid(item_number)
        url = f"{self._api_base()}/items/{item_guid}/files"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        norm: List[Dict] = []
        for row in rows:
            f = row.get("file", {}) if isinstance(row, dict) else {}
            file_guid = f.get("guid") or f.get("id")
            norm.append(
                {
                    "id": row.get("guid") or row.get("id"),
                    "fileGuid": file_guid,
                    "name": f.get("name") or f.get("title"),
                    "title": f.get("title"),
                    "filename": f.get("name") or f.get("title"),
                    "size": f.get("size"),
                    "haveContent": f.get("haveContent", True),
                    "downloadUrl": (
                        f"{self._api_base()}/files/{file_guid}/content"
                        if file_guid
                        else None
                    ),
                    "edition": f.get("edition"),
                    "updatedAt": f.get("lastModifiedDateTime")
                    or f.get("lastModifiedDate")
                    or f.get("creationDateTime"),
                    "attachmentGroupGuid": row.get("guid"),
                }
            )
        return norm

    def _api_resolve_revision_guid(self, item_number: str, selector: str | None) -> str:
        """Return the item GUID for the requested revision selector."""
        # Resolve base item (effective) guid from number
        effective_guid = self._api_resolve_item_guid(item_number)

        # If no selector, we default to EFFECTIVE
        sel = (selector or "EFFECTIVE").strip().upper()

        # Fetch revisions
        url = f"{self._api_base()}/items/{effective_guid}/revisions"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        revs = data.get("results", data if isinstance(data, list) else [])

        def pick(pred):
            for rv in revs:
                if pred(rv):
                    return rv.get("guid")
            return None

        # Named selectors
        if sel in {"WORKING"}:
            guid = pick(
                lambda rv: (rv.get("revisionStatus") or "").upper() == "WORKING"
                or rv.get("status") == 0
            )
            if not guid:
                raise ArenaError("No WORKING revision exists for this item.")
            return guid

        if sel in {"EFFECTIVE", "APPROVED", "RELEASED"}:
            # Prefer the one not superseded
            eff = [
                rv
                for rv in revs
                if (rv.get("revisionStatus") or "").upper() == "EFFECTIVE"
                or rv.get("status") == 1
            ]
            if not eff:
                raise ArenaError(
                    "No approved/effective revision exists for this item. Try using revision 'WORKING'."
                )
            current = next(
                (rv for rv in eff if not rv.get("supersededDateTime")), eff[-1]
            )
            return current.get("guid")

        # Specific label (e.g., "A", "B2")
        guid = pick(
            lambda rv: (rv.get("number") or rv.get("name"))
            and str(rv.get("number") or rv.get("name")).upper() == sel
        )
        if not guid:
            raise ArenaError(f'Revision "{selector}" not found for item {item_number}.')
        return guid

    def _api_list_files_by_item_guid(self, item_guid: str) -> list[dict]:
        url = f"{self._api_base()}/items/{item_guid}/files"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        norm = []
        for row in rows:
            f = row.get("file", {}) if isinstance(row, dict) else {}
            file_guid = f.get("guid") or f.get("id")
            norm.append(
                {
                    "id": row.get("guid") or row.get("id"),
                    "fileGuid": file_guid,
                    "title": f.get("title"),
                    "name": f.get("name"),
                    "filename": f.get("name"),
                    "size": f.get("size"),
                    "haveContent": f.get("haveContent", True),
                    "downloadUrl": (
                        f"{self._api_base()}/files/{file_guid}/content"
                        if file_guid
                        else None
                    ),
                    "edition": f.get("edition"),
                    "updatedAt": f.get("lastModifiedDateTime")
                    or f.get("lastModifiedDate")
                    or f.get("creationDateTime"),
                    "attachmentGroupGuid": row.get("guid"),
                    "storageMethodName": (
                        f.get("storageMethodName") or f.get("storageMethod")
                    ),
                    "location": f.get("location"),
                }
            )
        return norm

    def _api_get_file_details(self, file_guid: str) -> dict:
        url = f"{self._api_base()}/files/{file_guid}"
        self._log(f"GET {url}")
        r = self.session.get(url)
        r.raise_for_status()
        return self._ensure_json(r)

    def _api_create_file_edition(
        self,
        *,
        file_guid: str,
        file_path: Path,
        edition: str,
        title: str,
        description: Optional[str],
        file_format: Optional[str],
        category_guid: Optional[str],
        private: bool,
    ):
        url = f"{self._api_base()}/files/{file_guid}/editions"
        self._log(f"POST {url} (create new edition)")
        data_form = {
            "file.title": title,
            "file.description": description or "",
            "file.edition": str(edition),
            "file.format": file_format
            or (file_path.suffix[1:].lower() if file_path.suffix else "bin"),
            "file.storageMethodName": "FILE",
            "file.private": "true" if private else "false",
        }
        if category_guid:
            data_form["file.category.guid"] = category_guid

        filename = file_path.name
        with open(file_path, "rb") as fp:
            files = {"content": (filename, fp, "application/octet-stream")}
            existing_ct = self.session.headers.pop("Content-Type", None)
            try:
                resp = self.session.post(url, data=data_form, files=files)
            finally:
                if existing_ct is not None:
                    self.session.headers["Content-Type"] = existing_ct
        resp.raise_for_status()
        payload = self._try_json(resp)
        if payload is not None:
            payload.setdefault("status", resp.status_code)
            return payload
        return {
            "status": resp.status_code,
            "fileGuid": resp.headers.get("X-Arena-FileGuid") or file_guid,
            "edition": str(edition),
        }

    def _api_create_web_file_edition(
        self,
        *,
        file_guid: str,
        title: str,
        location_url: str,
        edition: str,
        description: Optional[str],
        file_format: Optional[str],
        category_guid: Optional[str],
        private: bool,
    ) -> dict:
        url = f"{self._api_base()}/files/{file_guid}/editions"
        self._log(f"POST {url} (create new web edition)")
        payload = {
            "file": {
                "title": title,
                "description": description or "",
                "edition": str(edition),
                "format": file_format or "url",
                "storageMethodName": "WEB",
                "location": location_url,
                "private": bool(private),
            }
        }
        if category_guid:
            payload["file"]["category"] = {"guid": category_guid}

        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        data = self._try_json(resp)
        if data is not None:
            data.setdefault("status", resp.status_code)
            return data
        return {
            "status": resp.status_code,
            "guid": resp.headers.get("X-Arena-FileGuid") or file_guid,
        }

    def _api_upload_or_update_file(
        self,
        *,
        item_number: str,
        file_path: Path,
        reference: Optional[str],
        title: Optional[str],
        category_name: str,
        file_format: Optional[str],
        description: Optional[str],
        primary: bool,
        latest_edition_association: bool,
        edition: str,
    ) -> Dict:
        if not file_path.exists() or not file_path.is_file():
            raise ArenaError(f"File not found: {file_path}")

        filename = file_path.name  # Use truncated SHA256 hash if no edition is provided
        if not edition:
            # Arena seems to only accept 16 characters of edition information.
            # The hex digest gives 16 hex × 4 bits = 64 bits of entropy.
            # Less than a million files, collision risk is practically zero (~1 / 10^8).
            edition = sha256_file(file_path)
        edition = str(edition)[:16]

        # 0) Resolve EFFECTIVE revision guid from item number
        effective_guid = self._api_resolve_item_guid(item_number)

        # 1) Resolve WORKING revision guid
        revs_url = f"{self._api_base()}/items/{effective_guid}/revisions"
        self._log(f"GET {revs_url}")
        r = self.session.get(revs_url)
        r.raise_for_status()
        data = self._ensure_json(r)
        rows = data.get("results", data if isinstance(data, list) else [])
        working_guid = None
        for rv in rows:
            if (str(rv.get("revisionStatus") or "").upper() == "WORKING") or (
                rv.get("status") == 0
            ):
                working_guid = rv.get("guid")
                break
        if not working_guid:
            raise ArenaError(
                "No WORKING revision exists for this item. Create a working revision in Arena, then retry."
            )

        # Helper to list associations for a given item/revision guid
        def _list_assocs(item_guid: str) -> list:
            url = f"{self._api_base()}/items/{item_guid}/files"
            self._log(f"GET {url}")
            lr = self.session.get(url)
            lr.raise_for_status()
            payload = self._ensure_json(lr)
            return payload.get("results", payload if isinstance(payload, list) else [])

        # Try to find existing association by exact filename (WORKING first, then EFFECTIVE)
        filename = file_path.name
        assoc = None
        if title:
            candidates = _list_assocs(working_guid)

            def _a_title(a):
                f = a.get("file") or {}
                return (f.get("title") or a.get("title") or "").strip().casefold()

            tnorm = title.strip().casefold()
            # Prefer primary + latestEditionAssociation if duplicates exist
            preferred = [
                a
                for a in candidates
                if _a_title(a) == tnorm
                and a.get("primary")
                and a.get("latestEditionAssociation")
            ]
            if preferred:
                assoc = preferred[0]
            else:
                any_match = [a for a in candidates if _a_title(a) == tnorm]
                if any_match:
                    assoc = any_match[0]

        for guid in (working_guid, effective_guid):
            assocs = _list_assocs(guid)
            # prefer primary && latestEditionAssociation, then any by name
            prim_latest = [
                a
                for a in assocs
                if a.get("primary")
                and a.get("latestEditionAssociation")
                and ((a.get("file") or {}).get("name") == filename)
            ]
            if prim_latest:
                assoc = prim_latest[0]
                break
            any_by_name = [
                a for a in assocs if (a.get("file") or {}).get("name") == filename
            ]
            if any_by_name:
                assoc = any_by_name[0]
                break

        # If an existing file is found: update its content (new edition)
        if assoc:
            file_guid = (assoc.get("file") or {}).get("guid")
            if not file_guid:
                raise ArenaError("Existing association found but no file.guid present.")
            post_url = f"{self._api_base()}/files/{file_guid}/content"
            self._log(f"POST {post_url} (multipart content update)")

            def _fallback_category_name() -> Optional[str]:
                file_meta = assoc.get("file") or {}
                cat = file_meta.get("category") or {}
                return cat.get("name")

            try:
                with open(file_path, "rb") as fp:
                    files = {"content": (filename, fp, "application/octet-stream")}
                    existing_ct = self.session.headers.pop("Content-Type", None)
                    try:
                        ur = self.session.post(post_url, files=files)
                    finally:
                        if existing_ct is not None:
                            self.session.headers["Content-Type"] = existing_ct
                ur.raise_for_status()

                # Update the edition label on the File itself
                try:
                    put_url = f"{self._api_base()}/files/{file_guid}"
                    self._log(f"PUT {put_url} (set edition={edition})")
                    pr = self.session.put(put_url, json={"edition": str(edition)})
                    pr.raise_for_status()
                except requests.HTTPError as exc:
                    # Don't fail the whole operation if the label update is rejected
                    self._log(f"Edition update failed for {file_guid}: {exc}")

                # Many tenants return 201 with no JSON for content updates. Be flexible.
                data = self._try_json(ur)
                if data is None:
                    # Synthesize a small success payload with whatever we can glean.
                    return {
                        "ok": True,
                        "status": ur.status_code,
                        "fileGuid": file_guid,
                        "location": ur.headers.get("Location"),
                        "edition": str(edition),
                    }
                return data
            except requests.HTTPError as exc:
                resp = getattr(exc, "response", None)
                status = getattr(resp, "status_code", None)
                payload = self._try_json(resp) if resp is not None else None
                if status == 403:
                    self._log(
                        "Existing file content update rejected: "
                        f"payload={payload!r} status={status}"
                    )
                if status == 403 and self._arena_payload_has_code(payload, 3084):
                    self._log(
                        "Existing file edition locked; creating a new edition on the same file."
                    )
                    # Gather metadata for edition create (prefer explicit args, fall back to Arena data)
                    file_record = self._api_get_file_details(file_guid)
                    file_data = file_record if isinstance(file_record, dict) else {}
                    # Determine attributes with graceful fallbacks
                    edition_title = (
                        title
                        or (assoc.get("file") or {}).get("title")
                        or file_data.get("title")
                        or filename
                    )
                    edition_description = (
                        description
                        if description is not None
                        else file_data.get("description")
                    )
                    edition_format = (
                        file_format
                        or (assoc.get("file") or {}).get("format")
                        or file_data.get("format")
                        or (file_path.suffix[1:].lower() if file_path.suffix else "bin")
                    )
                    category_guid = (
                        ((file_data.get("category") or {}).get("guid"))
                        if isinstance(file_data.get("category"), dict)
                        else None
                    )
                    private_flag = bool(file_data.get("private", False))

                    edition_resp = self._api_create_file_edition(
                        file_guid=file_guid,
                        file_path=file_path,
                        edition=str(edition),
                        title=edition_title,
                        description=edition_description,
                        file_format=str(edition_format) if edition_format else None,
                        category_guid=category_guid,
                        private=private_flag,
                    )

                    # Normalize response (make sure edition info is surfaced)
                    download_url = f"{self._api_base()}/files/{file_guid}/content"
                    if isinstance(edition_resp, dict):
                        edition_resp.setdefault("fileGuid", file_guid)
                        edition_resp.setdefault("edition", str(edition))
                        edition_resp.setdefault("downloadUrl", download_url)
                        edition_resp.setdefault("ok", True)
                        return edition_resp
                    return {
                        "ok": True,
                        "status": getattr(edition_resp, "status_code", None),
                        "fileGuid": file_guid,
                        "edition": str(edition),
                        "downloadUrl": download_url,
                    }
                else:
                    raise

        # Else: create a new association on WORKING
        # 2) Resolve file category guid by name
        cat_guid = self._api_resolve_file_category_guid(category_name)

        # 3) Prepare multipart (create association)
        title = title or file_path.name
        file_format = file_format or (
            file_path.suffix[1:].lower() if file_path.suffix else "bin"
        )
        description = description or "Uploaded via gladiator"

        data_form = {
            "file.title": title,
            "file.description": description,
            "file.category.guid": cat_guid,
            "file.format": file_format,
            "file.edition": str(edition),
            "file.storageMethodName": "FILE",
            "file.private": "false",
            "primary": "true" if primary else "false",
            "latestEditionAssociation": (
                "true" if latest_edition_association else "false"
            ),
        }
        if reference:
            data_form["reference"] = reference

        post_url = f"{self._api_base()}/items/{working_guid}/files"
        self._log(f"POST {post_url} (multipart)")

        with open(file_path, "rb") as fp:
            files = {"content": (filename, fp, "application/octet-stream")}
            existing_ct = self.session.headers.pop("Content-Type", None)
            try:
                cr = self.session.post(post_url, data=data_form, files=files)
            finally:
                if existing_ct is not None:
                    self.session.headers["Content-Type"] = existing_ct
        cr.raise_for_status()
        resp = self._ensure_json(cr)

        # Normalize common fields we use elsewhere
        row = resp if isinstance(resp, dict) else {}
        f = row.get("file", {})

        # Ensure the edition label is exactly what we asked for (some tenants ignore form edition)
        try:
            file_guid_created = (f or {}).get("guid")
            if file_guid_created and str(edition):
                put_url = f"{self._api_base()}/files/{file_guid_created}"
                self._log(f"PUT {put_url} (set edition={edition})")
                pr = self.session.put(put_url, json={"edition": str(edition)})
                pr.raise_for_status()
                # Update local 'f' edition if the PUT succeeded
                f["edition"] = str(edition)
        except requests.HTTPError as exc:
            self._log(
                f"Edition update after create failed for {file_guid_created}: {exc}"
            )

        return {
            "associationGuid": row.get("guid"),
            "primary": row.get("primary"),
            "latestEditionAssociation": row.get("latestEditionAssociation"),
            "file": {
                "guid": f.get("guid"),
                "title": f.get("title"),
                "name": f.get("name"),
                "size": f.get("size"),
                "format": f.get("format"),
                "category": (f.get("category") or {}).get("name"),
                "edition": f.get("edition") or str(edition),
                "lastModifiedDateTime": f.get("lastModifiedDateTime"),
            },
            "downloadUrl": (
                f"{self._api_base()}/files/{(f or {}).get('guid')}/content"
                if f.get("guid")
                else None
            ),
        }

    def _api_resolve_item_guid(self, item_number: str) -> str:
        url = f"{self._api_base()}/items/"
        params = {"number": item_number, "limit": 1, "responseview": "minimal"}
        self._log(f"GET {url} params={params}")
        r = self.session.get(url, params=params)
        r.raise_for_status()
        data = self._ensure_json(r)
        results = data.get("results") if isinstance(data, dict) else data
        if not results:
            raise ArenaError(f"Item number {item_number} not found")
        guid = (
            results[0].get("guid") or results[0].get("id") or results[0].get("itemId")
        )
        if not guid:
            raise ArenaError("API response missing item GUID")
        return guid

    def _api_resolve_file_category_guid(self, category_name: str) -> str:
        cats_url = f"{self._api_base()}/settings/files/categories"
        self._log(f"GET {cats_url}")
        r = self.session.get(cats_url)
        r.raise_for_status()
        cats = self._ensure_json(r).get("results", [])
        for c in cats:
            if c.get("name") == category_name:
                return c.get("guid")
        raise ArenaError(f'File category "{category_name}" not found.')

    def _api_create_web_file(
        self,
        *,
        category_guid: str,
        title: str,
        location_url: str,
        edition: str,
        description: Optional[str],
        file_format: Optional[str],
        private: bool = False,
    ) -> dict:
        """
        POST /files  (create File record with storageMethodName=WEB and a 'location')
        """
        url = f"{self._api_base()}/files"
        payload = {
            "category": {"guid": category_guid},
            "title": title,
            "description": description or "",
            "edition": str(edition),
            "format": file_format or "url",
            "private": bool(private),
            "storageMethodName": "WEB",
            "location": location_url,
        }
        self._log(f"POST {url} (create web file)")
        r = self.session.post(url, json=payload)
        r.raise_for_status()
        data = self._ensure_json(r)
        if not isinstance(data, dict) or not data.get("guid"):
            raise ArenaError("File create (WEB) returned no GUID")
        return data  # includes "guid", "number", etc.

    def _api_update_web_file(
        self,
        *,
        file_guid: str,
        category_guid: str,
        title: str,
        location_url: str,
        edition: str,
        description: Optional[str],
        file_format: Optional[str],
        private: bool = False,
    ) -> dict:
        """
        PUT /files/{guid} (update summary). For WEB/FTP/PLACE_HOLDER, include 'location'.
        """
        url = f"{self._api_base()}/files/{file_guid}"
        payload = {
            "category": {"guid": category_guid},
            "title": title,
            "description": description or "",
            "edition": str(edition),
            "format": file_format or "url",
            "private": bool(private),
            "storageMethodName": "WEB",
            "location": location_url,
        }
        self._log(f"PUT {url} (update web file)")
        r = self.session.put(url, json=payload)
        r.raise_for_status()
        return self._ensure_json(r)

    def _api_item_add_existing_file(
        self,
        *,
        item_guid: str,
        file_guid: str,
        primary: bool,
        latest_edition_association: bool,
        reference: Optional[str] = None,
    ) -> dict:
        url = f"{self._api_base()}/items/{item_guid}/files"
        payload = {
            "primary": bool(primary),
            "latestEditionAssociation": bool(latest_edition_association),
            "file": {"guid": file_guid},
        }
        if reference:
            payload["reference"] = reference
        r = self.session.post(url, json=payload)
        r.raise_for_status()
        return self._ensure_json(r)

    def upload_weblink_to_working(
        self,
        *,
        item_number: str,
        url: str,
        reference: Optional[str] = None,
        title: str,
        category_name: str = "Web Link",
        file_format: Optional[str] = "url",
        description: Optional[str] = None,
        primary: bool = True,
        latest_edition_association: bool = True,
        edition: Optional[str] = None,
    ) -> Dict:
        """
        Idempotent "upsert" of a WEB-link File on the WORKING revision of `item_number`.

        Match rules (WORKING first, then EFFECTIVE):
          - any association whose File has storageMethodName in {"WEB","FTP"} AND
            (File.title == title OR File.location == url)

        If found -> PUT /files/{fileGuid} with storageMethodName=WEB + location + edition.
        Else      -> POST /files (create) + POST /items/{workingGuid}/files (add existing).
        """
        # Compute an edition if none is provided (SHA256 of the URL, truncated to 16)
        if not edition:
            edition = hashlib.sha256(url.encode("utf-8")).hexdigest()
        edition = str(edition)[:16]

        # Resolve item GUIDs
        effective_guid = self._api_resolve_item_guid(item_number)
        revs_url = f"{self._api_base()}/items/{effective_guid}/revisions"
        self._log(f"GET {revs_url}")
        r = self.session.get(revs_url)
        r.raise_for_status()
        revs = self._ensure_json(r).get("results", [])
        working_guid = None
        for rv in revs:
            if (str(rv.get("revisionStatus") or "").upper() == "WORKING") or (
                rv.get("status") == 0
            ):
                working_guid = rv.get("guid")
                break
        if not working_guid:
            raise ArenaError(
                "No WORKING revision exists for this item. Create a working revision in Arena, then retry."
            )

        # Resolve category GUID
        cat_guid = self._api_resolve_file_category_guid(category_name)

        # Helper to list associations for a given item/revision guid
        def _list_assocs(guid: str) -> list[dict]:
            url2 = f"{self._api_base()}/items/{guid}/files"
            self._log(f"GET {url2}")
            lr = self.session.get(url2)
            lr.raise_for_status()
            payload = self._ensure_json(lr)
            return payload.get("results", payload if isinstance(payload, list) else [])

        # Try to find an existing WEB/FTP style file by title or URL
        def _pick_assoc_by_title_or_url(assocs: list[dict]) -> Optional[dict]:
            pick = None
            for a in assocs:
                f = a.get("file") or {}
                smn = str(
                    f.get("storageMethodName") or f.get("storageMethod") or ""
                ).upper()
                if smn not in {"WEB", "FTP"}:
                    continue
                f_title = (f.get("title") or "").strip()
                f_loc = (f.get("location") or "").strip()
                if (f_title and f_title == title) or (f_loc and f_loc == url):
                    if not pick:
                        pick = a
                        continue
                    # prefer latestEditionAssociation + primary
                    if (
                        a.get("latestEditionAssociation") and a.get("primary")
                    ) and not (
                        pick.get("latestEditionAssociation") and pick.get("primary")
                    ):
                        pick = a
            return pick

        assoc = _pick_assoc_by_title_or_url(
            _list_assocs(working_guid)
        ) or _pick_assoc_by_title_or_url(_list_assocs(effective_guid))

        # If found: update the File summary (ensures storageMethodName=WEB + new location/edition)
        if assoc:
            file_guid = (assoc.get("file") or {}).get("guid")
            if not file_guid:
                raise ArenaError(
                    "Existing web-link association found but missing file.guid"
                )
            try:
                updated = self._api_update_web_file(
                    file_guid=file_guid,
                    category_guid=cat_guid,
                    title=title,
                    location_url=url,
                    edition=str(edition),
                    description=description,
                    file_format=file_format,
                    private=False,
                )
                # Normalize to a consistent response
                return {
                    "ok": True,
                    "action": "updated",
                    "file": {
                        "guid": updated.get("guid"),
                        "number": updated.get("number"),
                        "title": updated.get("title"),
                        "edition": updated.get("edition"),
                        "storageMethodName": updated.get("storageMethodName"),
                        "location": updated.get("location"),
                    },
                    "associationGuid": assoc.get("guid"),
                    "primary": assoc.get("primary"),
                    "latestEditionAssociation": assoc.get("latestEditionAssociation"),
                }
            except requests.HTTPError as exc:
                resp = getattr(exc, "response", None)
                status = getattr(resp, "status_code", None)
                payload = self._try_json(resp) if resp is not None else None
                if status in (400, 403) and (
                    self._arena_payload_has_code(payload, 3084)
                    or self._arena_payload_has_code(payload, 3030)
                ):
                    self._log(
                        "Existing web-link edition locked; creating a new edition on the same file."
                    )
                    file_record = self._api_get_file_details(file_guid)
                    file_data = file_record if isinstance(file_record, dict) else {}
                    edition_title = (
                        title
                        or (assoc.get("file") or {}).get("title")
                        or file_data.get("title")
                        or ""
                    )
                    edition_description = (
                        description
                        if description is not None
                        else file_data.get("description")
                    )
                    edition_format = (
                        file_format
                        or (assoc.get("file") or {}).get("format")
                        or file_data.get("format")
                        or "url"
                    )
                    edition_category_guid = cat_guid or (
                        (file_data.get("category") or {}).get("guid")
                        if isinstance(file_data.get("category"), dict)
                        else None
                    )
                    edition_private = bool(file_data.get("private", False))

                    edition_resp = self._api_create_web_file_edition(
                        file_guid=file_guid,
                        title=edition_title or title,
                        location_url=url,
                        edition=str(edition),
                        description=edition_description,
                        file_format=edition_format,
                        category_guid=edition_category_guid,
                        private=edition_private,
                    )

                    payload_source = (
                        edition_resp.get("file")
                        if isinstance(edition_resp, dict)
                        and isinstance(edition_resp.get("file"), dict)
                        else edition_resp
                    )

                    def _get(key: str, default=None):
                        return (
                            payload_source.get(key, default)
                            if isinstance(payload_source, dict)
                            else default
                        )

                    return {
                        "ok": True,
                        "action": "updated",
                        "file": {
                            "guid": file_guid,
                            "number": _get("number"),
                            "title": _get("title", edition_title or title),
                            "edition": _get("edition", str(edition)),
                            "storageMethodName": _get("storageMethodName", "WEB"),
                            "location": _get("location", url),
                        },
                        "associationGuid": assoc.get("guid"),
                        "primary": assoc.get("primary"),
                        "latestEditionAssociation": assoc.get(
                            "latestEditionAssociation"
                        ),
                    }
                raise

        # Else: create a new WEB file, then associate it on WORKING
        created = self._api_create_web_file(
            category_guid=cat_guid,
            title=title,
            location_url=url,
            edition=str(edition),
            description=description,
            file_format=file_format,
            private=False,
        )
        file_guid = created.get("guid")
        assoc_resp = self._api_item_add_existing_file(
            item_guid=working_guid,
            file_guid=file_guid,
            primary=primary,
            latest_edition_association=latest_edition_association,
            reference=reference,
        )

        return {
            "ok": True,
            "action": "created",
            "associationGuid": assoc_resp.get("guid"),
            "primary": assoc_resp.get("primary"),
            "latestEditionAssociation": assoc_resp.get("latestEditionAssociation"),
            "file": {
                "guid": file_guid,
                "number": created.get("number"),
                "title": created.get("title"),
                "edition": created.get("edition"),
                "storageMethodName": created.get("storageMethodName") or "WEB",
                "location": created.get("location") or url,
            },
        }


__all__ = ["ItemClient"]
