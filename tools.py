import re

from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes

from data_store import (
    add_audit_log,
    customer_summary,
    find_customer,
    find_ticket,
    load_json,
    next_id,
    save_json,
    ticket_counts_by_status,
    ticket_summary,
    utc_now,
)

VALID_PRIORITIES = {"low", "medium", "high", "urgent"}
VALID_TONES = {"professional", "friendly", "concise"}
PRODUCT_NAME = "NimbusDesk"
SNIPPET_LENGTH = 160


def _snippet(text: str, length: int = SNIPPET_LENGTH) -> str:
    text = " ".join(text.split())
    if len(text) <= length:
        return text
    return text[: length - 3].rstrip() + "..."


def _match_kb_articles(ticket: dict, limit: int = 3) -> list[dict]:
    articles = load_json("knowledge_base.json")
    search_terms = set(ticket.get("tags", []))
    for word in re.findall(r"[a-z0-9]+", ticket["subject"].lower()):
        if len(word) > 2:
            search_terms.add(word)

    scored: list[tuple[int, dict]] = []
    for article in articles:
        haystack = " ".join(
            [
                article["title"],
                article["category"],
                article["body"],
                " ".join(article.get("keywords", [])),
            ]
        ).lower()
        score = sum(1 for term in search_terms if term in haystack)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [article for _, article in scored[:limit]]


def _draft_text(
    ticket: dict,
    customer: dict,
    tone: str,
    kb_articles: list[dict],
) -> str:
    kb_hint = ""
    if kb_articles:
        kb_hint = f" Based on our knowledge base ({kb_articles[0]['title']}), " + _snippet(
            kb_articles[0]["body"], 120
        ).lower()

    if tone == "friendly":
        return (
            f"Hi {customer['name']},\n\n"
            f"Thanks for reaching out about \"{ticket['subject']}\". "
            f"We're looking into this for you.{kb_hint}\n\n"
            f"We'll follow up with an update shortly.\n\n"
            f"Best,\n{PRODUCT_NAME} Support"
        )
    if tone == "concise":
        return (
            f"Hi {customer['name']},\n\n"
            f"We received your ticket about \"{ticket['subject']}\" and are investigating."
            f"{kb_hint}\n\n"
            f"— {PRODUCT_NAME} Support"
        )
    return (
        f"Hello {customer['name']},\n\n"
        f"Thank you for contacting {PRODUCT_NAME} support regarding "
        f"\"{ticket['subject']}\". Our team is reviewing the details you provided."
        f"{kb_hint}\n\n"
        f"We will provide a further update as soon as we have more information.\n\n"
        f"Regards,\n{PRODUCT_NAME} Support Team"
    )


def _append_internal_note(
    ticket: dict,
    body: str,
    author: str = "mcp-agent",
) -> None:
    ticket.setdefault("internal_notes", []).append(
        {
            "author": author,
            "created_at": utc_now(),
            "body": body,
        }
    )
    ticket["updated_at"] = utc_now()


def register_support_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        description="Search support knowledge base articles.",
        auth=require_scopes("kb:read"),
    )
    def search_knowledge_base(query: str, limit: int = 5) -> dict:
        needle = query.strip().lower()
        if not needle:
            return {"ok": False, "error": "Query is required"}

        limit = max(1, min(limit, 20))
        results = []
        for article in load_json("knowledge_base.json"):
            haystack = " ".join(
                [
                    article["title"],
                    article["category"],
                    article["body"],
                    " ".join(article.get("keywords", [])),
                ]
            ).lower()
            if needle in haystack:
                results.append(
                    {
                        "id": article["id"],
                        "title": article["title"],
                        "category": article["category"],
                        "snippet": _snippet(article["body"]),
                    }
                )

        return {"ok": True, "count": len(results[:limit]), "results": results[:limit]}

    @mcp.tool(
        description="Look up a customer profile by ID or email.",
        auth=require_scopes("customers:read"),
    )
    def get_customer_profile(customer_id_or_email: str) -> dict:
        customer = find_customer(customer_id_or_email)
        if customer is None:
            return {
                "ok": False,
                "error": "Customer not found",
                "customer_id_or_email": customer_id_or_email,
            }
        return {
            "ok": True,
            "customer": customer,
            "ticket_counts_by_status": ticket_counts_by_status(customer["id"]),
        }

    @mcp.tool(
        description="List support tickets for a customer.",
        auth=require_scopes("tickets:read"),
    )
    def list_customer_tickets(
        customer_id_or_email: str,
        status: str | None = None,
    ) -> dict:
        customer = find_customer(customer_id_or_email)
        if customer is None:
            return {
                "ok": False,
                "error": "Customer not found",
                "customer_id_or_email": customer_id_or_email,
            }

        tickets = [
            ticket_summary(ticket)
            for ticket in load_json("tickets.json")
            if ticket["customer_id"] == customer["id"]
            and (status is None or ticket["status"] == status)
        ]
        return {
            "ok": True,
            "customer": customer_summary(customer),
            "count": len(tickets),
            "tickets": tickets,
        }

    @mcp.tool(
        description="Get full details for a support ticket.",
        auth=require_scopes("tickets:read"),
    )
    def get_ticket(ticket_id: str) -> dict:
        ticket = find_ticket(ticket_id)
        if ticket is None:
            return {"ok": False, "error": "Ticket not found", "ticket_id": ticket_id}

        customer = find_customer(ticket["customer_id"])
        return {
            "ok": True,
            "ticket": ticket,
            "customer": customer_summary(customer) if customer else None,
        }

    @mcp.tool(
        description="Draft a deterministic support reply without modifying the ticket.",
        auth=require_scopes("replies:draft"),
    )
    def draft_support_reply(ticket_id: str, tone: str = "professional") -> dict:
        ticket = find_ticket(ticket_id)
        if ticket is None:
            return {"ok": False, "error": "Ticket not found", "ticket_id": ticket_id}

        tone = tone.lower()
        if tone not in VALID_TONES:
            return {
                "ok": False,
                "error": "Invalid tone",
                "tone": tone,
                "allowed": sorted(VALID_TONES),
            }

        customer = find_customer(ticket["customer_id"])
        if customer is None:
            return {
                "ok": False,
                "error": "Customer not found for ticket",
                "ticket_id": ticket_id,
            }

        matched_kb_articles = _match_kb_articles(ticket)
        return {
            "ok": True,
            "ticket_id": ticket_id,
            "draft": _draft_text(ticket, customer, tone, matched_kb_articles),
            "matched_kb_articles": [
                {
                    "id": article["id"],
                    "title": article["title"],
                    "category": article["category"],
                }
                for article in matched_kb_articles
            ],
        }

    @mcp.tool(
        description="Create a new support ticket.",
        auth=require_scopes("tickets:write"),
    )
    def create_ticket(
        customer_id_or_email: str,
        subject: str,
        description: str,
        priority: str = "medium",
    ) -> dict:
        customer = find_customer(customer_id_or_email)
        if customer is None:
            return {
                "ok": False,
                "error": "Customer not found",
                "customer_id_or_email": customer_id_or_email,
            }

        priority = priority.lower()
        if priority not in VALID_PRIORITIES:
            return {
                "ok": False,
                "error": "Invalid priority",
                "priority": priority,
                "allowed": sorted(VALID_PRIORITIES),
            }

        tickets = load_json("tickets.json")
        now = utc_now()
        ticket = {
            "id": next_id("tic_", [ticket["id"] for ticket in tickets]),
            "customer_id": customer["id"],
            "subject": subject.strip(),
            "description": description.strip(),
            "status": "open",
            "priority": priority,
            "created_at": now,
            "updated_at": now,
            "assigned_to": "support-tier-1",
            "tags": [],
            "internal_notes": [],
        }
        tickets.append(ticket)
        save_json("tickets.json", tickets)
        add_audit_log(
            "ticket.created",
            "ticket",
            ticket["id"],
            {"customer_id": customer["id"], "priority": priority},
        )
        return {"ok": True, "ticket": ticket}

    @mcp.tool(
        description="Add an internal note to a support ticket.",
        auth=require_scopes("tickets:write"),
    )
    def add_internal_note(
        ticket_id: str,
        body: str,
        author: str = "mcp-agent",
    ) -> dict:
        tickets = load_json("tickets.json")
        for ticket in tickets:
            if ticket["id"] != ticket_id:
                continue
            _append_internal_note(ticket, body.strip(), author)
            save_json("tickets.json", tickets)
            add_audit_log(
                "ticket.note_added",
                "ticket",
                ticket_id,
                {"author": author},
            )
            return {"ok": True, "ticket": ticket}

        return {"ok": False, "error": "Ticket not found", "ticket_id": ticket_id}

    @mcp.tool(
        description="Escalate a support ticket to another team.",
        auth=require_scopes("tickets:write"),
    )
    def escalate_ticket(
        ticket_id: str,
        reason: str,
        target_team: str = "support-tier-2",
    ) -> dict:
        tickets = load_json("tickets.json")
        for ticket in tickets:
            if ticket["id"] != ticket_id:
                continue

            if ticket["priority"] != "urgent":
                ticket["priority"] = "high"
            ticket["assigned_to"] = target_team
            _append_internal_note(
                ticket,
                f"Escalated to {target_team}: {reason.strip()}",
                author="mcp-agent",
            )
            save_json("tickets.json", tickets)
            add_audit_log(
                "ticket.escalated",
                "ticket",
                ticket_id,
                {"target_team": target_team, "reason": reason.strip()},
            )
            return {"ok": True, "ticket": ticket}

        return {"ok": False, "error": "Ticket not found", "ticket_id": ticket_id}

    @mcp.tool(
        description="Close a support ticket with a resolution note.",
        auth=require_scopes("tickets:write"),
    )
    def close_ticket(ticket_id: str, resolution: str) -> dict:
        tickets = load_json("tickets.json")
        for ticket in tickets:
            if ticket["id"] != ticket_id:
                continue

            ticket["status"] = "closed"
            _append_internal_note(
                ticket,
                f"Resolution: {resolution.strip()}",
                author="mcp-agent",
            )
            save_json("tickets.json", tickets)
            add_audit_log(
                "ticket.closed",
                "ticket",
                ticket_id,
                {"resolution": resolution.strip()},
            )
            return {"ok": True, "ticket": ticket}

        return {"ok": False, "error": "Ticket not found", "ticket_id": ticket_id}

    @mcp.tool(
        description="Issue a fake refund for a customer.",
        auth=require_scopes("refunds:write"),
    )
    def issue_refund(
        customer_id_or_email: str,
        amount: float,
        reason: str,
        ticket_id: str | None = None,
    ) -> dict:
        if amount <= 0:
            return {"ok": False, "error": "Amount must be positive", "amount": amount}

        if amount > 100:
            return {
                "ok": False,
                "error": "Manager approval is required for refunds above $100",
                "amount": amount,
            }

        customer = find_customer(customer_id_or_email)
        if customer is None:
            return {
                "ok": False,
                "error": "Customer not found",
                "customer_id_or_email": customer_id_or_email,
            }

        if ticket_id is not None and find_ticket(ticket_id) is None:
            return {"ok": False, "error": "Ticket not found", "ticket_id": ticket_id}

        refunds = load_json("refunds.json")
        refund = {
            "id": next_id("ref_", [item["id"] for item in refunds]),
            "customer_id": customer["id"],
            "amount": round(amount, 2),
            "reason": reason.strip(),
            "ticket_id": ticket_id,
            "status": "issued",
            "created_at": utc_now(),
        }
        refunds.append(refund)
        save_json("refunds.json", refunds)

        if ticket_id is not None:
            tickets = load_json("tickets.json")
            for ticket in tickets:
                if ticket["id"] == ticket_id:
                    _append_internal_note(
                        ticket,
                        f"Refund {refund['id']} issued for ${refund['amount']:.2f}: {reason.strip()}",
                    )
                    save_json("tickets.json", tickets)
                    break

        add_audit_log(
            "refund.issued",
            "refund",
            refund["id"],
            {
                "customer_id": customer["id"],
                "amount": refund["amount"],
                "ticket_id": ticket_id,
            },
        )
        return {"ok": True, "refund": refund}

    @mcp.tool(
        description="View recent audit log entries.",
        auth=require_scopes("audit:read"),
    )
    def view_audit_logs(limit: int = 20, action_type: str | None = None) -> dict:
        limit = max(1, min(limit, 100))
        logs = load_json("audit_logs.json")
        if action_type is not None:
            logs = [log for log in logs if log["action"] == action_type]
        logs = sorted(logs, key=lambda log: log["timestamp"], reverse=True)
        return {"ok": True, "count": len(logs[:limit]), "logs": logs[:limit]}
