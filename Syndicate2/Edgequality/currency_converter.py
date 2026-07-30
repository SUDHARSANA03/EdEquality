"""
Currency to Indian Rupee (INR / ₹) Conversion Module
Provides both numerical rate-based conversion and text-based cultural currency adaptation.
"""

import re
from typing import Union, Tuple, Dict, Any

# Standard Exchange Rates to INR (Indian Rupee)
EXCHANGE_RATES_TO_INR: Dict[str, float] = {
    "USD": 83.50,   # US Dollar
    "EUR": 90.50,   # Euro
    "GBP": 106.00,  # British Pound
    "AUD": 54.50,   # Australian Dollar
    "CAD": 61.00,   # Canadian Dollar
    "JPY": 0.55,    # Japanese Yen
    "SGD": 62.00,   # Singapore Dollar
    "AED": 22.70,   # UAE Dirham
    "SAR": 22.20,   # Saudi Riyal
    "CHF": 94.00,   # Swiss Franc
    "CNY": 11.50,   # Chinese Yuan
    "RUB": 0.95,    # Russian Ruble
    "KRW": 0.062,   # South Korean Won
    "INR": 1.00     # Indian Rupee
}

# Mapping of symbols/aliases to standard currency codes
SYMBOL_TO_CODE: Dict[str, str] = {
    "$": "USD",
    "US$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "A$": "AUD",
    "C$": "CAD",
    "S$": "SGD",
    "₹": "INR",
    "Rs": "INR",
    "Rs.": "INR"
}

def convert_currency_amount(amount: float, source_currency: str = "USD") -> Dict[str, Any]:
    """
    Converts a numeric currency amount to Indian Rupees (INR / ₹).
    
    Args:
        amount: Numerical value in source currency.
        source_currency: Currency code or symbol (e.g. 'USD', 'EUR', '$', 'GBP').
        
    Returns:
        Dict containing original amount, source currency, converted INR amount, and formatted string.
    """
    code = source_currency.upper().strip()
    if code in SYMBOL_TO_CODE:
        code = SYMBOL_TO_CODE[code]
        
    rate = EXCHANGE_RATES_TO_INR.get(code, 83.50)  # Default fallback to USD rate
    inr_val = round(amount * rate, 2)
    
    return {
        "original_amount": amount,
        "source_currency": code,
        "exchange_rate_to_inr": rate,
        "inr_amount": inr_val,
        "formatted_inr": f"₹{inr_val:,.2f}"
    }

def _match_case(source_str: str, target_str: str) -> str:
    """Helper to match the case of source_str onto target_str."""
    if source_str.isupper():
        return target_str.upper()
    elif source_str.islower():
        return target_str.lower()
    elif source_str and source_str[0].isupper():
        return target_str.capitalize()
    return target_str

def convert_text_currency_to_rupee(text: str, convert_numerical: bool = False) -> Tuple[str, list]:
    """
    Converts currency references in text to Indian Rupees (₹ / Rupees).
    
    Args:
        text: Input text containing foreign currency references.
        convert_numerical: If True, converts currency values using real exchange rates (e.g. $10 -> ₹835.00).
                          If False, converts currency symbols/words while preserving original numbers (e.g. $10 -> ₹10).
                          
    Returns:
        Tuple of (converted_text, conversion_log)
    """
    if not text:
        return "", []

    log = []
    converted = text

    if convert_numerical:
        # Pattern for currency symbol + amount e.g. $10, $0.75, €50, £12.50, USD 100
        # Group 1: Symbol/Code, Group 2: Amount
        pattern = r'(\$|€|£|¥|A\$|C\$|S\$|USD|EUR|GBP|AUD|CAD|JPY|SGD|AED|SAR)\s*(\d+(?:\.\d+)?)\b'
        
        def rate_replacer(match):
            curr_str = match.group(1)
            amt_str = match.group(2)
            try:
                amt = float(amt_str)
                code = SYMBOL_TO_CODE.get(curr_str, curr_str.upper())
                res = convert_currency_amount(amt, code)
                replacement = f"₹{res['inr_amount']:,.2f}" if '.' in amt_str else f"₹{int(res['inr_amount']):,}"
                log.append({
                    "original": match.group(0),
                    "adapted": replacement,
                    "reason": f"Converted {match.group(0)} using rate 1 {code} = ₹{res['exchange_rate_to_inr']}"
                })
                return replacement
            except ValueError:
                return match.group(0)

        converted = re.sub(pattern, rate_replacer, converted, flags=re.IGNORECASE)

    # Word/symbol replacements (Cultural adaptation)
    word_replacements = [
        # Symbols (with optional trailing spaces before numbers)
        (r'\$\s*(?=\d)', '₹', "Converted '$' before amount to '₹'"),
        (r'€\s*(?=\d)', '₹', "Converted '€' before amount to '₹'"),
        (r'£\s*(?=\d)', '₹', "Converted '£' before amount to '₹'"),
        (r'¥\s*(?=\d)', '₹', "Converted '¥' before amount to '₹'"),
        (r'€', '₹', "Converted '€' symbol to '₹'"),
        (r'£', '₹', "Converted '£' symbol to '₹'"),
        (r'¥', '₹', "Converted '¥' symbol to '₹'"),
        
        # Currency codes
        (r'\bUSD\b', 'INR', "Converted currency code 'USD' to 'INR'"),
        (r'\bEUR\b', 'INR', "Converted currency code 'EUR' to 'INR'"),
        (r'\bGBP\b', 'INR', "Converted currency code 'GBP' to 'INR'"),
        (r'\bAUD\b', 'INR', "Converted currency code 'AUD' to 'INR'"),
        (r'\bCAD\b', 'INR', "Converted currency code 'CAD' to 'INR'"),
        (r'\bJPY\b', 'INR', "Converted currency code 'JPY' to 'INR'"),
        (r'\bSGD\b', 'INR', "Converted currency code 'SGD' to 'INR'"),
        (r'\bAED\b', 'INR', "Converted currency code 'AED' to 'INR'"),
        
        # Currency Words (Case sensitive via match_case handler)
        (r'\bdollars\b', 'rupees', "Converted 'dollars' to 'rupees'"),
        (r'\bdollar\b', 'rupee', "Converted 'dollar' to 'rupee'"),
        (r'\bcents\b', 'paise', "Converted 'cents' to 'paise'"),
        (r'\bcent\b', 'paisa', "Converted 'cent' to 'paisa'"),
        (r'\beuros\b', 'rupees', "Converted 'euros' to 'rupees'"),
        (r'\beuro\b', 'rupee', "Converted 'euro' to 'rupee'"),
        (r'\bpounds\b', 'rupees', "Converted 'pounds' to 'rupees'"),
        (r'\bpound\b', 'rupee', "Converted 'pound' to 'rupee'"),
        (r'\byen\b', 'rupees', "Converted 'yen' to 'rupees'"),
        (r'\bdirhams\b', 'rupees', "Converted 'dirhams' to 'rupees'"),
        (r'\bdirham\b', 'rupee', "Converted 'dirham' to 'rupee'")
    ]

    for pat, repl, reason in word_replacements:
        matches = list(re.finditer(pat, converted, re.IGNORECASE))
        if matches:
            for m in reversed(matches):
                orig = m.group(0)
                # Preserve capitalization
                target_repl = _match_case(orig, repl) if orig.isalpha() else repl
                span = m.span()
                converted = converted[:span[0]] + target_repl + converted[span[1]:]
                log.append({
                    "original": orig,
                    "adapted": target_repl,
                    "reason": reason
                })

    return converted, log


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== CURRENCY TO RUPEE CONVERTER DEMO ===")
    
    # 1. Single Amount Conversion Examples
    test_amounts = [(100, "USD"), (50, "EUR"), (25, "GBP"), (1000, "JPY"), (75, "AED")]
    print("\n--- Direct Amount Conversions ---")
    for amt, curr in test_amounts:
        res = convert_currency_amount(amt, curr)
        print(f"  {amt} {curr} = {res['formatted_inr']} (Rate: 1 {curr} = ₹{res['exchange_rate_to_inr']})")

    # 2. Text Adaptation Examples
    sample_text = (
        "John bought a book for $15.50 and a coffee for €4.00. "
        "In total, he spent 20 dollars. He also saved 50 cents. "
        "The price in Japan was 2500 Yen (USD 20)."
    )

    print("\n--- Text Conversion (Symbolic / Cultural) ---")
    adapted_text, logs = convert_text_currency_to_rupee(sample_text, convert_numerical=False)
    print(adapted_text)

    print("\n--- Text Conversion (Numeric Rate Conversion) ---")
    num_text, num_logs = convert_text_currency_to_rupee(sample_text, convert_numerical=True)
    print(num_text)
