import uvicorn


def dev() -> None:
    uvicorn.run(
        "authcore.main:app",  # module:app instance
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


def prod() -> None:
    uvicorn.run(
        "authcore.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
