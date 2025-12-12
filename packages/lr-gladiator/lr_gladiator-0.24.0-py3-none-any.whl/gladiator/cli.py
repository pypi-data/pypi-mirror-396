#! /usr/bin/env python
# -*- coding: utf-8 -*-
# src/gladiator/cli.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import typer
from rich import print
from rich.table import Table
from rich.console import Console
from rich.status import Status
from getpass import getpass
import requests
import sys
import os
from urllib.parse import urlparse
from .config import LoginConfig, save_config, load_config, save_config_raw, CONFIG_PATH
from .arena import ArenaClient, ArenaError, ChangeClient

app = typer.Typer(add_completion=False, help="Arena PLM command-line utility")
console = Console()

# --- tiny helper to show a spinner when appropriate ---
from contextlib import contextmanager


@contextmanager
def spinner(message: str, enabled: bool = True):
    """
    Show a Rich spinner while the body executes.
    Auto-disables if stdout is not a TTY (e.g., CI) or enabled=False.
    """
    if enabled and sys.stdout.isatty():
        with console.status(message, spinner="dots"):
            yield
    else:
        yield


def _build_change_items_table(change_id: str, rows: list[dict]) -> Table:
    table = Table(title=f"Affected items for {change_id}")
    table.add_column("Item Number")
    table.add_column("Affected Rev")
    table.add_column("New Rev")
    table.add_column("Disposition")
    table.add_column("Notes")
    table.add_column("BOM", justify="center")
    table.add_column("Specs", justify="center")
    table.add_column("Files", justify="center")
    table.add_column("Source", justify="center")
    table.add_column("Cost", justify="center")

    for row in rows:
        affected = row.get("affectedItemRevision") or {}
        new_rev = row.get("newItemRevision") or {}
        dispositions = row.get("dispositionAttributes") or []
        disp_summary = ", ".join(
            f"{d.get('name')}: {d.get('value')}"
            for d in dispositions
            if d.get("value") is not None
        )
        views = {
            "BOM": row.get("bomView") or {},
            "Specs": row.get("specsView") or {},
            "Files": row.get("filesView") or {},
            "Source": row.get("sourcingView") or {},
            "Cost": row.get("costView") or {},
        }
        flags = [
            "*" if view.get("includedInThisChange") else "" for view in views.values()
        ]
        table.add_row(
            str(affected.get("number") or new_rev.get("number") or ""),
            str(affected.get("revisionNumber") or ""),
            str(row.get("newRevisionNumber") or new_rev.get("revisionNumber") or ""),
            disp_summary or "",
            str(row.get("notes") or ""),
            *flags,
        )
    return table


MAX_EDITION_LENGTH = 16


def _truncate_edition(value: Optional[str]) -> Optional[str]:
    """Clamp edition strings to Arena's 16-character limit."""
    if value is None:
        return None
    return str(value)[:MAX_EDITION_LENGTH]


def _print_json(data: object) -> None:
    """Write JSON to stdout without Rich formatting."""
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _normalize_revision_selector(value: Optional[str]) -> Optional[str]:
    """Return a trimmed revision selector or None for sentinel values."""
    if value is None:
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    if trimmed.casefold() in {"null", "none"}:
        return None
    return trimmed


def _format_http_error(err: requests.HTTPError) -> str:
    resp = getattr(err, "response", None)
    if resp is None:
        return str(err)

    snippet = ""
    try:
        data = resp.json()
    except Exception:
        body = (resp.text or "").strip()
        if body:
            snippet = " ".join(body.split())
    else:
        if isinstance(data, dict):
            keys = ("message", "error", "detail", "errors", "description")
            for key in keys:
                if key not in data:
                    continue
                value = data[key]
                if isinstance(value, (list, tuple)):
                    snippet = "; ".join(str(item) for item in value if item)
                elif value is not None:
                    snippet = str(value)
                if snippet:
                    break
            if not snippet:
                snippet = json.dumps(data)
        else:
            snippet = json.dumps(data)

    if snippet:
        snippet = snippet[:400]
        return f"{err} Body: {snippet}"
    return str(err)


@app.command()
def login(
    username: Optional[str] = typer.Option(
        None, "--username", envvar="GLADIATOR_USERNAME"
    ),
    password: Optional[str] = typer.Option(
        None, "--password", envvar="GLADIATOR_PASSWORD"
    ),
    base_url: Optional[str] = typer.Option(
        "https://api.arenasolutions.com/v1", help="Arena API base URL"
    ),
    verify_tls: bool = typer.Option(True, help="Verify TLS certificates"),
    non_interactive: bool = typer.Option(
        False, "--ci", help="Fail instead of prompting for missing values"
    ),
    reason: Optional[str] = typer.Option(
        "CI/CD integration", help="Arena-Usage-Reason header"
    ),
):
    """Create or update ~/.config/gladiator/login.json for subsequent commands."""
    if not username and not non_interactive:
        username = typer.prompt("Email/username")
    if not password and not non_interactive:
        password = getpass("Password: ")
    if non_interactive and (not username or not password):
        raise typer.BadParameter(
            "Provide --username and --password (or set env vars) for --ci mode"
        )

    # Perform login
    sess = requests.Session()
    sess.verify = verify_tls
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Arena-Usage-Reason": reason or "gladiator/cli",
        "User-Agent": "gladiator-arena/0.1",
    }
    url = f"{(base_url or '').rstrip('/')}/login"
    try:
        with spinner("Logging in…", enabled=sys.stdout.isatty()):
            resp = sess.post(
                url, headers=headers, json={"email": username, "password": password}
            )
            resp.raise_for_status()
    except Exception as e:
        typer.secho(
            f"Login failed: {e} Body: {getattr(resp, 'text', '')[:400]}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)

    data = resp.json()
    data.update({"base_url": base_url, "verify_tls": verify_tls, "reason": reason})
    save_config_raw(data)
    print(f"[green]Saved session to {CONFIG_PATH}[/green]")


def _client() -> ArenaClient:
    cfg = load_config()
    return ArenaClient(cfg)


def _change_client() -> ChangeClient:
    cfg = load_config()
    return ChangeClient(cfg)


@app.command("latest-approved")
def latest_approved(
    item: str = typer.Argument(..., help="Item/article number"),
    format: Optional[str] = typer.Option(
        None, "--format", "-f", help="Output format: human (default) or json"
    ),
):
    """Print latest approved revision for the given item number."""
    json_mode = (format or "").lower() == "json"
    try:
        with spinner(
            f"Resolving latest approved revision for {item}…", enabled=not json_mode
        ):
            rev = _client().get_latest_approved_revision(item)
        if json_mode:
            json.dump({"article": item, "revision": rev}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(rev)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        message = str(e)
        missing = "No approved/released revisions for item" in message
        if missing:
            if json_mode:
                json.dump(
                    {"article": item, "revision": None, "status": "missing"},
                    sys.stdout,
                    indent=2,
                )
                sys.stdout.write("\n")
                typer.secho(message, fg=typer.colors.YELLOW, err=True)
            else:
                typer.secho(message, fg=typer.colors.YELLOW)
            return
        typer.secho(message, fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("list-files")
def list_files(
    item: str = typer.Argument(..., help="Item/article number"),
    revision: Optional[str] = typer.Option(
        None,
        "--rev",
        help="Revision selector: WORKING | EFFECTIVE | <label> (default: EFFECTIVE)",
    ),
    format: Optional[str] = typer.Option(
        None, "--format", "-f", help="Output format: human (default) or json"
    ),
):
    """List files of an item."""
    json_mode = (format or "").lower() == "json"
    try:
        with spinner(
            f"Listing files for {item} ({revision or 'EFFECTIVE'})…",
            enabled=not json_mode,
        ):
            files = _client().list_files(item, revision)

        if json_mode:
            json.dump(
                {"article": item, "revision": revision, "files": files},
                sys.stdout,
                indent=2,
            )
            sys.stdout.write("\n")
            return

        table = Table(title=f"Files for {item} rev {revision or '(latest approved)'}")
        table.add_column("Title")
        table.add_column("Filename")
        table.add_column("Size", justify="right")
        table.add_column("Edition")
        table.add_column("Type")
        table.add_column("Location")
        for f in files:
            table.add_row(
                str(f.get("title")),
                str(f.get("name")),
                str(f.get("size")),
                str(f.get("edition")),
                str(f.get("storageMethodName") or ""),
                str(f.get("location") or ""),
            )
        print(table)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("info")
def info(
    item: str = typer.Argument(..., help="Item/article number"),
    revision: Optional[str] = typer.Option(
        None,
        "--rev",
        help="Revision selector: WORKING | EFFECTIVE | <label> (default: EFFECTIVE)",
    ),
    format: Optional[str] = typer.Option(
        None, "--format", "-f", help="Output format: human (default) or json"
    ),
    picture: bool = typer.Option(
        False,
        "--picture/--no-picture",
        help="Download the item's picture to <article>.png/jpg and include its path",
    ),
):
    """Display a concise summary for an item revision."""
    json_mode = (format or "").lower() == "json"
    selector = _normalize_revision_selector(revision)
    selector_label = selector or "EFFECTIVE"
    client = _client()
    picture_path: Optional[Path] = None
    try:
        with spinner(
            f"Fetching summary for {item} ({selector_label})…", enabled=not json_mode
        ):
            summary = client.get_item_summary(item, selector)
            if picture:
                picture_path = client.download_item_picture(
                    item,
                    selector,
                    dest_dir=Path("."),
                )

        summary = summary or {}
        if picture:
            summary["picturePath"] = str(picture_path) if picture_path else None

        if json_mode:
            payload = dict(summary or {})
            payload.setdefault("selector", selector_label)
            _print_json(payload)
            return

        table = Table(title=f"Item {summary.get('number') or item}")
        table.add_column("Field")
        table.add_column("Value")

        rows = [
            ("Item Number", summary.get("number") or item),
            ("Revision", summary.get("revision") or selector_label),
            ("Item Name", summary.get("name") or ""),
            ("Description", summary.get("description") or ""),
            ("Category", summary.get("category") or ""),
        ]

        lifecycle = summary.get("lifecyclePhase")
        if lifecycle:
            rows.append(("Lifecycle Phase", lifecycle))

        rev_status = summary.get("revisionStatus")
        if rev_status:
            rows.append(("Revision Status", rev_status))

        if picture:
            rows.append(
                (
                    "Picture Path",
                    str(picture_path) if picture_path else "Not available",
                )
            )

        for label, value in rows:
            table.add_row(label, str(value or ""))

        print(table)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("get-bom")
def get_bom(
    item: str = typer.Argument(..., help="Item/article number (e.g., 890-1001)"),
    revision: Optional[str] = typer.Option(
        None,
        "--rev",
        help='Revision selector: WORKING, EFFECTIVE (default), or label (e.g., "B2")',
    ),
    output: str = typer.Option(
        "table", "--output", help='Output format: "table" (default) or "json"'
    ),
    recursive: bool = typer.Option(
        False, "--recursive/--no-recursive", help="Recursively expand subassemblies"
    ),
    max_depth: Optional[int] = typer.Option(
        None,
        "--max-depth",
        min=1,
        help="Maximum recursion depth (1 = only children). Omit for unlimited.",
    ),
):
    """List the BOM lines for an item."""
    json_mode = output.lower() == "json"
    try:
        with spinner(
            f"Fetching BOM for {item} ({revision or 'EFFECTIVE'})"
            + (" [recursive]" if recursive else "")
            + "…",
            enabled=not json_mode,
        ):
            lines = _client().get_bom(
                item, revision, recursive=recursive, max_depth=max_depth
            )

        if json_mode:
            _print_json({"count": len(lines), "results": lines})
            return

        title_rev = revision or "(latest approved)"
        table = Table(title=f"BOM for {item} rev {title_rev}")
        table.add_column("Line", justify="right")
        table.add_column("Qty", justify="right")
        table.add_column("Number")
        table.add_column("Name")
        table.add_column("RefDes")

        for ln in lines:
            lvl = int(ln.get("level", 0) or 0)
            indent = "  " * lvl
            table.add_row(
                str(ln.get("lineNumber") or ""),
                str(ln.get("quantity") or ""),
                str(ln.get("itemNumber") or ""),
                f"{indent}{str(ln.get('itemName') or '')}",
                str(ln.get("refDes") or ""),
            )
        print(table)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("add-to-bom")
def add_to_bom(
    parent: str = typer.Argument(..., help="Parent assembly item number"),
    child: str = typer.Argument(..., help="Child item number to add or update"),
    quantity: Optional[float] = typer.Option(
        None,
        "--qty",
        "-q",
        help="Quantity to set (default 1 when creating; unchanged when omitted)",
    ),
    parent_revision: str = typer.Option(
        "WORKING",
        "--parent-rev",
        help="Parent revision selector (default: WORKING)",
    ),
    child_revision: Optional[str] = typer.Option(
        None,
        "--child-rev",
        help="Child revision selector (default: WORKING with EFFECTIVE fallback)",
    ),
    refdes: Optional[str] = typer.Option(
        None,
        "--refdes",
        help="Reference designator(s) to apply",
    ),
    notes: Optional[str] = typer.Option(
        None,
        "--notes",
        help="BOM line notes",
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json or human-readable summary (default)",
    ),
):
    """Add or update a BOM line on a parent assembly."""
    json_mode = (format or "").lower() == "json"
    try:
        with spinner(
            f"Updating BOM for {parent} ({parent_revision or 'WORKING'})…",
            enabled=not json_mode,
        ):
            result = _client().add_or_update_bom_line(
                parent_item_number=parent,
                child_item_number=child,
                parent_revision=parent_revision,
                child_revision=child_revision,
                quantity=quantity,
                ref_des=refdes,
                notes=notes,
            )

        if json_mode:
            json.dump(result, sys.stdout, indent=2)
            sys.stdout.write("\n")
            return

        action = result.get("action") or "updated"
        line = result.get("line") or {}
        line_item = line.get("item") or {}
        child_number = line_item.get("number") or line.get("itemNumber") or child
        qty_value = line.get("quantity")
        if qty_value is None and quantity is not None:
            qty_value = quantity
        refdes_value = line.get("refDes")
        notes_value = line.get("notes")

        message = f"[green]BOM line {action}[/green] for {child_number}"
        if qty_value is not None:
            message += f" (qty {qty_value})"
        if refdes_value:
            message += f" refdes: {refdes_value}"
        if notes_value:
            message += f" notes: {notes_value}"
        print(message)

    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("get-files")
def get_files(
    item: str = typer.Argument(..., help="Item/article number"),
    revision: Optional[str] = typer.Option(
        None, "--rev", help="Revision (default: latest approved)"
    ),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        help="Output directory (default: a folder named after the item number)",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive/--no-recursive",
        help="Recursively download files from subassemblies",
    ),
    max_depth: Optional[int] = typer.Option(
        None,
        "--max-depth",
        min=1,
        help="Maximum recursion depth for --recursive (1 = only direct children).",
    ),
):
    """Download files for an item."""
    json_mode = False  # this command prints file paths line-by-line (no JSON mode here)
    try:
        out_dir = out or Path(item)
        with spinner(
            f"Downloading files for {item} ({revision or 'EFFECTIVE'})"
            + (" [recursive]" if recursive else "")
            + f" → {out_dir}…",
            enabled=not json_mode,
        ):
            if recursive:
                paths = _client().download_files_recursive(
                    item, revision, out_dir=out_dir, max_depth=max_depth
                )
            else:
                paths = _client().download_files(item, revision, out_dir=out_dir)

        for p in paths:
            print(str(p))
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("create-change")
def create_change(
    category_name: str = typer.Option(
        "Engineering Change Order",
        "--category",
        help=(
            "Change category name (default: 'Engineering Change Order'). "
            "Examples: 'Documentation Change Order', 'Engineering Change Order'."
        ),
    ),
    title: str = typer.Option(..., "--title", help="Change title"),
    description: Optional[str] = typer.Option(
        None, "--description", help="Optional change description"
    ),
    effectivity_type: str = typer.Option(
        "PERMANENT_ON_APPROVAL",
        "--effectivity-type",
        help="Effectivity type: PERMANENT_ON_APPROVAL, PERMANENT_ON_DATE, TEMPORARY",
    ),
    planned_date: Optional[str] = typer.Option(
        None,
        "--planned-date",
        help="Planned effectivity timestamp (required for PERMANENT_ON_DATE)",
    ),
    expiration_date: Optional[str] = typer.Option(
        None,
        "--expiration-date",
        help="Expiration timestamp (required for TEMPORARY)",
    ),
    approval_deadline: Optional[str] = typer.Option(
        None,
        "--approval-deadline",
        help="Optional approval deadline timestamp",
    ),
    enforce_deadline: bool = typer.Option(
        False,
        "--enforce-deadline/--no-enforce-deadline",
        help="Toggle enforceApprovalDeadline flag",
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json (raw response) or table (default)",
    ),
):
    """Create a change order."""
    client = _change_client()
    try:
        category_guid = client.resolve_change_category_guid(category_name)
        with spinner(
            f"Creating change {title}…",
            enabled=sys.stdout.isatty(),
        ):
            result = client.create_change(
                category_guid=category_guid,
                title=title,
                description=description,
                effectivity_type=effectivity_type,
                planned_effectivity=planned_date,
                expiration_date=expiration_date,
                approval_deadline=approval_deadline,
                enforce_approval_deadline=enforce_deadline,
            )
        if (format or "").lower() == "json":
            _print_json(result)
        else:
            table = Table(title="Created change")
            table.add_column("Number")
            table.add_column("Title")
            table.add_column("Category")
            change_number = str(result.get("number") or "")
            change_title = str(result.get("title") or title)
            category_label = str(
                (result.get("category") or {}).get("name") or category_name
            )
            table.add_row(
                change_number,
                change_title,
                category_label,
            )
            print(table)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("get-change")
def get_change(
    change_id: str = typer.Argument(..., help="Change ID (e.g. CCO-000003)"),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json (raw response) or table (default)",
    ),
):
    """Show affected items for a change order."""
    client = _change_client()
    try:
        with spinner(
            f"Fetching change {change_id}…",
            enabled=sys.stdout.isatty(),
        ):
            result = client.get_change_items(change_number=change_id)
        if (format or "").lower() == "json":
            _print_json(result)
        else:
            rows = result.get("results") or []
            table = _build_change_items_table(change_id, rows)
            print(table)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("add-to-change")
def add_to_change(
    item_number: str = typer.Argument(..., help="Item/article number to add"),
    change_id: str = typer.Option(
        ...,
        "--change",
        "--change-id",
        help="Change ID (e.g. CCO-000003) that will receive the item",
    ),
    new_revision: Optional[str] = typer.Option(
        None,
        "--new-revision",
        help="Override the new revision label that will be created on the change",
    ),
    lifecycle_phase: Optional[str] = typer.Option(
        "In Production",
        "--lifecycle-phase",
        help="Lifecycle phase to assign to the new revision. Abandoned, Deprecated, In Design, In Production, Obsolete, Unreleased (default: 'In Production')",
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json (raw add response) or table (default)",
    ),
):
    """Add an item to a change order."""
    client = _change_client()
    try:
        with spinner(
            f"Adding {item_number} to change {change_id}…",
            enabled=sys.stdout.isatty(),
        ):
            result = client.add_item_to_change(
                change_number=change_id,
                item_number=item_number,
                new_revision=new_revision,
                lifecycle_phase=lifecycle_phase,
            )
        if (format or "").lower() == "json":
            _print_json(result)
        else:
            change_snapshot = client.get_change_items(change_number=change_id)
            rows = change_snapshot.get("results") or []
            table = _build_change_items_table(change_id, rows)
            print(table)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("submit-change")
def submit_change(
    change_id: str = typer.Argument(..., help="Change ID (e.g. ECO-000123)"),
    status: str = typer.Option(
        "SUBMITTED",
        "--status",
        help="Target status to set on the change (default: SUBMITTED)",
    ),
    comment: Optional[str] = typer.Option(
        None,
        "--comment",
        "-c",
        help="Optional submission comment",
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: json (raw response) or text (default)",
    ),
):
    """Submit or update the workflow status of a change order."""
    client = _change_client()
    try:
        with spinner(
            f"Submitting change {change_id} to status {status or 'SUBMITTED'}…",
            enabled=sys.stdout.isatty(),
        ):
            result = client.submit_change(
                change_number=change_id,
                status=status,
                comment=comment,
                administrators=None,
            )
        if (format or "").lower() == "json":
            _print_json(result)
        else:
            change_number = str(result.get("change", {}).get("number") or change_id)
            new_status = str(result.get("status") or (status or "").strip().upper())
            message = f"Change {change_number} status set to {new_status}"
            if comment:
                message += f" (comment: {comment})"
            print(f"[green]{message}[/green]")
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("upload-file")
def upload_file(
    item: str = typer.Argument(...),
    file: Path = typer.Argument(...),
    reference: Optional[str] = typer.Option(
        None, "--reference", help="Optional reference string"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Override file title (default: filename without extension)",
    ),
    category: str = typer.Option(
        "Firmware", "--category", help='File category name (default: "Firmware")'
    ),
    file_format: Optional[str] = typer.Option(
        None, "--format", help="File format (default: file extension)"
    ),
    description: Optional[str] = typer.Option(
        None, "--desc", help="Optional description"
    ),
    primary: bool = typer.Option(
        False, "--primary/--no-primary", help="Mark association as primary"
    ),
    edition: str = typer.Option(
        None,
        "--edition",
        help="Edition number when creating a new association of max 16 characters (default: SHA256[:16] checksum of file)",
    ),
):
    """
    Create or update a file.
    If a file with the same filename exists: update its content (new edition).
    Otherwise: create a new association on the WORKING revision (requires --edition)."""
    try:
        edition = _truncate_edition(edition)
        with spinner(f"Uploading {file.name} to {item}…", enabled=sys.stdout.isatty()):
            result = _client().upload_file_to_working(
                item,
                file,
                reference,
                title=title,
                category_name=category,
                file_format=file_format,
                description=description,
                primary=primary,
                edition=edition,
            )
        _print_json(result)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


@app.command("upload-weblink")
def upload_weblink(
    item: str = typer.Argument(..., help="Item/article number"),
    url: str = typer.Argument(..., help="HTTP(S) URL to associate as a web link"),
    reference: Optional[str] = typer.Option(
        None, "--reference", help="Optional reference string on the association"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="File title (default: derived from URL hostname/path)",
    ),
    category: str = typer.Option(
        "Source Code", "--category", help='File category name (default: "Source Code")'
    ),
    file_format: Optional[str] = typer.Option(
        "url",
        "--format",
        help='File format/extension label (default: "url")',
    ),
    description: Optional[str] = typer.Option(
        "None", "--description", help="Optional description"
    ),
    primary: bool = typer.Option(
        False,
        "--primary/--no-primary",
        help="Mark association as primary (default: false)",
    ),
    edition: Optional[str] = typer.Option(
        None,
        "--edition",
        help="Edition label of max 16 characters (default: SHA256(url)[:16])",
    ),
    latest_edition_association: bool = typer.Option(
        True,
        "--latest/--no-latest",
        help="Keep association pointed to the latest edition (default: true)",
    ),
):
    """
    Create or update a 'web link' file on the WORKING revision.
    If a matching link (by URL or title) exists, its File is updated in-place.
    Otherwise a new File is created and associated.
    """
    # Best-effort default title from URL if not provided
    if not title:
        try:
            u = urlparse(url)
            base = (u.netloc + u.path).rstrip("/") or u.netloc or url
            title = base.split("/")[-1] or base
        except Exception:
            title = url

    try:
        edition = _truncate_edition(edition)
        with spinner(f"Uploading web-link to {item}…", enabled=sys.stdout.isatty()):
            result = _client().upload_weblink_to_working(
                item_number=item,
                url=url,
                reference=reference,
                title=title,
                category_name=category,
                file_format=file_format,
                description=description,
                primary=primary,
                latest_edition_association=latest_edition_association,
                edition=edition,
            )
        _print_json(result)
    except requests.HTTPError as e:
        typer.secho(
            f"Arena request failed: {_format_http_error(e)}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(2)
    except ArenaError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(2)


if __name__ == "__main__":
    app()
