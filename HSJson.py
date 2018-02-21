import analytics
import datetime
import pytz
from types import *
import copy
from TGA import TGA
import json
import requests as req
import suds


def registrationManagerLookup(key):
    if key:
        out={}
        
        out['01'] = 'Victorian Registration and Qualifications Authority'
        out['02'] = 'Queensland Department of Education and Training'
        out['03'] = 'South Australian Dept of Further Education, Employment, Science and Technology'
        out['04'] = 'Western Australian Department of Education Services'
        out['05'] = 'Office of the Tasmanian Qualifications Authority'
        out['06'] = 'Northern Territory Department of Employment, Education and Training'
        out['07'] = 'Australian Capital Territory Department of Education and Training'
        out['08'] = 'New South Wales Department of Education and Training'
        out['11'] = 'TVET Australia'
        out['12'] = 'Australian Skills Quality Authority'
        out['20'] = 'The body authorised to endorse Training Packages  and State and Territory Government Vocational and Technical Education Ministers'
        
        return out[key]
    else:
        return ''

def dataManagerLookup(key):
    if key:
        out={}
        
        out['01'] = 'Victorian Registration and Qualifications Authority'
        out['02'] = 'Queensland Department of Education and Training'
        out['03'] = 'South Australian Dept of Further Education, Employment, Science and Technology'
        out['04'] = 'Western Australian Department of Education Services'
        out['05'] = 'Office of the Tasmanian Qualifications Authority'
        out['06'] = 'Northern Territory Department of Employment, Education and Training'
        out['07'] = 'Australian Capital Territory Department of Education and Training'
        out['08'] = 'New South Wales Department of Education and Training'
        out['12'] = 'Australian Skills Quality Authority'
        out['11'] = 'TVET Australia'
        out['20'] = 'Department of Education, Employment and Workplace Relations'
        
        return out[key]
    else:
        return ''

def stateCodeLookup(key):
    if key:
        out={}
        
        out['01'] = 'New South Wales'
        out['02'] = 'Victoria'
        out['03'] = 'Queensland'
        out['04'] = 'South Australia'
        out['05'] = 'Western Australia'
        out['06'] = 'Tasmania'
        out['07'] = 'Northern Territory'
        out['08'] = 'Australian Capital Territory'
        out['09'] = 'Other Australian territories or dependencies'
        out['99'] = 'Other (overseas but not an Australian territory or dependency)'
        
        return out[key]
    else:
        return ''

def contactRolesLookup(key):
    if key:
        out={}
        
        out['1'] = 'Chief Executive'
        out['2'] = 'Registration Enquiries'
        out['128'] = 'Managerial Agent'
        out['4'] = 'Public Enquiries'
        
        return out[key]
    else:
        return ''

def orgRolesLookup(key):
    if key:
        out = {}
        
        out['1'] = 'Registered Training Organisation'
        out['2'] = 'State Training Authority'
        out['4'] = 'Training Package Developer'
        out['8'] = 'Data Manager'
        out['16'] = 'Registration Manager'
        out['32'] = 'Recognition Manager'
        
        return out[key]
    else:
        return ''

def purposeCodeLookup(key):
    if key:
        out = {}
        
        out['01'] = 'National VET Statistical Collections and Surveys'
        out['99'] = 'Other purposes'
        
        return out[key]
    else:
        return ''

def orgEndReasonLookup(key):
    if key:
        out = {}
        
        out['01'] = 'Registration period expired and a new registration period was approved to follow immediately.'
        out['02'] = 'Registration period expired.'
        out['03'] = 'Registration period expired, registration is taken to continue while a renewal application is considered.'
        out['10'] = 'Registration period was cancelled with consent of the copyright holder.'
        out['11'] = 'Registration period was cancelled without consent of the copyright holder.'
        out['14'] = 'Registration period is current, organisation under external administration or voluntary liquidation'
        out['20'] = 'Registration period was ended to facilitate a transfer of accreditation to another Authority.'
        out[''] = ''
        
        return out[key]
    else:
        return ''

def nrtEndReasonLookup(key):
    if key:
        out = {}
        
        out['01'] = 'Accreditation period expired and a new accreditation period was approved to follow immediately.'
        out['02'] = 'Accreditation period expired.'
        out['03'] = 'Accreditation period expired, accreditation is taken to continue while a renewal application is considered.'
        out['10'] = 'Accreditation period was cancelled with consent of the copyright holder.'
        out['11'] = 'Accreditation period was cancelled without consent of the copyright holder.'
        out['20'] = 'Accreditation period was ended to facilitate a transfer of accreditation to another Authority.'
        out[''] = ''
        
        return out[key]
    else:
        return ''
    
def schemeCodeLookup(key):
    if key:
        out = {}
        
        out['01'] = 'ANZSCO'
        out['02'] = 'ASCO'
        out['03'] = 'Module/Unit of Competency Field of Education (ASCED6)'
        out['04'] = 'Qualification/Course Field of Education (ASCED4)'
        out['05'] = 'Qualification/Course Level of Education (Qual Level)'
        out['06'] = 'Nationally Recognised Training Type (NRT Type)'
        
        return out[key]
    else:
        return ''

def classSchemeLookup(key):
    
    return schemes[key]

def unix_millis(dt):
    #convert date to datetime
    if type(dt) == datetime.date:
        dt = datetime.datetime.combine(dt, datetime.datetime.min.time())
    #timezone -> UTC
#    dt -= datetime.timedelta(hours=24)
    #calculate millis
    epoch = datetime.datetime.utcfromtimestamp(0)
    return long((dt - epoch).total_seconds() * 1000.0)

def createJson0(obj):
    if type(obj) == ListType:
        out = [createJson0(item) for item in obj]
    elif type(obj) != InstanceType:
        out = obj
    else:
        out = dict((key, createJson0(getattr(obj, key))) for key in obj.__keylist__)
    return out

def createOrgJson(obj, out = {}, parentTrail = '', parentList = False):
    o = out
    if 'Scope' not in parentTrail and 'DeliveryNotification' not in parentTrail and 'OffsetMinutes' not in parentTrail:
        if type(obj) == ListType: #if the input is a list
            for item in obj:
                o = createOrgJson(item, out = o, parentTrail = parentTrail, parentList = True)
                
        elif type(obj) != InstanceType: #if the input is the at the bottom of the recursion
            
            if type(obj) == datetime.date or type(obj) ==datetime.datetime:
                value = unix_millis(obj)
            elif type(obj) == suds.sax.text.Text:
                try:
                    value = str(obj)
                except UnicodeEncodeError:
                    value =  obj.encode('utf-8')
            elif type(obj) == NoneType:
                value = ""
            else:
                value = str(obj)
            if 'datamanagerassignment_code' in parentTrail.lower():
                value = dataManagerLookup(obj)
                parentTrail = parentTrail[:-5]
            elif 'purposecode' in parentTrail.lower():
                value = purposeCodeLookup(obj)
                parentTrail = parentTrail[:-4]
            elif 'statecode' in parentTrail.lower():
                value = stateCodeLookup(obj)
                parentTrail = parentTrail[:-4]
            elif 'registrationmanagerassignment_code' in parentTrail.lower():
                value = registrationManagerLookup(obj)
                parentTrail = parentTrail[:-5]
            elif 'schemecode' in parentTrail.lower():
                value = schemeCodeLookup(obj)
            elif 'valuecode' in parentTrail.lower():
                value = classSchemeLookup(obj)
                parentTrail = parentTrail[:-4]
                    
            if 'endreasoncode' in parentTrail.lower() and obj!=None:
                value = orgEndReasonLookup(obj)
                parentTrail = parentTrail[:-4]
                parentTrail+="comments"
            o[parentTrail.lower()] = value
        else: #if the object is an instance
            for key in obj.__keylist__:
                if 'enddate' not in key.lower() or obj[key]>datetime.date.today():
                    if key == 'Contacts':
                        o['contacts'] = createContactJson(obj)
                    elif key == 'TradingNames':
                        o['tradingname_name'] = createTradingNameJson(obj.TradingNames)
                    else:
                        prefix = "" if parentTrail == "" else "_"
                        pt = parentTrail+prefix+key
                        if key.endswith('s') and not key.endswith('Abns') and not key.endswith('ddress') and not key.endswith('Restrictions') and not key.endswith('Minutes') and not key.endswith('EndReasonComments'):
                            pt = parentTrail
                        o = createOrgJson(getattr(obj, key), out = o, parentTrail=pt)
    return o

def createTradingNameJson(inst):
    out=''
    if type(inst)!=NoneType:
        for tn in inst[0]:
            out+=tn.Name + "; "
    return out
    
def createContactJson(obj):
    identities = []
    out=[]
    for contact in obj.Contacts[0]:
        if not contact.__contains__('EndDate'):
            js = contactRecursion(contact)
            identity = (js['firstname'], js['lastname'], js['email'], js['phone'])
            if identity not in identities:
                identities.append(identity)
                out.append(copy.deepcopy(js))
            else:
                index = identities.index(identity)
                newrole = out[index]['role'] + ';'+js['role']
                out[index]['role'] = newrole         
    return out

def contactRecursion(obj, key='', out={}):
    o=out
    if type(obj)!=InstanceType:
        if type(obj) == datetime.date:
            value = unix_millis(obj)
        elif type(obj)==NoneType:
            value = ''
        else:
            try:
                value = str(obj)
            except UnicodeEncodeError:
                value = obj.encode('utf-8')
        o[key.lower()] = value
    else:
        for attr in obj.__keylist__:
            if attr == 'LastName' and obj[attr]!=None:
                if len(obj[attr].split(' '))>1:
                    o['middlename'] = ''.join(obj[attr].split(' ')[1:])
                else:
                    o['middlename'] = ''
                value = obj[attr].split(' ')[0]
            if attr != 'TypeCode':
                prefix ='' if key =="" else "_"
                k=key+prefix+attr
                if 'StateCode' in k:
                    value = stateCodeLookup(obj[attr])
                    k = k[:-4]
                elif 'RoleCode' in k:
                    value = contactRolesLookup(obj[attr])
                    
                    k=k[:-4]
                else:
                    value = obj[attr]
                o = contactRecursion(value, key=k, out=o)
    return o 
   
def sendSegment(data):
    analytics.write_key="87GPbpE99eOSSdTT0VhrSTVJ4aCE2r9F"
    analytics.debug = True
    analytics.on_error = on_error
    analytics.identify('maxinetestdata', data)
    analytics.flush()
    
def on_error(error, items):
    print ("An error occured: ",error)


def mapHSattr(obj):
    if isCompany(obj):
        a = ['responsiblelegalperson_name', 'organisationlocation_address_line1', 'organisationlocation_address_line2', 'url_link', 'organisationlocation_address_postcode', 'url_startdate', 'organisationlocation_address_countrycode', 'registrationmanagerassignment_startdate', 'registrationmanagerassignment', 'datamanagerassignment', 'datamanagerassignment_startdate', 'responsiblelegalperson_startdate', 'classification_value']
        b = ['name', 'address', 'address2', 'website', 'zip', 'website_startdate', 'country', 'registrationmanager_startdate', 'registration_manager', 'datamanager', 'datamanager_startdate', 'name_startdate', 'rto_type']
    else:
        a=['organisationname', 'postaladdress_line1', 'postaladdress_postcode', 'postaladdress_state', 'postaladdress_countrycode', 'mobile']
        b=['company', 'address', 'zip', 'state', 'country','mobilephone']
    for pair in zip(a,b):
        old, new = pair
        obj = replaceKeyinDict(obj, old, new)
    if obj['country']=='1101':
        obj['country'] = 'Australia'
    return obj
    
def replaceKeyinDict(obj, oldkey, newkey):
    if oldkey in obj.keys():
        value = obj[oldkey]
        obj[newkey] = value
        del obj[oldkey]
    
    return obj
    
def dothething():
    print "Getting the RTO code list..."
    #RTOCodes = getRTOCodeList()
    count = 0
    countsofar=0
    tga = TGA()
    print "Done."
    print "Finding trading names..."
    for code in RTOCodes:
        countsofar+=1
        curTrade = 0
        TradingNames = tga.getOrgDetails(str(code)).TradingNames
        print "RTO code:",code
        if type(TradingNames) != NoneType:
            for tradingName in TradingNames[0]:
                if 'EndDate' not in tradingName.__keylist__:
                    curTrade+=1
            if curTrade>1:
                count+=1
        print ("Number of RTO with more than 1 trading names so far: {0}/{1}".format(count, countsofar))
    return count

def createJson(obj):
    o= createOrgJson(obj)
    o = mapHSattr(o)
    c = o['contacts']
    newc=[]
    for person in c:
        newc.append(mapHSattr(person))
    c=newc
    del o['contacts']
    del o['createddate_datetime']
    del o['updateddate_datetime']
    if 'restrictions_rtorestriction_code' in o.keys():
        del o['restrictions_rtorestriction_code'] 
    if 'registrationperiod_endreasoncode' in o.keys():
        del o['registrationperiod_endreasoncode']
    if '' in o.keys():
        del o['']
    o['state'] = o['organisationlocation_address_state']
    
    
    return (o, c)

def get_HS_Json(js, company=True):
	out={}
	l=[]
	for key in js.keys():
		if key != "organisation" and key != "emaildomain":
			l.append(hsnamevalue(key, js[key], company=company))
	out['properties'] = l
	
	return out

def hsnamevalue(key, value, company = True):
    out = {}
    if company:
        out['name'] = key
        out['value'] = value
    else:
        out['property'] = key
        out['value'] = value
    return out

def isCompany(obj):
    return True if type(obj)==dict and 'organisationcode_code' in obj.keys() else False

def checkEmails(l):
    '''
    take in a list of Json objects representing contacts
    output de-duplicated email-wise list of contacts
    '''
    out=[]
    temp = []
    for c in l:
        emailA = c['email'].lower()
        p = isEmailowner(c)
        if not p:
            if len(temp)>0:
                if (c, p) not in temp:
                    for o in temp:
                        emailB = o[0]['email'].lower()
                        print "\t"+str(emailA==emailB)
                        if emailA == emailB: # if not important and share email
                            if not o[1]:#if existant is not priority
                                temp.append((c, p))
                        else: # if not important and not share email
                            temp.append((c,p))
            else:
                temp.append((c,p))
        else:
            if (c, p) not in temp:
                for o in temp:
                    
                    emailB = o[0]['email'].lower()
                    print "\t"+str(emailA==emailB)
                    if emailA == emailB:# if important and share email
                        if not o[1]:
                            temp.remove(o)
                    temp.append((c, p))
    
    for c in temp:
        out.append(c[0])
                
    return out
    
def isEmailowner(c):
    '''
    take in a contact json, check if is the priority owner (firstname or lastname in email address)
    return bool
    '''
    email, firstname, lastname = c['email'], c['firstname'], c['lastname']
    
    return True if firstname.lower() in email or lastname.lower() in email else False
        
    
def createHSJson(obj):
    company = isCompany(obj)
    out = {}
    if not company:
#        obj = checkEmails(obj)
        out=[]
        dic={}
        for person in obj:
            l=[]
            roles = person['role']
            person['role'] = roles
            if person['email'] == '':
                del person['email']
            for key in person.keys():
                l.append(hsnamevalue(key,person[key], company=company))
            dic['properties'] = copy.deepcopy(l)
            out.append(copy.deepcopy(dic))
                
    else:
        l=[]
        keys = obj.keys()
        for key in keys:
            l.append(hsnamevalue(key, obj[key], company = company))
        out['properties'] = l
    
    return out


if __name__ == "__main__":
    base_url = 'https://tst.axcelerate.com.au/api/training/org/'
    code = '45241'
    tga = TGA()
    schemes = tga.getClassificationSchemes()
    r = tga.getOrgDetails(code)
    o, c = createJson(r)
    c0=createHSJson(c)
    o0=createHSJson(o)
#    codes = getRTOCodeList()
#    for code in codes:
#        tga =TGA()
#        r = tga.getOrgDetails(code)
#        o, c = createJson(r)
#        o = createHSJson(o)
    url = 'https://app.hubspot.com/oauth/authorize?client_id=d24e5302-1c44-4327-9f57-e107dfc1fd1d&redirect_uri=https://www.hubspot.com&scope=contacts%20content%20reports%20social%20automation%20timeline%20forms%20files%20hubdb%20transactional-email'