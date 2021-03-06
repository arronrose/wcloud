# -*- coding: utf8 -*-

import web
import logging
import base64

import ws_io
import ecode
import captcha_mng
import traceback


class Get:
    #{{{
    def GET(self):
        """
        input:
        output:
            rt: error code
            cid: captcha id
            img_data_b64: img raw data(base64)
        """
        rt = ecode.FAILED
        cid = ''
        img_data_b64 = ''

        try:
            cid, img_data = captcha_mng.get_captcha()
            if not cid:
                raise ecode.CREATE_CAPTHCA_FAIL

            img_data_b64 = base64.standard_b64encode( img_data)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get a captcha.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, cid=cid
            , img_data_b64=img_data_b64),error_info)
    #}}}


class Check:
    #{{{
    def GET(self):
        """
        input:
            cid: 
            value: 

        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['cid','value'])
            if not i:
                raise ecode.WS_INPUT

            if captcha_mng.check_captcha(i['cid'], i['value']):
                rt = ecode.OK
                error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('check a captcha.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

