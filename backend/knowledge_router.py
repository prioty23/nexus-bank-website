def select_knowledge_pages(intent):
    knowledge_map = {
        "account_information": [
            "EBL Home Page",
            "EBL Retail Deposits Page",
            "EBL SME Deposits Page",
            "EBL Verified Contact Information",
        ],
        "card_information": [
            "EBL Cards Page",
            "EBL Verified Contact Information",
        ],
        "loan_information": [
            "EBL Retail Loan Page",
            "EBL SME Loan Page",
            "EBL Verified Contact Information",
        ],
        "deposit_information": [
            "EBL Retail Deposits Page",
            "EBL SME Deposits Page",
            "EBL Verified Contact Information",
        ],
        "digital_banking": [
            "EBL Digital Banking Page",
            "EBL Verified Contact Information",
        ],
        "branch_locator": [
            "EBL Locator Page",
            "EBL Verified Contact Information",
        ],
    }

    return knowledge_map.get(intent, [
        "EBL Home Page",
        "EBL Verified Contact Information",
    ])
