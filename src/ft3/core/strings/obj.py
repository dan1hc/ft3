"""Strings objects."""

__all__ = (
    'Pattern',
    'KeyValueRedactionPattern',
    'KeyValueRedactionPatterns',
    'RedactionPattern',
    'RedactionPatterns',
    'StringWrapper',
    )

from . import cfg
from . import lib


class Constants(cfg.Constants):
    """Constants specific to this file."""


class Pattern:
    """Compiled regex patterns."""

    SnakeToCamelReplacements = lib.re.compile(r'(_[a-z0-9])')
    """
    Matches all lower case alphanumeric characters following any \
    non-leading underscore.

    ---

    Note: match is inclusive of underscores to improve substitution \
    performance.

    """

    CamelToSnakeReplacements = lib.re.compile(
        r'[A-Z0-9]([0-9]+|[a-z]+|([0-9][a-z])+)'
        )
    """Matches all Title Case and numeric components."""

    camelCase = lib.re.compile(r'^[a-z]+((\d)|([A-Z0-9][a-z0-9]{1,128})){0,32}$')
    """
    Matches strict [lower] camelCase (i.e. RESTful casing) according to \
    the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html#s5.3-camel-case).

    ---

    Unlike Google, does NOT allow for an optional uppercase character at \
    the end of the string.

    Strings with more than32IndividualWords or \
    withWordsLongerThan128Characters will not be matched.

    """

    snake_case = lib.re.compile(r'^[a-z0-9_]{1,4096}$')
    """
    Matches strict [lower] snake_case (i.e. python instance \
    / attribute / function casing).

    ---

    Strings longer than 4096 characters will not be matched.

    """

    DateTime = lib.re.compile(
        r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
        '('
            r'[ T][0-9]{2}:[0-9]{2}:[0-9]{2}'
            r'(\.([0-9]{1,6}))?'
        ')?'
        r'([+-][0-9]{2}:[0-9]{2})?'
        )
    """
    Matches valid python `datetime` strings.

    ---

    Note: validity is determined by parsability `fromisoformat()`.

    """

    Number = lib.re.compile(
        '^'
        '('
            r'[+-]?'
            r'([0-9](_?[0-9]){0,63})?'
            r'(\.)?'
            r'[0-9](_?[0-9]){0,63}'
            r'(e[+-]?[0-9](_?[0-9]){0,63})?'
        ')'
        '('
            'j'
            '|'
            '('
                r'[+-]'
                r'([0-9](_?[0-9]){0,63})?'
                r'(\.)?'
                r'[0-9](_?[0-9]){0,63}'
                r'(e[+-]?[0-9](_?[0-9]){0,63})?'
                'j'
            ')'
        ')?'
        '$'
        )
    """
    Matches integers, floats, scientific notation, and complex numbers.

    ---

    Supports precision up to 64 digits either side of a decimal point.

    Recognizes valid, pythonic underscore usage as well.

    """


class RedactionPattern:
    """
    Regex patterns to redact common, sensitive data.

    Sourced from trivy / aqua.
    https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/secret/builtin-rules.go

    """

    aws_access_key_id = lib.re.compile(
        r'(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|'
        r'AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'
        )
    github_pat = lib.re.compile(r'ghp_[0-9a-zA-Z]{36}')
    github_oauth = lib.re.compile(r'gho_[0-9a-zA-Z]{36}')
    github_app_token = lib.re.compile(r'(ghu|ghs)_[0-9a-zA-Z]{36}')
    github_refresh_token = lib.re.compile(r'ghr_[0-9a-zA-Z]{76}')
    github_fine_grained_pat = lib.re.compile(
        r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}'
        )
    gitlab_pat = lib.re.compile(r'glpat-[0-9a-zA-Z\-\_]{20}')
    private_key = lib.re.compile(
        r'(?i)-----\s*?BEGIN[ A-Z0-9_-]*?PRIVATE KEY( BLOCK)?\s*?-----[\s]*?'
        r'(?P<secret>[\sA-Za-z0-9=+/\\\r\n]+)[\s]*?-----\s*?END[ A-Z0-9_-]*?'
        r' PRIVATE KEY( BLOCK)?\s*?-----'
        )
    shopify_token = lib.re.compile(r'shp(ss|at|ca|pa)_[a-fA-F0-9]{32}')
    slack_access_token = lib.re.compile(r'xox[baprs]-([0-9a-zA-Z]{10,48})')
    stripe_publishable_token = lib.re.compile(
        r'(?i)pk_(test|live)_[0-9a-z]{10,32}'
        )
    stripe_secret_token = lib.re.compile(
        r'(?i)sk_(test|live)_[0-9a-z]{10,32}'
        )
    pypi_upload_token = lib.re.compile(
        r'pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\-_]{50,1000}'
        )
    gcp_service_account = lib.re.compile(r'\"type\": \"service_account\"')
    heroku_api_key = lib.re.compile(
        r'(?i)(?P<key>heroku[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]'
        r'{4}-[0-9A-F]{12})[\'\"]'
        )
    slack_web_hook = lib.re.compile(
        r'https:\/\/hooks\.slack\.com\/services\/[A-Za-z0-9+\/]{44,48}'
        )
    twilio_api_key = lib.re.compile(r'SK[0-9a-fA-F]{32}')
    age_secret_key = lib.re.compile(
        r'AGE-SECRET-KEY-1[QPZRY9X8GF2TVDW0S3JN54KHCE6MUA7L]{58}'
        )
    facebook_token = lib.re.compile(
        r'(?i)(?P<key>facebook[a-z0-9_ .\-,]{0,25})'
        r'(=|>|:=|\|\|:|<=|=>|:).{0,5}[\'\"](?P<secret>[a-f0-9]{32})[\'\"]'
        )
    twitter_token = lib.re.compile(
        r'(?i)(?P<key>twitter[a-z0-9_ .\-,]{0,25})'
        r'(=|>|:=|\|\|:|<=|=>|:).{0,5}[\'\"](?P<secret>[a-f0-9]{35,44})[\'\"]'
        )
    adobe_client_id = lib.re.compile(
        r'(?i)(?P<key>adobe[a-z0-9_ .\-,]{0,25})'
        r'(=|>|:=|\|\|:|<=|=>|:).{0,5}[\'\"](?P<secret>[a-f0-9]{32})[\'\"]'
        )
    adobe_client_secret = lib.re.compile(r'(?i)(p8e-)[a-z0-9]{32}')
    alibaba_access_key_id = lib.re.compile(
        r'(?i)([^0-9A-Za-z]|^)(?P<secret>(LTAI)[a-z0-9]{20})([^0-9A-Za-z]|$)'
        )
    alibaba_secret_key = lib.re.compile(
        r'(?i)(?P<key>alibaba[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{30})[\'\"]'
        )
    asana_client_id = lib.re.compile(
        r'(?i)(?P<key>asana[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[0-9]{16})[\'\"]'
        )
    asana_client_secret = lib.re.compile(
        r'(?i)(?P<key>asana[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{32})[\'\"]'
        )
    atlassian_api_token = lib.re.compile(
        r'(?i)(?P<key>atlassian[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{24})[\'\"]'
        )
    bitbucket_client_id = lib.re.compile(
        r'(?i)(?P<key>bitbucket[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{32})[\'\"]'
        )
    bitbucket_client_secret = lib.re.compile(
        r'(?i)(?P<key>bitbucket[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9_\-]{64})[\'\"]'
        )
    beamer_api_token = lib.re.compile(
        r'(?i)(?P<key>beamer[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>b_[a-z0-9=_\-]{44})[\'\"]'
        )
    clojars_api_token = lib.re.compile(r'(?i)(CLOJARS_)[a-z0-9]{60}')
    contentful_delivery_api_token = lib.re.compile(
        r'(?i)(?P<key>contentful[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9\-=_]{43})[\'\"]'
        )
    databricks_api_token = lib.re.compile(r'dapi[a-h0-9]{32}')
    discord_api_token = lib.re.compile(
        r'(?i)(?P<key>discord[a-z0-9_ .\-,]{0,25})'
        r'(=|>|:=|\|\|:|<=|=>|:).{0,5}[\'\"](?P<secret>[a-h0-9]{64})[\'\"]'
        )
    discord_client_id = lib.re.compile(
        r'(?i)(?P<key>discord[a-z0-9_ .\-,]{0,25})'
        r'(=|>|:=|\|\|:|<=|=>|:).{0,5}[\'\"](?P<secret>[0-9]{18})[\'\"]'
        )
    discord_client_secret = lib.re.compile(
        r'(?i)(?P<key>discord[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9=_\-]{32})[\'\"]'
        )
    doppler_api_token = lib.re.compile(
        r'(?i)[\'\"](dp\.pt\.)[a-z0-9]{43}[\'\"]'
        )
    dropbox_api_secret = lib.re.compile(
        r'(?i)(dropbox[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"]([a-z0-9]{15})[\'\"]'
        )
    dropbox_short_lived_api_token = lib.re.compile(
        r'(?i)(dropbox[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](sl\.[a-z0-9\-=_]{135})[\'\"]'
        )
    dropbox_long_lived_api_token = lib.re.compile(
        r'(?i)(dropbox[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"][a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\-_=]{43}[\'\"]'
        )
    duffel_api_token = lib.re.compile(
        r'(?i)[\'\"]duffel_(test|live)_[a-z0-9_-]{43}[\'\"]'
        )
    dynatrace_api_token = lib.re.compile(
        r'(?i)[\'\"]dt0c01\.[a-z0-9]{24}\.[a-z0-9]{64}[\'\"]'
        )
    easypost_api_token = lib.re.compile(
        r'(?i)[\'\"]EZ[AT]K[a-z0-9]{54}[\'\"]'
        )
    fastly_api_token = lib.re.compile(
        r'(?i)(?P<key>fastly[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9\-=_]{32})[\'\"]'
        )
    finicity_client_secret = lib.re.compile(
        r'(?i)(?P<key>finicity[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{20})[\'\"]'
        )
    finicity_api_token = lib.re.compile(
        r'(?i)(?P<key>finicity[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-f0-9]{32})[\'\"]'
        )
    flutterwave_public_key = lib.re.compile(
        r'(?i)FLW(PUB|SEC)K_TEST-[a-h0-9]{32}-X'
        )
    flutterwave_enc_key = lib.re.compile(r'FLWSECK_TEST[a-h0-9]{12}')
    frameio_api_token = lib.re.compile(r'(?i)fio-u-[a-z0-9\-_=]{64}')
    gocardless_api_token = lib.re.compile(
        r'(?i)[\'\"]live_[a-z0-9\-_=]{40}[\'\"]'
        )
    grafana_api_token = lib.re.compile(
        r'(?i)[\'\"]eyJrIjoi[a-z0-9\-_=]{72,92}[\'\"]'
        )
    hashicorp_tf_api_token = lib.re.compile(
        r'(?i)[\'\"][a-z0-9]{14}\.atlasv1\.[a-z0-9\-_=]{60,70}[\'\"]'
        )
    hubspot_api_token = lib.re.compile(
        r'(?i)(?P<key>hubspot[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-h0-9]{8}-[a-h0-9]{4}-[a-h0-9]{4}-'
        r'[a-h0-9]{4}-[a-h0-9]{12})[\'\"]'
        )
    intercom_api_token = lib.re.compile(
        r'(?i)(?P<key>intercom[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9=_]{60})[\'\"]'
        )
    intercom_client_secret = lib.re.compile(
        r'(?i)(?P<key>intercom[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-h0-9]{8}-[a-h0-9]{4}-[a-h0-9]{4}-'
        r'[a-h0-9]{4}-[a-h0-9]{12})[\'\"]'
        )
    ionic_api_token = lib.re.compile(
        r'(?i)(ionic[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).{0,5}'
        r'[\'\"](ion_[a-z0-9]{42})[\'\"]'
        )
    jwt_token = lib.re.compile(
        r'ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9\/\\_-]{17,}\.'
        r'(?:[a-zA-Z0-9\/\\_-]{10,}={0,2})?'
        )
    linear_api_token = lib.re.compile(
        r'(?i)lin_api_[a-z0-9]{40}'
        )
    linear_client_secret = lib.re.compile(
        r'(?i)(?P<key>linear[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).'
        r'{0,5}[\'\"](?P<secret>[a-f0-9]{32})[\'\"]'
        )
    lob_api_key = lib.re.compile(
        r'(?i)(?P<key>lob[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).'
        r'{0,5}[\'\"](?P<secret>(live|test)_[a-f0-9]{35})[\'\"]'
        )
    lob_pub_api_key = lib.re.compile(
        r'(?i)(?P<key>lob[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).'
        r'{0,5}[\'\"](?P<secret>(test|live)_pub_[a-f0-9]{31})[\'\"]'
        )
    mailchimp_api_key = lib.re.compile(
        r'(?i)(?P<key>mailchimp[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).'
        r'{0,5}[\'\"](?P<secret>[a-f0-9]{32}-us20)[\'\"]'
        )
    mailgun_token = lib.re.compile(
        r'(?i)(?P<key>mailgun[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).'
        r'{0,5}[\'\"](?P<secret>(pub)?key-[a-f0-9]{32})[\'\"]'
        )
    mailgun_signing_key = lib.re.compile(
        r'(?i)(?P<key>mailgun[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:).'
        r'{0,5}[\'\"](?P<secret>[a-h0-9]{32}-[a-h0-9]{8}-[a-h0-9]{8})[\'\"]'
        )
    mapbox_api_token = lib.re.compile(
        r'(?i)(pk\.[a-z0-9]{60}\.[a-z0-9]{22})'
        )
    messagebird_api_token = lib.re.compile(
        r'(?i)(?P<key>messagebird[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{25})[\'\"]'
        )
    messagebird_client_id = lib.re.compile(
        r'(?i)(?P<key>messagebird[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-h0-9]{8}-[a-h0-9]{4}-[a-h0-9]{4}-[a-h0-9]'
        r'{4}-[a-h0-9]{12})[\'\"]'
        )
    new_relic_user_api_key = lib.re.compile(
        r'[\'\"](NRAK-[A-Z0-9]{27})[\'\"]'
        )
    new_relic_user_api_id = lib.re.compile(
        r'(?i)(?P<key>newrelic[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[A-Z0-9]{64})[\'\"]'
        )
    new_relic_browser_api_token = lib.re.compile(
        r'[\'\"](NRJS-[a-f0-9]{19})[\'\"]'
        )
    npm_access_token = lib.re.compile(r'(?i)[\'\"](npm_[a-z0-9]{36})[\'\"]')
    planetscale_password = lib.re.compile(r'(?i)pscale_pw_[a-z0-9\-_\.]{43}')
    planetscale_api_token = lib.re.compile(
        r'(?i)pscale_tkn_[a-z0-9\-_\.]{43}'
        )
    postman_api_token = lib.re.compile(r'(?i)PMAK-[a-f0-9]{24}\-[a-f0-9]{34}')
    pulumi_api_token = lib.re.compile(r'pul-[a-f0-9]{40}')
    rubygems_api_token = lib.re.compile(r'rubygems_[a-f0-9]{48}')
    sendgrid_api_token = lib.re.compile(r'(?i)SG\.[a-z0-9_\-\.]{66}')
    sendinblue_api_token = lib.re.compile(
        r'(?i)xkeysib-[a-f0-9]{64}\-[a-z0-9]{16}'
        )
    shippo_api_token = lib.re.compile(r'shippo_(live|test)_[a-f0-9]{40}')
    linkedin_client_secret = lib.re.compile(
        r'(?i)(?P<key>linkedin[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z]{16})[\'\"]'
        )
    linkedin_client_id = lib.re.compile(
        r'(?i)(?P<key>linkedin[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{14})[\'\"]'
        )
    twitch_api_token = lib.re.compile(
        r'(?i)(?P<key>twitch[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}[\'\"](?P<secret>[a-z0-9]{30})[\'\"]'
        )
    typeform_api_token = lib.re.compile(
        r'(?i)(?P<key>typeform[a-z0-9_ .\-,]{0,25})(=|>|:=|\|\|:|<=|=>|:)'
        r'.{0,5}(?P<secret>tfp_[a-z0-9\-_\.=]{59})'
        )
    dockerconfig_secret = lib.re.compile(
        r'(?i)(\.(dockerconfigjson|dockercfg):\s*\|*\s*('
        r'?P<secret>(ey|ew)+[A-Za-z0-9\/\+=]+))'
        )


RedactionPatterns: dict[str, lib.re.Pattern[str]] = {
    k.upper(): v
    for k, v
    in RedactionPattern.__dict__.items()
    if isinstance(v, lib.re.Pattern)
    }
"""
Regex patterns to redact common, sensitive data.

Sourced from trivy / aqua.
https://github.com/aquasecurity/trivy/blob/main/pkg/fanal/secret/builtin-rules.go

"""


class KeyValueRedactionPattern:
    """Regex patterns to redact common, sensitive data."""

    api_key_token = lib.re.compile(
        r'(api|secret)+.?(key|token)',
        flags=lib.re.IGNORECASE
        )
    """Matches common names for api keys, tokens, etc."""

    authorization_header = lib.re.compile(
        r'(authorization|bearer)+',
        flags=lib.re.IGNORECASE
        )
    """Matches an authorization / bearer token header."""

    conn_string_password = lib.re.compile(r'(:\/\/)+\w+(:[^:@]+)@')
    """Matches passwords in database connection strings."""

    credit_card = lib.re.compile(
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3'
        r'(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|'
        r'(?:2131|1800|35\d{3})\d{11})\b'
        )
    """Matches an [ostensibly] valid credit card number."""


KeyValueRedactionPatterns: dict[str, lib.re.Pattern[str]] = {
    k.upper(): v
    for k, v
    in KeyValueRedactionPattern.__dict__.items()
    if isinstance(v, lib.re.Pattern)
    }
"""Regex patterns to redact common, sensitive data."""


StringWrapper = lib.textwrap.TextWrapper(
    width=Constants.WRAP_WIDTH,
    break_long_words=True,
    break_on_hyphens=True,
    max_lines=Constants.CUTOFF_LEN,
    expand_tabs=False,
    replace_whitespace=False,
    drop_whitespace=False,
    tabsize=Constants.INDENT,
    placeholder=''
    )
"""Wraps long strings."""
