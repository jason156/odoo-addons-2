# -*- coding: utf-8 -*-
##############################################################################
#    Copyright (c) 2016 - Open2bizz
#    Author: Open2bizz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
import requests
from urlparse import urlparse
from werkzeug.wrappers import Response
from odoo import http
import base64
from odoo.tools import config
import logging
logger = logging.getLogger(__name__)

import time

class Orbeon(http.Controller):
    orbeon_base_route = 'orbeon'
    
    @http.route('/%s/<path:path>' % orbeon_base_route, type='http', auth="user", csrf=False)
    def render_orbeon_page(self, path, redirect=None, **kw):
        print '++++++++++++:%s' % path
        orbeon_server = http.request.env["orbeon.server"].search_read([], ['url'])
        if len(orbeon_server) == 0:
            return 'Orbeon server not found'
        else :
            orbeon_server = orbeon_server[0]
        o = urlparse(orbeon_server['url'])
        
        odoo_session = http.request.session

        print '============%s' % http.request.httprequest.headers.items()
        orbeon_headers = ['cookie']
        in_headers = { name : value for (name, value) in http.request.httprequest.headers.items()
                   if name.lower() in orbeon_headers}
        
        in_headers.update({'Openerp-Server' : 'localhost'})
        in_headers.update({'Openerp-Port' : str(config.get('xmlrpc_port'))})
        in_headers.update({'Openerp-Database' :  odoo_session.get('db') })
        in_headers.update({'Authorization' : 'Basic %s' % base64.b64encode("%s:%s" % (odoo_session.get('login'), odoo_session.get('password')) ) } )
        
        logger.debug('Calling Orbeon on url %s with header %s' % (o.netloc, in_headers))
        curl = urlparse(http.request.httprequest.url)._replace(netloc=o.netloc)
        
        print('========>%s' % http.request.httprequest.method)
        print('========>%s' % http.request.httprequest.stream)
        print('========>%s' % http.request.httprequest.files)
#         if len(http.request.httprequest.files) > 0:
#             print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFILES!!!!!!!!!!!!!!!!!')
#             r=http.request.httprequest.stream
#             print type(r)
#             print (http.request.httprequest.files)
#             print len(http.request.httprequest.get_data()) 
#             ## http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.MultiDict
#             for rec in http.request.httprequest.files.iteritems():
#                 print type(rec[1])
#                 print rec[1].filename
#                 rec[1].save('/tmp/%s' % rec[1].filename, buffer_size=16384)
            #print len(r)
#             print r.read()
#             for line in r.read():
#                 print 'nl:%s' % line
#                 # filter out keep-alive new lines
#                 if line:
#                     decoded_line = line.decode('utf-8')
#                     print(json.loads(decoded_line))
        #time.sleep(10)
        print http.request.httprequest.get_data()
        resp = requests.request(
            method=http.request.httprequest.method,
            url=curl.geturl(),
            headers=in_headers,
            data=http.request.httprequest.get_data(),
            #cookies=http.request.httprequest.cookies,
            files=http.request.httprequest.files,
            allow_redirects=False) 
        
#         excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection'
#                             , 'openerp-server', 'openerp-port', 'openerp-database', 'authorization' ]
        excluded_headers = ['transfer-encoding'
                            , 'openerp-server', 'openerp-port', 'openerp-database' , 'authorization']

        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        #response = resp
        return response    
    