from .utils import get_config, match_format

import server
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)

class Request(server.Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = None


class Server(server.Server):
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
        id = request.groups[0]
    except ValueError:
        raise server.HTTPException("paste not found", code=404)

    record = await server.db.fetchrow("SELECT content, author FROM pastes WHERE id=$1", id)
    if not record:
        raise server.HTTPException("paste not found", code=404)

    request.set_body(dict(record))
    request.status = 200


@server.post("/api/pastes")
async def post_paste(request):
    body = request.body
    if not match_format(body, {"body": str, "lang": str}):
        raise server.HTTPException("invalid body format", code=400)
    
    id = generate_id()
    
    if request.author:
        await server.db.execute("INSERT INTO pastes (id, content, owner_id) values ($1, $2, $3)", id, body["body"], request.author.id)
    else:
        await server.db.execute("INSERT INTO pastes (id, content) values ($1, $2)", id, body["body"])

    request.set_body({"id": id})
    request.status = 201
