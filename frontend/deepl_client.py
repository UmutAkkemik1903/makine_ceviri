"""Utility script for interacting with the DeepL API.

The script demonstrates how to translate plain text (as well as XML/HTML)
and how to use the Write/Rephrase endpoint for text improvements. It expects
the DeepL authentication key to be stored in the environment variable
`DEEPL_API_KEY`. Optionally, the base API URL can be overridden via the
`DEEPL_API_BASE` environment variable.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from dotenv import load_dotenv
import requests

DEFAULT_BASE_URL = "https://api.deepl.com/v2"
FREE_BASE_URL = "https://api-free.deepl.com/v2"
TRANSLATE_PATH = "/translate"
REPHRASE_PATH = "/write/rephrase"


class DeepLClient:
    """Small helper wrapper around the DeepL REST endpoints."""

    def __init__(self, auth_key: str, base_url: Optional[str] = None) -> None:
        if not auth_key:
            raise ValueError("DeepL auth key must be provided")
        self.auth_key = auth_key
        chosen_base = base_url.strip() if base_url else DEFAULT_BASE_URL
        chosen_base = chosen_base.rstrip("/")
        if not chosen_base.endswith("/v2"):
            chosen_base = f"{chosen_base}/v2"
        self.base_url = chosen_base
        self.headers = {
            "Authorization": f"DeepL-Auth-Key {self.auth_key}",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        merged_headers = {**self.headers}
        if headers:
            merged_headers.update(headers)

        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            json=json_body,
            headers=merged_headers,
            timeout=30,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            # Surface API errors with body attached for easier debugging
            raise RuntimeError(
                f"DeepL API request failed ({exc.response.status_code}): {exc.response.text}"
            ) from exc

        if not response.content:
            return {}
        return response.json()

    def translate_text(
        self,
        text: Union[str, Sequence[str]],
        *,
        target_lang: str,
        source_lang: Optional[str] = None,
        preserve_formatting: bool = True,
        formality: Optional[str] = None,
    ) -> Union[str, List[str]]:
        """Translate text into the desired target language."""
        is_sequence = isinstance(text, Sequence) and not isinstance(text, (str, bytes))
        text_payload: List[str] = [str(item) for item in text] if is_sequence else [str(text)]
        payload: Dict[str, Any] = {
            "text": text_payload,
            "target_lang": target_lang,
        }
        if source_lang:
            payload["source_lang"] = source_lang
        if preserve_formatting:
            payload["preserve_formatting"] = 1
        if formality:
            payload["formality"] = formality

        result = self._request(
            "POST",
            TRANSLATE_PATH,
            data=payload,
        )
        translations: Iterable[Dict[str, Any]] = result.get("translations", [])
        if not translations:
            raise RuntimeError("DeepL translation response did not contain any results")
        translated_values = [item.get("text", "") for item in translations]
        if is_sequence:
            return translated_values
        return translated_values[0]

    def rephrase_text(
        self,
        text: str,
        *,
        target_lang: str,
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Use the Write/Rephrase endpoint for text improvements."""
        body: Dict[str, Any] = {
            "text": [text],
            "target_lang": target_lang,
        }
        if mode:
            body["mode"] = mode

        result = self._request(
            "POST",
            REPHRASE_PATH,
            json_body=body,
            headers={"Content-Type": "application/json"},
        )
        improvements = result.get("improvements", [])
        if not improvements:
            raise RuntimeError("DeepL rephrase response did not contain any improvements")
        return improvements[0]


def build_client_from_env() -> DeepLClient:
    # Load environment variables from a local .env file if present.
    load_dotenv()
    auth_key = os.getenv("DEEPL_API_KEY")
    if not auth_key:
        raise RuntimeError(
            "DEEPL_API_KEY environment variable is not set. Set it before running the script."
        )
    base_url = os.getenv("DEEPL_API_BASE")
    if base_url:
        base_url = base_url.rstrip("/")
    else:
        base_url = FREE_BASE_URL if auth_key.endswith(":fx") else DEFAULT_BASE_URL
    return DeepLClient(auth_key=auth_key, base_url=base_url)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interact with the DeepL API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    translate_parser = subparsers.add_parser("translate", help="Translate text")
    translate_parser.add_argument("text", help="Text to translate")
    translate_parser.add_argument(
        "--target-lang",
        default="TR",
        help="Target language code (default: TR)",
    )
    translate_parser.add_argument(
        "--source-lang",
        help="Optional source language code (auto-detected if omitted)",
    )
    translate_parser.add_argument(
        "--formality",
        choices=["default", "more", "less"],
        help="Adjust formality for supported languages",
    )

    rephrase_parser = subparsers.add_parser("rephrase", help="Improve text using Write API")
    rephrase_parser.add_argument("text", help="Text to improve")
    rephrase_parser.add_argument(
        "--target-lang",
        default="EN-US",
        help="Target language variant for the improved text (default: EN-US)",
    )
    rephrase_parser.add_argument(
        "--mode",
        choices=["default", "shorter", "longer", "simpler", "morePrecise"],
        help="Optional rephrase mode (requires DeepL Pro)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = build_client_from_env()

    if args.command == "translate":
        translated_text = client.translate_text(
            args.text,
            target_lang=args.target_lang,
            source_lang=args.source_lang,
            formality=None if args.formality == "default" else args.formality,
        )
        print(json.dumps({"translated_text": translated_text}, ensure_ascii=False, indent=2))
    elif args.command == "rephrase":
        improvement = client.rephrase_text(
            args.text,
            target_lang=args.target_lang,
            mode=None if args.mode == "default" else args.mode,
        )
        print(json.dumps({"improvement": improvement}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
