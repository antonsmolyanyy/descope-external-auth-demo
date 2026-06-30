CUSTOMERS = [
    {
        "id": "cus_001",
        "name": "Maya Chen",
        "email": "maya.chen@example.com",
        "company": "Northstar Robotics",
        "plan": "Enterprise",
        "status": "active",
        "created_at": "2025-11-14",
        "health_score": 82,
        "tags": ["enterprise", "high-value", "sso"],
        "notes": "Uses SSO and SCIM. Very sensitive to downtime during deploy windows.",
    },
    {
        "id": "cus_002",
        "name": "Eli Johnson",
        "email": "eli.johnson@example.com",
        "company": "BrightCart",
        "plan": "Growth",
        "status": "active",
        "created_at": "2026-01-22",
        "health_score": 64,
        "tags": ["billing", "growth"],
        "notes": "Recently upgraded. Has had repeated billing confusion.",
    },
    {
        "id": "cus_003",
        "name": "Sofia Ramirez",
        "email": "sofia.ramirez@example.com",
        "company": "Atlas Legal",
        "plan": "Starter",
        "status": "trial",
        "created_at": "2026-06-03",
        "health_score": 48,
        "tags": ["trial", "onboarding"],
        "notes": "Needs onboarding help and basic setup guidance.",
    },
]

TICKETS = [
    {
        "id": "tic_1001",
        "customer_id": "cus_001",
        "subject": "SSO users cannot log in after certificate rotation",
        "description": "Some users are seeing an invalid SAML response after the IdP certificate was rotated.",
        "status": "open",
        "priority": "urgent",
        "created_at": "2026-06-24T09:15:00Z",
        "updated_at": "2026-06-24T09:15:00Z",
        "assigned_to": "support-tier-2",
        "tags": ["sso", "saml", "certificate"],
        "internal_notes": [
            {
                "author": "system",
                "created_at": "2026-06-24T09:20:00Z",
                "body": "Customer reports this started after IdP cert rotation.",
            }
        ],
    },
    {
        "id": "tic_1002",
        "customer_id": "cus_002",
        "subject": "Invoice total does not match expected Growth plan price",
        "description": "Customer says their invoice includes an unexpected seat overage charge.",
        "status": "open",
        "priority": "medium",
        "created_at": "2026-06-25T15:40:00Z",
        "updated_at": "2026-06-25T15:40:00Z",
        "assigned_to": "billing-support",
        "tags": ["billing", "invoice"],
        "internal_notes": [],
    },
    {
        "id": "tic_1003",
        "customer_id": "cus_003",
        "subject": "How do I invite my first teammate?",
        "description": "Trial customer needs help adding a teammate and assigning a role.",
        "status": "open",
        "priority": "low",
        "created_at": "2026-06-26T18:05:00Z",
        "updated_at": "2026-06-26T18:05:00Z",
        "assigned_to": "support-tier-1",
        "tags": ["onboarding", "users", "roles"],
        "internal_notes": [],
    },
]

KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "title": "Troubleshooting SAML certificate rotation",
        "category": "SSO",
        "body": "When an IdP signing certificate is rotated, make sure the new certificate is uploaded to the service provider configuration. Confirm the entity ID, ACS URL, and signing algorithm match the IdP configuration.",
        "keywords": ["sso", "saml", "certificate", "idp", "rotation"],
    },
    {
        "id": "kb_002",
        "title": "Understanding seat overage charges",
        "category": "Billing",
        "body": "Seat overage charges are added when the workspace has more active users than the plan includes. Review active seats, pending invitations, and billing cycle dates before issuing a credit.",
        "keywords": ["billing", "invoice", "seat", "overage", "credit"],
    },
    {
        "id": "kb_003",
        "title": "Inviting teammates and assigning roles",
        "category": "Onboarding",
        "body": "Admins can invite teammates from the Members page. Choose a role during invitation, or update it later from member settings.",
        "keywords": ["invite", "teammate", "role", "admin", "onboarding"],
    },
    {
        "id": "kb_004",
        "title": "Refund policy for support agents",
        "category": "Billing",
        "body": "Support agents may draft refund recommendations, but refunds above $100 require manager approval. Always add an internal note explaining the reason for the refund.",
        "keywords": ["refund", "credit", "billing", "approval"],
    },
]

REFUNDS: list[dict] = []
AUDIT_LOGS: list[dict] = []

SEED_FILES = {
    "customers.json": CUSTOMERS,
    "tickets.json": TICKETS,
    "knowledge_base.json": KNOWLEDGE_BASE,
    "refunds.json": REFUNDS,
    "audit_logs.json": AUDIT_LOGS,
}
