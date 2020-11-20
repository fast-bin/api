from .utils import get_config, match_format, generate_id

import server as http
import asyncpg

import logging
import json


logging.basicConfig(level=logging.INFO)

class Request(http.Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = None


class Server(http.Server):
    config = get_config()

    async def init(self):
        config = self.config["database"]
        
        self.db = await asyncpg.connect(**config)
    
    def get_request(self, *args, **kwargs):
        return Request(*args, **kwargs)


server = Server()

@server.get("/api/pastes/(.+)")
async def get_paste(request):
    try:
        id = int(request.groups[0])
    except ValueError:
        raise http.HTTPException("paste not found", code=404)

    record = await server.db.fetchrow("SELECT owner_id, content FROM pastes WHERE id=$1", id)
    if not record:
        raise http.HTTPException("paste not found", code=404)

    request.set_body(dict(record))
    request.status = 200


@server.post("/api/pastes")
async def post_paste(request):
    try:
        body = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        raise http.HTTPException("invalid body format", code=400)
    
    print(body)
    if "body" not in body:
        raise http.HTTPException("invalid body format", code=400)
    
    id = generate_id()
    
    if request.author:
        await server.db.execute("INSERT INTO pastes (id, content, owner_id) values ($1, $2, $3)", id, body["body"], request.author.id)
    else:
        await server.db.execute("INSERT INTO pastes (id, content) values ($1, $2)", id, body["body"])

    request.set_body({"id": id})
    request.status = 201
