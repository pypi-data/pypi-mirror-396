from queue import PriorityQueue
from queue import Queue
from threading import Thread
import time
import json
import requests
import random
import string
from urllib.parse import urlparse
from dicttoxml import dicttoxml
import xmltodict
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from requests_toolbelt.utils import dump

requests.packages.urllib3.disable_warnings()
normalval="discobiscuits"
badval="discobiscuits'!@#$%^&*)(?><\",\\n\\r嘍嘊'!@#$%^&*)(?><\","

class Fuzzer(Thread):
    def __init__(self,queue,url,method,headers,session_cookies,body,num_of_cookies,num_of_threads,delay,wordlist,value_type,custom_value):
        Thread.__init__(self)
        self.results_queue = queue
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.delay = delay
        self.session_cookies = session_cookies
        self.num_of_cookies = num_of_cookies
        self.num_of_threads = num_of_threads
        self.wordlist = wordlist
        self.cookie_groups=[]
        self.value_type = value_type
        self.custom_value = custom_value
        self.lines=[]
        self.baseParams = {}
        self.baseCookies = {}
        self.addthose = []
        self.originalresponse = {}
        self.xmlroot = False
        with open(wordlist) as read:
            self.lines=read.read().splitlines()

    def brute(self,cookies_group):
        cookies_group.update(self.baseCookies)
        response = self.request(cookies_group)
        #now we compare to original if not similar then return params_group else return None
        res = self.compare(response)
        if res[6]!="":
            #print(response.text)
            return {"status_code":res[0],"reflects":res[1],"words":res[2],"bytes":res[3],"different_type":res[4],"different_status":res[5],"diffs":res[6],"request":dump.dump_response(response,request_prefix="").decode('utf-8','ignore').split("\r\n>")[0]}
        return None
    def formCookieHeader(self,cookies_group):
        cookiestr=""
        for cookie in cookies_group:
            cookiestr=cookiestr+cookie+"="+cookies_group[cookie]+"; "
        return cookiestr.strip().strip(';')
       
    def request(self,cookies_group):
        self.removeContentType()
        self.setHeaderValue(self.headers,"Cookie",self.formCookieHeader(cookies_group))
        self.baseParams.update({"rand":''.join(random.choices(string.ascii_lowercase+string.digits, k=5))})
        req = requests.Request(method="get", url=self.url, headers=self.headers,params=self.baseParams) #,cookies=cookies_group)
        prep = req.prepare()
        #prep.headers=headers_group
        resp = None
        with requests.Session() as session:
            #session.proxies = {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"}
            try:
                resp = session.send(prep, verify=False,allow_redirects=False)
                if resp == None:
                    try:
                        resp = session.send(prep, verify=False,allow_redirects=False)
                    except:
                        pass
            except:
                try:
                    resp = session.send(prep, verify=False,allow_redirects=False)
                    if resp == None:
                        try:
                            resp = session.send(prep, verify=False,allow_redirects=False)
                        except:
                            pass
                except:
                    pass
        return resp
        
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
        boundary = self.getHeaderValue(self.headers,"Content-Type")
        if boundary != None:
            boundary = boundary.split("oundary=")[-1]
        bodyparts = self.body.strip().rstrip('--').split("--"+boundary)
        parts = []
        for part in bodyparts:
            if part != '':
                parts.append(part.strip('--').strip())
        for item in parts:
            value = item.split('\n\n',1)[1]
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
                    self.baseParams.update(json.loads(self.body))
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
    def removeContentType(self):
        for header in self.headers:
            if header.lower()=="content-type":
                del self.headers[header] 
                return
            
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
        return ""
    
    def numOfHeader(self,headers,headername):
        count = 0
        for header in headers:
            if header.lower() == headername.lower():
                count+=1
        return count
    
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
        num_of_reflects = response.text.count("discobiscuits")+response.text.count("172.172.172.172")+headerstr.count("discobiscuits")+headerstr.count("172.172.172.172")
        if self.value_type != "bad" and self.value_type != "normal":
            num_of_reflects = num_of_reflects + response.text.count(self.custom_value)+headerstr.count(self.custom_value)
        num_of_headers = len(response.headers)
        content_type = self.getHeaderValue(response.headers,"content-type")
        status_code = response.status_code
        num_of_cookies = self.numOfHeader(response.headers,"set-cookie")
        num_of_lines = len(response.text.split("\n"))
        size_of_headers = len(str(response.headers))
        return {"size_of_headers":size_of_headers,"num_of_lines":num_of_lines,"num_of_cookies":num_of_cookies,"status_code":status_code,"num_of_bytes":num_of_bytes,"num_of_words":num_of_words,"num_of_reflects":num_of_reflects,"num_of_headers":num_of_headers,"content_type":content_type}
            
    def compare(self,response):
        if response == None:
            return (0,0,0,0,False,False,"")
        diffs=""
        diff = False #different content type
        status_diff = False #different status code
        props = self.getResponseProps(response)
        if props["num_of_reflects"] > 0: #!= self.originalresponse[reqtype]["num_of_reflects"]:
            diffs+="Reflect-"
        if self.originalresponse == {}:
            return (props["status_code"],props["num_of_reflects"],props["num_of_words"],props["num_of_bytes"],diff,status_diff,diffs.strip("-"))
        if props["content_type"]!=self.originalresponse["content_type"]:
            diffs+="Content_Type-"
            diff = True
        if props["status_code"]!=self.originalresponse["status_code"]:
            diffs+="Status_Code-"
            status_diff = True
        if props["num_of_words"]!=self.originalresponse["num_of_words"]:
            diffs+="Words-"
        if props["num_of_lines"]!=self.originalresponse["num_of_lines"]:
            diffs+="Lines-"
        if abs(props["num_of_bytes"]-self.originalresponse["num_of_bytes"]) > 5:
            diffs+="Body Size-"
        if props["num_of_headers"]!=self.originalresponse["num_of_headers"]:
            diffs+="Headers Number-"
        if props["num_of_cookies"]!=self.originalresponse["num_of_cookies"]:
            diffs+="Cookies-"
        if abs(props["size_of_headers"]-self.originalresponse["size_of_headers"]) > 5:
            diffs+="Headers Size-"
        return (props["status_code"],props["num_of_reflects"],props["num_of_words"],props["num_of_bytes"],diff,status_diff,diffs.strip("-"))
        
    def filterHeaders(self):
        for header in self.headers.copy():
            if header.lower().startswith("accept"):
                del self.headers[header]
            if header.lower().startswith("if-"):
                del self.headers[header]
            if header.lower() == "connection":
                del self.headers[header]
            if header.lower().startswith("upgrade-insecure-requests"):
                del self.headers[header]
            if header.lower().startswith("sec-fetch-"):
                del self.headers[header]
            if header.lower() == "te":
                del self.headers[header]
            
    def calculateOriginal(self):
        #we set the "Accept-Encoding: identity" to prevent compressed responses
        try:
            req = requests.Request(method="get", url=self.url, headers=self.headers,params=self.baseParams)
            prep = req.prepare()
            response = None
            with requests.Session() as session:
                response = session.send(prep, verify=False,allow_redirects=False)
                if response == None:
                    response = session.send(prep, verify=False,allow_redirects=False)
            if response != None:
                self.originalresponse = self.getResponseProps(response)
                self.loadSetCookies(response)
        except:
            self.originalresponse = {}
    def chooseCookieValue(self):
        val = ""
        if self.value_type == "bad":
            val = badval
        elif self.value_type == "normal":
            val = normalval
        else:
            if self.custom_value.startswith("http"):
                val = self.custom_value+"/discobiscuits"
            else:
                val = self.custom_value
        return val
        
    def loadCookies(self):
        cookiestr=self.getHeaderValue(self.headers,"cookie")
        if cookiestr=="":
            return
        cookies=cookiestr.split(';')
        for cookie in cookies:
            cookie=cookie.strip()
            parts=cookie.split('=')
            if len(parts)<2:
                parts[1] = ""
            if not parts[0] in self.session_cookies:
                self.addthose.append(parts[0])
            else:
                self.baseCookies.update({parts[0]:parts[1]})
    def loadSetCookies(self,response):
        for header in response.headers:
            if header.lower() == "set-cookie":
                name = response.headers[header].split('=')[0]
                if not name in self.session_cookies:
                    if not name in self.addthose:
                        self.addthose.append(name)
    def run(self):
        #set accept-encoding to identity to avoid compressed response
        self.headers = self.setHeaderValue(self.headers,"Accept-Encoding","identity")
        #get base params
        self.getParams()
        #get base cookies
        self.loadCookies()
        #calculate original response
        self.calculateOriginal()
        #add host header is not there
        hostname = urlparse(self.url).netloc
        if self.getHeaderName(self.headers,"host") == None:
            self.headers["Host"] = hostname
        # add newly discovered cookies to list
        print(self.baseCookies)
        for entry in self.addthose:
            self.lines.append(entry)
        #divide parameters into groups
        chunk = {}
        for i in range(len(self.lines)):
            chunk.update({self.lines[i]:self.chooseCookieValue()})
            if i % self.num_of_cookies == 0:
                self.cookie_groups.append(chunk)
                chunk={}
        if i % self.num_of_cookies != 0:
            if chunk != {}:
                self.cookie_groups.append(chunk)
        #print just to be sure
        #print(self.param_groups)   #verified now go on
        if self.delay <= 0 and self.num_of_threads > 1:
            #send them to pool
            threadpool = ThreadPoolExecutor(max_workers=self.num_of_threads)
            #try to pass both reqtype and params_group to brute then make the compare in brute and return None if similar or params_group if not similar
            #futures = (threadpool.submit(self.brute, grp) for grp in self.param_groups)
            futures=[]
            for grp in self.cookie_groups:
                futures.append(threadpool.submit(self.brute, grp))
            for i, result in enumerate(as_completed(futures)):
                if result.result():
                    self.results_queue.put(result.result())
        else:
            for grp in self.cookie_groups:
                result = self.brute(grp)
                if result:
                    self.results_queue.put(result)
                if self.delay > 0:
                    time.sleep(self.delay)
        self.results_queue.put(None)
        
class CookieHammer:
    def __init__(self,url,method="GET",headers={},session_cookies=[],body="",num_of_cookies=20,num_of_threads=10,delay=0,wordlist="burp7070/headers.lst",value_type="normal",custom_value=""):
        self.results_queue = Queue()
        self.url = url
        self.method = method
        self.headers = headers
        self.num_of_cookies = num_of_cookies
        self.num_of_threads = num_of_threads
        self.delay = delay
        self.body = body
        self.session_cookies = session_cookies
        self.value_type = value_type
        self.custom_value = custom_value
        self.wordlist = wordlist
        fuzzer = Fuzzer(self.results_queue,self.url,self.method,self.headers,self.session_cookies,self.body,self.num_of_cookies,self.num_of_threads,self.delay,self.wordlist,self.value_type,self.custom_value)
        fuzzer.start()
        
    def __iter__(self):
        return self

    def __next__(self):
        res = self.results_queue.get()
        self.results_queue.task_done()
        if not res:
            raise StopIteration
        return res

