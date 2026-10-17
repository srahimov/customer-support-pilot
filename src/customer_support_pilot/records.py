CUSTOMERS = {
    "FOX-C1001": {
        "customer_id": "FOX-C1001",
        "name": "Elena Martinez",
        "customer_type": "residential",
        "state": "CA",
        "products": ["car", "home"],
        "registered_trucks": 0,
    },
    "FOX-C1002": {
        "customer_id": "FOX-C1002",
        "name": "Pacific Route Logistics LLC",
        "customer_type": "business",
        "state": "CA",
        "products": ["truck"],
        "registered_trucks": 3,
    },
    "FOX-C1003": {
        "customer_id": "FOX-C1003",
        "name": "Lone Star Distribution LLC",
        "customer_type": "business",
        "state": "TX",
        "products": ["car", "truck"],
        "registered_trucks": 6,
    },
    "FOX-C1004": {
        "customer_id": "FOX-C1004",
        "name": "Jack Johnson",
        "customer_type": "residential",
        "state": "CO",
        "products": ["car", ],
        "registered_trucks": 0,
    },
    "FOX-C1005": {
        "customer_id": "FOX-C1005",
        "name": "Max Shipping LLC",
        "customer_type": "business",
        "state": "TX",
        "products": ["car", "truck"],
        "registered_trucks": 3,
    },
    "FOX-C1006": {
        "customer_id": "FOX-C1006",
        "name": "ABC Distribution LLC",
        "customer_type": "business",
        "state": "NM",
        "products": ["home", "truck"],
        "registered_trucks": 2,
    },
}

POLICIES = {
    # Elena Martinez: car and home
    "FOX-P2001": {
        "policy_id": "FOX-P2001",
        "customer_id": "FOX-C1001",
        "product": "personal_auto",
        "status": "active",
        "effective_date": "2026-06-01",
        "expiration_date": "2027-06-01",
    },
    "FOX-P2002": {
        "policy_id": "FOX-P2002",
        "customer_id": "FOX-C1001",
        "product": "homeowners",
        "status": "active",
        "effective_date": "2026-07-15",
        "expiration_date": "2027-07-15",
    },

    # Pacific Route Logistics LLC: truck
    "FOX-P2003": {
        "policy_id": "FOX-P2003",
        "customer_id": "FOX-C1002",
        "product": "commercial_truck",
        "status": "active",
        "effective_date": "2026-09-01",
        "expiration_date": "2027-09-01",
    },

    # Lone Star Distribution LLC: truck and car
    "FOX-P2004": {
        "policy_id": "FOX-P2004",
        "customer_id": "FOX-C1003",
        "product": "commercial_truck",
        "status": "active",
        "effective_date": "2026-08-01",
        "expiration_date": "2027-08-01",
    },
    "FOX-P2005": {
        "policy_id": "FOX-P2005",
        "customer_id": "FOX-C1003",
        "product": "commercial_auto",
        "status": "active",
        "effective_date": "2026-08-01",
        "expiration_date": "2027-08-01",
    },

    # Jack Johnson: car
    "FOX-P2006": {
        "policy_id": "FOX-P2006",
        "customer_id": "FOX-C1004",
        "product": "personal_auto",
        "status": "active",
        "effective_date": "2026-05-10",
        "expiration_date": "2027-05-10",
    },

    # Max Shipping LLC: car and truck
    "FOX-P2007": {
        "policy_id": "FOX-P2007",
        "customer_id": "FOX-C1005",
        "product": "commercial_auto",
        "status": "active",
        "effective_date": "2026-04-01",
        "expiration_date": "2027-04-01",
    },
    "FOX-P2008": {
        "policy_id": "FOX-P2008",
        "customer_id": "FOX-C1005",
        "product": "commercial_truck",
        "status": "active",
        "effective_date": "2026-04-01",
        "expiration_date": "2027-04-01",
    },

    # ABC Distribution LLC: home and truck
    "FOX-P2009": {
        "policy_id": "FOX-P2009",
        "customer_id": "FOX-C1006",
        "product": "dwelling_property",
        "status": "active",
        "effective_date": "2026-03-15",
        "expiration_date": "2027-03-15",
    },
    "FOX-P2010": {
        "policy_id": "FOX-P2010",
        "customer_id": "FOX-C1006",
        "product": "commercial_truck",
        "status": "active",
        "effective_date": "2026-03-15",
        "expiration_date": "2027-03-15",
    },
}

INVOICES = {
    "FOX-I3001": {
        "invoice_id": "FOX-I3001",
        "customer_id": "FOX-C1001",
        "policy_ids": ["FOX-P2001", "FOX-P2002"],
        "currency": "USD",
        "amount_cents": 34500,
        "paid_cents": 34500,
        "due_date": "2026-10-20",
    },
    "FOX-I3002": {
        "invoice_id": "FOX-I3002",
        "customer_id": "FOX-C1002",
        "policy_ids": ["FOX-P2003"],
        "currency": "USD",
        "amount_cents": 186000,
        "paid_cents": 60000,
        "due_date": "2026-10-20",
    },
    "FOX-I3003": {
        "invoice_id": "FOX-I3003",
        "customer_id": "FOX-C1003",
        "policy_ids": ["FOX-P2004", "FOX-P2005"],
        "currency": "USD",
        "amount_cents": 425000,
        "paid_cents": 0,
        "due_date": "2026-10-20",
    },
    "FOX-I3004": {
        "invoice_id": "FOX-I3004",
        "customer_id": "FOX-C1004",
        "policy_ids": ["FOX-P2006"],
        "currency": "USD",
        "amount_cents": 15200,
        "paid_cents": 15200,
        "due_date": "2026-10-20",
    },
    "FOX-I3005": {
        "invoice_id": "FOX-I3005",
        "customer_id": "FOX-C1005",
        "policy_ids": ["FOX-P2007", "FOX-P2008"],
        "currency": "USD",
        "amount_cents": 263500,
        "paid_cents": 0,
        "due_date": "2026-10-20",
    },
    "FOX-I3006": {
        "invoice_id": "FOX-I3006",
        "customer_id": "FOX-C1006",
        "policy_ids": ["FOX-P2009", "FOX-P2010"],
        "currency": "USD",
        "amount_cents": 142000,
        "paid_cents": 142000,
        "due_date": "2026-10-20",
    },
}

TICKETS = {
    "FOX-T4001": {
        "ticket_id": "FOX-T4001",
        "customer_id": "FOX-C1001",
        "department": "billing",
        "subject": "Invoice payment confirmation",
        "status": "resolved",
        "latest_update": (
            "Payment confirmed for invoice FOX-I3001. "
            "Customer received payment confirmation."
        ),
        "updated_at": "2026-10-15T16:00:00Z",
    },
    "FOX-T4002": {
        "ticket_id": "FOX-T4002",
        "customer_id": "FOX-C1002",
        "department": "billing",
        "subject": "Partial payment allocation question",
        "status": "in_progress",
        "latest_update": (
            "Billing team is reviewing payment allocation "
            "for invoice FOX-I3002. No adjustment has been approved."
        ),
        "updated_at": "2026-10-15T18:30:00Z",
    },
    "FOX-T4003": {
        "ticket_id": "FOX-T4003",
        "customer_id": "FOX-C1003",
        "department": "document_delivery",
        "subject": "Certificate of insurance request",
        "status": "open",
        "latest_update": (
            "Certificate request received for policy FOX-P2004. "
            "Document review is pending."
        ),
        "updated_at": "2026-10-15T17:15:00Z",
    },
    "FOX-T4004": {
        "ticket_id": "FOX-T4004",
        "customer_id": "FOX-C1004",
        "department": "technical_support",
        "subject": "Unable to sign in to customer portal",
        "status": "resolved",
        "latest_update": (
            "Password reset completed. "
            "Customer confirmed portal access was restored."
        ),
        "updated_at": "2026-10-15T15:45:00Z",
    },
    "FOX-T4005": {
        "ticket_id": "FOX-T4005",
        "customer_id": "FOX-C1005",
        "department": "billing",
        "subject": "Payment due-date extension request",
        "status": "open",
        "latest_update": (
            "Extension requested for invoice FOX-I3005. "
            "Billing review is pending; the due date is unchanged."
        ),
        "updated_at": "2026-10-15T19:00:00Z",
    },
    "FOX-T4006": {
        "ticket_id": "FOX-T4006",
        "customer_id": "FOX-C1006",
        "department": "policy_service",
        "subject": "Property mailing-address correction",
        "status": "waiting_for_customer",
        "latest_update": (
            "Customer was asked to confirm the requested mailing address. "
            "No policy record has been changed."
        ),
        "updated_at": "2026-10-15T20:00:00Z",
    },
}