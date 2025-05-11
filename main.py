from fastapi import FastAPI
from .routers import usuarios
#from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
def get_echo_test():
    return {"message": "Echo Test OK"}

app.include_router(usuarios.router)
