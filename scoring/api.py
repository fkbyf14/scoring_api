#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from application_logic import MethodRequest, \
    get_score, get_interests, OnlineScoreRequest, ClientsInterestsRequest
from store import Store

LOGGING = ".logging/logging.log"
SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
        # ed24237f3302c9a49ad8a8ca7d25e27f77ee5a49e5ac066ce9fa38022f648af41dfe3c6a4b06908b66928a5dcb3565c6022b2c837f76769b1c96349b5e91a5b4
    else:
        digest = hashlib.sha512(str(request.account) + str(request.login) + SALT).hexdigest()
        # 55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95
    print digest
    if digest == str(request.token):
        return True
    return False


def method_handler(request, ctx, store):
    response = dict()
    body_of_request = request["body"]
    method_request = MethodRequest(body_of_request)

    if not method_request.is_valid():
        return method_request.errors, INVALID_REQUEST

    if not check_auth(method_request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    arguments = request["body"]["arguments"]

    if method_request.is_online_score:
        try:
            score_req = OnlineScoreRequest(arguments)

            if not score_req.is_valid():
                return score_req.errors, INVALID_REQUEST

            ctx["has"] = arguments.keys()

            if method_request.is_admin:
                response["score"] = int(ADMIN_SALT)
                return response, OK

            response["score"] = get_score(store, arguments)

            response, code = response, OK
        except Exception as e:
            return e.args, INVALID_REQUEST
    if method_request.is_clients_interests:

        try:
            interests_req = ClientsInterestsRequest(arguments)

            if not interests_req.is_valid():
                return interests_req.errors, INVALID_REQUEST

            ctx["nclients"] = len(arguments["client_ids"])
            response = get_interests(store, arguments)
            response, code = response, OK
        except Exception as e:
            return e.args, INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "online_score": method_handler,
        "clients_interests": method_handler
    }
    store = Store('localhost', 6379, 0)

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST
        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}

        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()

    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
