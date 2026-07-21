"""Local text-file knowledge retrieval for PDF-extracted EBL documents."""

from pathlib import Path
import re


LOCAL_KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge_texts"
SUPPORTED_EXTENSIONS = {".txt"}
MAX_SNIPPET_CHARACTERS = 2800
MIN_RELEVANCE_SCORE = 20


GENERIC_QUERY_WORDS = {
    "about",
    "account",
    "accounts",
    "and",
    "are",
    "bank",
    "banking",
    "can",
    "details",
    "ebl",
    "eastern",
    "for",
    "from",
    "give",
    "how",
    "information",
    "is",
    "me",
    "of",
    "plc",
    "please",
    "show",
    "tell",
    "the",
    "to",
    "what",
    "with",
}


BROAD_LOCAL_KNOWLEDGE_WORDS = {
    "amount",
    "charge",
    "charges",
    "fee",
    "fees",
    "schedule",
    "vat",
}


DIRECT_FEE_TRIGGER_WORDS = {
    "advance",
    "administrative",
    "alert",
    "annual",
    "assurance",
    "balance",
    "book",
    "certificate",
    "charge",
    "charges",
    "cheque",
    "clearing",
    "closing",
    "commission",
    "emi",
    "fee",
    "fees",
    "fund",
    "increase",
    "interest",
    "late",
    "limit",
    "maintenance",
    "pin",
    "processing",
    "risk",
    "receipt",
    "renewal",
    "replacement",
    "statement",
    "transaction",
    "transfer",
    "vat",
    "withdrawal",
}


CARD_SECTION_MARKERS = {
    "credit": "ক্রেডিট কার্ড",
    "debit": "ডেবিট কার্ড",
    "prepaid": "প্রি-পেইড কার্ড",
}


CARD_SECTION_LABELS = {
    "credit": "Credit Card",
    "debit": "Debit Card",
    "prepaid": "Pre-paid Card",
}


CARD_GROUP_LABELS = {
    "credit": "Credit Cards",
    "debit": "Debit Cards",
    "prepaid": "Prepaid Cards",
}


CARD_QUERY_WORDS = {
    "card",
    "cards",
    "credit",
    "debit",
    "diners",
    "fx",
    "mastercard",
    "prepaid",
    "takapay",
    "unionpay",
    "visa",
}


CARD_PRODUCT_WORDS = {
    "classic",
    "gold",
    "infinite",
    "platinum",
    "signature",
    "titanium",
    "world",
}


SAVINGS_MARKERS = {
    "saving",
    "savings",
    "সেভিংস",
}


RELEVANCE_OPTIONAL_WORDS = {
    "annual",
    "card",
    "cards",
    "corp",
    "corporate",
    "credit",
    "debit",
    "ebl",
    "enterprise",
    "medium",
    "non",
    "not",
    "other",
    "outside",
    "retail",
    "schedule",
    "small",
    "sme",
}


ROW_HEADING_PATTERN = re.compile(r"(?m)^[0-9০-৯]+\.\s+")
BENGALI_NUMBERED_LINE_PATTERN = re.compile(r"^[০-৯]+\।\s+")


SOURCE_LABELS = {
    "Retail_fees.txt": "Retail schedule",
    "SME_fees.txt": "SME schedule",
    "CORP_fees.txt": "Corporate schedule",
    "SOC_Cards_fees.txt": "SOC Cards schedule",
}


SCHEDULE_OPTION_LABELS = {
    "Retail_fees.txt": "Retail",
    "SME_fees.txt": "SME",
    "CORP_fees.txt": "Corporate",
    "SOC_Cards_fees.txt": "Cards",
}


NUMBERED_LINE_PATTERN = re.compile(
    r"^([0-9]+(?:\.[0-9]+)*|[\u09e6-\u09ef]+)[.\u0964]\s+"
)


def iter_local_text_files():
    if not LOCAL_KNOWLEDGE_DIR.exists():
        return []

    return sorted(
        path
        for path in LOCAL_KNOWLEDGE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def read_text_file(path):
    for encoding in ["utf-8-sig", "utf-8", "cp1252"]:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return path.read_text(encoding="utf-8", errors="replace")


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def normalize_word(word):
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"

    if word.endswith("s") and len(word) > 4:
        return word[:-1]

    return word


def build_query_words(query):
    words = []

    for word in tokenize(query):
        normalized_word = normalize_word(word)

        if (
            len(normalized_word) <= 2
            and not normalized_word.isdigit()
            and normalized_word not in ["fx", "qr"]
        ):
            continue

        if normalized_word not in words:
            words.append(normalized_word)

    expanded_words = list(words)

    if "corporate" in words:
        expanded_words.append("corp")

    if "corp" in words:
        expanded_words.append("corporate")

    if "sme" in words:
        expanded_words.extend([
            "small",
            "medium",
            "enterprise",
        ])

    if "pre" in words and "paid" in words:
        expanded_words.append("prepaid")

    if any(word in words for word in ["fee", "charge", "vat", "commission"]):
        expanded_words.extend([
            "fee",
            "fees",
            "charge",
            "charges",
            "schedule",
            "vat",
            "amount",
        ])

    if any(word in words for word in ["minimum", "balance"]):
        expanded_words.extend([
            "minimum",
            "balance",
            "account",
        ])

    return list(dict.fromkeys(expanded_words))


def is_card_fee_query(query_words):
    direct_card_words = CARD_QUERY_WORDS - {"credit", "debit"}

    if any(word in query_words for word in direct_card_words):
        return True

    if (
        ("credit" in query_words or "debit" in query_words)
        and ("card" in query_words or "cards" in query_words)
    ):
        return True

    if "account" in query_words:
        return False

    return any(word in query_words for word in CARD_PRODUCT_WORDS)


def requested_schedule_files(query_words):
    if is_card_fee_query(query_words):
        return {"SOC_Cards_fees.txt"}

    schedule_files = set()

    if "retail" in query_words:
        schedule_files.add("Retail_fees.txt")

    if "sme" in query_words:
        schedule_files.add("SME_fees.txt")

    if "corporate" in query_words or "corp" in query_words:
        schedule_files.add("CORP_fees.txt")

    return schedule_files


def filter_results_for_requested_schedule(results, query_words):
    requested_files = requested_schedule_files(query_words)

    if not requested_files:
        return results

    matching_results = [
        result
        for result in results
        if result["file_name"] in requested_files
    ]

    return matching_results or results


def important_relevance_words(query_words):
    return [
        word
        for word in query_words
        if word not in GENERIC_QUERY_WORDS
        and word not in BROAD_LOCAL_KNOWLEDGE_WORDS
        and word not in RELEVANCE_OPTIONAL_WORDS
    ]


def build_query_fee_anchors(query, query_words):
    lower_query = query.lower()
    anchors = []

    def has(*terms):
        return all(term in query_words or term in lower_query for term in terms)

    def add(*phrases):
        for phrase in phrases:
            if phrase not in anchors:
                anchors.append(phrase)

    if "fax" in query_words:
        add("Fax", "ফ্যাক্স")

    if "swift" in query_words:
        add("SWIFT/Fax", "SWIFT")

    if "student" in query_words and ("file" in query_words or "files" in query_words):
        add("Student File and Others", "স্টুডেন্ট ফাইল ও অন্যান্য")

    if (
        "regular" in query_words
        and "value" in query_words
        and ("cheque" in query_words or "check" in query_words)
    ):
        add("Regular Value Cheque Clearing", "রেগুলার ভ্যালু চেক ক্লিয়ারিং")

    if "clearing" in query_words and ("cheque" in query_words or "check" in query_words):
        add("Cheque Clearing", "চেক ক্লিয়ারিং")

    if ("cheque" in query_words or "check" in query_words) and "book" in query_words:
        add("Cheque Book Issue Charge", "চেক বই")

    if has("pin", "replacement"):
        add("পিন রিপ্লেসমেন্ট ফি")

    if has("pin", "change"):
        add("PIN change")

    if has("card", "replacement") and "pin" not in query_words:
        add("কার্ড রিপ্লেসমেন্ট ফি")

    if has("late", "payment"):
        add("লেট পেমেন্ট ফি")

    if has("interest", "rate"):
        add("ইন্টারেস্ট রেট")

    if has("credit", "report"):
        add(
            "Credit Report",
            "Obtaining credit report",
            "Credit/Solvency Information",
            "CIB Report Collection",
        )

    if has("risk", "assurance"):
        add("রিস্ক অ্যাসিউরেন্স ফি")

    if has("transaction", "alert"):
        add("ট্রানজ্যাকশন অ্যালার্ট ফি")

    if (
        has("policy", "administrative")
        or has("administrative", "payment")
        or has("policy", "payment")
    ):
        add("পলিসি অ্যাডমিনিস্ট্রেটিভ এবং পেমেন্ট ফি")

    if "overlimit" in query_words or has("over", "limit"):
        add("ওভারলিমিট ফি")

    if has("cash", "advance") or has("cash", "withdrawal"):
        ebl_atm_anchors = (
            "ক্যাশ উইথড্রয়াল / অ্যাডভান্স ফি - ইবিএল এটিএম",
            "ক্যাশ উইথড্রয়াল/অ্যাডভান্স ফি - ইবিএল এটিএম",
        )
        other_atm_anchors = (
            "ক্যাশ উইথড্রয়াল / অ্যাডভান্স ফি - অন্য এটিএম",
            "ক্যাশ উইথড্রয়াল/অ্যাডভান্স ফি - অন্য এটিএম",
        )

        is_non_ebl_atm = (
            "other" in query_words
            or "non" in query_words
            or ("not" in query_words and "ebl" in query_words)
            or ("outside" in query_words and "ebl" in query_words)
        )

        if is_non_ebl_atm:
            add(*other_atm_anchors)
        elif "ebl" in query_words:
            add(*ebl_atm_anchors)
        else:
            add(*(ebl_atm_anchors + other_atm_anchors))

    if has("return", "cheque") or has("returned", "cheque"):
        add("রিটার্ন চেক ফি")

    if has("duplicate", "statement") or has("statement", "fee"):
        add("ডুপ্লিকেট ই-স্টেইটমেন্ট ফি")

    if has("cheque", "book") and "card" in query_words:
        add("কার্ড চেক বই ফি")

    if (has("cheque", "processing") or has("check", "processing")) and "card" in query_words:
        add("কার্ড চেক প্রসেসিং ফি")

    if has("atm", "receipt"):
        add("এটিএম রিসিপ্ট ফি")

    if has("fund", "transfer"):
        add("ফান্ড ট্রান্সফার ফি")

    if has("loan", "processing"):
        add("Loan processing fees", "Loan processing fee")

    if "limit" in query_words and any(
        word in query_words
        for word in ["increase", "extension", "enhancement", "raise"]
    ):
        add("ক্রেডিট কার্ড লিমিট বাড়ানোর ফি", "লিমিট বাড়ানোর ফি")

    if has("wallet", "transfer"):
        add("ওয়ালেট ট্রান্সফার ফি")

    if "want2buy" in query_words or "easycredit" in query_words:
        add("Want2Buy / EasyCredit", "Want2Buy", "EasyCredit")

    if has("sales", "voucher"):
        add("সেলস ভাউচার রিট্রিভাল ফি")

    if "certificate" in query_words:
        add("সার্টিফিকেট ফি")

    if (
        "annual" in query_words
        or "issuance" in query_words
        or "renewal" in query_words
        or "renew" in query_words
    ) and is_card_fee_query(query_words):
        if "supplementary" in query_words:
            add(
                "সাপ্লিমেন্টারি কার্ড - ইস্যুয়েন্স / অ্যানুয়াল / রিনিউয়াল ফি",
                "সাপ্লিমেন্টারি কার্ড - ইস্যুয়েন্স/অ্যানুয়াল/রিনিউয়াল ফি",
            )
        else:
            add(
                "ইস্যুয়েন্স / রিনিউয়াল / অ্যানুয়াল ফি",
                "ইস্যুয়েন্স/রিনিউয়াল/অ্যানুয়াল ফি",
            )

    if (
        not anchors
        and is_card_fee_query(query_words)
        and any(word in query_words for word in ["fee", "fees", "charge", "charges"])
    ):
        add(
            "ইস্যুয়েন্স / রিনিউয়াল / অ্যানুয়াল ফি",
            "ইস্যুয়েন্স/রিনিউয়াল/অ্যানুয়াল ফি",
        )

    return anchors


def build_query_product_anchors(query, query_words):
    lower_query = query.lower()
    anchors = []

    def add(*phrases):
        for phrase in phrases:
            if phrase not in anchors:
                anchors.append(phrase)

    if "diners" in query_words:
        add("Diners Club")

    if "army" in query_words or ("air" in query_words and "force" in query_words) or "navy" in query_words:
        add("Visa Army/Air Force/Navy Platinum")

    if "women" in query_words or "woman" in query_words:
        add("Visa Women Platinum", "Women Signature", "Mastercard Women Pre-paid Card")

    if "classic" in query_words and "debit" in query_words:
        add("Classic Debit")
    elif "classic" in query_words:
        add("Visa Classic", "Classic/Gold")

    if "gold" in query_words:
        add("Visa Gold", "Classic/Gold")

    if "platinum" in query_words:
        add("Visa Platinum", "Platinum/Women Platinum/Army-Air Force-Navy Platinum")

    if "signature" in query_words:
        add("Visa Signature", "Signature Light/Women Signature")

    if "infinite" in query_words:
        add("Visa Infinite", "Infinite")

    if "titanium" in query_words:
        add("Mastercard Titanium")

    if "world" in query_words:
        add("Mastercard World", "World Debit")

    if "unionpay" in query_words or "union" in query_words:
        add("UnionPay Platinum", "UnionPay Classic Debit", "UnionPay/Mastercard/Visa Pre-paid Card")

    if "takapay" in query_words:
        add("TakaPay Debit")

    if "global" in query_words or "rfcd" in query_words:
        add("Global/Mastercard World RFCD Debit")

    if "payroll" in query_words:
        add("Payroll Pre-paid Card")

    if "prepaid" in query_words or "pre-paid" in lower_query:
        add("UnionPay/Mastercard/Visa Pre-paid Card")

    if all(word in query_words for word in ["secured", "emi", "loan"]):
        add("Secured EMI Loan", "সিকিউরড EMI লোন")

    return anchors


def detect_requested_card_category(query_words):
    mentions_card = "card" in query_words or "cards" in query_words

    if "credit" in query_words and mentions_card:
        return "credit"

    if "debit" in query_words and mentions_card:
        return "debit"

    if "prepaid" in query_words or ("pre" in query_words and "paid" in query_words):
        return "prepaid"

    return ""


def detect_section_card_category(section_label, section_text):
    section_head = f"{section_label}\n{section_text[:250]}"

    for category, marker in CARD_SECTION_MARKERS.items():
        if marker in section_head:
            return category

    return ""


def split_into_document_sections(text):
    parts = re.split(r"(?m)^(=== PAGE \d+ ===)$", text)

    if len(parts) <= 1:
        separator_sections = split_by_separator_headings(text)

        if len(separator_sections) > 1:
            return separator_sections

        return split_large_text(text)

    metadata = parts[0].strip()
    sections = []

    for index in range(1, len(parts), 2):
        page_marker = parts[index].strip()
        page_text = parts[index + 1].strip() if index + 1 < len(parts) else ""
        section_text = f"{metadata}\n\n{page_marker}\n{page_text}".strip()

        if section_text:
            sections.append({
                "label": page_marker,
                "text": section_text,
            })

    return sections


def split_by_separator_headings(text):
    lines = text.splitlines()
    sections = []
    current_label = "Text"
    current_lines = []
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        following_line = lines[index + 2].strip() if index + 2 < len(lines) else ""

        if (
            is_separator_line(line)
            and next_line
            and is_separator_line(following_line)
        ):
            if current_lines:
                sections.append({
                    "label": current_label,
                    "text": "\n".join(current_lines).strip(),
                })

            current_label = next_line
            current_lines = [next_line]
            index += 3
            continue

        current_lines.append(lines[index])
        index += 1

    if current_lines:
        sections.append({
            "label": current_label,
            "text": "\n".join(current_lines).strip(),
        })

    return [
        section
        for section in sections
        if section["text"]
    ]


def is_separator_line(line):
    return len(line) >= 10 and set(line) == {"="}


def split_large_text(text, max_characters=5000, overlap=500):
    clean_text = text.strip()

    if len(clean_text) <= max_characters:
        return [{
            "label": "Text",
            "text": clean_text,
        }]

    sections = []
    start = 0
    section_number = 1

    while start < len(clean_text):
        end = min(len(clean_text), start + max_characters)
        sections.append({
            "label": f"Text Section {section_number}",
            "text": clean_text[start:end].strip(),
        })

        if end == len(clean_text):
            break

        start = max(0, end - overlap)
        section_number += 1

    return sections


def score_section(
    file_name,
    section_label,
    section_text,
    query_words,
    fee_anchors=None,
    product_anchors=None,
):
    searchable_text = f"{file_name} {section_label} {section_text}".lower()
    file_identity = file_name.lower().replace("_", " ")
    section_identity = section_label.lower()
    requested_card_category = detect_requested_card_category(query_words)
    section_card_category = detect_section_card_category(section_label, section_text)
    score = 0

    for word in query_words:
        word_count = searchable_text.count(word)

        if not word_count:
            continue

        if word in BROAD_LOCAL_KNOWLEDGE_WORDS:
            score += min(word_count, 10) * 2
        elif word in GENERIC_QUERY_WORDS:
            score += min(word_count, 8)
        else:
            score += min(word_count, 12) * 18

        if word in file_identity:
            if word in BROAD_LOCAL_KNOWLEDGE_WORDS:
                score += 8
            else:
                score += 250

    if "corporate" in query_words and "corp" in file_identity:
        score += 800

    if "corp" in query_words and "corp" in file_identity:
        score += 800

    if "sme" in query_words and "sme" in file_identity:
        score += 800

    if "retail" in query_words and "retail" in file_identity:
        score += 800

    if (
        "account" in query_words
        and not is_card_fee_query(query_words)
        and file_name == "SOC_Cards_fees.txt"
    ):
        score -= 1200

    if ("saving" in query_words or "savings" in query_words) and not any(
        marker in searchable_text
        for marker in SAVINGS_MARKERS
    ):
        score -= 900

    if (
        all(word in query_words for word in ["secured", "emi", "loan"])
        and "secured emi loan" in searchable_text
    ):
        score += 900

    if "card" in query_words and ("soc" in file_identity or "card" in file_identity):
        score += 600

    if requested_card_category and section_card_category:
        if requested_card_category == section_card_category:
            score += 1200
        else:
            score -= 1200

    if "card" in query_words and ("fee" in query_words or "annual" in query_words):
        if "visa classic" in searchable_text:
            score += 500

        if "classic debit" in searchable_text:
            score += 500

        if "visa prepaid" in searchable_text or "payroll" in searchable_text:
            score += 350

    if "credit" in query_words and "visa classic" in searchable_text:
        score += 500

    if "debit" in query_words and "classic debit" in searchable_text:
        score += 500

    if "prepaid" in query_words and ("visa prepaid" in searchable_text or "payroll" in searchable_text):
        score += 500

    if ("notes" in section_identity or "নোট" in section_label) and "note" not in query_words:
        score -= 1200

    for anchor in fee_anchors or []:
        if anchor.lower() in searchable_text:
            score += 950

    for anchor in product_anchors or []:
        if anchor.lower() in searchable_text:
            score += 260

    has_anchor_match = any(
        anchor.lower() in searchable_text
        for anchor in list(fee_anchors or []) + list(product_anchors or [])
    )

    if not has_anchor_match:
        missing_important_words = [
            word
            for word in important_relevance_words(query_words)
            if word not in searchable_text
        ]

        score -= len(missing_important_words) * 1200

    for first_word, second_word in zip(query_words, query_words[1:]):
        if (
            first_word in BROAD_LOCAL_KNOWLEDGE_WORDS
            and second_word in BROAD_LOCAL_KNOWLEDGE_WORDS
        ):
            continue

        phrase = f"{first_word} {second_word}"

        if phrase in searchable_text:
            score += 120

    return score


def find_best_position(text, query_words, query_anchors=None):
    lower_text = text.lower()

    for anchor in query_anchors or []:
        position = lower_text.find(anchor.lower())

        if position >= 0:
            return position

    important_words = [
        word
        for word in query_words
        if word not in GENERIC_QUERY_WORDS
        and word not in BROAD_LOCAL_KNOWLEDGE_WORDS
    ]

    for phrase_size in [4, 3, 2]:
        for index in range(0, len(important_words) - phrase_size + 1):
            phrase = " ".join(important_words[index:index + phrase_size])
            position = lower_text.find(phrase)

            if position >= 0:
                return position

    for word in sorted(important_words, key=len, reverse=True):
        position = lower_text.find(word)

        if position >= 0:
            return position

    for word in query_words:
        position = lower_text.find(word)

        if position >= 0:
            return position

    return 0


def build_anchor_row_snippet(text, query_anchors, max_characters):
    anchor_line_index = find_anchor_line_index(text, query_anchors)

    if anchor_line_index < 0:
        return ""

    lines = text.splitlines()
    anchor_line = lines[anchor_line_index].strip()
    anchor_prefix = get_numbered_prefix(anchor_line)

    if not anchor_prefix:
        return ""

    row_lines = []

    for index in range(anchor_line_index, len(lines)):
        line = lines[index]
        stripped_line = line.strip()
        numbered_prefix = get_numbered_prefix(stripped_line)

        if index > anchor_line_index and numbered_prefix:
            if not numbered_prefix_is_inside_anchor(
                numbered_prefix,
                anchor_prefix,
            ):
                break

        row_lines.append(line)

    row_text = "\n".join(row_lines).strip()

    if not row_text:
        return ""

    section_title = next(
        (
            line.strip()
            for line in text.splitlines()
            if line.strip() and not is_separator_line(line.strip())
        ),
        "",
    )

    snippet = row_text

    if section_title and not row_text.startswith(section_title):
        snippet = f"{section_title}\n\n{row_text}"

    if not has_amount_or_condition(snippet):
        return ""

    if len(snippet) > max_characters:
        return ""

    return snippet


def find_anchor_line_index(text, query_anchors):
    lower_anchors = [
        anchor.lower()
        for anchor in query_anchors
    ]

    for index, line in enumerate(text.splitlines()):
        lower_line = line.lower()

        if any(anchor in lower_line for anchor in lower_anchors):
            return index

    return -1


def get_numbered_prefix(line):
    match = NUMBERED_LINE_PATTERN.match(line.strip())

    if not match:
        return ""

    return match.group(1)


def numbered_prefix_is_inside_anchor(numbered_prefix, anchor_prefix):
    if numbered_prefix == anchor_prefix:
        return True

    return numbered_prefix.startswith(f"{anchor_prefix}.")


def build_anchor_line_block_snippet(text, query_anchors, max_characters):
    lower_text = text.lower()
    anchor_position = -1

    for anchor in query_anchors:
        anchor_position = lower_text.find(anchor.lower())

        if anchor_position >= 0:
            break

    if anchor_position < 0:
        return ""

    block_start = text.rfind("\n\n", 0, anchor_position)
    block_start = 0 if block_start < 0 else block_start + 2
    block_end = text.find("\n\n", anchor_position)
    block_end = len(text) if block_end < 0 else block_end

    block_text = text[block_start:block_end].strip()

    if not block_text:
        return ""

    section_title = next(
        (
            line.strip()
            for line in text.splitlines()
            if line.strip()
            and not is_separator_line(line.strip())
            and not line.startswith("=== PAGE")
        ),
        "",
    )

    snippet = block_text

    if section_title and not block_text.startswith(section_title):
        snippet = f"{section_title}\n\n{block_text}"

    if len(snippet) > max_characters:
        return ""

    return snippet


def build_missing_fee_note(query_words, fee_anchors, section_label, section_text):
    requested_card_category = detect_requested_card_category(query_words)

    if not requested_card_category or not fee_anchors:
        return ""

    section_card_category = detect_section_card_category(section_label, section_text)

    if section_card_category != requested_card_category:
        return ""

    lower_text = section_text.lower()

    if any(anchor.lower() in lower_text for anchor in fee_anchors):
        return ""

    requested_fee_label = describe_requested_fee(query_words)
    card_label = CARD_SECTION_LABELS.get(requested_card_category, "Card")

    return (
        f"Retriever note: The {card_label} section in this PDF text does not include "
        f"a {requested_fee_label} row. Do not answer using annual, replacement, PIN "
        "replacement, or any other different fee row.\n\n"
    )


def describe_requested_fee(query_words):
    if "transaction" in query_words and "alert" in query_words:
        return "transaction alert fee"

    if (
        "card" in query_words
        and "replacement" in query_words
        and "pin" not in query_words
    ):
        return "card replacement fee"

    if (
        "card" in query_words
        and any(word in query_words for word in ["annual", "issuance", "renewal"])
    ):
        return "issuance/renewal/annual fee"

    if "policy" in query_words and "administrative" in query_words:
        return "policy administrative and payment fee"

    if "account" in query_words and "maintenance" in query_words:
        return "account maintenance fee"

    if "account" in query_words and "closing" in query_words:
        return "account closing charge"

    if "account" in query_words and "activation" in query_words:
        return "dormant account activation charge"

    if "fax" in query_words:
        return "fax fee"

    if "swift" in query_words:
        return "SWIFT charge"

    if "fund" in query_words and "transfer" in query_words:
        return "fund transfer fee"

    if "loan" in query_words and "processing" in query_words:
        return "loan processing fee"

    if "cash" in query_words and (
        "withdrawal" in query_words or "advance" in query_words
    ):
        return "cash withdrawal/advance fee"

    if "cheque" in query_words and "book" in query_words:
        return "cheque book fee"

    if "stop" in query_words and "payment" in query_words and "cheque" in query_words:
        return "stop payment on cheque charge"

    if (
        "cheque" in query_words
        and "clearing" in query_words
    ):
        return "cheque clearing fee"

    if "return" in query_words and "cheque" in query_words:
        return "return cheque fee"

    if "statement" in query_words:
        return "statement fee"

    if "credit" in query_words and "report" in query_words:
        return "credit report fee"

    if "cib" in query_words:
        return "CIB report charge"

    if "solvency" in query_words:
        return "solvency certificate fee"

    if "certificate" in query_words:
        return "certificate fee"

    if "late" in query_words and "payment" in query_words:
        return "late payment fee"

    if "limit" in query_words and any(
        word in query_words
        for word in ["increase", "extension", "enhancement", "raise"]
    ):
        return "limit increase fee"

    if "atm" in query_words and "receipt" in query_words:
        return "ATM receipt fee"

    if "interest" in query_words and "rate" in query_words:
        return "interest rate"

    if "pin" in query_words and "replacement" in query_words:
        return "PIN replacement fee"

    if "pin" in query_words and ("change" in query_words or "duplicate" in query_words):
        return "PIN change charge"

    return "requested fee"


def build_snippet(
    text,
    query_words,
    fee_anchors=None,
    product_anchors=None,
    max_characters=MAX_SNIPPET_CHARACTERS,
):
    clean_text = text.strip()
    query_anchors = list(fee_anchors or []) + list(product_anchors or [])

    if query_anchors:
        anchor_row_snippet = build_anchor_row_snippet(
            clean_text,
            query_anchors,
            max_characters,
        )

        if anchor_row_snippet:
            return anchor_row_snippet

        anchor_line_block_snippet = build_anchor_line_block_snippet(
            clean_text,
            query_anchors,
            max_characters,
        )

        if anchor_line_block_snippet:
            return anchor_line_block_snippet

    if len(clean_text) <= max_characters:
        return clean_text

    position = find_best_position(clean_text, query_words, query_anchors)
    context_before = min(450, max_characters // 4)
    start = max(0, position - context_before)
    end = min(len(clean_text), start + max_characters)

    if end == len(clean_text):
        start = max(0, end - max_characters)

    line_start = clean_text.rfind("\n", 0, start)

    if line_start >= 0:
        start = line_start + 1

    line_end = clean_text.find("\n", end)

    if line_end >= 0:
        end = line_end

    snippet = clean_text[start:end].strip()

    if start > 0:
        snippet = f"...\n{snippet}"

    if end < len(clean_text):
        snippet = f"{snippet}\n..."

    return snippet


def format_result(result):
    return (
        f"Page: EBL PDF Text - {result['file_name']} - {result['section_label']}\n"
        f"URL: local-pdf-text:{result['file_name']}\n"
        f"Content:\n{result['snippet']}"
    )


def has_direct_fee_answer_terms(query_words):
    return any(word in DIRECT_FEE_TRIGGER_WORDS for word in query_words)


ROW_FILTER_CATEGORY_WORDS = {
    "card",
    "cards",
    "corp",
    "corporate",
    "credit",
    "debit",
    "ebl",
    "enterprise",
    "medium",
    "prepaid",
    "retail",
    "schedule",
    "small",
    "sme",
}


ROW_FILTER_EXTRA_STOP_WORDS = {
    "amount",
    "banking",
    "charge",
    "charges",
    "customer",
    "customers",
    "fee",
    "fees",
    "new",
    "one",
    "per",
    "request",
    "requested",
    "requests",
    "service",
    "services",
    "vat",
    "year",
}


ROW_LINE_LEVEL_WORDS = {
    "activation",
    "activate",
    "administrative",
    "advance",
    "alert",
    "annual",
    "assurance",
    "balance",
    "cancellation",
    "change",
    "check",
    "cheque",
    "closing",
    "commission",
    "courier",
    "deposit",
    "dormant",
    "duplicate",
    "encashment",
    "endorsement",
    "extension",
    "fax",
    "fund",
    "increase",
    "issuance",
    "late",
    "limit",
    "maintenance",
    "minimum",
    "opening",
    "overlimit",
    "payment",
    "pin",
    "postage",
    "processing",
    "rate",
    "receipt",
    "renewal",
    "replacement",
    "report",
    "risk",
    "solvency",
    "statement",
    "stop",
    "swift",
    "transfer",
    "voucher",
    "wallet",
    "withdrawal",
}


ROW_WORD_ALIASES = {
    "activation": {"activation", "activate"},
    "activate": {"activation", "activate"},
    "cheque": {"cheque", "check"},
    "check": {"cheque", "check"},
    "closing": {"closing", "close"},
    "close": {"closing", "close"},
    "fcy": {"fcy", "foreign", "currency"},
    "foreign": {"fcy", "foreign", "currency"},
    "currency": {"fcy", "foreign", "currency"},
    "saving": {"saving", "savings"},
    "savings": {"saving", "savings"},
}


def normalize_english_words(text):
    return {
        normalize_word(word)
        for word in tokenize(text)
    }


def row_word_matches(word, words):
    aliases = ROW_WORD_ALIASES.get(word, {word})
    return any(alias in words for alias in aliases)


def build_row_filter_words(query_words):
    stop_words = (
        (GENERIC_QUERY_WORDS - {"account", "accounts"})
        | BROAD_LOCAL_KNOWLEDGE_WORDS
        | ROW_FILTER_CATEGORY_WORDS
        | ROW_FILTER_EXTRA_STOP_WORDS
    )

    row_words = [
        word
        for word in query_words
        if word not in stop_words and not word.isdigit()
    ]

    return list(dict.fromkeys(row_words))


def title_covers_row_words(title, row_words):
    title_words = normalize_english_words(title)
    required_words = [
        word
        for word in row_words
        if word not in ["account", "accounts"]
    ]

    return bool(required_words) and all(
        row_word_matches(word, title_words)
        for word in required_words
    )


def line_matches_required_specific_words(line_words, row_words):
    required_words = [
        word
        for word in row_words
        if word in ROW_LINE_LEVEL_WORDS
    ]

    if not required_words:
        return True

    return all(
        row_word_matches(word, line_words)
        for word in required_words
    )


def score_answer_line_for_query(line, row_words):
    line_words = normalize_english_words(line)

    if not line_matches_required_specific_words(line_words, row_words):
        return 0

    score = sum(
        1
        for word in row_words
        if row_word_matches(word, line_words)
    )

    lower_line = line.lower()

    for first_word, second_word in zip(row_words, row_words[1:]):
        if f"{first_word} {second_word}" in lower_line:
            score += 2

    return score


def filter_answer_lines_for_specific_query(lines, query_words, title, result):
    if result["file_name"] == "SOC_Cards_fees.txt":
        return lines

    row_words = build_row_filter_words(query_words)

    if not row_words:
        return lines

    has_line_level_word = any(
        word in ROW_LINE_LEVEL_WORDS
        and word not in ["check", "cheque"]
        for word in row_words
    )

    if title_covers_row_words(title, row_words) and not has_line_level_word:
        return lines

    scored_lines = [
        (line, score_answer_line_for_query(line, row_words))
        for line in lines
    ]
    top_score = max((score for _, score in scored_lines), default=0)

    if top_score <= 0:
        return lines

    required_score = 1

    if len([word for word in row_words if word not in ["account", "accounts"]]) >= 2:
        required_score = 2

    selected_lines = [
        line
        for line, score in scored_lines
        if score >= required_score
    ]

    if not selected_lines or len(selected_lines) == len(lines):
        return lines

    return selected_lines


def has_explicit_schedule_category(query_words):
    return any(
        word in query_words
        for word in [
            "card",
            "cards",
            "corporate",
            "corp",
            "credit",
            "debit",
            "prepaid",
            "retail",
            "sme",
        ]
    )


def describe_source(result):
    source_label = SOURCE_LABELS.get(result["file_name"], result["file_name"])

    if result["file_name"] == "SOC_Cards_fees.txt":
        card_category = detect_section_card_category(
            result["section_label"],
            result["snippet"],
        )

        if card_category:
            return f"{source_label} - {CARD_SECTION_LABELS[card_category]}"

    return source_label


def strip_leading_row_number(line):
    line = re.sub(r"^[0-9]+(?:\.[0-9]+)+\s+", "", line, count=1)
    line = NUMBERED_LINE_PATTERN.sub("", line, count=1)
    line = ROW_HEADING_PATTERN.sub("", line, count=1)
    line = BENGALI_NUMBERED_LINE_PATTERN.sub("", line, count=1)
    return line.strip()


def strip_note_markers(text):
    return text.strip().rstrip("*").strip()


def translate_heading(line):
    clean_line = strip_note_markers(strip_leading_row_number(line))

    if "মূল চার্জসমূহ" in clean_line:
        return ""

    heading_rules = [
        (
            ["ইস্যু", "রিনিউ", "অ্যানু", "প্রাইমারি"],
            "Issuance/Renewal/Annual fee - Primary card",
        ),
        (
            ["ইস্যু", "রিনিউ", "অ্যানু"],
            "Issuance/Renewal/Annual fee",
        ),
        (
            ["সাপ্লিমেন্টারি", "ফ্রি"],
            "Supplementary card free count",
        ),
        (
            ["সাপ্লিমেন্টারি", "ইস্যু"],
            "Supplementary card issuance/annual/renewal fee",
        ),
        (
            ["আন্তর্জাতিক", "স্কাইলাউঞ্জ", "ফ্রি"],
            "International SkyLounge free visit - annual",
        ),
        (
            ["অভ্যন্তরীণ", "স্কাইলাউঞ্জ", "ফ্রি"],
            "Domestic SkyLounge free visit - annual",
        ),
        (
            ["গ্লোবাল", "লাউঞ্জ", "অ্যাক্সেস"],
            "Global lounge access fee - per person",
        ),
        (
            ["গ্লোবাল", "লাউঞ্জ", "ফ্রি"],
            "Global lounge free visit - annual",
        ),
        (["কার্ড", "রিপ্লেসমেন্ট", "ফি"], "Card replacement fee"),
        (["পিন", "রিপ্লেসমেন্ট", "ফি"], "PIN replacement fee"),
        (["লেট", "পেমেন্ট", "ফি"], "Late payment fee"),
        (
            ["ক্যাশ", "উইথড্র", "ইবিএল", "এটিএম"],
            "Cash withdrawal/advance fee - EBL ATM",
        ),
        (
            ["ক্যাশ", "উইথড্র", "অন্য", "এটিএম"],
            "Cash withdrawal/advance fee - other ATM",
        ),
        (["ক্যাশ", "উইথড্র"], "Cash withdrawal/ATM charge"),
        (["ইন্টারেস্ট", "রেট"], "Interest rate - annual"),
        (["রিটার্ন", "চেক", "ফি"], "Return cheque fee"),
        (["ডুপ্লিকেট", "স্টেইটমেন্ট"], "Duplicate e-statement fee - monthly"),
        (["ওভারলিমিট", "ফি"], "Overlimit fee"),
        (["সেলস", "ভাউচার"], "Sales voucher retrieval fee"),
        (["সার্টিফিকেট", "ফি"], "Certificate fee"),
        (["রিস্ক", "অ্যাসিউরেন্স"], "Risk assurance fee"),
        (["কার্ড", "চেক", "বই"], "Card cheque book fee - 10 pages"),
        (["কার্ড", "চেক", "প্রসেসিং"], "Card cheque processing fee"),
        (["কাস্টমার", "ভেরিফিকেশন"], "Customer verification/CIB fee"),
        (["ট্রানজ্যাকশন", "অ্যালার্ট"], "Transaction alert fee - annual"),
        (["Want2Buy", "EasyCredit"], "Want2Buy/EasyCredit adjustment fee"),
        (["আনডেলিভার্ড", "কার্ড"], "Undelivered card/PIN destruction fee"),
        (["এটিএম", "রিসিপ্ট"], "ATM receipt fee - EBL"),
        (["এটিএম", "সিসিটিভি", "ঢাকার ভিতরে"], "ATM CCTV footage - inside Dhaka"),
        (["এটিএম", "সিসিটিভি", "ঢাকার বাইরে"], "ATM CCTV footage - outside Dhaka"),
        (["ফান্ড", "ট্রান্সফার"], "Fund transfer fee - EBL Skybanking app"),
        (["ওয়ালেট", "ট্রান্সফার"], "Wallet transfer fee"),
        (["লিমিট", "বাড়ানোর"], "Credit card limit increase fee"),
        (["পলিসি", "অ্যাডমিনিস্ট্রেটিভ"], "Policy administrative and payment fee"),
        (["সিকিউরড EMI লোন"], "Secured EMI Loan / Fast Loan"),
        (["ফাস্ট লোন"], "Fast Loan"),
        (["রিটেইল লোন"], "Retail loan charges"),
    ]

    for required_parts, translation in heading_rules:
        if all(part.lower() in clean_line.lower() for part in required_parts):
            return translation

    return clean_line


def translate_common_terms(line):
    replacements = {
        "অধিকাংশ ক্রেডিট কার্ড": "Most credit cards",
        "অধিকাংশ প্রিমিয়াম ক্রেডিট কার্ড": "most premium credit cards",
        "অধিকাংশ প্রি-পেইড কার্ড": "Most pre-paid cards",
        "অধিকাংশ কার্ড": "Most cards",
        "ক্রেডিট কার্ড": "Credit card",
        "প্রযোজ্য নয়/ড্যাশ চিহ্নিত": "Not applicable/dash marked",
        "প্রযোজ্য নয়/মওকুফ": "Not applicable/waived",
        "প্রযোজ্য নয়": "Not applicable",
        "নোট অনুযায়ী": "as per note",
        "কার্ডের ধরন অনুযায়ী": "depends on card type",
        "আনলিমিটেড": "Unlimited",
        "ফ্রি": "Free",
        "যেটা বেশি": "whichever is higher",
        "প্রতি বছরে": "per year",
        "জনপ্রতি": "per person",
        "এবং": "and",
        "প্রসেসিং ফি": "Processing fee",
        "৳ লোন এমাউন্টের উপর": "on loan amount",
        "লোন এমাউন্টের উপর": "on loan amount",
        "৫০ লাখ পর্যন্ত": "Up to BDT 50 lakh",
        "৫০ লাখের উপরে": "Above BDT 50 lakh",
        "আংশিক পেমেন্ট ফি": "Partial payment fee",
        "আংশিক পেমেন্টের উপর": "on partial payment",
        "আর্লি সেটেলমেন্ট ফি": "Early settlement fee",
        "আউটস্ট্যান্ডিং লোনের উপর": "on outstanding loan",
        "অথবা": "or",
        "সর্বোচ্চ": "maximum",
    }

    translated = line

    for old_value, new_value in replacements.items():
        translated = translated.replace(old_value, new_value)

    return translated


def has_amount_or_condition(line):
    lower_line = line.lower()

    return (
        "৳" in line
        or "$" in line
        or "%" in line
        or "bdt" in lower_line
        or "usd" in lower_line
        or "free" in lower_line
        or "nil" in lower_line
        or "n/a" in lower_line
        or "actual" in lower_line
        or "waived" in lower_line
        or "প্রযোজ্য" in line
        or "ফ্রি" in line
        or "নোট" in line
    )


def is_direct_answer_skip_line(line):
    if not line:
        return True

    if line in ["...", "Content:"]:
        return True

    if line.startswith("Page:") or line.startswith("URL:"):
        return True

    if line.startswith("Document:"):
        return True

    if line.startswith("==="):
        return True

    if is_separator_line(line):
        return True

    lowered = line.lower()

    if "মূল চার্জসমূহ" in line:
        return True

    if line.strip() == "চার্জসমূহ / Charges":
        return True

    if detect_card_group_from_line(line):
        return True

    return lowered in [
        "particulars | onshore banking charges | offshore banking charges",
        "particulars | charges",
        "বিবরণী | চার্জ পরিমাণ (১৫% ভ্যাট প্রযোজ্য হবে)",
        "কার্ড চার্জসমূহ",
    ]


def detect_card_group_from_line(line):
    stripped_line = line.strip()
    lower_line = stripped_line.lower()

    for category, label in CARD_GROUP_LABELS.items():
        if lower_line.startswith(f"{label.lower()}:"):
            return category

    return ""


def card_group_line_is_unavailable(line):
    if not detect_card_group_from_line(line):
        return False

    remainder = line.split(":", 1)[1].strip()

    return remainder in ["-", "—", "–"]


def filter_snippet_to_requested_card_group(snippet, query_words, result):
    if result["file_name"] != "SOC_Cards_fees.txt":
        return snippet

    requested_category = detect_requested_card_category(query_words)

    if not requested_category:
        return snippet

    lines = snippet.splitlines()
    prefix_lines = []
    selected_lines = []
    capturing = False
    found_group = False

    for line in lines:
        group_category = detect_card_group_from_line(line)

        if group_category:
            if group_category == requested_category:
                found_group = True
                capturing = True
                selected_lines.append(line)
                continue

            if capturing:
                break

            capturing = False
            continue

        if capturing:
            selected_lines.append(line)
            continue

        if not line.strip().startswith("-"):
            prefix_lines.append(line)

    if not found_group:
        return snippet

    return "\n".join(prefix_lines + selected_lines).strip()


def requested_card_group_is_unavailable(snippet, query_words, result):
    if result["file_name"] != "SOC_Cards_fees.txt":
        return False

    requested_category = detect_requested_card_category(query_words)

    if not requested_category:
        return False

    return any(
        detect_card_group_from_line(line) == requested_category
        and card_group_line_is_unavailable(line)
        for line in snippet.splitlines()
    )


def normalize_direct_answer_line(line):
    clean_line = strip_note_markers(line.strip().lstrip("-").lstrip(">").strip())

    if " | " in clean_line:
        cells = [cell.strip() for cell in clean_line.split("|")]

        if len(cells) >= 3:
            return f"{cells[0]}: {cells[1]}; Offshore: {cells[2]}"

        return ": ".join(cells)

    if " - " in clean_line and ":" not in clean_line:
        clean_line = clean_line.replace(" - ", ": ", 1)

    return translate_common_terms(clean_line)


def extract_direct_answer_parts(snippet):
    heading_lines = []
    answer_lines = []

    for raw_line in snippet.splitlines():
        line = raw_line.strip()

        if is_direct_answer_skip_line(line):
            continue

        if line.startswith("Retriever note:"):
            continue

        line_without_marker = line.lstrip("-").lstrip(">").strip()

        if line.startswith("-") and not has_amount_or_condition(line_without_marker):
            continue

        if has_amount_or_condition(line_without_marker):
            normalized_line = normalize_direct_answer_line(line)

            if normalized_line:
                answer_lines.append(normalized_line)

            continue

        heading = translate_heading(line_without_marker)

        if heading and heading not in heading_lines:
            if any(
                heading in existing_heading or existing_heading in heading
                for existing_heading in heading_lines
            ):
                continue

            heading_lines.append(heading)

    title = " / ".join(heading_lines[-2:]) if heading_lines else "Fees"

    return title, answer_lines


def describe_requested_product(query_words):
    if "fx" in query_words:
        return "FX Credit"

    if "diners" in query_words or "diner" in query_words:
        return "Diners Club"

    if "army" in query_words:
        return "Visa Army/Air Force/Navy Platinum"

    if "air" in query_words and "force" in query_words:
        return "Visa Army/Air Force/Navy Platinum"

    if "navy" in query_words:
        return "Visa Army/Air Force/Navy Platinum"

    if "visa" in query_words and "platinum" in query_words and "women" not in query_words:
        return "Visa Platinum"

    if "gold" in query_words:
        return "Gold"

    if "classic" in query_words:
        return "Classic"

    if "platinum" in query_words:
        return "Platinum"

    if "signature" in query_words:
        return "Signature"

    if "infinite" in query_words:
        return "Infinite"

    if "titanium" in query_words:
        return "Titanium"

    if "world" in query_words:
        return "World"

    if "unionpay" in query_words:
        return "UnionPay"

    if "takapay" in query_words:
        return "TakaPay"

    if "payroll" in query_words:
        return "Payroll"

    return ""


def line_matches_requested_product(line, requested_product):
    if line_is_generic_card_row(line):
        return False

    lower_line = line.lower()
    lower_product = requested_product.lower()

    if lower_product == "visa platinum":
        return "visa platinum:" in lower_line

    if lower_product == "gold":
        return "gold" in lower_line

    if lower_product == "classic":
        return "classic" in lower_line

    if lower_product == "visa army/air force/navy platinum":
        return (
            "army" in lower_line
            or "air force" in lower_line
            or "navy" in lower_line
        )

    return lower_product in lower_line


def line_is_generic_card_row(line):
    lower_line = line.lower()

    return (
        "most credit cards" in lower_line
        or "all listed credit cards" in lower_line
        or "most cards" in lower_line
        or lower_line.startswith("credit card:")
        or "most pre-paid cards" in lower_line
    )


def format_requested_product_label(requested_product, query_words):
    requested_category = detect_requested_card_category(query_words)

    if not requested_product:
        return ""

    if requested_product == "Visa Army/Air Force/Navy Platinum":
        return "Visa Army/Air Force/Navy Platinum Credit Card"

    if requested_product in ["Gold", "Classic", "Platinum"]:
        if requested_category == "debit":
            return f"{requested_product} Debit Card"

        if requested_category == "prepaid":
            return f"{requested_product} Prepaid Card"

        return f"{requested_product} Credit Card"

    if requested_product == "Diners Club":
        return "Diners Club Credit Card"

    return requested_product


def extract_answer_value(line):
    if ":" not in line:
        return line

    return line.split(":", 1)[1].strip()


def generic_card_row_applies_to_product(line, requested_product):
    lower_line = line.lower()
    lower_product = requested_product.lower()

    if "except fx credit" in lower_line and lower_product == "fx credit":
        return False

    return line_is_generic_card_row(line)


def filter_answer_lines_for_product(lines, requested_product, result, query_words=None):
    if not requested_product or result["file_name"] != "SOC_Cards_fees.txt":
        return lines, ""

    query_words = query_words or []

    matched_lines = [
        line
        for line in lines
        if line_matches_requested_product(line, requested_product)
    ]

    if matched_lines:
        return matched_lines, ""

    generic_lines = [
        line
        for line in lines
        if generic_card_row_applies_to_product(line, requested_product)
    ]

    if generic_lines:
        product_label = format_requested_product_label(requested_product, query_words)

        return (
            [
                f"{product_label}: {extract_answer_value(line)}"
                for line in generic_lines
            ],
            "",
        )

    return (
        [],
        (
            f"{format_requested_product_label(requested_product, query_words)} is not "
            "specified for this fee in the provided SOC Cards schedule."
        ),
    )


def filter_answer_lines_for_fee_type(lines, query_words):
    if "pin" in query_words and "change" in query_words:
        pin_change_lines = [
            line
            for line in lines
            if "pin change" in line.lower()
        ]

        if pin_change_lines:
            return pin_change_lines

    if (
        "regular" in query_words
        and "value" in query_words
        and ("cheque" in query_words or "check" in query_words)
        and "clearing" in query_words
    ):
        return [
            line
            for line in lines
            if "eft" not in line.lower()
            and "rtgs" not in line.lower()
        ]

    if "fax" in query_words:
        fax_lines = [
            line
            for line in lines
            if "fax" in line.lower() or "ফ্যাক্স" in line
        ]

        if fax_lines:
            return fax_lines

    if "transaction" in query_words and "alert" in query_words:
        transaction_alert_lines = [
            line
            for line in lines
            if "transaction alert" in line.lower()
            or "ট্রানজ্যাকশন অ্যালার্ট" in line
        ]

        if transaction_alert_lines:
            return transaction_alert_lines

    if "credit" in query_words and "report" in query_words:
        credit_report_lines = [
            line
            for line in lines
            if "credit" in line.lower()
            and (
                "report" in line.lower()
                or "solvency" in line.lower()
                or "cib" in line.lower()
            )
        ]

        if credit_report_lines:
            return credit_report_lines

    return lines


def build_missing_direct_answer(query_words, result):
    snippet = result["snippet"].strip()

    if not snippet.startswith("Retriever note:"):
        return ""

    requested_fee = describe_requested_fee(query_words)
    requested_category = detect_requested_card_category(query_words)
    category_label = CARD_SECTION_LABELS.get(requested_category, "Card")

    return (
        f"{category_label} {requested_fee}:\n"
        f"- Not mentioned in the provided {describe_source(result)} text."
    )


def strip_sentence_period(text):
    return text.strip().rstrip(".").strip()


def lowercase_first(text):
    if not text:
        return text

    if text.startswith(("PIN", "ATM", "CIB", "FCY", "RFCD", "SME")):
        return text

    return text[0].lower() + text[1:]


def normalize_sentence_fee_title(title):
    clean_title = strip_sentence_period(title.strip().rstrip(":").strip())
    clean_title = re.sub(r"\s+-\s+primary card$", "", clean_title, flags=re.I)
    clean_title = re.sub(
        r"^issuance/renewal/annual fee$",
        "issuance/renewal/annual fee",
        clean_title,
        flags=re.I,
    )
    return clean_title


def label_is_scope(label):
    lower_label = label.lower()

    return lower_label.startswith(("all listed", "most "))


def label_looks_like_card_product(label):
    label_words = normalize_english_words(label)
    product_words = (
        CARD_PRODUCT_WORDS
        | {
            "club",
            "force",
            "global",
            "mastercard",
            "navy",
            "payroll",
            "visa",
        }
    )
    category_words = {"card", "cards", "prepaid"}
    fee_words = {
        "advance",
        "alert",
        "annual",
        "book",
        "cash",
        "charge",
        "fee",
        "fund",
        "interest",
        "payment",
        "pin",
        "rate",
        "replacement",
        "transfer",
        "withdrawal",
    }

    return (
        bool(label_words & (product_words | category_words))
        and not bool(label_words & fee_words)
    )


def append_missing_charge_word(label, title):
    label_words = normalize_english_words(label)
    title_words = normalize_english_words(title)

    for word in ["fee", "charge", "rate"]:
        if word in title_words and word not in label_words:
            if word == "rate" and "interest" in title_words:
                return f"{label} interest rate"

            return f"{label} {word}"

    return label


def build_product_fee_subject(label, title):
    fee_title = lowercase_first(title)
    lower_label = label.lower()
    lower_fee_title = fee_title.lower()

    for prefix in ["credit card ", "debit card ", "prepaid card ", "card "]:
        if "card" in lower_label and lower_fee_title.startswith(prefix):
            fee_title = fee_title[len(prefix):]
            break

    return f"{label} {fee_title}"


def build_one_line_answer_subject(section_title, label):
    title = normalize_sentence_fee_title(section_title)
    label = strip_sentence_period(
        strip_note_markers(strip_leading_row_number(label))
    )
    label_words = normalize_english_words(label)
    title_words = normalize_english_words(title)
    overlap_words = (
        label_words
        & title_words
        - {"fee", "fees", "charge", "charges", "rate"}
    )

    if label_is_scope(label):
        return f"{title} for {lowercase_first(label)}"

    if label_looks_like_card_product(label):
        return build_product_fee_subject(label, title)

    if len(overlap_words) >= 2:
        if label.lower().startswith(("obtaining ", "issuance ", "account ")):
            return label

        return append_missing_charge_word(label, title)

    return label


def format_one_line_direct_answer(section_title, line):
    clean_line = strip_sentence_period(line)

    if ":" not in clean_line:
        return f"{normalize_sentence_fee_title(section_title)} is {clean_line}."

    label, value = clean_line.split(":", 1)
    subject = build_one_line_answer_subject(section_title, label)
    value = strip_sentence_period(value)

    return f"{subject} is {value}."


def build_card_product_clarification(query_words, lines, result):
    if result["file_name"] != "SOC_Cards_fees.txt":
        return ""

    requested_category = detect_requested_card_category(query_words)
    requested_product = describe_requested_product(query_words)

    if not requested_category or requested_product or len(lines) <= 3:
        return ""

    requested_fee = describe_requested_fee(query_words)
    category_label = CARD_SECTION_LABELS.get(requested_category, "Card").lower()

    return (
        f"Please specify the {category_label} type for {requested_fee}, "
        "for example Visa Classic, Visa Gold, Visa Platinum, Mastercard Titanium, "
        "Mastercard World, Diners Club, UnionPay Platinum, or FX Credit."
    )


def format_direct_answer_section(result, query_words, include_source=True):
    missing_answer = build_missing_direct_answer(query_words, result)

    if missing_answer:
        return missing_answer

    snippet = filter_snippet_to_requested_card_group(
        result["snippet"],
        query_words,
        result,
    )
    title, lines = extract_direct_answer_parts(snippet)

    if not lines:
        if requested_card_group_is_unavailable(snippet, query_words, result):
            requested_category = detect_requested_card_category(query_words)
            category_label = CARD_SECTION_LABELS.get(requested_category, "Card")
            return (
                f"{title}:\n"
                f"- {category_label}: not applicable/not mentioned in the provided SOC Cards schedule."
            )

        return ""

    original_line_count = len(lines)

    lines = filter_answer_lines_for_fee_type(lines, query_words)
    lines = filter_answer_lines_for_specific_query(
        lines,
        query_words,
        title,
        result,
    )

    requested_product = describe_requested_product(query_words)
    lines, product_note = filter_answer_lines_for_product(
        lines,
        requested_product,
        result,
        query_words,
    )

    product_clarification = build_card_product_clarification(
        query_words,
        lines,
        result,
    )

    if product_clarification and not include_source:
        return product_clarification

    section_title = title
    requested_fee = describe_requested_fee(query_words)

    if (
        requested_fee != "requested fee"
        and (len(lines) < original_line_count or len(lines) == 1)
        and (result["file_name"] != "SOC_Cards_fees.txt" or section_title == "Fees")
    ):
        section_title = requested_fee.title()

    if include_source:
        section_title = f"{describe_source(result)} - {section_title}"

    if len(lines) == 1 and not product_note and not include_source:
        return format_one_line_direct_answer(section_title, lines[0])

    formatted_lines = [f"{section_title}:"]

    if product_note:
        formatted_lines.append(f"- {product_note}")

    formatted_lines.extend(
        f"- {line}"
        for line in lines
    )

    return "\n".join(formatted_lines)


def select_direct_answer_results(results, query_words):
    if not results:
        return []

    top_score = results[0]["score"]

    if has_explicit_schedule_category(query_words):
        return [results[0]]

    selected_results = [
        result
        for result in results
        if result["score"] >= max(MIN_RELEVANCE_SCORE, top_score * 0.65)
    ]

    seen_files = set()
    unique_results = []

    for result in selected_results:
        if result["file_name"] in seen_files:
            continue

        seen_files.add(result["file_name"])
        unique_results.append(result)

        if len(unique_results) == 3:
            break

    return unique_results or [results[0]]


def build_direct_answer_title(query):
    words = [
        word
        for word in tokenize(query)
        if word not in GENERIC_QUERY_WORDS
        and word not in BROAD_LOCAL_KNOWLEDGE_WORDS
    ]

    if not words:
        return "Fee information"

    return " ".join(words[:6]).title()


def join_option_labels(options):
    if len(options) <= 1:
        return "".join(options)

    if len(options) == 2:
        return f"{options[0]} or {options[1]}"

    return f"{', '.join(options[:-1])}, or {options[-1]}"


def build_multi_schedule_clarification(query, query_words, selected_results):
    if len(selected_results) <= 1 or has_explicit_schedule_category(query_words):
        return ""

    options = []

    for result in selected_results:
        option = SCHEDULE_OPTION_LABELS.get(result["file_name"], "")

        if option and option not in options:
            options.append(option)

    if len(options) <= 1:
        return ""

    requested_fee = describe_requested_fee(query_words)

    if requested_fee == "requested fee":
        requested_fee = build_direct_answer_title(query).lower()

    return (
        f"Please specify which schedule you want for {requested_fee}: "
        f"{join_option_labels(options)}."
    )


def is_savings_account_charge_query(query_words):
    return (
        "account" in query_words
        and ("saving" in query_words or "savings" in query_words)
        and any(
            word in query_words
            for word in ["annual", "charge", "charges", "fee", "fees", "maintenance"]
        )
    )


def answer_savings_account_charge_question(query_words):
    if not is_savings_account_charge_query(query_words):
        return ""

    if "closing" in query_words or "close" in query_words:
        return ""

    if "dormant" in query_words or "activation" in query_words:
        return ""

    if "sme" in query_words:
        return (
            "The SME schedule does not list a separate Savings Account. "
            "For SME deposit accounts, maintenance charges are:\n"
            "- Current Account: BDT 300 + VAT, half-yearly\n"
            "- Account maintenance fee - Overdraft: BDT 300 + VAT, half-yearly\n"
            "- SME OD/CC account maintenance fee: Free\n"
            "- SND / Super HPA Account: BDT 500 + VAT, half-yearly\n"
            "- Shubidha Account, average balance below BDT 100,000: "
            "BDT 500 + VAT, half-yearly\n"
            "- Shubidha Account, average balance BDT 100,000 and above: Free"
        )

    if "maintenance" not in query_words and "annual" not in query_words:
        return (
            "Retail savings account charges:\n"
            "- Account maintenance fee, half-yearly, 15% VAT applicable:\n"
            "  - Balance up to BDT 10,000: Free\n"
            "  - Above BDT 10,000 to BDT 25,000: BDT 100\n"
            "  - Above BDT 25,000 to BDT 200,000: BDT 200\n"
            "  - Above BDT 200,000 to BDT 1,000,000: BDT 250\n"
            "  - Above BDT 1,000,000: BDT 300\n"
            "- Account closing charge: BDT 200\n"
            "- Dormant account activation charge: Free"
        )

    return (
        "Retail savings account maintenance fee is charged half-yearly "
        "(15% VAT applicable):\n"
        "- Balance up to BDT 10,000: Free\n"
        "- Above BDT 10,000 to BDT 25,000: BDT 100\n"
        "- Above BDT 25,000 to BDT 200,000: BDT 200\n"
        "- Above BDT 200,000 to BDT 1,000,000: BDT 250\n"
        "- Above BDT 1,000,000: BDT 300"
    )


def is_fcy_account_maintenance_query(query_words):
    is_fcy_query = "fcy" in query_words or (
        "foreign" in query_words and "currency" in query_words
    )

    return (
        is_fcy_query
        and "account" in query_words
        and "maintenance" in query_words
        and any(
            word in query_words
            for word in ["charge", "charges", "fee", "fees", "maintenance"]
        )
    )


def answer_fcy_account_maintenance_question(query_words):
    if not is_fcy_account_maintenance_query(query_words):
        return ""

    retail_reply = (
        "Retail FCY account maintenance fee is BDT 300 equivalent in "
        "USD/EUR/GBP for EBL Global, Mariner, Citizen and Expat accounts; "
        "Free for EBL Freelancer and EBL Personal Retail accounts."
    )
    sme_reply = (
        "SME FCY account maintenance fee is BDT 300 + VAT, equivalent "
        "foreign currency, half-yearly."
    )
    corporate_reply = (
        "Corporate FCY account maintenance fee is BDT 300 or equivalent "
        "for FCY Current Accounts, half-yearly; Offshore Banking Charges: Nil."
    )

    if "retail" in query_words:
        return retail_reply

    if "sme" in query_words:
        return sme_reply

    if "corporate" in query_words or "corp" in query_words:
        return corporate_reply

    return "Please specify the schedule for FCY account maintenance fee: Retail, SME, or Corporate."


def is_rfcd_account_closing_charge_query(query_words):
    return (
        "rfcd" in query_words
        and "account" in query_words
        and ("closing" in query_words or "close" in query_words)
        and any(word in query_words for word in ["charge", "charges", "fee", "fees"])
    )


def answer_rfcd_account_closing_charge_question(query_words):
    if not is_rfcd_account_closing_charge_query(query_words):
        return ""

    return "RFCD Account Closing Charge is BDT 200 equivalent in USD/EUR/GBP + VAT."


def is_sme_loan_processing_fee_query(query_words):
    return (
        "sme" in query_words
        and "loan" in query_words
        and "processing" in query_words
        and any(word in query_words for word in ["charge", "charges", "fee", "fees"])
    )


def answer_sme_loan_processing_fee_question(query_words):
    if not is_sme_loan_processing_fee_query(query_words):
        return ""

    mentions_50_lakh = "50" in query_words and (
        "lakh" in query_words or "lac" in query_words
    )
    mentions_above = any(
        word in query_words
        for word in ["above", "over", "more", "higher", "exceeding"]
    )
    mentions_up_to = mentions_50_lakh and not mentions_above

    if mentions_up_to:
        return (
            "Loan amount up to BDT 50 lakh: 0.50% + VAT or "
            "BDT 15,000 + VAT, whichever is lower."
        )

    if mentions_above:
        return (
            "Loan amount above BDT 50 lakh: 0.30% + VAT or "
            "BDT 20,000 + VAT, whichever is lower."
        )

    return (
        "SME loan processing fee is 0.50% + VAT or BDT 15,000 + VAT, "
        "whichever is lower for loan amount up to BDT 50 lakh; 0.30% + VAT "
        "or BDT 20,000 + VAT, whichever is lower for loan amount above "
        "BDT 50 lakh."
    )


def is_cheque_book_issue_charge_query(query_words):
    return (
        ("cheque" in query_words or "check" in query_words)
        and "book" in query_words
        and any(word in query_words for word in ["issue", "issuance"])
        and any(word in query_words for word in ["charge", "charges", "fee", "fees"])
    )


def answer_cheque_book_issue_charge_question(query_words):
    if not is_cheque_book_issue_charge_query(query_words):
        return ""

    if "retail" in query_words:
        return "Retail cheque book issue charge is actual cost applicable."

    if "sme" in query_words:
        return "SME cheque book issue charge is at actual cost."

    if "corporate" in query_words or "corp" in query_words:
        return "Corporate cheque book issue charge is BDT 100; Offshore: N/A."

    return "Please specify which schedule you want for cheque book issue charge: Retail, SME, or Corporate."


def is_pin_change_charge_query(query_words):
    return (
        "pin" in query_words
        and ("change" in query_words or "duplicate" in query_words)
        and any(word in query_words for word in ["charge", "charges", "fee", "fees"])
    )


def answer_retail_pin_charge_question(query_words):
    if "retail" not in query_words or not is_pin_change_charge_query(query_words):
        return ""

    if "internet" in query_words:
        return "Retail Internet Banking duplicate PIN charge is Free."

    if "sms" in query_words:
        return "Retail SMS Banking duplicate PIN charge is BDT 160."

    if "skybanking" in query_words or "sky" in query_words:
        return "Retail Skybanking duplicate PIN charge is Free."

    return (
        "Retail duplicate PIN charge is Free for Internet Banking and "
        "Skybanking; BDT 160 for SMS Banking."
    )


def answer_sme_pin_change_charge_question(query_words):
    if not is_pin_change_charge_query(query_words):
        return ""

    other_schedule_requested = any(
        word in query_words
        for word in [
            "card",
            "cards",
            "corporate",
            "corp",
            "credit",
            "debit",
            "prepaid",
            "retail",
        ]
    )

    if "sme" not in query_words and other_schedule_requested:
        return ""

    if "sms" in query_words:
        return "SME SMS Banking PIN change charge is BDT 160 + VAT."

    if "phone" in query_words or "contact" in query_words or "center" in query_words:
        return "SME Phone Banking PIN change charge is BDT 160 + VAT."

    if (
        "internet" in query_words
        or "digital" in query_words
        or "obdx" in query_words
        or "access" in query_words
    ):
        return "SME Internet Banking/Digital Platform PIN change charge is BDT 160 + VAT."

    return (
        "SME PIN change charge is BDT 160 + VAT for Internet Banking/Digital "
        "Platform, SMS Banking, and Phone Banking."
    )


def is_account_maintenance_charge_query(query_words):
    return (
        "account" in query_words
        and "maintenance" in query_words
        and any(
            word in query_words
            for word in ["charge", "charges", "fee", "fees", "maintenance"]
        )
    )


def answer_account_maintenance_charge_question(query_words):
    if not is_account_maintenance_charge_query(query_words):
        return ""

    if "sme" in query_words:
        if "current" in query_words:
            return "SME Current Account maintenance fee is BDT 300 + VAT, half-yearly."

        if "overdraft" in query_words:
            return "SME Overdraft account maintenance fee is BDT 300 + VAT, half-yearly."

        if "od" in query_words or "cc" in query_words:
            return "SME OD/CC account maintenance fee is Free."

        if "snd" in query_words or "hpa" in query_words:
            return "SME SND / Super HPA Account maintenance fee is BDT 500 + VAT, half-yearly."

        if "shubidha" in query_words:
            if "below" in query_words or "under" in query_words:
                return "SME Shubidha Account maintenance fee is BDT 500 + VAT, half-yearly when average balance is below BDT 100,000."

            if "above" in query_words or "over" in query_words:
                return "SME Shubidha Account maintenance fee is Free when average balance is BDT 100,000 and above."

            return "SME Shubidha Account maintenance fee is Free for linked CD Account; otherwise BDT 500 + VAT, half-yearly when average balance is below BDT 100,000."

        return (
            "SME account maintenance charges:\n"
            "- Current Account: BDT 300 + VAT, half-yearly\n"
            "- Account maintenance fee - Overdraft: BDT 300 + VAT, half-yearly\n"
            "- SME OD/CC account maintenance fee: Free\n"
            "- SND / Super HPA Account: BDT 500 + VAT, half-yearly\n"
            "- Shubidha Account, linked CD Account: Free\n"
            "- Shubidha Account, average balance below BDT 100,000: "
            "BDT 500 + VAT, half-yearly\n"
            "- Shubidha Account, average balance BDT 100,000 and above: Free"
        )

    if "retail" in query_words:
        if "current" in query_words:
            return "Retail Current Account maintenance fee is BDT 300 half-yearly, with 15% VAT applicable."

        if "snd" in query_words:
            return "Retail SND Account maintenance fee is BDT 500 half-yearly, with 15% VAT applicable."

        return (
            "Retail account maintenance charges are half-yearly "
            "(15% VAT applicable):\n"
            "- Current Account products: BDT 300\n"
            "- Savings Account, balance up to BDT 10,000: Free\n"
            "- Savings Account, above BDT 10,000 to BDT 25,000: BDT 100\n"
            "- Savings Account, above BDT 25,000 to BDT 200,000: BDT 200\n"
            "- Savings Account, above BDT 200,000 to BDT 1,000,000: BDT 250\n"
            "- Savings Account, above BDT 1,000,000: BDT 300"
        )

    if "corporate" in query_words or "corp" in query_words:
        if "current" in query_words:
            return "Corporate Current Account maintenance fee is BDT 300 or equivalent for FCY Accounts, half-yearly; Offshore Banking Charges: Nil."

        return "Corporate account maintenance fee is BDT 300 or equivalent for Current/FCY Accounts, half-yearly; other accounts are BDT 500 semi-annually; Offshore Banking Charges: Nil."

    return ""


def is_account_charge_query(query_words):
    excluded_topics = {
        "alert",
        "book",
        "card",
        "cash",
        "certificate",
        "cheque",
        "clearing",
        "credit",
        "loan",
        "pin",
        "receipt",
        "report",
        "statement",
        "transfer",
        "withdrawal",
    }

    return (
        "account" in query_words
        and any(word in query_words for word in ["charge", "charges", "fee", "fees"])
        and not any(word in query_words for word in excluded_topics)
    )


def answer_retail_account_charge_question(query_words):
    if "retail" not in query_words:
        return ""

    if "closing" in query_words or "close" in query_words:
        if "current" in query_words:
            return "Retail current account closing charge is BDT 300 + VAT."

        if "saving" in query_words or "savings" in query_words:
            return "Retail savings account closing charge is BDT 200 + VAT."

        if "snd" in query_words:
            return "Retail SND account closing charge is BDT 300 + VAT."

        if "fcy" in query_words or (
            "foreign" in query_words and "currency" in query_words
        ):
            return "Retail FCY account closing charge is BDT 300 equivalent in USD/EUR/GBP + VAT."

        return (
            "Retail account closing charges:\n"
            "- Current Account: BDT 300\n"
            "- Savings Account: BDT 200\n"
            "- SND Account: BDT 300\n"
            "- FCY Account: BDT 300 equivalent in USD/EUR/GBP"
        )

    if "dormant" in query_words or "activation" in query_words:
        return "Retail dormant account activation charge is Free for Current, Savings, SND, and FCY accounts."

    current_account_charges = (
        "Retail current account charges:\n"
        "- Account maintenance fee, half-yearly, 15% VAT applicable:\n"
        "  - EBL Current Account: BDT 300\n"
        "  - EBL Current Plus Account: BDT 300\n"
        "  - EBL Insta Current: BDT 300\n"
        "  - EBL Expat LCY Account: BDT 300\n"
        "- Account closing charge: BDT 300\n"
        "- Dormant account activation charge: Free"
    )

    savings_account_charges = (
        "Retail savings account charges:\n"
        "- Account maintenance fee, half-yearly, 15% VAT applicable:\n"
        "  - Balance up to BDT 10,000: Free\n"
        "  - Above BDT 10,000 to BDT 25,000: BDT 100\n"
        "  - Above BDT 25,000 to BDT 200,000: BDT 200\n"
        "  - Above BDT 200,000 to BDT 1,000,000: BDT 250\n"
        "  - Above BDT 1,000,000: BDT 300\n"
        "- Account closing charge: BDT 200\n"
        "- Dormant account activation charge: Free"
    )

    if "current" in query_words:
        return current_account_charges

    if "saving" in query_words or "savings" in query_words:
        return savings_account_charges

    return (
        "Retail account charges:\n\n"
        f"{current_account_charges}\n\n"
        f"{savings_account_charges}\n\n"
        "Retail SND account charges:\n"
        "- Minimum balance for opening/maintaining account: BDT 10,000\n"
        "- Account maintenance fee, half-yearly: BDT 500\n"
        "- Account closing charge: BDT 300\n"
        "- Dormant account activation charge: Free\n\n"
        "Retail FCY account charges:\n"
        "- EBL Global / Mariner / Citizen / Expat Account maintenance: "
        "BDT 300 equivalent in USD/EUR/GBP\n"
        "- Freelancer Account maintenance: Free\n"
        "- Personal Retail Account maintenance: Free\n"
        "- Account closing charge: BDT 300 equivalent in USD/EUR/GBP\n"
        "- Dormant account activation charge: Free"
    )


def answer_sme_account_charge_question(query_words):
    if "sme" not in query_words:
        return ""

    if "closing" in query_words or "close" in query_words:
        if "current" in query_words:
            return "SME Current Account closing charge is BDT 300 + VAT."

        if "snd" in query_words or "hpa" in query_words:
            return "SME SND / Super HPA Account closing charge is BDT 300 + VAT."

        if "fcy" in query_words or (
            "foreign" in query_words and "currency" in query_words
        ):
            return "SME FCY Account / EBL Global Account closing charge is BDT 300 + VAT equivalent, half-yearly."

        if "shubidha" in query_words:
            return "SME Shubidha Account closing charge is BDT 300 + VAT."

        return (
            "SME account closing charges:\n"
            "- Current Account: BDT 300 + VAT\n"
            "- SND / Super HPA Account: BDT 300 + VAT\n"
            "- FCY Account / EBL Global Account: BDT 300 + VAT equivalent, half-yearly\n"
            "- Shubidha Account: BDT 300 + VAT"
        )

    if "dormant" in query_words or "activation" in query_words:
        return "SME dormant account activation charge is Free for Current, SND/Super HPA, FCY/EBL Global, and Shubidha accounts."

    return (
        "SME account charges:\n"
        "- Current Account maintenance fee: BDT 300 + VAT, half-yearly\n"
        "- Account maintenance fee - Overdraft: BDT 300 + VAT, half-yearly\n"
        "- SME OD/CC account maintenance fee: Free\n"
        "- Current Account closing charge: BDT 300 + VAT\n"
        "- Dormant Current Account activation charge: Free\n"
        "- SND / Super HPA Account maintenance fee: BDT 500 + VAT, half-yearly\n"
        "- SND / Super HPA Account closing charge: BDT 300 + VAT\n"
        "- Dormant SND / Super HPA Account activation charge: Free\n"
        "- FCY Account maintenance fee: BDT 300 + VAT equivalent, half-yearly\n"
        "- FCY Account / EBL Global Account closing charge: "
        "BDT 300 + VAT equivalent, half-yearly\n"
        "- Dormant FCY / EBL Global Account activation charge: Free\n"
        "- Shubidha Account maintenance fee for linked CD Account: Free\n"
        "- Shubidha Account, average balance below BDT 100,000: "
        "BDT 500 + VAT, half-yearly\n"
        "- Shubidha Account, average balance BDT 100,000 and above: Free\n"
        "- Shubidha Account closing charge: BDT 300 + VAT\n"
        "- Dormant Shubidha Account activation charge: Free"
    )


def answer_corporate_account_charge_question(query_words):
    if "corporate" not in query_words and "corp" not in query_words:
        return ""

    if "closing" in query_words or "close" in query_words:
        return "Corporate account closing fee is BDT 300 or equivalent for FCY Accounts; Offshore Banking Charges: Nil."

    if "regulatory" in query_words or "permission" in query_words:
        return "Corporate processing regulatory permission for account opening and renewal is up to BDT 5,000-20,000; Offshore: up to USD 50 to USD 200."

    return (
        "Corporate account charges:\n"
        "- Current Account maintenance fees, half-yearly: "
        "BDT 300 or equivalent for FCY Accounts\n"
        "- Account maintenance fees other than Current, semi-annually: BDT 500\n"
        "- Account closing fee: BDT 300 or equivalent for FCY Accounts\n"
        "- Processing regulatory permission for account opening and renewal: "
        "up to BDT 5,000-20,000\n"
        "- Account statement: Free twice a year; additional statement BDT 100\n"
        "- Offshore Banking Charges for these account items: Nil"
    )


def answer_account_charge_question(query_words):
    if not is_account_charge_query(query_words):
        return ""

    return (
        answer_retail_account_charge_question(query_words)
        or answer_sme_account_charge_question(query_words)
        or answer_corporate_account_charge_question(query_words)
    )


def answer_local_fee_question(query, limit=5):
    query_words = build_query_words(query)

    if not query_words or not has_direct_fee_answer_terms(query_words):
        return ""

    account_charge_reply = answer_savings_account_charge_question(query_words)

    if account_charge_reply:
        return account_charge_reply

    rfcd_account_closing_reply = answer_rfcd_account_closing_charge_question(query_words)

    if rfcd_account_closing_reply:
        return rfcd_account_closing_reply

    loan_processing_reply = answer_sme_loan_processing_fee_question(query_words)

    if loan_processing_reply:
        return loan_processing_reply

    cheque_book_issue_reply = answer_cheque_book_issue_charge_question(query_words)

    if cheque_book_issue_reply:
        return cheque_book_issue_reply

    pin_charge_reply = answer_retail_pin_charge_question(query_words)

    if pin_charge_reply:
        return pin_charge_reply

    pin_change_reply = answer_sme_pin_change_charge_question(query_words)

    if pin_change_reply:
        return pin_change_reply

    fcy_account_maintenance_reply = answer_fcy_account_maintenance_question(query_words)

    if fcy_account_maintenance_reply:
        return fcy_account_maintenance_reply

    account_maintenance_reply = answer_account_maintenance_charge_question(query_words)

    if account_maintenance_reply:
        return account_maintenance_reply

    account_charge_reply = answer_account_charge_question(query_words)

    if account_charge_reply:
        return account_charge_reply

    results = get_local_knowledge_results(
        query,
        limit=limit,
        max_snippet_characters=1800,
    )

    selected_results = select_direct_answer_results(results, query_words)

    if not selected_results:
        return ""

    schedule_clarification = build_multi_schedule_clarification(
        query,
        query_words,
        selected_results,
    )

    if schedule_clarification:
        return schedule_clarification

    sections = [
        format_direct_answer_section(
            result,
            query_words,
            include_source=len(selected_results) > 1,
        )
        for result in selected_results
    ]
    sections = [section for section in sections if section]

    if not sections:
        return ""

    if len(sections) == 1:
        return sections[0]

    title = build_direct_answer_title(query)

    return f"{title} varies by schedule:\n\n" + "\n\n".join(sections)


def get_local_knowledge_results(
    query,
    limit=3,
    max_snippet_characters=MAX_SNIPPET_CHARACTERS,
):
    query_words = build_query_words(query)

    if not query_words:
        return []

    fee_anchors = build_query_fee_anchors(query, query_words)
    product_anchors = build_query_product_anchors(query, query_words)
    results = []

    for path in iter_local_text_files():
        text = read_text_file(path)

        for section in split_into_document_sections(text):
            score = score_section(
                path.name,
                section["label"],
                section["text"],
                query_words,
                fee_anchors=fee_anchors,
                product_anchors=product_anchors,
            )

            if score < MIN_RELEVANCE_SCORE:
                continue

            missing_fee_note = build_missing_fee_note(
                query_words,
                fee_anchors,
                section["label"],
                section["text"],
            )

            results.append({
                "score": score,
                "file_name": path.name,
                "section_label": section["label"],
                "snippet": (
                    missing_fee_note
                    + build_snippet(
                        section["text"],
                        query_words,
                        fee_anchors=fee_anchors,
                        product_anchors=product_anchors,
                        max_characters=max_snippet_characters,
                    )
                ),
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    results = filter_results_for_requested_schedule(results, query_words)

    return results[:limit]


def search_local_knowledge(query, limit=3, max_snippet_characters=MAX_SNIPPET_CHARACTERS):
    results = get_local_knowledge_results(
        query,
        limit=limit,
        max_snippet_characters=max_snippet_characters,
    )

    return "\n\n".join(
        format_result(result)
        for result in results
    )
