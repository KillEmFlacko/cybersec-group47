import json

from sanic import response
from sanic.views import HTTPMethodView

import secretsharing as ss
from lab_svr.tables import contacts, shares


class ShareView(HTTPMethodView):
    async def get(self, request):
        """
        Restituisce una response di carattere generico, usata per testare lo stato
        di funzionamento del server.
        :param request: Client request.
        :return: Response object.
        """
        return response.text("OK")

    async def post(self, request):
        """
        Gestisce le richieste di caricamento di nuovi share da parte degli utenti.
        :param request: Client request contenete lo share.
        :return: Response object.
        """
        # Vengono servite solo request contenenti json
        if request.content_type != 'application/json':
            response.text('FORBIDDEN', status=403)
        prs_js = json.loads(request.json)

        # Controllo che nel json siano presenti i campi attesi
        try:
            # ID associato all'evento di contatto
            # tra due utenti.
            cont_id = prs_js['contact_id']
            # Coordinate del punto nel polinomio,
            # cioè dello share.
            x = prs_js['share']['x']
            y = prs_js['share']['y']
        except KeyError:
            return response.text('ERROR', status=400)

        # Controllo se è presente uno share con lo stesso contact_id,
        # in modo da poter ricostruire il segreto, cioè la coppia
        # di EphID coinvolti nell contatto.
        get_shares_q = shares.select().where(shares.c.contact_id == cont_id)
        rows = await request.app.db.fetch_all(get_shares_q)

        query = None
        if len(rows) == 0:
            # Se non è stato trovato nessuno share, allora presumo che
            # questo sia uno share associato ad un nuovo contatto e quindi
            # lo aggiungo al database.
            query = shares.insert().values(contact_id=cont_id, x=x, y=y)
        elif len(rows) == 1:
            row = rows[0]
            # Nel caso sia stato già trovato uno share, controlliamo se è
            # diverso da quello che vogliamo caricare e in tal caso lo inseriamo.
            if row['x'] != x:
                query = shares.insert().values(contact_id=cont_id, x=x, y=y)
            else:
                response.text('FORBIDDEN', status=403)
        else:
            return response.text('FORBIDDEN', status=403)

        if query is not None: await request.app.db.execute(query)

        # Controllo se ci sono due share realtivi ad un contatto.
        rows = await request.app.db.fetch_all(get_shares_q)
        if len(rows) == 2:
            # Se ci sono due share allora ricostruisco il contatto/segreto.
            x1 = int.from_bytes(bytes.fromhex(rows[0]['x']), 'big')
            y1 = int.from_bytes(bytes.fromhex(rows[0]['y']), 'big')
            x2 = int.from_bytes(bytes.fromhex(rows[1]['x']), 'big')
            y2 = int.from_bytes(bytes.fromhex(rows[1]['y']), 'big')

            sh1 = [x1, y1]
            sh2 = [x2, y2]

            s = ss.recover_secret([sh1, sh2])
            s_b = s.to_bytes(32, 'big')

            # Il segreto contiene gli EphID concatenati.
            ephid1 = s_b[:16].hex()
            ephid2 = s_b[16:].hex()

            # Salvo il nuovo contatto nel database.
            query = contacts.insert().values(id=cont_id, ephid1=ephid1, ephid2=ephid2)
            await request.app.db.execute(query)
        return response.text('ACCEPTED')
