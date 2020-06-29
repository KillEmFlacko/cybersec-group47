from sanic.response import json
from project.lab_svr.tables import contacts


def setup_routes(app):
    @app.route("/")
    async def test(request):
        return json({"hello": "world"})

    @app.route("/contacts")
    async def contacts_list(request):
        query = contacts.select()
        rows = await request.lab_svr_app.db.fetch_all(query)
        return json({
            'contacts': [{row['ephid1']: row['ephid2']} for row in rows]
        })