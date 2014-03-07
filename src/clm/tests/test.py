# -*- coding: utf-8 -*-
# @COPYRIGHT_begin
#
# Copyright [2010-2014] Institute of Nuclear Physics PAN, Krakow, Poland
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @COPYRIGHT_end

#!/usr/bin/python

import os
import sys
import copy
import urllib2
import requests
import simplejson

myparams={'user_id':1, 'data':{'remote':[1,2,10]}}
r=requests.post("http://localhost:8000/cm/user/user/add_missing/", data=simplejson.dumps(myparams))

class Test:
    clm = None
    log_file = None
    
    stored_results = []
    test_results = []
    def __init__(self, settings):
        self.clm = settings.clm
        self.log_file = open(settings.log_file, 'w')
    
    def log(self, result):
        self.test_results.append(result)
        print result
    
    def call(self, call_path, params, store_as=None, expected_state='ok'):
        if clm == None:
            raise Exception('CLM Not configured')
            
        json_params = simplejson.dumps(params)
        
        r = simplejson.loads(requests.post(self.clm + "/" + call_path, data=json_params))
        
        status = None
        if r['state'] == expected_state:
            status = 'done'
        elif r['state'] != expected_state:
        
        result = ['status' = status,
                  'clm': str(self.clm),
                  'path': str(call_path),
                  'params': str(json_params),
                  'response': r,
                  'stored_results': copy.copy(self.stored_results)]
                  
        self.test_results.append(result)
        return result

    def run(self):
        pass
    
    def start(self):
        try:
            self.run()
        except Exception, e:
            self.log("Could not start tests: %s" % str(e))
            
