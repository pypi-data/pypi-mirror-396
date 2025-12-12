import asyncio
#import concurrent.futures

import json
import time
import re
import itertools

from typing import Optional
from typing_extensions import Final
from pyrsistent import m, pmap, PMap
from pymonad.either import Either, Left, Right
from pymonad.promise import Promise
from pymonad.tools import curry


from semantic.common.utils import msg, err, redMsg, greenMsg, to_json_ld_type, resolve_either, reject_promised, reject_either,  instance_count, idForPath, property_value_type, has_nested_list
from semantic.common.common_types import SchemaId, PipeArg, TripleType, QueryOptions
from semantic.api.semantic_client import semanticClient

'''
    terminology:
                       <- Reverse | Forward ->
                domain <- subject.predicate -> range

                use: Forward
                  triple(  subject, predicate, range )
                use: Reverse
                  triple( domain, predicate ,subject )
                use: DoubleReverse
                  triple( domain2, predicate2, domain1 ) and triple (domain1, predicate1, subject )
'''



class query_object:
    '''
        post-conditions: result.frame is array of (nested) TripleType
    '''

    def __init__(self, type: Optional[str]=None):
        
        self.type: str = type
        self.triples: list[TripleType] = list() 
        self.type_class_module: str = None
        self.typeQueryLast: bool = False

        '''
            we have full info to add a query by type at the end of the query
            however, better to make the user make an explicit where_type call
            to allow the user to avoid query by type (explicit wins over implicit
        '''
        if type:
            self.type_triple: TripleType = {
                                                "type": 'QueryTriple',
                                                "use": 'Forward',
                                                "where": 'WhereType',
                                                "predicate": 'type',
                                                "value": self.type
                                        }
            self.append(self.type_triple)
            #greenMsg("query_object: triples "+json.dumps(self.type_triple, indent=6))
    
    def module_for_type(self, module: str):
        self.type_class_module = module
        return self
        
    def shiftTypeQueryLast(self, last: bool):
        self.typeQueryLast = last
        return self

    def append(self, type_triple: TripleType):
        if type_triple:
            self.triples.append(type_triple)
        else:
            redMsg('append: _triple is not defined')
        return self

    
    def where_samples(self, sample_set_prop, sample_set_value):

        uri_triple: TripleType = {
                                                "type": 'QueryTriple',
                                                "use": 'Reverse',
                                                "where": 'WhereSamples',
                                                "predicate": sample_set_prop,
                                                "value": sample_set_value
                                }
        self.append(uri_triple)
        return reverse_predicate(use='ReverseData', obj= self, property= 'hasSample')

    def where_uri(self, *uri: str):

        isNested = has_nested_list(uri)
       
        uris = list(itertools.chain.from_iterable(uri)) if isNested else uri

        isMultiple = len(uris) > 1

        uri_triple: TripleType = {
                                                "type": 'QueryTriple',
                                                "use": 'Forward',
                                                "where": 'WhereUris' if isMultiple else 'WhereUri',
                                                "predicate": '@id',
                                                "value": uris if isMultiple else uris[0]
                                }
        self.append(uri_triple)
        return self

    def where_type(self,  type: str):
        '''
            module and type are required for anyobject property match
            due to requirement for determining property value type from 
            the type schema defined in module

            non-property query such as by id do not need module and type

            users have to explicitly call where_type to query by type
        '''

        type_triple: TripleType = {
                                                "type": 'QueryTriple',
                                                "use": 'Forward',
                                                "where": 'WhereType',
                                                "predicate": 'type',
                                                "value": type if len(type) > 1 else type[0]
                                        }
        if type:
            self.type = type
            self.append(type_triple)
        else:
            redMsg('where_type: type is not defined')

        #greenMsg(f'where_type triples {json.dumps(self.triples, indent=6)}')
        return self

    # def where_property(self, property: str, value_type: Optional[str]=None):
        #return predicate(use= 'Forward', obj= self, property= property, value_type= value_type)


    def where_property(self, property: str):
        return predicate(use= 'Forward', obj= self, property= property)

    def where_reverse_property(self, property: str ):
        return reverse_predicate(use='Reverse', obj= self, property=  property)
        

    def where_property_element(self, property: str, index: int):
        return predicate( use='Forward', obj= self, property= property, index= index)


    def selecting(self, *properties):
        [ predicate(use= 'Selecting', obj= self, property= prop) for prop in properties ]    
        return self
    
    def  query(self):
        head = 0
    
        if len(self.triples) == 0:
            redMsg('Error: no where clause (query) defined on object: suggest subject.where_type(type=type))')

        #greenMsg(f'query triples {json.dumps(self.triples, indent=6)}')

        if self.typeQueryLast == True and self.triples[head]['predicate'] == 'type':
            '''
                triple for type in some cases should come last for datalog performance reasons (softer, outer constraint)
            '''
            tail = len(self.triples) - 1
            self.triples[tail], self.triples[head] = self.triples[head], self.triples[tail]
        
        result = to_json_ld_type(self.triples)
        #greenMsg(f'query result {json.dumps(result, indent=6)}')
        return result
    
   
class predicate:
   
    def __init__(self, use: str, obj: query_object , property: str, index: Optional[int] = None):
        self.use = use
        self.obj = obj

        self.property = property
        self.index = index
        self.value_type = None
        if use == 'Selecting':
            type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": 'Selecting',
                                        "where": 'Selecting',
                                        "matches": None,
                                        "predicate": property,
                                        "value": property,
                                        "valueType": None,
                                        "index": None
                        }
            self.obj.append(type_triple)
            

    def matches_any_value(self):
        #greenMsg(f"matches_value: self.object.type_class_module: {self.object.type_class_module} self.object.type {self.object.type} self.property {self.property}")

        where :str = 'WhereProperty'
        '''
        if self.index is not None and t is not None:
            where = 'WherePropertyElement'
        '''
      
        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": where,
                                        "matches": 'MatchesAnyValue',
                                        "predicate": self.property,
                                        "value": None,
                                        "valueType": None,
                                        "index": self.index
                        }
        self.obj.append(type_triple)
        return self.obj
    

    def matches_value(self, value: any, value_type: Optional[str]=None, returnPredicate: Optional[bool]=None):
        #greenMsg(f"matches_value: self.obj.type_class_module: {self.obj.type_class_module} self.obj.type {self.obj.type} self.property {self.property}")
    
        self.value_type = value_type
        have_value_type = (not value_type is None)

        t = value_type if have_value_type else property_value_type(self.obj.type_class_module, self.obj.type, self.property).get('woqlclass') if self.obj.type_class_module is not None else 'xsd:string'
        #greenMsg(f"matches_value: self.value_type t {t}          have_value_type {have_value_type}")

        where :str = 'WhereProperty'
        if self.index is not None and t is not None:
            where = 'WherePropertyElement'
      
        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": where,
                                        "matches": 'MatchesValue',
                                        "predicate": self.property,
                                        "value": value,
                                        "valueType": t,
                                        "index": self.index
                        }
        self.obj.append(type_triple) 

        if returnPredicate:
            return self 
        else: 
            return self.obj

    def matches_sub_string(self, value: any, returnPredicate: Optional[bool]= False):

        self.value_type = 'xsd:string'

        where :str = 'WhereProperty'
        if self.index is not None:
            where = 'WherePropertyElement'
      
        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": where,
                                        "matches": 'MatchesSubString',
                                        "predicate": self.property,
                                        "value": value,
                                        "valueType": self.value_type,
                                        "index": self.index
                        }
        self.obj.append(type_triple)
        return self if returnPredicate else self.obj


    def matches_uri(self, uri: str):
        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": 'WhereProperty',
                                        "matches": 'MatchesUri',
                                        "predicate": self.property,
                                        "value": uri
                        }
        self.obj.append(type_triple)
        return self.obj


    def matches_condition(self, operand: str, value: any, value_type: Optional[str] = None):

        self.value_type = value_type
        have_value_type = (value_type is not None)
        t = value_type if have_value_type else property_value_type(self.obj.type_class_module, self.obj.type, self.property)['woqlclass']
        #greenMsg(f"matches_condition: self.value_type t {t}")
      
        where :str = 'WhereProperty'
        if self.index is not None and t is not None:
            where = 'WherePropertyElement'

        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": where,
                                        "matches": 'MatchesCondition',
                                        "predicate": self.property,
                                        "value": value,
                                        "valueType": t,
                                        "operand": operand,
                                        "index": self.index
                        }
        self.obj.append(type_triple)
        return self.obj

    
    def matches_object(self, range_object: query_object):

    
        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": 'WhereProperty',
                                        "matches": 'MatchesQuery',
                                        "predicate": self.property,
                                        "value": range_object.query()
                        }
        self.obj.append(type_triple)
        return self.obj


    def matches_any_object(self):

        greenMsg(f"matches_any_:object  ")
      
        where :str = 'WhereProperty'
       
        type_triple: TripleType = { 
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": where,
                                        "matches": 'MatchesAny',
                                        "predicate": self.property,
                                        "value": None,
                                        "valueType": None,
                                        "index": self.index
                        }
        self.obj.append(type_triple)
        return self.obj

    
 
class reverse_predicate:
    def __init__(self, use: str, obj: query_object, property: str, index: Optional[int] = None):
        self.obj = obj
        self.property = property
        self.index = index
        self.use = use          #todo: merge with predicate by use of use : Reverse
    
    
    def matches_object(self, domain_object: query_object):
       
        '''
            MatchesQuery on server side needs to know if there is a select_values in domain_object.triples
            since it results in a select.triple instead of a read_document on the MatchesQuery
            question instead of the flat woqlQuery map in objectQuery, we should have a recursive woqlQuery instead
            the following lookahead is required due to the the current flat processing of tripleTypes rather than a recurse through it
        '''
        selects = next( (triple.get('value') for triple in domain_object.triples if triple.get('use') == 'Selecting'), None)

        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": 'WhereReverseProperty',
                                        "matches": 'MatchesQuery',
                                        "predicate": self.property,
                                        "value": domain_object.query(),
                                        "selects": selects
                        }
        self.obj.append(type_triple)
        return self.obj



    def matches_any_object(self):
      
        where :str = 'WhereReverseProperty'
        if self.index is not None:
            where = 'WherePropertyElement'
      
        type_triple: TripleType = {
                                        "type": 'QueryTriple',
                                        "use": self.use,
                                        "where": where,
                                        "matches": 'MatchesAny',
                                        "predicate": self.property,
                                        "value": None,
                                        "valueType": None,
                                        "index": self.index
                        }
        self.obj.append(type_triple)
        return self.obj
