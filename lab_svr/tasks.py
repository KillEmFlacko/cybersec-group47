from datetime import timedelta, datetime

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from numpy.random._generator import Generator
from randomgen.aes import AESCounter
from sanic.log import logger
from sanic_scheduler import task
from sqlalchemy import text


def setup_tasks():
    """
    Configura i task da eseguire periodicamente.
    :return: None
    """
    # La funzione di hash utilizzata.
    hash_f = hashes.Hash(hashes.SHA256(), backend=default_backend())

    @task(start=timedelta(seconds=5), period=timedelta(days=1))
    async def daily_task(app):
        # Carico l'ultimo ID letto.
        try:
            f = open(app.config.ID_FILE, 'r')
            last_id = int(f.readline())
        except (IOError, ValueError):
            # Se non ho nessun nuovo ID allora li scarico tutti.
            last_id = -1

        # Invio la request al server principale per farmi restituire la lista degli SKt caricati
        # dall'ultimo controllo.
        params = {'last_id': last_id}
        resp = requests.get('https://' + app.config.MAIN_SVR + '/', params=params, verify=app.config.CA_DIR)

        rows_list = resp.json()['skts']
        # Itero sugli SKt ricevuti
        for rec in rows_list:
            # Per ogni SKt ricevuto calcolo quanti giorni è stato infetto, in
            # modo da generare i reletivi EphID.
            start_date = datetime.strptime(rec['start_date'], app.config.DATE_FORMAT)
            created_date = datetime.strptime(rec['created_date'], app.config.DATE_FORMAT)
            days = (created_date - start_date).days
            # Inizio l'SKt attuale da utilizzare nei controlli
            act_skt = bytes.fromhex(rec['skt'])
            # Vedo se è disponibile un nonce utilizzato per caricare
            # i dati al server degli epidemiologi.
            try:
                act_nonce = bytes.fromhex(rec['nonce'])
            except (TypeError, KeyError):
                act_nonce = None

            # Nel caso sia presente il nonce allora calcolo le x
            # utilizzate per generare gli share.
            hash_out_str = None
            if act_nonce is not None:
                h = hash_f.copy()
                h.update(act_skt + act_nonce)
                hash_out = h.finalize()
                hash_out_str = hash_out.hex()

            # Itero sui giorni in cui l'utente risultava infetto.
            for i in range(0, days):
                # Per ogni giorno predispongo il generatore per gli EphID
                prf = hmac.HMAC(act_skt, hashes.SHA256(), backend=default_backend())
                prf.update(b"broadcast key")
                prf_out = prf.finalize()
                bit_gen = AESCounter(key=int.from_bytes(prf_out[16:], "big"))
                gen = Generator(bit_gen)

                # Itero sulle n parti della giornata a cui corrisponde
                # un EphID
                for j in range(0, app.config.DAY_PARTS):
                    # Genero l'EphID prendendo i successimi 16 byte
                    ephid = gen.bytes(16)
                    # Predispongo la chiamata della funzione
                    # definita sul database e che si occupa di eliminare
                    # i contatti e gli share considerati non autentici.
                    query_txt = text('SELECT "DELETE_FAKE"(:ephid,:hash)')
                    query_txt = query_txt.bindparams(ephid=ephid.hex(), hash=hash_out_str)
                    result = await app.db.execute(query_txt)
                    if app.config.DEBUG:
                        logger.info('EphID : ' + ephid.hex() + ', SKt : ' + act_skt.hex())
                        logger.info("Fake contacts found : " + str(result) +
                                    ', Nonce : ' + str(act_nonce or 'None'))
                # Calcolo l'SKt del giorno successivo.
                h = hash_f.copy()
                h.update(act_skt)
                act_skt = h.finalize()

        # Nel caso abbia ricevuto nuovi SKt allora salvo
        # l'ID dell'ultimo SKt restituito dal server principale.
        if len(rows_list) > 0:
            f = open(app.config.ID_FILE, 'w')
            f.write(str(rows_list[-1]['id']))
