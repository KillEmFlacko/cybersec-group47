import json
from datetime import datetime

from sanic import response
from sanic.log import logger
from sanic.views import HTTPMethodView

from main_svr.tables import infects


class MainView(HTTPMethodView):
    async def get(self, request):
        """
        Questo metodo si occupa di servire le richieste di nuovi SKt.
        :param request: Client request.
        :return: Response object.
        """
        # Nel caso non venga fornito il parametro last_id utilizziamo
        # questa request per controllare che il server sia in funzione.
        try:
            last_id = int(request.args['last_id'][0])
        except KeyError:
            return response.text("OK")
        logger.info("Requested SKts from : " + str(last_id))

        # Costruiamo la query per richiedere tutti gli SKt
        # con id maggiore dell'ultimo id letto dall'utente.
        query = infects.select().where(infects.c.id > last_id)
        rows = await request.app.db.fetch_all(query)

        # Restituiamo all'utente una response in formato json e
        # contenente tutti gli SKt successivi a last_id trovati nel database.
        return response.json({
            'skts': [{'id': row['id'], 'skt': row['skt'], 'nonce': row['nonce'],
                      'start_date': row['start_date'].isoformat(),
                      'created_date': row['created_date'].isoformat()} for row in rows]
        })

    async def post(self, request):
        """
        Questo metodo si occupa di servire i caricamenti di nuovi SKt sul database.
        :param request: Client reqeust.
        :return: Response object.
        """
        # Si accettano solamente request di tipo json
        if request.content_type != 'application/json':
            return response.text('BAD REQUEST', status=400)

        # Nel json vi saranno due campi obbligatori
        prs_js = json.loads(request.json)
        try:
            # L'SKt dell'utente segnalato infetto
            skt = prs_js['skt']
            # La data d'inizio dell'infezione #
            # (Solitamente 14 giorni prima dei sintomi)
            str_date = prs_js['start_date']
            start_date = datetime.strptime(str_date, request.app.config.DATE_FORMAT)
        except KeyError:
            return response.text('BAD REQUEST', status=400)

        # Vi sarà anche un campo opzionale: il nonce
        # utilizzato per la notifica dei contatti agli
        # epidemiologi.
        try:
            nonce = prs_js['nonce']
        except KeyError:
            # Nel caso il nonce non sia presente
            # significa che l'utente non ha dato
            # l'autorizzazione alla condivisione
            # dei dati con gli epidemiologi
            nonce = None

        # Controlliamo se si tratta di una notifica duplicata,
        # in tal caso la scartiamo
        query = infects.select().where(infects.c.skt == skt)
        rows = await request.app.db.fetch_all(query)

        if len(rows) > 0:
            return response.text('FORBIDDEN', status=403)

        # Se la notifica risulta valida, allora l'aggiungiamo al database
        if nonce is None:
            query = infects.insert().values(skt=skt, start_date=start_date)
        else:
            query = infects.insert().values(skt=skt, nonce=nonce, start_date=start_date)

        await request.app.db.execute(query)
        return response.text("OK")
