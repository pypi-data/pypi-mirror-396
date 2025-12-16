from queue import Queue
from threading import Thread
import time
import requests
import json
from dicttoxml import dicttoxml
import xmltodict
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from requests_toolbelt.utils import dump
import copy

requests.packages.urllib3.disable_warnings()
normalval="discobiscuits"
badval="discobiscuits'!@#$%^&*)(?><\",\n\r嘍嘊'!@#$%^&*)(?><\","
xmlbadval="discobiscuits'!@#$%^&*)(?\",\n\r'!@#$%^&*)(?\","

class Fuzzer(Thread):
    def __init__(self,queue,url,method,headers,body,request_types,num_of_params,num_of_threads,delay,wordlist,value_type,custom_value,addtojsonbranch):
        Thread.__init__(self)
        self.results_queue = queue
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.delay = delay
        self.request_types = request_types
        self.num_of_params = num_of_params
        self.num_of_threads = num_of_threads
        self.wordlist = wordlist
        self.param_groups=[]
        self.value_type = value_type
        self.custom_value = custom_value
        self.typesheaders = {}
        self.lines=[]
        self.baseParams = {}
        self.originalresponse = {}
        self.addtojsonbranch = addtojsonbranch
        self.jsonbodylist = False
        self.xmlroot = False
        with open(wordlist) as read:
            self.lines=read.read().splitlines()
    def dumprequest(self,response):
        return dump.dump_response(response,request_prefix="").decode('utf-8','ignore').split("\r\n>")[0]
        
    def change_json_value(self,jsonobj,p_dict):
        temp_json = copy.deepcopy(jsonobj)
        temp = temp_json
        for key in self.addtojsonbranch:
            temp = temp[key]
        temp.update(p_dict)
        return temp_json
        
    def brute(self,few_params,reqtype):
        params_group = copy.deepcopy(self.baseParams)
        if self.addtojsonbranch!=[]:
            params_group = self.change_json_value(params_group,few_params)
        else:
            params_group.update(few_params)
        response = self.request(params_group,reqtype)
        #now we compare to original if not similar then return params_group else return None
        res = self.compare(reqtype,response)
        if res[6]!="":
            return {"status_code":res[0],"reflects":res[1],"words":res[2],"bytes":res[3],"different_type":res[4],"different_status":res[5],"diffs":res[6],"request":self.dumprequest(response)}
        return None
    
    def request(self,params_group,reqtype):
        if reqtype=="get":
            try:
                resp = requests.get(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.get(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="postquery":
            try:
                resp = requests.post(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.post(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="postform":
            try:
                resp = requests.post(url=self.url, data=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.post(url=self.url, data=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="postmultipart":
            #here we should change the params_group from this type: {"":""} to this {"":(None,"")}
            newgrp = {}
            for param in params_group:
                newgrp.update({param:(None,params_group[param])})
            try:
                resp = requests.post(url=self.url, files=newgrp,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.post(url=self.url, files=newgrp,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="postjson":
            try:
                if self.jsonbodylist:
                    resp = requests.post(url=self.url, json=[params_group],headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                else:
                    resp = requests.post(url=self.url, json=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    if self.jsonbodylist:
                        resp = requests.post(url=self.url, json=[params_group],headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    else:
                        resp = requests.post(url=self.url, json=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="postxml":
            #we should here change the value of each parameter
            if self.value_type == "bad":
                newgrp = {}
                for param in params_group:
                    newgrp.update({param:params_group[param].replace('>','').replace('<','').replace('嘍嘊','')})
                try:
                    resp = requests.post(url=self.url, data=dicttoxml(newgrp, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    try:
                        resp = requests.post(url=self.url, data=dicttoxml(newgrp, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                        return resp
                    except:
                        pass
            else:
                try:
                    resp = requests.post(url=self.url, data=dicttoxml(params_group, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    try:
                        resp = requests.post(url=self.url, data=dicttoxml(params_group, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                        return resp
                    except:
                        pass
        ##########put
        if reqtype=="putquery":
            try:
                resp = requests.put(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.put(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="putform":
            try:
                resp = requests.put(url=self.url, data=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.put(url=self.url, data=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="putmultipart":
            #here we should change the params_group from this type: {"":""} to this {"":(None,"")}
            newgrp = {}
            for param in params_group:
                newgrp.update({param:(None,params_group[param])})
            try:
                resp = requests.put(url=self.url, files=newgrp,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.put(url=self.url, files=newgrp,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="putjson":
            try:
                if self.jsonbodylist:
                    resp = requests.put(url=self.url, json=[params_group],headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                else:
                    resp = requests.put(url=self.url, json=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    if self.jsonbodylist:
                        resp = requests.put(url=self.url, json=[params_group],headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    else:
                        resp = requests.put(url=self.url, json=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="putxml":
            #we should here change the value of each parameter
            if self.value_type == "bad":
                newgrp = {}
                for param in params_group:
                    newgrp.update({param:params_group[param].replace('>','').replace('<','').replace('嘍嘊','')})
                try:
                    resp = requests.put(url=self.url, data=dicttoxml(newgrp, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    try:
                        resp = requests.put(url=self.url, data=dicttoxml(newgrp, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                        return resp
                    except:
                        pass
            else:
                try:
                    resp = requests.put(url=self.url, data=dicttoxml(params_group, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    try:
                        resp = requests.put(url=self.url, data=dicttoxml(params_group, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                        return resp
                    except:
                        pass
        ##########patch
        if reqtype=="patchquery":
            try:
                resp = requests.patch(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.patch(url=self.url, params=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="patchform":
            try:
                resp = requests.patch(url=self.url, data=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.patch(url=self.url, data=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="patchmultipart":
            #here we should change the params_group from this type: {"":""} to this {"":(None,"")}
            newgrp = {}
            for param in params_group:
                newgrp.update({param:(None,params_group[param])})
            try:
                resp = requests.patch(url=self.url, files=newgrp,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    resp = requests.patch(url=self.url, files=newgrp,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="patchjson":
            try:
                if self.jsonbodylist:
                    resp = requests.patch(url=self.url, json=[params_group],headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                else:
                    resp = requests.patch(url=self.url, json=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                return resp
            except:
                try:
                    if self.jsonbodylist:
                        resp = requests.patch(url=self.url, json=[params_group],headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    else:
                        resp = requests.patch(url=self.url, json=params_group,headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    pass
        if reqtype=="patchxml":
            #we should here change the value of each parameter
            if self.value_type == "bad":
                newgrp = {}
                for param in params_group:
                    newgrp.update({param:params_group[param].replace('>','').replace('<','').replace('嘍嘊','')})
                try:
                    resp = requests.patch(url=self.url, data=dicttoxml(newgrp, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    try:
                        resp = requests.patch(url=self.url, data=dicttoxml(newgrp, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                        return resp
                    except:
                        pass
            else:
                try:
                    resp = requests.patch(url=self.url, data=dicttoxml(params_group, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                    return resp
                except:
                    try:
                        resp = requests.patch(url=self.url, data=dicttoxml(params_group, root=self.xmlroot, attr_type=False).decode('utf-8'),headers=self.typesheaders[reqtype], verify=False,allow_redirects=False)
                        return resp
                    except:
                        pass
        ##########
        return None
        
    def isJsonBody(self):
        try:
            j=json.loads(self.body)
            if type(j)==dict:
                return True
            else:
                return False
        except:
            return False
    
    def isXmlBody(self):
        try:
            xmltodict.parse(self.body)
            return True
        except:
            return False
            
    def parseMultipart(self):
        params = {}
        boundary = self.ctype
        boundary = boundary.split("oundary=")[-1]
        bodyparts = self.body.strip().rstrip('--').split("--"+boundary)
        parts = []
        for part in bodyparts:
            if part != '':
                parts.append(part.strip('--').strip())
        for item in parts:
            try:
                value = item.split('\r\n\r\n',1)[1]
            except:
                try:
                    value = item.split('\n\n',1)[1]
                except:
                    print("Exception in parsing multipart line: 515")
                    value = ''
            chunks = item.split()
            name = chunks[2].split('=')[1].strip('";\'')
            if chunks[3].startswith("filename="):
                filename = chunks[3].split('=')[1].strip('";\'')
            params.update({name:value})
        return params
            
    def getParams(self):
        query = ""
        if '?' in self.url and not self.url.endswith('?'):
            query = self.url.split('?',1)[1]
        self.url = self.url.split('?')[0]
        if query != "":
            paramchunks = query.split('&')
            for chunk in paramchunks:
                minichunk = chunk.split('=')
                if len(minichunk)>1:
                    self.baseParams.update({minichunk[0]:minichunk[1]})
                else:
                    self.baseParams.update({minichunk[0]:""})
        if self.body!="":
            ctype = self.getHeaderValue(self.headers,"Content-Type")
            if ctype == None:
                ctype=""          
            if "boundary" in ctype.lower():
                self.baseParams.update(self.parseMultipart())
            elif self.isJsonBody():
                try:
                    jsonload = json.loads(self.body)
                    if type(jsonload)==type(list()):
                        self.baseParams.update(jsonload[0])
                        self.jsonbodylist = True
                    else:
                        self.baseParams.update(jsonload)
                        self.jsonbodylist = False
                except:
                    pass
            
            elif self.isXmlBody():
                try:
                    params = xmltodict.parse(self.body)
                    if len(params) == 1 and params["root"]:
                        self.baseParams.update(params["root"])
                        self.xmlroot = True
                    else:
                        self.baseParams.update(params)
                        self.xmlroot = False
                except:
                    pass
            else:
                paramchunks = self.body.split('&')
                for chunk in paramchunks:
                    minichunk = chunk.split('=')
                    if len(minichunk)>1:
                        self.baseParams.update({minichunk[0]:minichunk[1]})
                    else:
                        self.baseParams.update({minichunk[0]:""})
            
    def setContentTypeold(self,ctype):
        newheaders={}
        for header in self.headers:
            if header.lower()=="content-type":
                if ctype == "get":
                    try:
                        del self.headers[header]
                    except:
                        pass
                elif "xml" in ctype:
                    self.headers[header]="application/xml"
                elif "json" in ctype:
                    self.headers[header]="application/json"
                elif "multipart" in ctype:
                    try:
                        del self.headers[header]
                    except:
                        pass
                else:
                    self.headers[header]="application/x-www-form-urlencoded"
                return
        if ctype == "get" or "multipart" in ctype:
            return
        if "xml" in ctype:
            self.headers["Content-Type"]="application/xml"
        elif "json" in ctype:
            self.headers["Content-Type"]="application/json"
        else:
            self.headers["Content-Type"]="application/x-www-form-urlencoded"
            
    def setContentType(self,ctype):
        newheaders={}
        contentisthere = False
        if ctype.lower()=='get' or "multipart" in ctype.lower():
            for header in self.headers:
                if header.lower()!="content-type":
                    newheaders[header] = self.headers[header]
        elif "xml" in ctype.lower():
            for header in self.headers:
                if header.lower()!="content-type":
                    newheaders[header] = self.headers[header]
                else:
                    contentisthere = True  #the content-type header is there
                    newheaders[header] = "application/xml"
            if not contentisthere: #the content type header is not there we must add it
                newheaders["Content-Type"] = "application/xml"
        elif "json" in ctype.lower():
            for header in self.headers:
                if header.lower()!="content-type":
                    newheaders[header] = self.headers[header]
                else:
                    contentisthere = True
                    newheaders[header] = "application/json"
            if not contentisthere:
                newheaders["Content-Type"] = "application/json"
        elif "form" in ctype.lower():
            for header in self.headers:
                if header.lower()!="content-type":
                    newheaders[header] = self.headers[header]
                else:
                    contentisthere = True
                    newheaders[header] = "application/x-www-form-urlencoded" 
            if not contentisthere:
                newheaders["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            newheaders = self.headers.copy()
            
        return newheaders
            
    def setHeaderValue(self,headers,headername,new_value):
        for header in headers:
            if header.lower() == headername.lower():
                headers[header] = new_value
                return headers
        headers[headername] = new_value
        return headers
        
    def getHeaderValue(self,headers,headername):
        for header in headers:
            if header.lower() == headername.lower():
                return headers[header]
        return None
    
    def numOfHeader(self,headers,headername):
        count = 0
        for header in headers:
            if header.lower() == headername.lower():
                count+=1
        return count
    def getDefaultType(self):
        if self.method.lower() == "get":
            return "get"
        else:
            contype = self.getHeaderValue(self.headers,"content-type")
            if contype != None:
                if "boundary" in contype:
                    if self.method.lower() == "post":
                        return "postmultipart"
                    if self.method.lower() == "put":
                        return "putmultipart"
                    if self.method.lower() == "patch":
                        return "patchmultipart"
                    if self.method.lower() == "delete":
                        return "deletemultipart"
                elif "json" in contype:
                    if self.method.lower() == "post":
                        return "postjson"
                    if self.method.lower() == "put":
                        return "putjson"
                    if self.method.lower() == "patch":
                        return "patchjson"
                    if self.method.lower() == "delete":
                        return "deletejson"
                elif "xml" in contype:
                    if self.method.lower() == "post":
                        return "postxml"
                    if self.method.lower() == "put":
                        return "putxml"
                    if self.method.lower() == "patch":
                        return "patchxml"
                    if self.method.lower() == "delete":
                        return "deletexml"
                else:
                    if self.method.lower() == "post":
                        return "postform"
                    if self.method.lower() == "put":
                        return "putform"
                    if self.method.lower() == "patch":
                        return "patchform"
                    if self.method.lower() == "delete":
                        return "deleteform"
            else:
                return None
            
    
    def getHeaderName(self,headers,headername):
        count = 0
        for header in headers:
            if header.lower() == headername.lower():
                return header
        return None
        
    def getResponseProps(self,response):
        try:
            num_of_bytes = int(self.getHeaderValue(response.headers,"Content-Length"))
        except:
            num_of_bytes = len(response.content)
        num_of_words = len(response.content.split())
        headerstr=str(response.headers)
        num_of_reflects = response.text.count("discobiscuits")+headerstr.count("discobiscuits")
        if self.value_type != "bad" and self.value_type != "normal":
            num_of_reflects = num_of_reflects + response.text.count(self.custom_value)+headerstr.count(self.custom_value)
        num_of_headers = len(response.headers)
        content_type = self.getHeaderValue(response.headers,"content-type")
        status_code = response.status_code
        num_of_cookies = self.numOfHeader(response.headers,"set-cookie")
        num_of_lines = len(response.text.split("\n"))
        size_of_headers = len(str(response.headers))
        return {"size_of_headers":size_of_headers,"num_of_lines":num_of_lines,"num_of_cookies":num_of_cookies,"status_code":status_code,"num_of_bytes":num_of_bytes,"num_of_words":num_of_words,"num_of_reflects":num_of_reflects,"num_of_headers":num_of_headers,"content_type":content_type}
            
    def compare(self,reqtype,response):
        if response == None:
            return (0,0,0,0,False,False,"")
        diffs=""
        diff = False #different content type
        status_diff = False #different status code
        props = self.getResponseProps(response)
        if props["num_of_reflects"] > 0: #!= self.originalresponse[reqtype]["num_of_reflects"]:
            diffs+="Reflect-"
        if self.originalresponse[reqtype] == {}:
            return (props["status_code"],props["num_of_reflects"],props["num_of_words"],props["num_of_bytes"],diff,status_diff,diffs.strip("-"))
        if props["content_type"]!=self.originalresponse[reqtype]["content_type"]:
            diffs+="Content_Type-"
            diff = True
        if props["status_code"]!=self.originalresponse[reqtype]["status_code"]:
            diffs+="Status_Code-"
            status_diff = True
        if props["num_of_words"]!=self.originalresponse[reqtype]["num_of_words"]:
            diffs+="Words-"
        if props["num_of_lines"]!=self.originalresponse[reqtype]["num_of_lines"]:
            diffs+="Lines-"
        if abs(props["num_of_bytes"]-self.originalresponse[reqtype]["num_of_bytes"]) > 5:
            diffs+="Body Size-"
        if props["num_of_headers"]!=self.originalresponse[reqtype]["num_of_headers"]:
            diffs+="Headers Number-"
        if props["num_of_cookies"]!=self.originalresponse[reqtype]["num_of_cookies"]:
            diffs+="Cookies-"
        if abs(props["size_of_headers"]-self.originalresponse[reqtype]["size_of_headers"]) > 5:
            diffs+="Headers Size-"
        return (props["status_code"],props["num_of_reflects"],props["num_of_words"],props["num_of_bytes"],diff,status_diff,diffs.strip("-"))
        
            
    def calculateOriginal(self):
        #we set the "Accept-Encoding: identity" to prevent compressed responses
        try:
            if self.method.lower()!="get":
                req = requests.Request(method=self.method, url=self.url, headers=self.headers,data=self.body)
            else:
                req = requests.Request(method=self.method, url=self.url, headers=self.headers)
            prep = req.prepare()
            #if self.method.lower()!="get":
            #    prep.body = self.body
            response = None
            with requests.Session() as session:
                response = session.send(prep, verify=False,allow_redirects=False)
                if response == None:
                    response = session.send(prep, verify=False,allow_redirects=False)
            if response != None:
                self.originalresponse["base"] = self.getResponseProps(response)
            #time.sleep(60)
        except:
            pass
        for reqtype in self.request_types:
            response = self.request(self.baseParams,reqtype)
            if response != None:
                self.originalresponse[reqtype] = self.getResponseProps(response)
                if "base" in self.originalresponse:
                    res = self.compare("base",response)
                    if res[6]!="":
                         self.results_queue.put({"status_code":res[0],"reflects":res[1],"words":res[2],"bytes":res[3],"different_type":res[4],"different_status":res[5],"diffs":res[6],"request":self.dumprequest(response)})
            else:
                self.originalresponse[reqtype] = {}        
                
            
        
    def run(self):
        #set accept-encoding to identity to avoid compressed response
        print("=================")
        print(self.request_types)
        self.headers = self.setHeaderValue(self.headers,"Accept-Encoding","identity")
        if self.request_types == []:
            ct = self.getDefaultType()
            if ct != None:
                self.request_types = [ct]
            else:
                self.results_queue.put(None)
                return
        print("=================")
        print(self.request_types)
        #get base params
        self.getParams()
        #calculate original response
        self.calculateOriginal()
        for reqtype in self.request_types:
            self.typesheaders[reqtype] = self.setContentType(reqtype)
        #divide parameters into groups
        chunk = {}
        for i in range(len(self.lines)):
            if self.value_type == "normal":
                chunk.update({self.lines[i]:normalval})
            elif self.value_type == "bad":
                chunk.update({self.lines[i]:badval})
            else:
                if self.custom_value.startswith("http"):
                    self.custom_value=self.custom_value+"/discobiscuits"
                chunk.update({self.lines[i]:self.custom_value})
            if i % self.num_of_params == 0:
                self.param_groups.append(chunk)
                chunk={}
        if i % self.num_of_params != 0:
            if chunk != {}:
                self.param_groups.append(chunk)
        #print just to be sure
        #print(self.param_groups)   #verified now go on
        if self.delay <= 0 and self.num_of_threads > 1:
            #send them to pool
            threadpool = ThreadPoolExecutor(max_workers=self.num_of_threads)
            #try to pass both reqtype and params_group to brute then make the compare in brute and return None if similar or params_group if not similar
            #futures = (threadpool.submit(self.brute, grp) for grp in self.param_groups)
            futures=[]
            for grp in self.param_groups:
                for reqtype in self.request_types:
                    futures.append(threadpool.submit(self.brute, grp, reqtype))
            for i, result in enumerate(as_completed(futures)):
                if result.result():
                    self.results_queue.put(result.result())
        else:
            for grp in self.param_groups:
                for reqtype in self.request_types:
                    result = self.brute(grp,reqtype)
                    if result:
                        self.results_queue.put(result)
                    if self.delay > 0:
                        time.sleep(self.delay)
        self.results_queue.put(None)
        
class ParamHammer:
    def __init__(self,url,method="GET",headers={},body="",request_types=["get"],num_of_params=20,num_of_threads=10,delay=0,wordlist="params.txt",value_type="normal",custom_value="",addtojsonbranch=""):
        self.results_queue = Queue()
        self.url = url
        self.method = method
        self.headers = headers
        self.num_of_params = num_of_params
        self.num_of_threads = num_of_threads
        self.delay = delay
        self.body = body
        if addtojsonbranch != "":
            self.addtojsonbranch = addtojsonbranch.split(",")
        else:
            self.addtojsonbranch = []
        self.value_type = value_type
        self.custom_value = custom_value
        self.wordlist = wordlist
        self.request_types = request_types
        fuzzer = Fuzzer(self.results_queue,self.url,self.method,self.headers,self.body,self.request_types,self.num_of_params,self.num_of_threads,self.delay,self.wordlist,self.value_type,self.custom_value,self.addtojsonbranch)
        fuzzer.start()
        
    def __iter__(self):
        return self

    def __next__(self):
        res = self.results_queue.get()
        self.results_queue.task_done()
        if not res:
            raise StopIteration
        return res

