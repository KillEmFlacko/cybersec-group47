import json

from sanic import response
from sanic.views import HTTPMethodView

import secretsharing as ss
from lab_svr.tables import contacts, shares


class ShareView(HTTPMethodView):
    async def get(self, request):
        return response.text("OK")

    async def post(self, request):
        if request.content_type != 'application/json':
            response.text('FORBIDDEN',status=403)
        prs_js = json.loads(request.json)
        cont_id = prs_js['contact_id']
        x = prs_js['share']['x']
        y = prs_js['share']['y']
        get_shares_q = shares.select().where(shares.c.contact_id == cont_id)
        rows = await request.app.db.fetch_all(get_shares_q)

        query = None
        if len(rows) == 0:
            query = shares.insert().values(contact_id=cont_id, x=x, y=y)
        elif len(rows) == 1:
            row = rows[0]
            if row['x'] != x:
                query = shares.insert().values(contact_id=cont_id, x=x, y=y)
            else:
                response.text('FORBIDDEN',status=403)
        else:
            return response.text('FORBIDDEN',status=403)

        if query is not None: await request.app.db.execute(query)

        rows = await request.app.db.fetch_all(get_shares_q)
        if len(rows) == 2:
            x1 = int.from_bytes(bytes.fromhex(rows[0]['x']), 'big')
            y1 = int.from_bytes(bytes.fromhex(rows[0]['y']), 'big')
            x2 = int.from_bytes(bytes.fromhex(rows[1]['x']), 'big')
            y2 = int.from_bytes(bytes.fromhex(rows[1]['y']), 'big')

            sh1 = [x1, y1]
            sh2 = [x2, y2]

            s = ss.recover_secret([sh1, sh2])
            s_b = s.to_bytes(32, 'big')
            ephid1 = s_b[:16].hex()
            ephid2 = s_b[16:].hex()

            query = contacts.insert().values(id=cont_id, ephid1=ephid1, ephid2=ephid2)
            await request.app.db.execute(query)
        return response.text('ACCEPTED')
