def check_http_status_code(response, extra_text=""):
    if response.status_code >= 300:
        txt = response.json() if response.status_code < 500 else response.text[:500]
        raise Exception(f"{extra_text} Some thing wrong {response.status_code}, {txt}")