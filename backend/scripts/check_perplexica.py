from __future__ import annotations

from app.config import get_settings
from app.infrastructure.web.perplexica_client import PerplexicaClient


def main() -> None:
    settings = get_settings()
    client = PerplexicaClient(settings.perplexica_url)
    print(f"perplexica_url={settings.perplexica_url}")
    print(f"health={client.health()}")
    providers = client.providers()
    print(f"providers={len(providers)}")
    for provider in providers:
        print(f"- {provider.get('name')} ({provider.get('id')})")


if __name__ == "__main__":
    main()
