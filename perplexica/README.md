# Vane / Perplexica

Esta carpeta mantiene el nombre `perplexica` por compatibilidad del proyecto, pero el upstream actual es Vane.

Vane se ejecuta con Docker:

```powershell
.\scripts\run_vane.ps1
```

La UI queda en `http://localhost:3000`.
El SearXNG interno queda expuesto como fallback en `http://localhost:4000`.
Si Vane corre en Docker y Ollama corre en Windows, configura Ollama con:

```text
http://host.docker.internal:11434
```

Scripts:

- `scripts\run_vane.ps1`
- `scripts\stop_vane.ps1`
- `scripts\check_vane.ps1`
- `scripts\logs_vane.ps1`

## Instalacion validada

El contenedor usa la imagen:

```powershell
itzcrazykns1337/vane:latest
```

Comando equivalente:

```powershell
docker run -d -p 3000:3000 -p 4000:8080 -v vane-data:/home/vane/data --name vane itzcrazykns1337/vane:latest
```

La configuracion persistente queda en el volumen Docker `vane-data`.

## Pruebas

```powershell
Invoke-RestMethod http://localhost:3000/api/providers
Invoke-RestMethod "http://localhost:4000/search?q=OWASP%20Top%2010&format=json"
```

Resultado actual:

- `/api/providers` funciona y muestra el provider `http://host.docker.internal:11434`.
- `/api/search` queda en timeout en este equipo; el backend lo documenta y usa SearXNG como fallback controlado.
