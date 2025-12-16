from brizz._internal.models import PatternEntry

DEFAULT_PII_PATTERN_ENTRIES: list[PatternEntry] = [
    # Email addresses
    # Example: user@example.com, john.doe+tag@company.org
    PatternEntry(
        name="email_addresses",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    ),
    # Phone numbers (US format)
    # Example: +1-555-123-4567, (555) 123-4567, 555.123.4567
    PatternEntry(
        name="us_phone_numbers",
        pattern=r"\b(?:\+?1[-.\s]*)?(?:\(?([0-9]{3})\)?|([0-9]{3}))[-.\s]*([0-9]{3})[-.\s]*([0-9]{4})\b",
    ),
    # Social Security Numbers
    # Example: 123-45-6789, 987654321
    PatternEntry(
        name="ssn",
        pattern=r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b",
    ),
    # Credit card numbers
    # Example: 4532015112830366, 5555555555554444, 378282246310005
    PatternEntry(
        name="credit_cards",
        pattern=r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
    ),
    # Example: 4532-0151-1283-0366, 5555 5555 5555 4444
    PatternEntry(
        name="credit_cards_with_separators",
        pattern=r"\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    ),
    # IP addresses (IPv4)
    # Example: 192.168.1.1, 10.0.0.1, 172.16.254.1
    PatternEntry(
        name="ipv4_addresses",
        pattern=r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?!\.[0-9])\b",
    ),
    # API keys/tokens
    # Example: api_key=abc123def456ghi789, token: "sk_live_abcd1234efgh5678"
    PatternEntry(
        name="generic_api_keys",
        pattern=r'\b(?:[Aa][Pp][Ii][_-]?[Kk][Ee][Yy]|[Tt][Oo][Kk][Ee][Nn]|[Ss][Ee][Cc][Rr][Ee][Tt])[_-]?[=:]?\s*["\']?([a-zA-Z0-9\-_.]{20,})["\']?\b',
    ),
    # Example: sk-proj-abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx
    PatternEntry(name="openai_keys", pattern=r"\bsk[-_][a-zA-Z0-9]{20,}\b"),
    # Example: YWxhZGRpbjpvcGVuc2VzYW1lMTIzNDU2Nzg5MDEyMzQ1Njc4OTA=
    # More restrictive: must have base64 indicators and be longer
    PatternEntry(name="base64_secrets", pattern=r"\b[A-Za-z0-9+/]{64,}={0,2}\b"),
    # AWS Keys
    # Example: AKIAIOSFODNN7EXAMPLE, ASIAQBQN4ABCD1234567
    PatternEntry(name="aws_access_keys", pattern=r"\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
    # Example: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    # More restrictive: must contain some mixed case and special chars
    PatternEntry(
        name="aws_secret_keys",
        pattern=r"\b[A-Za-z0-9/+=]*[A-Z][A-Za-z0-9/+=]*[a-z][A-Za-z0-9/+=]*[/+=][A-Za-z0-9/+=]{30,}\b",
    ),
    # GitHub tokens
    # Example: ghp_1234567890abcdef1234567890abcdef12345678
    PatternEntry(name="github_tokens", pattern=r"\bghp_[a-zA-Z0-9]{36}\b"),
    # Slack tokens
    # Example: xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx
    PatternEntry(
        name="slack_tokens",
        pattern=r"\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,34}\b",
    ),
    # Stripe keys
    # Example: sk_test_4eC39HqLyjWDarjtT1zdp7dc, pk_live_abcdef123456
    PatternEntry(name="stripe_keys", pattern=r"\b(?:sk|pk)_(?:test|live)_[a-zA-Z0-9]{24,}\b"),
    # JWT tokens
    # Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4g...
    PatternEntry(
        name="jwt_tokens",
        pattern=r"\beyJ[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]{2,}\b",
    ),
    # MAC addresses
    # Example: 00:1B:44:11:3A:B7, AA-BB-CC-DD-EE-FF
    PatternEntry(name="mac_addresses", pattern=r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    # IPv6 addresses
    # Example: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    PatternEntry(name="ipv6_addresses", pattern=r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"),
    # Medical records
    # Example: MRN-1234567, mrn 9876543210
    PatternEntry(name="medical_record_numbers", pattern=r"\b(?:[Mm][Rr][Nn])[-\s]?\d{6,10}\b"),
    # Bitcoin addresses
    # Example: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa, 3FupnbKjEJSRSQjpBgELWJDJP7Q6qXZ8Nz
    PatternEntry(name="bitcoin_addresses", pattern=r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"),
    # Ethereum addresses
    # Example: 0x742d35cc6635c0532925a3b8d1d28f9ca1bd1ffe
    PatternEntry(name="ethereum_addresses", pattern=r"\b0x[a-fA-F0-9]{40}(?![a-fA-F0-9])\b"),
    # UUIDs
    # Example: 123e4567-e89b-12d3-a456-426614174000
    PatternEntry(
        name="uuids",
        pattern=r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?![0-9a-fA-F-])\b",
    ),
    # Database connection strings
    # Example: mongodb://user:pass@host:27017/db, postgres://user:password@localhost:5432/mydb
    PatternEntry(
        name="database_connections",
        pattern=r"\b(?:[Mm][Oo][Nn][Gg][Oo][Dd][Bb]|[Pp][Oo][Ss][Tt][Gg][Rr][Ee][Ss]|[Mm][Yy][Ss][Qq][Ll]|[Rr][Ee][Dd][Ii][Ss]|[Mm][Ss][Ss][Qq][Ll]|[Oo][Rr][Aa][Cc][Ll][Ee]):\/\/[^\s]+\b",
    ),
    # Private keys
    # Example: -----BEGIN RSA PRIVATE KEY-----
    PatternEntry(name="rsa_private_keys", pattern=r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
    # Example: -----BEGIN PGP PRIVATE KEY BLOCK-----
    PatternEntry(name="pgp_private_keys", pattern=r"-----BEGIN PGP PRIVATE KEY BLOCK-----"),
    # Example: -----BEGIN CERTIFICATE-----
    PatternEntry(name="certificates", pattern=r"-----BEGIN CERTIFICATE-----"),
    # Date of birth patterns
    # Example: 03/15/1985, 12-25-1990
    PatternEntry(
        name="date_of_birth_us",
        pattern=r"\b(?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])[-/](?:19|20)\d{2}\b",
    ),
    # Example: 1985-03-15, 1990/12/25
    PatternEntry(
        name="date_of_birth_iso",
        pattern=r"\b(?:19|20)\d{2}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12]\d|3[01])\b",
    ),
    # US Identification Numbers
    # Example: 123456789, A12345678
    PatternEntry(name="us_passport_numbers", pattern=r"\b[A-Z]?\d{6,9}\b"),
    # Example: CA12345678, NY123456789012
    PatternEntry(
        name="drivers_license",
        pattern=r"\b[A-Z]{1,2}\d{3,8}[-\s]?\d{2,5}[-\s]?\d{2,5}[-\s]?\d{1,5}[-\s]?\d?\b",
    ),
    # Example: 12345678901234567, 987654321
    # More restrictive: must be at least 10 digits to avoid catching common numbers
    PatternEntry(name="bank_account_numbers", pattern=r"\b\d{10,17}\b"),
    # Example: 121000248, 011000015
    PatternEntry(
        name="aba_routing_numbers",
        pattern=r"\b((0[0-9])|(1[0-2])|(2[1-9])|(3[0-2])|(6[1-9])|(7[0-2])|80)([0-9]{7})\b",
    ),
    # Example: 1234567890A, 9876543210Z
    PatternEntry(name="health_insurance_numbers", pattern=r"\b\d{10}[A-Z]\b"),
    # Example: EMP-123456, EMPLOYEE 7890123, E12345
    PatternEntry(
        name="employee_ids",
        pattern=r"\b(?:[Ee][Mm][Pp]|[Ee][Mm][Pp][Ll][Oo][Yy][Ee][Ee]|[Ee])[-\s]?\d{5,8}\b",
    ),
    # Example: 12-3456789, 98-7654321
    PatternEntry(name="tax_ein", pattern=r"\b\d{2}-\d{7}\b"),
    # Example: 1EG4-TE5-MK73, 2AB7-CD8-EF90
    PatternEntry(
        name="medicare_beneficiary_id",
        pattern=r"\b[1-9][A-Z][A-Z0-9]\d-[A-Z][A-Z0-9]\d-[A-Z][A-Z0-9]\d{2}\b",
    ),
    # Example: 1234567890, 1987654321
    PatternEntry(name="national_provider_id", pattern=r"\b1\d{9}\b"),
    # Example: AB1234567, XY9876543
    PatternEntry(name="dea_numbers", pattern=r"\b[A-Z]{2}\d{7}\b"),
    # Example: 912-70-1234, 987 80 5678
    PatternEntry(name="itin", pattern=r"\b9\d{2}(?:[ \-]?)[7,8]\d(?:[ \-]?)\d{4}\b"),
    # Vehicle and Location
    # Example: 1HGBH41JXMN109186, JH4TB2H26CC000000
    PatternEntry(name="vin_numbers", pattern=r"\b[A-HJ-NPR-Z0-9]{17}\b"),
    # Example: 40.7128, -74.0060 (NYC coordinates)
    PatternEntry(
        name="coordinates",
        pattern=r"\b[-+]?(?:[0-8]?\d(?:\.\d+)?|90(?:\.0+)?),\s*[-+]?(?:1[0-7]\d(?:\.\d+)?|180(?:\.0+)?|[0-9]?\d(?:\.\d+)?)\b",
    ),
    # Example: ABC-1234, 123-DEF, 7ABC123
    PatternEntry(
        name="us_license_plates",
        pattern=r"\b[A-Z]{1,3}[-\s]\d{1,4}[A-Z]?\b|\b\d{1,2}[A-Z]{1,3}\d{1,4}\b",
    ),
    # Example: 90210, 10001-1234
    PatternEntry(name="us_zip_codes", pattern=r"\b(\d{5}-\d{4}|\d{5})\b"),
    # Example: 123 Main Street, Anytown CA 90210
    PatternEntry(
        name="us_street_addresses",
        pattern=r"\b\d{1,8}\b[\s\S]{10,100}?\b(AK|AL|AR|AZ|CA|CO|CT|DC|DE|FL|GA|HI|IA|ID|IL|IN|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VT|WA|WI|WV|WY)\b\s\d{5}\b",
    ),
    # International Banking
    # Example: GB82WEST12345698765432, DE89370400440532013000
    PatternEntry(name="iban", pattern=r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b"),
    # Example: CHASUS33XXX, DEUTDEFF500
    # SWIFT BIC: 4 letter bank code + 2 letter country + 2 char location + optional 3 char branch
    PatternEntry(name="swift_bic", pattern=r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b"),
    # Additional API Keys and Tokens
    # Example: ya29.a0AfH6SMC1234567890abcdefghijklmnopqrstuvwxyz
    PatternEntry(name="google_oauth", pattern=r"\bya29\.[a-zA-Z0-9_-]{60,}\b"),
    # Example: AAAAabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
    PatternEntry(name="firebase_tokens", pattern=r"\bAAAA[A-Za-z0-9_-]{100,}\b"),
    # Example: 123456789012-abcdefghijklmnop.apps.googleusercontent.com
    PatternEntry(name="google_app_ids", pattern=r"\b[0-9]+-\w+\.apps\.googleusercontent\.com\b"),
    # Example: facebook_secret: "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
    PatternEntry(
        name="facebook_secrets",
        pattern=(
            r"\b(facebook_secret|FACEBOOK_SECRET|facebook_app_secret|FACEBOOK_APP_SECRET)"
            r"[a-z_ =\s\"'\:]{0,5}[^a-zA-Z0-9][a-f0-9]{32}[^a-zA-Z0-9]"
        ),
    ),
    # Example: github_token: "ghp_1234567890abcdef1234567890abcdef12345678"
    PatternEntry(
        name="github_keys",
        pattern=(
            r"\b(GITHUB_SECRET|GITHUB_KEY|github_secret|github_key|github_token|GITHUB_TOKEN|"
            r"github_api_key|GITHUB_API_KEY)[a-z_ =\s\"'\:]{0,10}[^a-zA-Z0-9][a-zA-Z0-9]{40}[^a-zA-Z0-9]"
        ),
    ),
    # Example: heroku_api_key: "12345678-1234-1234-1234-123456789012"
    PatternEntry(
        name="heroku_keys",
        pattern=(
            r"\b(heroku_api_key|HEROKU_API_KEY|heroku_secret|HEROKU_SECRET)"
            r"[a-z_ =\s\"'\:]{0,10}[^a-zA-Z0-9-]\w{8}(?:-\w{4}){3}-\w{12}[^a-zA-Z0-9\-]"
        ),
    ),
    # Example: slack_api_key: "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
    PatternEntry(
        name="slack_api_keys",
        pattern=(
            r"\b(slack_api_key|SLACK_API_KEY|slack_key|SLACK_KEY)"
            r"[a-z_ =\s\"'\:]{0,10}[^a-f0-9][a-f0-9]{32}[^a-f0-9]"
        ),
    ),
    # Example: xoxp-1234567890-1234567890123-abcdefghijklmnopqrstuvwx
    PatternEntry(name="slack_api_tokens", pattern=r"\b(xox[pb](?:-[a-zA-Z0-9]+){4,})\b"),
    # Extended Private Keys and Certificates
    # Example: -----BEGIN DSA PRIVATE KEY-----
    PatternEntry(
        name="dsa_private_keys",
        pattern=r"-----BEGIN DSA PRIVATE KEY-----(?:[a-zA-Z0-9\+\=\/\"']|\s)+?-----END DSA PRIVATE KEY-----",
    ),
    # Example: -----BEGIN EC PRIVATE KEY-----
    PatternEntry(
        name="ec_private_keys",
        pattern=(
            r"-----BEGIN (?:EC|ECDSA) PRIVATE KEY-----(?:[a-zA-Z0-9\+\=\/\"']|\s)+?"
            r"-----END (?:EC|ECDSA) PRIVATE KEY-----"
        ),
    ),
    # Example: -----BEGIN ENCRYPTED PRIVATE KEY-----
    PatternEntry(
        name="encrypted_private_keys",
        pattern=r"-----BEGIN ENCRYPTED PRIVATE KEY-----(?:.|\s)+?-----END ENCRYPTED PRIVATE KEY-----",
    ),
    # Example: -----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----
    PatternEntry(
        name="ssl_certificates",
        pattern=r"-----BEGIN CERTIFICATE-----(?:.|\n)+?\s-----END CERTIFICATE-----",
    ),
    # Example: ssh-dss AAAAB3NzaC1kc3MAAACBAP1/U4EddRIpUt9KnC7s5Of2EbdSPO9EAMMeP4C2USZpRV1AIlH7WT2NWPq/...
    PatternEntry(name="ssh_dss_public", pattern=r"\bssh-dss [0-9A-Za-z+/]+[=]{2}\b"),
    # Example: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7S3ItRlYQp... user@hostname
    PatternEntry(
        name="ssh_rsa_public",
        pattern=r"\bssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3} [^@]+@[^@]+\b",
    ),
    # Example: PuTTY-User-Key-File-2: ssh-rsa
    PatternEntry(
        name="putty_ssh_keys",
        pattern=r"PuTTY-User-Key-File-2: ssh-(?:rsa|dss)\s*Encryption: none(?:.|\s?)*?Private-MAC:",
    ),
    # International Phone Numbers
    # Example: +33 1 23 45 67 89, 0123456789
    PatternEntry(
        name="france_phone_numbers",
        pattern=r"\b([0O]?[1lI][1lI])?[3E][3E][0O]?[\dOIlZEASB]{9}\b",
    ),
    # Example: +49 30 12345678, 01791234567
    PatternEntry(name="german_phone_numbers", pattern=r"\b[\d\w]\d{2}[\d\w]{6}\d[\d\w]\b"),
    # Example: +44 20 7946 0958, 02079460958
    PatternEntry(
        name="uk_phone_numbers",
        pattern=r"\b([0O]?[1lI][1lI])?[4A][4A][\dOIlZEASB]{10,11}\b",
    ),
    # International IDs
    # Example: MORGA657054SM9IJ35
    PatternEntry(name="uk_drivers_license", pattern=r"\b[A-Z]{5}\d{6}[A-Z]{2}\d{1}[A-Z]{2}\b"),
    # Example: 1234567890GBR1234567U123456789
    PatternEntry(name="uk_passport", pattern=r"\b\d{10}GB[RP]\d{7}[UMF]{1}\d{9}\b"),
    # Example: 12.345.678, 98.765.432
    PatternEntry(name="argentina_dni", pattern=r"\b\d{2}\.\d{3}\.\d{3}\b"),
    # Example: TFN: 123456789, TFN 987654321
    PatternEntry(name="australia_tfn", pattern=r"\b[Tt][Ff][Nn](:|:\s|\s|)(\d{8,9})\b"),
    # Example: AB123456, CD987654
    PatternEntry(name="canada_passport", pattern=r"\b[\w]{2}[\d]{6}\b"),
    # Example: HR12345678901
    PatternEntry(name="croatia_vat", pattern=r"\bHR\d{11}\b"),
    # Example: CZ12345678, CZ1234567890
    PatternEntry(name="czech_vat", pattern=r"\bCZ\d{8,10}\b"),
    # Example: 1234567890, 123456-7890
    PatternEntry(name="denmark_personal_id", pattern=r"\b(?:\d{10}|\d{6}[-\s]\d{4})\b"),
    # Example: 123456789012
    PatternEntry(name="france_national_id", pattern=r"\b\d{12}\b"),
    # Example: 1234567890123, 1234567890123 45
    PatternEntry(name="france_ssn", pattern=r"\b(?:\d{13}|\d{13}\s\d{2})\b"),
    # Example: 12114567890
    PatternEntry(name="france_passport", pattern=r"\b\d{2}11\d{5}\b"),
    # Example: A1234567, B9876543
    PatternEntry(name="california_drivers_license", pattern=r"\b[A-Z]{1}\d{7}\b"),
    # Medical and Healthcare
    # Example: 12345-123-12, 1234-1234-1
    PatternEntry(name="hipaa_ndc", pattern=r"\b\d{4,5}-\d{3,4}-\d{1,2}\b"),
    # Security and Network
    # Example: CVE-2021-1234, CVE-2023-1234567
    PatternEntry(name="cve_numbers", pattern=r"\b[Cc][Vv][Ee]-\d{4}-\d{4,7}\b"),
    # Example: https://login.microsoftonline.com/common/oauth2/v2.0/token
    PatternEntry(
        name="microsoft_oauth",
        pattern=r"https://login\.microsoftonline\.com/common/oauth2/v2\.0/token|https://login\.windows\.net/common/oauth2/token",
    ),
    # Example: postgres://user:pass@host:5432/db
    PatternEntry(
        name="postgres_connections",
        pattern=r"\b(?:[Pp][Oo][Ss][Tt][Gg][Rr][Ee][Ss]|[Pp][Gg][Ss][Qq][Ll])\:\/\/",
    ),
    # Example: https://app.box.com/s/abc123def456
    PatternEntry(name="box_links", pattern=r"https://app\.box\.com/[s|l]/\S+"),
    # Example: https://www.dropbox.com/s/abc123def456/file.txt
    PatternEntry(name="dropbox_links", pattern=r"https://www\.dropbox\.com/(?:s|l)/\S+"),
    # Credit Card Variants
    # Example: 371449635398431, 378282246310005
    PatternEntry(name="amex_cards", pattern=r"\b3[47][0-9]{13}\b"),
    # Example: 4532015112830366, 4111111111111111
    PatternEntry(name="visa_cards", pattern=r"\b4[0-9]{12}(?:[0-9]{3})?\b"),
    # Example: 6011000990139424, 6455000000000000
    PatternEntry(
        name="discover_cards",
        pattern=r"\b65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}\b",
    ),
    # Example: 4532-0151-1283-0366, 5555 5555 5555 4444 123
    PatternEntry(
        name="enhanced_credit_cards",
        pattern=r"\b((4\d{3}|5[1-5]\d{2}|2\d{3}|3[47]\d{1,2})[\s\-]?\d{4,6}[\s\-]?\d{4,6}?([\s\-]\d{3,4})?(\d{3})?)\b",
    ),
    # Bank Routing Numbers (US specific)
    # Example: 321170538
    PatternEntry(name="bbva_routing_ca", pattern=r"^321170538$"),
    # Example: 121000358, 026009593
    PatternEntry(name="boa_routing_ca", pattern=r"^(?:121|026)00(?:0|9)(?:358|593)$"),
    # Example: 322271627
    PatternEntry(name="chase_routing_ca", pattern=r"^322271627$"),
    # Example: 321171184, 322271724
    PatternEntry(name="citibank_routing_ca", pattern=r"^32(?:11|22)71(?:18|72)4$"),
    # Example: 121122676, 122235821
    PatternEntry(name="usbank_routing_ca", pattern=r"^12(?:1122676|2235821)$"),
    # Example: 122243350
    PatternEntry(name="united_bank_routing_ca", pattern=r"^122243350$"),
    # Example: 121042882
    PatternEntry(name="wells_fargo_routing_ca", pattern=r"^121042882$"),
    # Unrealistic alphanumeric identifiers
    # Example: USER789012, use_234234dfw, aoaoao22_)32, asdasdad1234234r23rfv23523, 234234efsdfsf______@
    PatternEntry(
        name="generic_non_usual",
        pattern=r"(?:^|\s)(?=[A-Za-z0-9_\)\*\=@]*[A-Za-z])(?=[A-Za-z0-9_\)\*\=@]*[0-9])([A-Za-z0-9_\)\*\=@]{5,})(?=\s|$)",
    ),
]
