from fastapi import FastAPI

app = FastAPI(
    title="API practica 1.1",
    description="Backend de la practica 1.1 desplegado en un contenedor Docker",
    version="0.1.0",
)


@app.get("/health", summary="Estado del servicio")
def health():
    return {"status": "ok"}


@app.get("/version", summary="Version de la API")
def version():
    return {"version": app.version}


@app.get("/ping", summary="Prueba de conexion")
def ping():
    return {"message": "pong"}
