from mcp.server.fastmcp import FastMCP
import os
import json
import requests

mcp = FastMCP("Byteplant MCP")

EV_TOKEN = os.environ.get("EV_TOKEN", "")
PV_TOKEN = os.environ.get("PV_TOKEN", "")
AV_TOKEN = os.environ.get("AV_TOKEN", "")


def make_data(data, error=None):
    out = {}
    if error:
        out["ok"] = False
        out["error"] = error
    else:
        out["ok"] = True
        out["data"] = data
    return out

def request_email(email, timeout):
    params = {
        "APIKey" : EV_TOKEN,
        "EmailAddress" : email,
        "Timeout" : timeout
    }
    try:
        data = json.loads(requests.post("https://api.email-validator.net/api/verify", params=params).text)
        return make_data(data)
    except Exception as e:
        return make_data(data=None, error=f"Error: {e}")


@mcp.tool()
def validate_email(email: str, timeout: int) -> str:
    """Validate email address

    Args:
        email: An email address to validate [required]
        timeout: timeout in seconds (int) [optional; default 10s, min 5s, max 300s]
    """
    data = request_email(email, timeout)
    if not data['ok']:
        return data['error']
    data = data['data']
    res = "Byteplant Email Validation Report\n"
    if data.get("status"):
        res += f"Validation status code: {data.get('status')}\n"
    if data.get("info"):
        res += f"Validation info: {data.get('info')}\n"
    if data.get("freemail"):
        res += f"Is freemai: {data.get('freemail')}\n"
    if data.get("ratelimit_remain"):
        res += f"Number of API requests remaining before the API rate limit is reached: {data.get('ratelimit_remain')}\n"
    if data.get("ratelimit_seconds"):
        res += f"Number of seconds remaining in the current rate limit interval: {data.get('ratelimit_seconds')}\n"
    return res

def request_phone(phone, code, locale, mode, timeout):
    params = {
        "APIKey" : PV_TOKEN,
        "PhoneNumber" : phone,
        "CountryCode" : code, 
        "Locale" : locale,
        "Mode" : mode,
        "Timeout": timeout
    }
    try:
        data = json.loads(requests.post("https://api.phone-validator.net/api/v2/verify", params=params).text)
        return make_data(data)
    except Exception as e:
        return make_data(data=None, error=f"Error: {e}")


@mcp.tool()
def validate_phone(phone: str, code: str, locale: str, mode: str, timeout: int) -> str:
    """Validate phone number

    Args:
        phone: Phone number to validate [required]
        code: Two letter ISO 3166-1 country code [optional; if phone number is in international format, empty string if not specified]
        locale: IETF language tag for Geocoding (string) [optional; default 'en-US']
        mode: express (static checks only)/extensive (full validation) [optional; default = extensive]
        timeout: timeout in seconds (int) [optional; default 10s, min 5s, max 300s]
    """
    data = request_phone(phone, code, locale, mode, timeout)
    if not data['ok']:
        return data['error']
    data = data['data']
    res = "Byteplant Phone Number Validation Report\n"
    if data.get("status"):
        res += f"Validation status code: {data.get('status')}\n"
    if data.get("linetype"):
        res += f"Line type: {data.get('linetype')}\n"
    if data.get("location"):
        res += f"Geographical location (city, county, state): {data.get('location')}\n"
    if data.get("countrycode"):
        res += f"Two letter ISO 3166-1 country code: {data.get('countrycode')}\n"
    if data.get("formatnational"):
        res += f"Phone number in national format: {data.get('formatnational')}\n"
    if data.get("formatinternational"):
        res += f"Phone number in international format: {data.get('formatinternational')}\n"
    if data.get("mcc"):
        res += f"Mobile country code to identify a mobile network operator (carrier) using the GSM (including GSM-R), UMTS, and LTE networks : {data.get('mcc')}\n"
    if data.get("formatinternational"):
        res += f"Mobile network code to identify a mobile network operator (carrier) using the GSM (including GSM-R), UMTS, and LTE networks : {data.get('mnc')}\n"
    if data.get("ratelimit_remain"):
        res += f"Number of API requests remaining before the API rate limit is reached: {data.get('ratelimit_remain')}\n"
    if data.get("ratelimit_seconds"):
        res += f"Number of seconds remaining in the current rate limit interval: {data.get('ratelimit_seconds')}\n"
    return res

def request_address(code, street_adr, street_num, additional_info, city, postal, state, geocoding, locale, charset, timeout):
    params = {
        "APIKey" : AV_TOKEN,
        "CountryCode" : code,
        "StreetAddress" : street_adr, 
        "StreetNumber" : street_num,
        "AdditionalAddressInfo" : additional_info,
        "City": city,
        "PostalCode" : postal,
        "State" : state, 
        "Geocoding" : "true" if geocoding == True else "false",
        "Locale" : locale,
        "OutputCharset": charset,
        "Timeout": timeout
    }
    try:
        data = json.loads(requests.post("https://api.address-validator.net/api/verify", params=params).text)
        return make_data(data)
    except Exception as e:
        return make_data(data=None, error=f"Error: {e}")



@mcp.tool()
def validate_address(code: str, street_adr: str, street_num: str, additional_info: str, city: str, postal: str, state: str, geocoding: bool, locale: str, charset: str, timeout: int) -> str:
    """Validate address

    Args:
        code: two-letter ISO 3166-1 country code (string), set to 'XX' for international [required]
        street_adr: street/housenumber/building, may include unit/apt etc. (string)[required]
        street_num: housenumber/building [optional] (string), housenumber/building can either be part of StreetAddress or be provided separately.
        additional_info: building/unit/apt/floor etc. [optional] (string)
        city: city or locality (city, district) [optional] (string)
        postal: zip/postal code [optional] (string)
        State: state/province [optional] (string)
        geocoding: enable Geocoding [true|false]; default: false [optional] (bool)
        locale: output language for countries with multiple postal languages - use only to translate addresses, always leave empty for address validation [IETF language tag]; default: local language [optional] (string)
        charset: output character set [us-ascii|utf-8]; default: 'utf-8' [optional] (string)
        timeout: timeout in seconds (int) [optional; default 10s, min 5s, max 300s]
    """
    data = request_address(code, street_adr, street_num, additional_info, city, postal, state, geocoding, locale, charset, timeout)
    if not data['ok']:
        return data['error']
    data = data['data']
    res = "Byteplant Address Validation Report\n"
    if data.get("status"):
        res += "Validation status: "
        if data.get('status') == "VALID":
            res += "VALID: address is correct and deliverable.\n"
        elif data.get('status') == "SUSPECT":
            res += "SUSPECT: address is incorrect and needs corrections to be deliverable, a suggested correction is provided.\n"
        elif data.get('status') == "INVALID":
            res += "INVALID: address is incorrect and not deliverable - either there is no match at all in the reference data or the address is ambiguous and there are a lot of different matches. In these cases automatic correction suggestions are not available.\n"
        else:
            res += f"{data.get('status')}\n"
    if data.get("formattedaddress"):
        res += f"Full address in standardized format: {data.get('formattedaddress')}\n"
    if data.get("supplement"):
        res += f"Additional address details (building / unit / apt / suite etc.): {data.get('supplement')}\n"
    if data.get("street"):
        res += f"Street address in standardized format: {data.get('street')}\n"
    if data.get("streetnumber"):
        res += f"Street number in standardized format: {data.get('streetnumber')}\n"
    if data.get("postalcode"):
        res += f"Zip / postal code in standardized format: {data.get('postalcode')}\n"
    if data.get("city"):
        res += f"City in standardized format: {data.get('city')}\n"
    if data.get("rdi"):
        res += f"Residential Delivery Indicator (Commercial / Residential): {data.get('rdi')}\n"
    if data.get("district"):
        res += f"District in standardized format: {data.get('district')}\n"
    if data.get("county"):
        res += f"County in standardized format: {data.get('county')}\n"
    if data.get("state"):
        res += f"State / province in standardized format: {data.get('state')}\n"
    if data.get("country"):
        res += f"Two-letter ISO 3166-1 country code: {data.get('country')}\n"
    if data.get("latitude"):
        res += f"Latitude: {data.get('latitude')}\n"
    if data.get("longitude"):
        res += f"longitude: {data.get('longitude')}\n"
    if data.get("diagnostics"):
        res += f"Diagnostic hints, indicating errors in the address input: {data.get('diagnostics')}\n"
    if data.get("corrections"):
        res += f"Correction hints, indicating which parts of the address input have been fixed: {data.get('corrections')}\n"
    if data.get("ratelimit_remain"):
        res += f"Number of API requests remaining before the API rate limit is reached: {data.get('ratelimit_remain')}\n"
    if data.get("ratelimit_seconds"):
        res += f"Number of seconds remaining in the current rate limit interval: {data.get('ratelimit_seconds')}\n"

    return res

def main():
    mcp.run(transport="stdio")