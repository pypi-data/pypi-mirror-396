#########################################################################
#             GNU HEALTH HOSPITAL MANAGEMENT - GTK CLIENT               #
#                      https://www.gnuhealth.org                        #
#########################################################################
#       The GNUHealth HMIS client based on the Tryton GTK Client        #
#########################################################################
#
# SPDX-FileCopyrightText: 2008-2024 The Tryton Community <info@tryton.org>
# SPDX-FileCopyrightText: 2017-2024 GNU Health Community <info@gnuhealth.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This file is part of GNU Health.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import base64
import json
import logging
import socket
import threading
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from gi.repository import GLib

from gnuhealth.config import CONFIG
from gnuhealth.jsonrpc import object_hook

logger = logging.getLogger(__name__)


ID = str(uuid.uuid4())
CHANNELS = [
    'client:%s' % ID,
]


def listen(connection):
    if not CONFIG['thread']:
        return
    listener = threading.Thread(
        target=_listen, args=(connection,), daemon=True)
    listener.start()


def _listen(connection):
    bus_timeout = CONFIG['client.bus_timeout']
    session = connection.session
    authorization = base64.b64encode(session.encode('utf-8'))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': b'Session ' + authorization,
    }

    wait = 1
    last_message = None
    url = None
    while connection.session == session:
        if url is None:
            if connection.url is None:
                time.sleep(1)
                continue
            url = connection.url + '/bus'
        request = Request(url,
                          data=json.dumps({
                              'last_message': last_message,
                              'channels': CHANNELS,
                          }).encode('utf-8'),
                          headers=headers)
        logger.info('poll channels %s with last message %s',
                    CHANNELS, last_message)
        try:
            response = urlopen(request, timeout=bus_timeout)
            wait = 1
        except socket.timeout:
            wait = 1
            continue
        except Exception as error:
            if isinstance(error, HTTPError):
                if error.code in (301, 302, 303, 307, 308):
                    url = error.headers.get('Location')
                    continue
                elif error.code == 501:
                    logger.info("Bus not supported")
                    break
            logger.error(
                "An exception occurred while connecting to the bus. "
                "Sleeping for %s seconds",
                wait, exc_info=error)
            time.sleep(min(wait, bus_timeout))
            wait *= 2
            continue

        if connection.session != session:
            break

        data = json.loads(response.read(), object_hook=object_hook)
        if data['message']:
            last_message = data['message']['message_id']
            GLib.idle_add(handle, data['message'])


def handle(message):
    from gnuhealth.gui.main import Main

    app = Main()
    if message['type'] == 'notification':
        app.show_notification(
            message.get('title', ''), message.get('body', ''),
            message.get('priority', 1))
