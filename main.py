#!/usr/bin/env python
#
# Copyright Paulo Alem <biggahed@gmail.com>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
from google.appengine.ext import db


VERIFY_TOKEN = "yourkeyhere"

class Update(db.Model):
    body = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        """
        Echoes hub.challenge to confirm to facebook that this server is 
        configured to accept callbacks
        """
        if (self.request.get('hub.mode') == "subscribe"
        and self.request.get('hub.verify_token') == VERIFY_TOKEN
        and self.request.get('hub.challenge')):
            self.response.write(self.request.get('hub.challenge'))
        else:
            self.abort(400)

    def post(self):
        """
        Stores facebook updates
        """
        body = self.request.body
        update = Update()
        update.body = body
        update.put()

class ListHandler(webapp2.RequestHandler):
    def get(self):
        """
        Lists stored Facebook Updates

        GET Params:
        limit -- Number of updates to return
        """
        limit = self.request.get('limit', 10)
        logging.info(limit)
        updates = db.GqlQuery(
            "SELECT * "
            "FROM Update "
            "ORDER BY date DESC "
            "LIMIT {}".format(limit)
        )
        self.response.out.write("<h1>Last {} updates</h1>".format(limit))
        self.response.out.write("<ol>")
        for update in updates:
            self.response.out.write("<li>")
            self.response.out.write("<p>@{}</p>".format(update.date))
            self.response.out.write("<pre>{}</pre>".format(update.body))
            self.response.out.write("</li>")
        self.response.out.write("</ol>")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/list', ListHandler)
], debug=True)
