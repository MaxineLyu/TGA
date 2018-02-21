import requests as req
import json
import sudsUse as su
import time
from datetime import datetime
from TGA import *
import pickle
import urllib2
import os
import utils

'''
deleteHardBounced(csv)
'''


class HSautomation():
    def __init__(self, codes2upload=[]):
        print "Initializing..."

        self.new_company = []
        self.updated = []
        self.cid2scale={}
        self.code2cid = {}

        self.codelist = []
        
        self.sofar = {}  # RTOcode uploaded so far
        self.currentCompany = {}  # current company
        self.currentContacts = []  # current contacts
        self.currentCompanyId = None
        self.currentvids = []
        self.existedContacts = {}
        self.baseurl = "https://api.hubapi.com/"
        self.hapikey = "7542f67a-16dc-4936-ae03-cdc24543b4d0"
        self.tga = TGA()
        self.error = {}
        self.headers = {"content-type": "application/json"}

        print "Getting the RTO code list..."

        self.codes = codes2upload
        self.ourCustomer = []

        print "List got."
        self.currentIndex = 0  # current index of the code list
        print "Initialization done."

    def store_all_org(self, codelist=None):
        if not self.codelist and not codelist: self.codelist = self.tga.getCodeList()
        for code in self.codelist:
            self.store_one_org(code)
        self.solve_error()

        return self.sofar

    def store_one_org(self, code):
        try:
            print "Storing org details of code", code
            org = self.tga.getOrgDetails(code)
            self.sofar[code] = org
            print "Done."
            if code in self.error.keys():
                print "Removing from error log."
                del self.error[code]
        except Exception, e:
            print "Failed. Put in error log."
            self.error[code] = e

    def solve_error(self):
        while self.error:
            code = self.error.keys()[0]
            print "Solving error of code", code
            self.store_one_org(code)
        
    
    def runOrgScalePipe(self, codelist=None):
        print "Getting {:RTOcode: :Cid} ..."
        code2cid = self.code2cid if self.code2cid else self.getCompanyCids()
        print "Done."
        if not codelist or self.codelist:
            print "Getting code list..."
            codelist = self.tga.getCodeList()
            print "Done."

          
        for code in codelist:
            try:
                print "Code:", code
                org = self.tga.getOrgDetails(code)
                self.sofar.append(org)
                if org.DeliveryNotifications and org.Scopes:
                    if code in code2cid.keys():
                        print "Cid:", code2cid[code]
                        score, qualsno = self.tga.get_org_scale(org)
                        print "Score:", score
                        self.cid2scale[(code2cid[code], code)] = (score, qualsno)
                    else:
                        print "New company {} found!".format(code)
                        self.new_company.append(code)
            except Exception, e:
                self.error[code] = e
                time.sleep(15)
        utils.savePickle(var=self.sofar, filename="all_TGA")
        utils.savePickle(var=self.cid2scale, filename="cid2scale")
        utils.savePickle(var=self.error, filename="scalepipeError")
        utils.savePickle(var=self.new_company, filename="new_company")
#        for cid, code in self.cid2scale.keys():
#            print "Updating company with RTOcode: {}".format(code)
#            self._updateCompany('scale_score', self.cid2scale[(cid, code)], companyID=cid)
#            print "Update finished"
#            self.updated.append(code)
        

    def _addContact2Company(self, vid, companyId):
        print "Adding contacts to company"

        url = 'https://api.hubapi.com/companies/v2/companies/{0}/contacts/{1}?hapikey={2}'.format(str(companyId),
                                                                                                  str(vid),
                                                                                                  self.hapikey)

        print url
        r = req.put(url)
        self._printR(r)

        return json.loads(r.text)

    def _getContactValue(self, data, key):
        ps = data['properties']
        for p in ps:
            if key in p.values():
                return p['value']

    def _getCompanyValue(self, key):
        ps = self.currentCompany['properties']
        for p in ps:
            if key in p.values():
                return p['value']

    def _updateCompany(self, key, value, companyID=None):
        ID = companyID if companyID else self.currentCompanyId
        data = {
            "properties": [
                {
                    "name": key,
                    "value": value
                }
            ]
        }
        url = self.baseurl + "companies/v2/companies/{0}?hapikey={1}".format(ID, self.hapikey)
        r = req.put(url, data=json.dumps(data), headers=self.headers)

        #        self._printR(r)
        return r

    def uploadCompany(self, company):
        '''
		return r
		'''
        print "Uploading company..."

        url = self.baseurl + "companies/v2/companies?hapikey=" + self.hapikey
        r = req.post(url, data=json.dumps(company), headers=self.headers)

        self._printR(r)

        return json.loads(r.text)

    def uploadContact(self, contact):
        '''
		return r
		'''
        print "Uploading contact ..."
        url = self.baseurl + "contacts/v1/contact/?hapikey=" + self.hapikey

        r = req.post(url, data=json.dumps(contact), headers=self.headers)
        self._printR(r)

        return json.loads(r.text)

    def _uploadContacts(self, inp=None):
        print "Uploading contacts ..."
        data = inp if inp else self.currentContacts
        self.currentvids = []
        emails = []
        r = None

        url = self.baseurl + "contacts/v1/contact/?hapikey=" + self.hapikey
        for person in data:
            email = self._getContactValue(person, 'email')
            if email and email not in emails:
                print "\t Uploading contact with email {0}".format(email)
                try:
                    r = req.post(url, data=json.dumps(person), headers=self.headers)
                    self._printR(r)
                    vid = json.loads(r.text)['vid']
                    self.currentvids.append(vid)
                    self._addContact2Company(vid, self.currentCompanyId)
                    emails.append(email.lower())
                except Exception, e:
                    self.error.append((self.currentCompanyId, e))
                    self.existedContacts[email] = self._getCompanyValue('name')
                    self._updateCompany('email', email)

        print "\tContacts uplodaing finished"
        return r

    def _uploadCompany(self, inp=None):
        data = inp if inp else self.currentCompany

        print "\tUploading the company..."
        url = self.baseurl + "companies/v2/companies?hapikey=" + self.hapikey
        r = req.post(url, data=json.dumps(data), headers=self.headers)

        self._printR(r)
        self.currentCompanyId = json.loads(r.text)['companyId']

        print "\tCompany uplodaing finished"

        return r

    def getContactbyId(self, Id):
        url = self.baseurl + "contacts/v1/contact/vid/{0}/profile?hapikey={1}".format(str(Id), self.hapikey)
        r = req.get(url, headers=self.headers)
        self._printR(r)

        return r

    def getACompanyPropValues(self, companyId, keys=[]):
        '''
		Return a dictionary that
		always has companyId as well as
		all the values belong to keys under 'properties'
		'''
        if type(companyId)== str: companyId=self.code2cid[companyId]
        url = self.baseurl + "companies/v2/companies/{0}?hapikey={1}".format(companyId, self.hapikey)
        r = req.get(url).text
        c = json.loads(r)

        out = {}
        out['companyId'] = companyId

        if keys == []:
            keys = c['properties'].keys()
        out = dict((key, c['properties'][key]['value']) for key in keys)
        out['companyId'] = c['companyId']

        return out

    def getCompanyPropKeys(self):
        url = self.baseurl + "properties/v1/companies/properties?hapikey=" + self.hapikey
        r = req.get(url).text
        ps = json.loads(r)
        out = []

        for p in ps:
            out.append(p['name'])

        return out

    def _uploadnassociate(self):
        self._uploadCompany()
        self._uploadContacts()

    def _printR(self, r):
        #        if r.text['status'] == 'error':
        print "*************************************************************************"
        print r.text
        print self.currentCompanyId
        print "*************************************************************************"
        print

    def _saveError(self):
        with open('error-{0}.pickle'.format(datetime.strftime(datetime.today(), '%Y-%m-%dT%H-%S')), 'w') as f:
            pickle.dump(self.error, f)

    def _saveExistedContacts(self):
        with open('existedContacts2Company-{0}.pickle'.format(dateti
                  me.strftime(datetime.today(), '%Y-%m-%dT%H-%S')),
                  'w') as f:
            pickle.dump(self.existedContacts, f)

    def _getCompanyValuesPerPage(self, companies, dic={}, outterkey='companyId'):
        '''
		'''
        for c in companies:
            inner = {}
            keys = c['properties'].keys()
            for key in keys:
                value = c['properties'][key]['value'].lower()
                if key == outterkey:
                    if value in dic.keys():
                        dic[value].append(inner)
                    else:
                        dic[value] = [inner]  # for duplication detection
                else:
                    inner[key] = value

            companyId = c['companyId']
            if outterkey == 'companyId':
                value = companyId
            else:
                inner['companyId'] = companyId

        return dic

    def _getCompanyCidPerPage(self, companies, dic={}):

        for c in companies:
            if 'organisationcode_code' in c['properties'].keys():
                dic[c['properties']['organisationcode_code']['value']] = c['companyId']

        return dic

    def getCompanyCids(self):
        url = self.baseurl + "companies/v2/companies/paged?hapikey={0}&properties=organisationcode_code&limit=250".format(
            self.hapikey)
        r = req.get(url)
        r = json.loads(r.text)
        out = {}

        offset = r['offset']
        hasmore = r['has-more']

        while hasmore:
            companies = r['companies']
            out = self._getCompanyCidPerPage(companies, dic=out)
            r = req.get(url + "&offset={0}".format(str(offset)))
            r = json.loads(r.text)
            offset = r['offset']
            hasmore = r['has-more']

        companies = r['companies']
        out = self._getCompanyCidPerPage(companies, dic=out)
        
        self.code2cid = out
        return out

    def getContactByEmail(self, email):
        url = self.baseurl + "contacts/v1/contact/email/{0}/profile?hapikey={1}".format(email, self.hapikey)
        r = req.get(url)
        r = json.loads(r.text)
        return r

    def deleteContact(self, vid):
        url = self.baseurl + "contacts/v1/contact/vid/{0}?hapikey={1}".format(vid, self.hapikey)
        r = req.delete(url)
        r = json.loads(r.text)

        return r

    def getAllCompanyValues(self, keys, innerkey):
        '''
		type(keys) = list
		'''
        url = self.baseurl + "companies/v2/companies/paged?hapikey={0}&limit=250".format(self.hapikey)
        for key in keys:
            url += "&properties={0}".format(str(key))
        r = req.get(url).text
        r = json.loads(r)

        offset, hasmore = r['offset'], r['has-more']

        out = {}
        while hasmore:
            companies = r['companies']
            out = self._getCompanyValuesPerPage(companies, dic=out, outterkey=innerkey)
            r = req.get(url + "&offset={0}".format(str(offset)))

            r = json.loads(r.text)
            offset, hasmore = r['offset'], r['has-more']

        companies = r['companies']
        out = self._getCompanyValuesPerPage(companies, dic=out, outterkey=innerkey)

        return out

    def globalBouncedEmails(self, csv):
        csv = utils.readCSV(csv)
        if csv[0][4] == "Global Bounce" and csv[0][1] == "Portal Bounce":
            emails = [row[0] for row in csv if row[1] == "TRUE" or row[4] == "TRUE"]
            return emails
        else:
            print "4th column of the CSV file is not Global Bounce"

    def deleteHardBounced(self, csv):
        emails = self.globalBouncedEmails(csv)

        for email in emails:
            try:
                r = self.getContactByEmail(email)
                vid = r['vid']
                r = self.deleteContact(vid)
                print r
            except Exception, e:
                print e

    def findDuplication(self, data):
        '''
		'''
        out = {}
        keys = data.keys()

        for key in keys:
            l = data[key]
            if len(l) > 1:
                out[key] = l

        return out

    def run(self, code=None):
        self.ourCustomer = self.getCompanyCids().keys()
        if code:
            tga = TGA()
            r = tga.getOrgDetails(code)
            o, c = su.createJson(r)
            self.currentCompany, self.currentContacts = su.createHSJson(o), su.createHSJson(c)
            print "Done creating!"
            print "Uploading..."
            self._uploadnassociate()

        else:
            for code in self.codes:
                r = self.tga.getOrgDetails(code)
                print "Creating the Json data for code {0}".format(code)

                o, c = su.createJson(r)
                self.currentCompany, self.currentContacts = su.createHSJson(o), su.createHSJson(c)
                print "Done creating!"
                print "Uploading..."
                self._uploadnassociate()

                isOurCustomer = "true" if code in self.ourCustomer else "false"
                self._updateCompany('axcelerate_customer', isOurCustomer)

                self.sofar.append(code)
                print "Upload successful. RTOcodes so far: " + str(self.sofar)

            #                except Exception, e:
            #                    self.error.append((code, e))
            #
            #                except urllib2.URLError, e:
            #                    self.error.append((code, e))
        self._saveError()
        self._saveExistedContacts()


def getContactvids():
    """
    get a list of existed vids beforehand, for vid creation
    """
    apikey = "7542f67a-16dc-4936-ae03-cdc24543b4d0"
    url = "https://api.hubapi.com/contacts/v1/lists/all/contacts/all?hapikey={0}&count=400".format(apikey)
    r = req.get(url)
    r = json.loads(r.text)
    out = []
    for c in r["contacts"]:
        print c
        out.append(c["vid"])

    return out


def tryDropdownFormat():
    apikey = "7542f67a-16dc-4936-ae03-cdc24543b4d0"
    data = o0

    headers = {"content-type": "application/json"}
    url0 = "https://api.hubapi.com/companies/v2/companies?hapikey=" + apikey
    url1 = "https://api.hubapi.com/contacts/v1/contact/?hapikey=" + apikey
    r = req.post(url0, data=json.dumps(data), headers=headers)

    return r


def loadErrorPickle():
    path = "D:/Project/TGA"
    files = os.listdir(path)
    l = []

    for fl in files:
        if fl.startswith("error"):
            with open(fl, 'r') as f:
                e = pickle.load(f)
                l.extend(e)
    return l


def createCodeDict():
    with open('error.pickle', 'r') as f:
        l = pickle.load(f)

    dic = dict((i[0], i[1]) for i in l)

    return dic


def createErrorDict():
    with open('error.pickle', 'r') as f:
        l = pickle.load(f)

    dic = dict((str(i[1]), []) for i in l)

    for i in l:
        l0 = dic[str(i[1])]
        l0.append(i[0])

    return dic


def saveAsPickle(filename, var):
    with open(filename + ".pickle", 'w') as f:
        pickle.dump(var, f)


def checkHSmissed():
    hs = HSautomation()
    o = hs.getCompanyCids()

    out = []

    codes = govL

    for code in o.keys():
        if code not in codes:
            out.append(code)

    return out


if __name__ == "__main__":
    hs = HSautomation()
    orgs = hs.store_all_org()
    utils.savePickle(var=orgs, filename="AllOrgs")