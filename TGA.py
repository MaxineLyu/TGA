from __future__ import division

from suds.client import Client
from suds.wsse import *
import requests as req


class TGA(object):
    def __init__(self, username, password):
        self.security = Security()
        self.token = UsernameToken(username, password)
                
        self.username = username
        self.password = password
        self.security.tokens.append(self.token)
        self.activeCodes = []
        
        self.orgService = "https://ws.training.gov.au/Deewr.Tga.Webservices/OrganisationService.svc?wsdl"
        self.trainService = "https://ws.training.gov.au/Deewr.Tga.Webservices/TrainingComponentService.svc?wsdl"
        self.classService = "https://ws.training.gov.au/Deewr.Tga.Webservices/ClassificationService.svc?wsdl"
        
        
    def getOrgDetails(self, code):
        
        client = Client(self.orgService)
        
        client.set_options(wsse=self.security)
        request = client.factory.create('OrganisationDetailsRequest')
        request.Code = code
        result = client.service.GetDetails(request)
        
        return result

    def getTrainDetails(self, code):
        
        client = Client(self.trainService)
        client.set_options(wsse=self.security)
        request = client.factory.create('TrainingComponentDetailsRequest')
        request.Code = code
        result = client.service.GetDetails(request)
        
        return result
        
    def getClassDetails(self):
        
        client = Client(self.classService)
        client.set_options(wsse=self.security)
        #request = client.factory.create('OrganisationDetailsRequest')
        
        return client
    
    def getCodeList(self):
        print "Getting code list..."
        activeCodes = []
        
        client = Client(self.orgService)
        client.set_options(wsse=self.security)
        
        request = client.factory.create('OrganisationNameSearchRequest')
        
        request.CurrentNamesOnly = True
        request.ExcludeNotRtos = True
        
        
        result = client.service.Search(request)
        out = []
        for org in result.Results[0]:
            if org.HasActiveRegistration:
                out.append(org.Code)

        print "Done."

        return out
        
        
    def getClassificationSchemes(self):
        client = Client(self.orgService)
        client.set_options(wsse=self.security)
        
        r = client.service.GetClassificationSchemes()
        classes = r[0][0].ClassificationValues.ClassificationValue
        
        dic = {}
        
        for c in classes:
            dic[c.Value.encode('utf-8')] = c.Name.encode('utf-8')
        return dic
    
    def getCodeListAx(self):
        activeRTOCode = []
        
        base_url = "https://tst.axcelerate.com.au/api/training/org/"
        r = req.get(base_url + 'search', 
                     params={'excludeInactive':1}, 
                     headers={'accept':'application/json',
                              'wstoken':'6FF2BFCF-04CE-4AE9-931F878BE478DFBA',
                              'apitoken':'778F701B-2A92-486B-BDE632F30B859293'})
        out = r.json()
        displayLength = out['displayLength']
        totalItems = out['total']
        pages = totalItems//displayLength + 1
        curPage = 0
        
        while curPage<pages:
            r = req.get(base_url + 'search', 
                     params={'excludeInactive':1, 'page':curPage}, 
                     headers={'accept':'application/json',
                              'wstoken':'6FF2BFCF-04CE-4AE9-931F878BE478DFBA',
                              'apitoken':'778F701B-2A92-486B-BDE632F30B859293'})
            out = r.json()
            curPage+=1
            for RTO in out['results']:
                if RTO['HASACTIVEREGISTRATION']=='Active':
                    activeRTOCode.append(RTO['CODE'])
        return set(activeRTOCode)

    def create_delivery_dict(self, org):
        '''for notif in org.DeliveryNotifications.DeliveryNotificationg:
        :return: {:NrtCode: [:state]}
        '''
        dic={}
        for notif in org.DeliveryNotifications.DeliveryNotification:
            delivery_scopes = [notifscope.Code for notifscope in notif.Scopes.DeliveryNotificationScope]
            state_count = 0 if not notif.GeographicAreas else len(notif.GeographicAreas.DeliveryNotificationGeographicArea)
            for scope_name in delivery_scopes: dic[scope_name] = state_count
        return dic

    def get_org_scale(self, org):
        delivery_dict = self.create_delivery_dict(org)
        
        print (sum(delivery_dict.values()), len(delivery_dict.keys()), sum(delivery_dict.values())/(len(delivery_dict.keys())*8) * 100)
        
        return sum(delivery_dict.values())/(len(delivery_dict.keys())*8) * 100
        
#        nrtcodes = set([scope.Code for notif in org.DeliveryNotifications.DeliveryNotification for scope in notif.Scopes.DeliveryNotificationScope])
#        
#        print delivery_dict
#        print len(nrtcodes)
#
#        return (sum([delivery_dict[nrtcode] for nrtcode in nrtcodes])/(len(nrtcodes) * 8) * 100, len(nrtcodes))



if __name__ == "__main__":
    tga = TGA()
#    r = tga.getTrainDetails("BSB60215")
#    orgService = "https://ws.training.gov.au/Deewr.Tga.Webservices/OrganisationService.svc?wsdl"
#    security = Security()
#    token = UsernameToken(username, password)
#    security.tokens.append(token)
#    
#    client = Client(orgService)
#    client.set_options(wsse=security)
#    
#    
#    r = tga.getClassificationSchemes()