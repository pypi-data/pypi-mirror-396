import requests

ENCODE_URL = "https://nishxnt-97--encode.modal.run"
DECODE_URL = "https://nishxnt-97--decode.modal.run"


def encode_bits(prompt: str, bits: str, **kwargs):
    payload = {
        "prompt": prompt,
        "bits": bits,
    }
    payload.update(kwargs)
    resp = requests.post(ENCODE_URL, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()  # {texts, tokens, ac_token_counts}


def decode_bits(prompt: str, tokens, ac_token_count=None, **kwargs):
    payload = {
        "prompt": prompt,
        "tokens": tokens,
        "ac_token_count": ac_token_count,
    }
    payload.update(kwargs)
    resp = requests.post(DECODE_URL, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()["bits"]
