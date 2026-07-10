from __future__ import annotations

from app.config import get_settings
from app.infrastructure.ollama.ollama_client import OllamaClient


def main() -> None:
    settings = get_settings()
    client = OllamaClient(settings.ollama_base_url)
    print(f"health={client.health()}")
    models = [item.get("name") for item in client.list_models()]
    print("models=" + ", ".join(models))


if __name__ == "__main__":
    main()
