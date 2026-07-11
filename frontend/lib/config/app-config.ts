export const appConfig = {
  name: "Modelo IA Carrera",
  backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000",
  defaultTopK: 5,
} as const;
