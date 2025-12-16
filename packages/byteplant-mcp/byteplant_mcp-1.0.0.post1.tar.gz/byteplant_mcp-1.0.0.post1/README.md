<!-- mcp-name: io.github.byteplant-dev/byteplant-mcp -->
# Byteplant Validator MCP Server
Email, Phone Number, and Address Validation for the Model Context Protocol (MCP)

This package provides an MCP server that uses Byteplant’s Email-Validator, Phone-Validator, and Address-Validator APIs to deliver real-time live validation in any MCP-compatible client.

## Features
- Email validation
- Phone number validation
- Postal address validation
- Fast studio MCP server 
- Local execution
- Easy integration with Claude Desktop

## Requirements
- Python ≥ 3.12
- A Byteplant API key (one for each validator). [You can register to get one here](https://www.byteplant.com/account/)
- MCP Client (e.g. Claude Desktop)


## MCP Configuration (Claude Desktop)
### 1. Installation
First, install the python module. You can use local installation (like `venv`) or global.
```bash
pip install byteplant-mcp
```
### 2. Configuration
Next, add the MCP server to Claude configuration.
```json
{
	"mcpServers": {
		"byteplant": {
			"command": "path/to/python/installation",
			"args": ["-m", "byteplant-mcp"],
			"env": {
				"EV_TOKEN": "<EMAIL VALIDATOR API TOKEN>",
				"PV_TOKEN": "<PHONE VALIDATOR API TOKEN>",
				"AV_TOKEN": "<ADDRESS VALIDATOR API TOKEN>"
			}
		}
	}
}	
```

## Byteplant's Email, Phone, and Address Validation Tools 
### 1. `validate_email`

## Real-Time Email Validation API

The Email Validation API returns the deliverability status and detailed information for the email that is provided as input.

---

## API Endpoint

| Parameter | Value |
|------|-------|
| **API URL** | `https://api.email-validator.net/api/verify` |
| **Method** | `GET` or `POST` |

### Example API Request (GET)

https://api.email-validator.net/api/verify?EmailAddress=support@byteplant.com&APIKey=your
 API key

---

## Input Parameters

| Parameter | Description |
|-----------|-------------|
| **EmailAddress** | Email address to validate (string). |
| **APIKey** | Your API key (string). |
| **Timeout** | Timeout in seconds (int). *Default:* `10` (min `5`, max `300`). |

---

## API Result (JSON)

| Parameter | Description |
|--------|-------------|
| **status** | API result code. `401`, `118`, `119` indicate API errors:<br>• `401` → Email address missing<br>• `118` → Rate Limit Exceeded<br>• `119` → API Key Invalid or Depleted |
| **info** | [Short status description.](https://www.byteplant.com/email-validator/validation-results.html) |
| **details** | [Full status description.](https://www.byteplant.com/email-validator/validation-results.html) |
| **freemail** | Indicates if email is from a freemail provider (`true` / `false`). |
| **ratelimit_remain** | Remaining API requests before rate limit is reached (default: 100 requests / 300s). |
| **ratelimit_seconds** | Seconds remaining in the current rate-limit interval. |


### 2. `validate_phone`

## Real-Time Phone Validation API

The Real-Time Phone Verification API validates a single phone number in real-time.  
It returns the status (`VALID_CONFIRMED`, `VALID_UNCONFIRMED`, `INVALID`) as well as details such as line type, carrier/operator, and location.

---

## API Endpoint

| Parameter | Value |
|------|-------|
| **API URL** | `https://api.phone-validator.net/api/v2/verify` |
| **Method** | `GET` or `POST` |

### Example API Request (GET)

https://api.phone-validator.net/api/v2/verify?PhoneNumber=09874-322466&CountryCode=de&APIKey=your
 API key

---

## Input Parameters

| Parameter | Description |
|-----------|-------------|
| **PhoneNumber** | Phone number to validate (string, URL encoded). Accepts national format or international format with leading `+` (`+` → `%2B`, space → `%20`). |
| **CountryCode** | Two-letter ISO 3166-1 country code (string). *Optional if number is in international format.* |
| **Locale** | IETF language tag for geocoding (string). *Optional; default:* `en-US`. |
| **Mode** | Validation mode (string): `express` (static checks) or `extensive` (full validation). *Optional; default:* `extensive`. |
| **APIKey** | Your API key (string). |
| **Timeout** | Timeout in seconds (int). *Optional; default:* `10` (min `5`, max `300`). |

---

## API Result (JSON)

| Parameter | Description |
|--------|-------------|
| **status** | `VALID_CONFIRMED`, `VALID_UNCONFIRMED`, `INVALID`, `DELAYED`, `RATE_LIMIT_EXCEEDED`, `API_KEY_INVALID_OR_DEPLETED` |
| **linetype** | `FIXED_LINE`, `MOBILE`, `VOIP`, `TOLL_FREE`, `PREMIUM_RATE`, `SHARED_COST`, `PERSONAL_NUMBER`, `PAGER`, `UAN`, `VOICEMAIL` |
| **location** | Geographical location (city, county, state). |
| **countrycode** | Two-letter ISO 3166-1 country code. |
| **formatnational** | Phone number in national format. |
| **formatinternational** | Phone number in international format. |
| **mcc** | Mobile Country Code (GSM/UMTS/LTE). |
| **mnc** | Mobile Network Code (GSM/UMTS/LTE). |
| **ratelimit_remain** | Remaining API requests before rate limit is hit (default limit: 100 requests / 300s). |
| **ratelimit_seconds** | Seconds remaining in current rate-limit interval. |


### 3 `validate_address`

## Real-Time Phone Validation API

The Address Validation API returns the deliverability status and detailed information for the address that is provided as input.

---

## API Endpoint

| Parameter     | Value |
|----------|-------|
| **API URL** | `https://api.address-validator.net/api/verify` |
| **Method**  | `GET` or `POST` |

---

### Example API Request (GET)

https://api.address-validator.net/api/verify?StreetAddress=Heilsbronner Str. 4&City=Neuendettelsau&PostalCode=91564&CountryCode=de&Geocoding=true&APIKey=your API key

## Input Parameters

| Parameter | Description |
|----------|-------------|
| **CountryCode** | Two-letter ISO 3166-1 country code (string). Use `'XX'` for international. |
| **StreetAddress** | Street/house number/building; may include unit/apartment info (string). |
| **StreetNumber** | House number/building (*optional*) (string).<br>House number/building may be part of `StreetAddress` or provided separately. |
| **AdditionalAddressInfo** | Building/unit/apt/floor etc. (*optional*) (string) |
| **City** | City or locality (city, district) (*optional*) (string) |
| **PostalCode** | ZIP / postal code (*optional*) (string) |
| **State** | State/province (*optional*) (string) |
| **Geocoding** | Enable Geocoding (`true`/`false`); default: `false` (*optional*) |
| **Locale** | Output language for countries with multiple postal languages—use only for translation; leave empty for validation. Default: local language (*optional*) |
| **OutputCharset** | Output character set: `us-ascii` or `utf-8` (default). (*optional*) |
| **APIKey** | Your API key (string) |
| **Timeout** | Timeout in seconds (default: 10s, min 5s, max 300s) (int) |

## General Usage Notes

Always use commas (",") to separate address elements where needed.

StreetAddress may contain the complete address; optional fields may be left empty.

### China / Japan / Korea

Native script: Use big → small order for all fields.

English script: Use small → big order for all fields.

## API Result (JSON)

| Parameter | Description |
|-------|-------------|
| **status** | VALID: address is correct and deliverable.<br>SUSPECT: address is incorrect and needs corrections to be deliverable, a suggested correction is provided.<br>INVALID: address is incorrect and not deliverable - either there is no match at all in the reference data or the address is ambiguous and there are many matches. In these cases automatic correction suggestions are not available.<br>DELAYED, NO_COUNTRY, RATE_LIMIT_EXCEEDED, API_KEY_INVALID_OR_DEPLETED, RESTRICTED, INTERNAL_ERROR |
| **formattedaddress** | Full address in standardized format. |
| **supplement** | Additional address details (building / unit / apt / suite etc.). |
| **street** | Street address in standardized format. |
| **streetnumber** | Street number in standardized format. |
| **postalcode** | ZIP / postal code in standardized format. |
| **city** | City in standardized format. |
| **type** | Address type: S = Street address / P = P.O. Box, Pick-Up, or other delivery service. |
| **rdi** | Residential Delivery Indicator (Commercial / Residential). |
| **district** | District in standardized format. |
| **county** | County in standardized format. |
| **state** | State / province in standardized format. |
| **country** | Two-letter ISO 3166-1 country code. |
| **latitude** | Latitude (for valid addresses if Geocoding is enabled). |
| **longitude** | Longitude (for valid addresses if Geocoding is enabled). |
| **diagnostics** | Detailed diagnostic hints, indicating errors in the address input. |
| **corrections** | Detailed correction hints, indicating which parts of the address input have been fixed. |
| **ratelimit_remain** | Number of API requests remaining before the API rate limit is reached (default API rate limit allows 100 API requests in 300s). |
| **ratelimit_seconds** | Number of seconds remaining in the current rate limit interval. |

## Environment Variables
- `EV_TOKEN`: Your Email Validator API Token
- `PV_TOKEN`: Your Phone Validator API Token
- `AV_TOKEN`: Your Address Validator API Token
You may use only the tokens for the services you use (e.g. only Email Validator), in that case leave the others tokens empty.

## Contact
- Website: https://www.byteplant.com
- Get your API key: https://www.byteplant.com/account/

- Email: contact@byteplant.com