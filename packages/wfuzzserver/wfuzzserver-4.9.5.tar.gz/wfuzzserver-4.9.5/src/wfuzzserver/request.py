import json
from dicttoxml import dicttoxml
import xmltodict
import re
import copy

class Request:
    def __init__(self,url,headers=[],body="",fuzzcookies=False,fuzzheaderslist=[]):
        self.url = url
        self.headers = self.unSerializeHeaders(headers)
        self.body = body
        self.baseParams = {"url":{},"urlparams":[],"body":{},"headers":{},"cookies":{}}
        self.ctype = self.getHeaderValue(self.headers,"Content-Type")
        self.xmlroot = False
        self.jsonbody = False
        self.xmlbody = False
        self.multipartbody = False
        self.jsonbodylist = False
        self.graphqlbody = False
        self.cookiebanlist = ["JSESSIONID","PHPSESSID",".ASPXAUTH","csrftoken","XSRF-TOKEN","ASP.NET_SessionId","ASPSESSIONIDSCRCQSRD"]
        self.bodyparametersbanlist = ["__VIEWSTATEGENERATOR","__EVENTARGUMENT","__VIEWSTATE","__EVENTTARGET","__EVENTVALIDATION"]
        #self.fuzzcookieslist = copy.deepcopy(fuzzcookieslist)
        self.fuzzcookies = fuzzcookies
        self.fuzzheaderslist = copy.deepcopy(fuzzheaderslist)
        self.getParams()
            
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
                    print("Exception in parsing multipart line: 43")
                    value = ''
            chunks = item.split()
            name = chunks[2].split('=')[1].strip('";\'')
            if chunks[3].startswith("filename="):
                filename = chunks[3].split('=')[1].strip('";\'')
            params.update({name:value})
        return params
        
    def getHeaderValue(self,headers,headername):
        for header in headers:
            if header.lower() == headername.lower():
                return headers[header]
        return ""

    def delHeader(self,headers,headername):
        for header in list(headers):
            if header.lower() == headername.lower():
                del headers[header]
        
    def getParams(self):
        frags = self.url.split('?')[0].split("/")
        if not "FUZZ" in self.url.split("?")[0]:
            for i in range(len(frags)):
                if re.match(r"^[a-z0-9]{32}$",frags[i]) or re.match(r"^[0-9]+$",frags[i]) or re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",frags[i]):
                    self.baseParams["urlparams"].append(frags[i])
                else:
                    if any(frags[i].endswith(ext) for ext in [".aac",".ttf",".mp4",".swf",".js",".css",".jpg",".png",".gif",".woff",".woff2",".svg",".ico",".jpeg"]):
                        self.baseParams["urlparams"].append(frags[i])
        else:
            for i in range(len(frags)):
                if "FUZZ" in frags[i]:
                    self.baseParams["urlparams"].append(frags[i].replace("FUZZ",""))
            f1 = self.url.split("?")[0].replace("FUZZ","")
            f2 = ""
            try:
                f2 = self.url.split("?")[1]
                self.url = f1+"?"+f2
            except:
                self.url = f1
            
        if "FUZZ" in json.dumps(self.headers):
            for header in self.headers:
                if "FUZZ" in self.headers[header]:
                    self.headers[header] = self.headers[header].replace("FUZZ","")
                    self.baseParams["headers"].update({header:self.headers[header]})
        if self.fuzzcookies:
            #extract cookies
            cookiesstr = self.getHeaderValue(self.headers,"Cookie")
            if cookiesstr != "":
                cookies = cookiesstr.split(';')
                for cookie in cookies:
                    cookiechunks = cookie.strip().split('=')
                    if len(cookiechunks)<2:
                        cookiechunks[1]=""
                    self.baseParams["cookies"][cookiechunks[0]] = cookiechunks[1]
        #now goign for others
        query = ""
        if '?' in self.url and not self.url.endswith('?'):
            query = self.url.split('?',1)[1]
        if query != "":
            paramchunks = query.split('&')
            for chunk in paramchunks:
                minichunk = chunk.split('=')
                if len(minichunk)>1:
                    self.baseParams["url"].update({minichunk[0]:minichunk[1]})
                else:
                    self.baseParams["url"].update({minichunk[0]:""})
        if self.body!="":         
            if "boundary" in self.ctype.lower():
                self.multipartbody = True
                self.baseParams["body"].update(self.parseMultipart())
            elif "/json" in self.ctype.lower():
                try:
                    jsonload = json.loads(self.body)
                    if type(jsonload)==list:
                        self.jsonbodylist = True
                        self.baseParams["body"].update(jsonload[0])
                    else:
                        ##check if it graphql body
                        if ("query" in jsonload or "graphql" in self.url.split('?')[0]) and "variables" in jsonload and len(jsonload["variables"])>0 and type(jsonload["variables"]) == type(dict()):
                            self.graphqlbody = True                            
                        self.baseParams["body"].update(jsonload)
                    if self.graphqlbody:
                        self.jsonbody = False
                    else:
                        self.jsonbody = True
                except:
                    pass
            
            elif "/xml" in self.ctype.lower():
                try:
                    params = xmltodict.parse(self.body)
                    self.xmlbody = True
                    if len(params) == 1 and params["root"]:
                        self.baseParams["body"].update(params["root"])
                        self.xmlroot = True
                    else:
                        self.baseParams["body"].update(params)
                        self.xmlroot = False
                except:
                    pass
            else:
                paramchunks = self.body.split('&')
                for chunk in paramchunks:
                    minichunk = chunk.split('=')
                    if len(minichunk)>1:
                        self.baseParams["body"].update({minichunk[0]:minichunk[1]})
                    else:
                        self.baseParams["body"].update({minichunk[0]:""})
                        
    def serializeHeaders(self,headersdict):
        headers = []
        for header in headersdict:
            headers.append(header+": "+headersdict[header])
        return headers
        
    def unSerializeHeaders(self,headerslist):
        headers = {}
        for header in headerslist:
            hh = header.split(":",1)
            headers.update({hh[0].strip():hh[1].strip()})
        return headers
        
    def get_json_paths(self,paths,father,d):
        if type(d) == type(dict()):
            for key in d:
                self.get_json_paths(paths,father+[key],d[key])
        elif type(d) == type(list()):
            for i in range(len(d)):
                self.get_json_paths(paths,father+[i],d[i])
        else:
            paths.append(father)
    def change_json_value(self,jsonobj,path,newval):
        temp_json = copy.deepcopy(jsonobj)
        temp = temp_json
        for key in path:
            if type(temp[key]) != type(str()):
                temp = temp[key]
            else:
                temp[key] = newval
        return temp_json
    def get_json_value(self,jsonobj,path):
        temp_json = jsonobj
        for key in path:
            temp_json = temp_json[key]
        return str(temp_json)
        
    def reBuildAll(self,payloadpos="append"):
        variations = []
        body = ""
        headers = []
        body = self.body
        headers = self.serializeHeaders(self.headers)
        for mainparam in self.baseParams["url"]:
            if mainparam in self.bodyparametersbanlist:
                continue
            url = self.url.split('?')[0]+"?"
            for param in self.baseParams["url"]:
                if mainparam == param:
                    if payloadpos=="append":
                        url = url+param+"="+self.baseParams["url"][param]+"FUZZ"+"&"
                    else:
                        url = url+param+"=FUZZ&"
                else:
                    url = url+param+"="+self.baseParams["url"][param]+"&"
            url = url.strip('&')
            url = url.strip('?')
            variations.append(("urlencode",url,headers,body))
        body = self.body
        headers = self.serializeHeaders(self.headers)
        for mainparam in self.baseParams["urlparams"]:
            urlparts = self.url.split('?')
            if payloadpos=="append":
                urlparts[0] = urlparts[0].replace(mainparam,mainparam+"FUZZ")
            else:
                urlparts[0] = urlparts[0].replace(mainparam,"FUZZ")
            url = '?'.join(urlparts)
            variations.append(("urlencode",url,headers,body))
        if self.body != "":
            if self.jsonbody:
                url = self.url
                headers = self.serializeHeaders(self.headers)
                if self.jsonbodylist:
                    #temp = json.loads(self.body)[0]
                    paths = []
                    self.get_json_paths(paths,[],self.baseParams["body"])
                    for path in paths:
                        originalval = self.get_json_value(self.baseParams["body"],path)
                        if payloadpos=="append":
                            newtemp = self.change_json_value(self.baseParams["body"],path,originalval+"FUZZ")
                        else:
                            newtemp = self.change_json_value(self.baseParams["body"],path,"FUZZ")
                        body = json.dumps([newtemp])
                        variations.append(("jsonencode",url,headers,body))
                else:
                    #temp = json.loads(self.body)
                    paths = []
                    self.get_json_paths(paths,[],self.baseParams["body"])
                    for path in paths:
                        originalval = self.get_json_value(self.baseParams["body"],path)
                        if payloadpos=="append":
                            newtemp = self.change_json_value(self.baseParams["body"],path,originalval+"FUZZ")
                        else:
                            newtemp = self.change_json_value(self.baseParams["body"],path,"FUZZ")
                        body = json.dumps(newtemp)
                        variations.append(("jsonencode",url,headers,body))
            elif self.graphqlbody:
                url = self.url
                headers = self.serializeHeaders(self.headers)
                paths = []
                self.get_json_paths(paths,["variables"],self.baseParams["body"]["variables"])
                for path in paths:
                    originalval = self.get_json_value(self.baseParams["body"],path)
                    if payloadpos=="append":
                        newtemp = self.change_json_value(self.baseParams["body"],path,originalval+"FUZZ")
                    else:
                        newtemp = self.change_json_value(self.baseParams["body"],path,"FUZZ")
                    body = json.dumps(newtemp)
                    variations.append(("jsonencode",url,headers,body))
            elif self.xmlbody:
                url = self.url
                headers = self.serializeHeaders(self.headers)
                paths = []
                self.get_json_paths(paths,[],self.baseParams["body"])
                for path in paths:
                    originalval = self.get_json_value(self.baseParams["body"],path)
                    if payloadpos=="append":
                        newtemp = self.change_json_value(self.baseParams["body"],path,originalval+"FUZZ")
                    else:
                        newtemp = self.change_json_value(self.baseParams["body"],path,"FUZZ")
                    body = dicttoxml(newtemp, root=self.xmlroot, attr_type=False).decode()
                    variations.append(("none",url,headers,body))
                
            elif self.multipartbody:
                url = self.url
                headers = self.serializeHeaders(self.headers)
                for mainparam in self.baseParams["body"]:
                    if payloadpos=="append":
                        body = self.body.replace("\n"+self.baseParams["body"][mainparam],"\n"+self.baseParams["body"][mainparam]+"FUZZ")
                    else:
                        body = self.body.replace("\n"+self.baseParams["body"][mainparam],"\nFUZZ")
                    variations.append(("none",url,headers,body))
            else:
                url = self.url
                headers = self.serializeHeaders(self.headers)
                for mainparam in self.baseParams["body"]:
                    if mainparam in self.bodyparametersbanlist:
                        continue
                    body = ""
                    for param in self.baseParams["body"]:
                        if param == mainparam:
                            if payloadpos=="append":
                                body = body+"&"+param+"="+self.baseParams["body"][param]+"FUZZ"
                            else:
                                body = body+"&"+param+"=FUZZ"
                        else:
                            body = body+"&"+param+"="+self.baseParams["body"][param]
                    body = body.strip('&')
                    variations.append(("urlencode",url,headers,body))
        url = self.url
        body = self.body
        cookieheaders = copy.deepcopy(self.headers)
        if self.baseParams["cookies"]!={}:
            for maincookie in self.baseParams["cookies"]:
                if maincookie in self.cookiebanlist:
                    continue
                cookieheader=""
                for cookie in self.baseParams["cookies"]:
                    if maincookie == cookie:
                        if payloadpos=="append":
                            cookieheader = cookieheader+cookie+"="+self.baseParams["cookies"][cookie]+"FUZZ; "
                        else:
                            cookieheader = cookieheader+cookie+"=FUZZ; "
                    else:
                        cookieheader = cookieheader+cookie+"="+self.baseParams["cookies"][cookie]+"; "
                self.delHeader(cookieheaders,"cookie")
                cookieheaders["Cookie"] = cookieheader.strip().rstrip(";")
                variations.append(("urlencode",url,self.serializeHeaders(cookieheaders),body))
        url = self.url
        body = self.body
        if self.baseParams["headers"]!={}:
            for mainheader in self.baseParams["headers"]:
                headers = []
                for header in self.headers:
                    if header == mainheader:
                        if payloadpos=="append":
                            headers.append(header+": "+self.headers[header]+"FUZZ")
                        else:
                            headers.append(header+": FUZZ")
                    else:
                        headers.append(header+": "+self.headers[header])
                variations.append(("none",url,headers,body))
        if self.fuzzheaderslist != []:
            for mainheader in self.fuzzheaderslist:
                if not mainheader in self.baseParams["headers"]:
                    headers = []
                    if self.getHeaderValue(self.headers,mainheader)!="":
                        for header in self.headers:
                            if header.lower() == mainheader.lower():
                                if payloadpos=="append":
                                    headers.append(header+": "+self.headers[header]+"FUZZ")
                                else:
                                    headers.append(header+": FUZZ")
                            else:
                                headers.append(header+": "+self.headers[header])
                    else:
                        for header in self.headers:
                            headers.append(header+": "+self.headers[header])
                        if mainheader.lower() == "user-agent":
                            if payloadpos=="append":
                                headers.append(mainheader+": Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.54 Mobile Safari/537.36FUZZ")
                            else:
                                headers.append(mainheader+": FUZZ")
                        elif mainheader.lower() == "x-forwarded-for":
                            if payloadpos=="append":
                                headers.append(mainheader+": 127.0.0.1FUZZ")
                            else:
                                headers.append(mainheader+": FUZZ") 
                        else:
                            headers.append(mainheader+": FUZZ")
                    variations.append(("none",url,headers,body))  
        return variations
