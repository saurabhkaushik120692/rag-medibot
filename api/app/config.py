# app/config.py

# Role database configurations
ROLE_ACCESS_MAPPING = {
    "admin": ["general", "clinical", "nursing", "billing", "equipment"],
    "doctor": ["general", "clinical", "nursing"],
    "nurse": ["general", "nursing"],
    "billing_executive": ["general", "billing"],
    "technician": ["general", "equipment"]
}

# User credential verification database: {username: (password, role)}
MOCK_USERS = {
    "dr.mehta": ("doctor", "doctor"),
    "nurse.priya": ("nurse", "nurse"),
    "billing.ravi": ("billing_executive", "billing_executive"),
    "admin.sys": ("admin", "admin"),
    "tech.anand": ("technician", "technician"),
}
