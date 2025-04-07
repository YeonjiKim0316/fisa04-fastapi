from fastapi import FastAPI

app = FastAPI()

# 아무것도 받지 않으면 손님이 뜨고, name에 뭔가 값을 전달하면 해당 값이 뜨도록 
@app.get("/welcome")
@app.get("/welcome/{name}")
def welcome(name: str="손님"):
    return {"name": name}