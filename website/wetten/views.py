#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from django.utils import simplejson as json
import urllib2
import QueryNetwork as QN
import CitesParser as CP
import SparqlHelper as sparql
import re
import pickle

def index(request):
    return HttpResponse("Gebruiksinfo")

def doc(request, document):
    sparqlHelper = sparql.SparqlHelper()
    humanDescriptions = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/human_descriptions.pickle', 'r'))
    # List of BWB's in the subset
    bwbDocuments = ['BWBR0002226', 
                    'BWBR0002227', 
                    'BWBR0002320', 
                    'BWBR0005537', 
                    'BWBR0011353', 
                    'BWBR0027018']
    
    bwb_links = []
    for bwbDocument in bwbDocuments:
        bwb_links.append(sparqlHelper.getLatestTitleAndExpressionForBWB(bwbDocument))
    
    metalexData = urllib2.urlopen('http://doc.metalex.eu/doc/' + document)
    metalexXML = metalexData.read()
    bwb = re.findall('BWBR\d{7}', document)[0]
    
    query = QN.QueryNetwork()
    entities = query.sortEntitiesForBWB(bwb)
    
    context = {'metalexXML': metalexXML, 
               'entities': entities, 
               'bwb_links': bwb_links, 
               'descriptions': humanDescriptions}
    return render(request, 'wetten/doc.html', context)

def related(request):
    parser = CP.CitesParser()
    human_descriptions = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/human_descriptions.pickle'))
    bwb_titles = pickle.load(open('/Users/Ivan/Documents/Beta-gamma/KI jaar 2/Afstudeerproject/Project/Python/wetten.nl/bwb_titles.pickle'))
    
    entity = request.GET.get('entity')
    entityDescription = parser.entityDescription(entity)
    if entityDescription:
        query = QN.QueryNetwork()
        
        if not query.entityIsInGraph(entityDescription):
            return HttpResponse(json.dumps({'success': False}))
        
        relatedEntities = query.sortRelatedEntities(entityDescription)  
        
        # Render div's for internal sources
        template = loader.get_template('wetten/related.html')
        context = Context({'entities': relatedEntities['internal'],
                           'descriptions': human_descriptions,
                           'bwb_titles': False})
        internal = template.render(context)
        
        # Render div's for external sources
        context = Context({'entities': relatedEntities['external'],
                           'descriptions': human_descriptions,
                           'bwb_titles': bwb_titles})
        external = template.render(context)
        
        data = {'success': True,
               'internal': internal,
               'external': external
               }
        
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponse(json.dumps({'success': False}))
    
def relatedContent(request):
    sparqlHelper = sparql.SparqlHelper()
    entity = request.GET.get('entity')
    
    # Get latest expression
    expression = sparqlHelper.getLatestDocForEntity(entity)
    metalexData = urllib2.urlopen(expression)
    metalexXML = metalexData.read()
    
    closeLink = '<div id="close_details">Sluit dit venster</div>\n'
    return HttpResponse(closeLink + metalexXML)
        