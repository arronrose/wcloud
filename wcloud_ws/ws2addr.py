# -*- coding: utf8 -*-



import web
import ecode
import ws_io
import addr_db
import config
import logging
import traceback


class OrgList:
    #{{{
    def GET(self):
        """
        input:
        output:
            rt:
            orglist:
        """
        rt = ecode.FAILED
        orglist = []

        try:
            orglist = addr_db.get_org_list()
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org list.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,orglist=orglist),error_info)
    #}}}


class OrgAddr:
    #{{{
    def GET(self):
        """
        input:
            org_name:
        output:
            rt:
            orgaddr:
        """
        rt = ecode.FAILED
        orgaddr = {}

        try:
            i = ws_io.ws_input(['org_name'])
            if not i:
                raise ecode.WS_INPUT

            orgaddr = addr_db.get(i['org_name'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org list.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,orgaddr=orgaddr),error_info)
    #}}}


class AddOrg:
    #{{{
    def POST(self):
        """
        input:
            org_name:
            push_serv:
            ws_serv:
            wf_serv:
            eg_serv:
        output:
            rt:
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['org_name','push_serv','ws_serv','wf_serv'
                ,'eg_serv'])
            if not i:
                raise ecode.WS_INPUT

            addr_db.add_org(i['org_name'],i['push_serv'],i['ws_serv']
                    ,i['wf_serv'],i['eg_serv'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('add org.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class DelOrg:
    #{{{
    def POST(self):
        """
        input:
            org_name:
        output:
            rt:
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['org_name'])
            if not i:
                raise ecode.WS_INPUT

            addr_db.del_org(i['org_name'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('del org ')
            error_info = str(traceback.format_exc()).replace("\n"," ")


        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

