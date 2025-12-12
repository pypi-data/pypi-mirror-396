
'''
    TODO: remove these functions from map_utils.py and update client's imports
'''
import os
import sys
import time
import datetime
import base64
import copy
import asyncio
from datetime import datetime


from typing import get_origin
from typing_extensions import Final
from functools import reduce
import json
from pymonad.promise import Promise
from pymonad.either import Left, Right
from pyrsistent import PMap

from urllib.parse import unquote
from semantic.common.common_types import SchemaId, WoqlValue




def topic_for_db_id(db_id: str, suffix: str):
    return db_id+'/'+suffix

def subscription_topics(db_id):
    config_response_topic_suffix: Final ='configResponse'
    service_response_topic_suffix: Final ='serviceResponse'
    return [topic_for_db_id(db_id, config_response_topic_suffix), topic_for_db_id(db_id, service_response_topic_suffix)]
 

def config_request_topic(db_id):
    config_request_topic_suffix: Final ='configRequest'
    return topic_for_db_id(db_id, config_request_topic_suffix)

def service_request_topic(db_id):
    service_request_topic_suffix: Final ='serviceRequest'
    return topic_for_db_id(db_id, service_request_topic_suffix)



def typeName(elem):
    return type(elem).__name__

def err(msg):
    sys.stderr.write(msg + '\n')

def sort_by_instance(item):
    return len(item['@type']) + len(item['name'])

def redMsg(msg): 
    sys.stdout.write("\033[91m {}\033[00m" .format(msg) + '\n')
def greenMsg(msg): 
    sys.stdout.write("\033[92m {}\033[00m" .format(msg) + '\n')

def msg(msg):
    sys.stdout.write(msg + '\n')

def err(msg):
    sys.stdout.write(redMsg(msg) + '\n')


def urlEncode(name):
    noSlashOrColonOrPound = name.replace('/', '%2F').replace(':','%3A').replace('#','%23').replace('+', '%2B')

    return noSlashOrColonOrPound

def plusEncode(name):
    encoded = name.replace('+', '%2B')
    return encoded

def plusSeparatedPath(path):
    # remove first / and replace rest with + for terminus use
    plussedPath = path.replace('/','', 1).replace('/', '+')
    return plussedPath

def urlDecode(name):
    return unquote(name)

def lexical_id_from_sample(uri: str, format: int, delimiter: str):
        '''
        concept:
                        Used by clients to generate a lexical id for use by the db, in generating uris derived from a sample uri
                        This is intended for use on State instances that refers to a Sample instance
                        The state instances need an efficient id derived from the Samples time stamp
                        If this is used for Samples, the the 
        pre-conditions:  
                        uri is of type Sample (nb: given use: there is no sense in a type param for uri here)
                        lexical key of Sample uri is formulated as [ "sampleIndex", "timeStamp"]
            
        '''
        sample = uri.find('Sample') + 7
        decoded = urlDecode(uri[sample:])
        plus = decoded.find('+')
        sample_index = decoded[0:plus]
        time_stamp = decoded[plus+1:]
        #greenMsg(f'lexical_id_from_sample decoded {decoded} sampleIndex {sample_index} timeStamp {time_stamp}')

        return lexical_id(sample_index, time_stamp, format, delimiter)




format_state: str = ''
delimiter_state: str = ''

class id_constructor:
    '''
    concept:
                 lexical id strategy should be constant and shared in both user code and type constructors
    requirement:
                 shared state 
    '''
    def __init__(self, format: str=format_state, delimiter: str=delimiter_state):
        self.format = format
        self.delimiter = delimiter
        format_state = format
        delimiter_state = delimiter

    def lexical_id(self, sample_index: int, time_stamp: str):
        '''
        concept:
                        Used to specify the lexical id that the db will use to generate a uri
                
        pre-conditions:  
                
                        format 0 is sampleIndex + timeStamp (standard most-least significant timeStamp format)
                        format 1 is timeStamp + sampleIndex
                        format 2 is reversed timeStamp (least-most significant timeStamp format) + sampleIndex
                        format 3 is sampleIndex + reversed timeStamp 

                        delimiter None : leave as is
                        delimiter '', '.', ' ', '-' etc are used as delimiters
        post-conditions:
                        no url encoding, consistent string delimiting (or None) according to delimiter
        comment:
                        format 3 or 1 with delimiter '' is presumed optimal for insertion speed
        '''

        #greenMsg(f'lexical_id sampleIndex {sample_index} timeStamp {time_stamp}')

        formatted: str = ''
        sample_index_str = str(sample_index)

        match self.format:
            case 0:
                formatted = decoded
            case 1:
                formatted = time_stamp+'+'+sample_index_str
            case 2: 
                formatted = datetime.strptime(time_stamp, '%Y-%m-%dT%H:%M:%S.%f').strftime('%f%S:%M:%HT%d-%m-%Y')+'+'+sample_index_str
            case 3:
                formatted = sample_index_str+'+'+datetime.strptime(time_stamp, '%Y-%m-%dT%H:%M:%S.%f').strftime('%f%S:%M:%HT%d-%m-%Y')
            case _:
                redMsg('lexical_id_from_sample Error: format out of bounds')
        
        result: str

        if self.delimiter != None:
            result = formatted.replace('+',self.delimiter).replace('.',self.delimiter).replace('T',self.delimiter).replace('-',self.delimiter).replace(':',self.delimiter)
        else:
            result = formatted

        #greenMsg(f'lexical_id formatted {formatted} result {result} ')
        return result

    def defined_format():
        return self.format

    def defined_delimiter():
        return self.delimiter

def to_json_ld_type(obj):
    '''
        return a copy of obj with type replaced with @type
        this is due to the pydantic's use of python classes where members cannot begin with @
    '''
    #greenMsg('to_json_ld_type obj in: '+json.dumps(obj, indent=6))
    if type(obj) is list:
        result = [to_json_ld_type(o) for o in obj ]
    else: 
        result = copy.deepcopy(obj)
        for k,v in result.items():   
            if isinstance(v, dict) and 'type' in v:
                result[k]['@type'] =  result.get(k).pop('type')
            elif type(v) is list or type(v) is tuple:
                rhs: list = list()
                for o in v:
                    if isinstance(o,dict) and not '@id' in o:
                        rhs.append(to_json_ld_type(o))
                    else:
                        rhs.append(o)
                result[k]= rhs
        
        result['@type'] = result.pop('type') if (result.get('type') is not None and result.get('@type') is None) else result.get('@type')
    #greenMsg('to_json_ld_type obj out: '+json.dumps(result, indent=6))
    return result


def idForPath(type, path, lexicalField):
    # path is name in the format a/b/c
    # nb assumes no @id existence
    # preconditions:  path is not url encoded
    # non-invariance: terminus' lexical id generation is subject to change, the following may break
    # nb: sensitive to lexical id generation fields, assumes only name (path) and potentially an UsdSpecifier enum (as the lexicalField)
    # terminus' uses the char '+' to seperate lexical fields and these shal not be encoded

    schemaPrefix = 'terminusdb:///schema#'
    lexicalField = schemaPrefix+'UsdSpecifier/'+lexicalField if lexicalField != None and lexicalField.find('Specifier') > -1 else lexicalField
    id = path
   # ref.replace('/', '%2F')
    id = type+'/'+id
    if lexicalField is not None:
        if isinstance(lexicalField, list):
          id = [ id+'+'+element for element in lexicalField]
        elif not isinstance(lexicalField, str):
          id = id+'+'+str(lexicalField)
        else:
          id = id+'+'+lexicalField
  
    return { "@id": id }


#def uri_for_sample(schema_id, type, sample_index, time_stamp):
 #   return 'terminusdb://'+schema_id+'/data/'+type+'/'+str(sample_index)+'+'+urlEncode(time_stamp)

def emulated_uri(schema_id, type, lexical_id):
    return 'terminusdb://'+schema_id+'/data/'+type+'/'+urlEncode(lexical_id)


def refForPath(type, path, lexicalField):
    # path is name in the format a/b/c
    # nb assumes no @id existence
    # preconditions:  path is not url encoded
    # non-invariance: terminus' lexical id generation is subject to change, the following may break
    # nb: sensitive to lexical id generation fields, assumes only name (path) and potentially an UsdSpecifier enum (as the lexicalField)
    # terminus' uses the char '+' to seperate lexical fields and these shal not be encoded

    schemaPrefix = 'terminusdb:///schema#'
    lexicalField = schemaPrefix+'UsdSpecifier/'+lexicalField if lexicalField != None and lexicalField.find('Specifier') > -1 else lexicalField
    ref = path
   # ref.replace('/', '%2F')
    ref = urlEncode(type+'_'+ref)
    if lexicalField is not None:
        if isinstance(lexicalField, list):
          ref = [ ref+'+'+urlEncode(element) for element in lexicalField]
        elif not isinstance(lexicalField, str):
          ref = ref+'+'+urlEncode(str(lexicalField))
        else:
          ref = ref+'+'+urlEncode(lexicalField)

    ref = ref+'_URI'
    
    # terminus will url encode the ref
    return ref

    #return { "@ref": plusEncode(ref) }

def defineSchemaId( name: str, version: str, instance:str, dbIp: str) -> SchemaId:
   schemaDef: SchemaId =  dict(schemaName= name, schemaVersion= version, instanceName= instance, dbUri= dbIp)
   return schemaDef

def getDbId(schema: SchemaId) -> str:
    #msg('schema '+json.dumps(schema, indent=6))
    return schema.get('schemaName')+'-'+schema.get('schemaVersion')+'-'+schema.get('instanceName') if schema is not None else None

def dbId(schemaName, schemaVersion, instanceName):
    return schemaName+'-'+schemaVersion+'-'+instanceName

#def out_either_func(e_func, err_msg):
#    return e_func.either(lambda e: f'Error: {err_msg}: {e}', lambda x: x())

def out_either(eith, err_msg):
    return eith.either(lambda e: f'Error: {err_msg}: {e}', lambda x: x)

def dethunk(thunk, err_msg):
     return  thunk().either(lambda e: f'Error: {err_msg}: {e}', lambda x: x)

async def reject_promised(args):
     return await Promise(lambda resolve, reject: reject(args))

async def resolve_promised(x):
     return await Promise(lambda resolve, reject: resolve(x))

async def resolve_either(args):
     return  await Promise(lambda resolve, reject: resolve(Right(args)))

async def reject_either(args):
     return  await Promise(lambda resolve, reject: resolve(Left(args)))
     
async def chain_out(args):
     #piped_either = await args
     piped_either = await args
     return piped_either.either(lambda e: f'Error: out_promised_either : {e}', lambda x: x['doc'])

def circular_index(current, size):
    return (current + 1) % size





def instance_count(typeMap: PMap):
   count = 0
   types = typeMap.keys()
   for type in types:
       instanceMap: PMap = typeMap.get(type) 
       if instanceMap is not None:
          count = count + len(instanceMap.keys())
   #greenMsg('instance_count '+str(count))
   return count

def custom_encoder(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, bytes):
        return base64.b64encode(x).decode()
    else:
        raise TypeError


def isObject(doc):
    isObj: bool = False
    try:
        docs = doc if type(doc) is list else [doc]
        for obj in docs:
            if obj is dict:
                for key in obj.keys():
                    if (key != '@capture' and key != '@type' and key != '@id') :
                        o = obj.get(key)
                        if type(o) is list:
                            isObj = isObject(o)
                        else:
                            isObj = type(o) is dict
                        if isObj:
                            greenMsg(f'isObject for {obj.get("@type")}´s {key}: {isObj}')
                            return isObj
        greenMsg(f'isObject {isObj}')
    except Exception as e:
        redMsg(f'isObject: Exception: {e}')
    return isObj



def property_value_type(module_path, type, property_name):
    #greenMsg(f'property_value_type: module_path {module_path} type: {type} property_name: {property_name}')

    result: WoqlValue = { "woqlclass": 'tbd', "woqltype": 'tbd' }

    try:
        type_class = getattr(sys.modules[module_path], type)
        t: str = str(type_class.model_fields[property_name].annotation)
        structure = get_origin(t)
        #redMsg(f'property_value_type t : {t}')

        woqltype =  'Array' if structure is list else 'Class'

        woqlclass =  "xsd:double" if 'float' in t else "xsd:integer" if 'int' in t else "xsd:string"

        result: WoqlValue = { "woqlclass": woqlclass, "woqltype": woqltype }

        #redMsg(f'property_value_type woql_value : {json.dumps(result)}')
    except KeyError as e:  
        redMsg(f"property_value_type: KeyError  {e}")
        msg(f"    make sure you are importing the type module and type: \n    from {e} import {type}\n    in your application code (or environment.py)")

    
    return result



'''
deprecated following

class batchScheduler:
    def __init__(self, max_count):
        
            period units: seconds
            batch size vs batch frequency is not fully known for db
            working assumption is that frequency is the independent parameter
            targeting 1 Hz, optimal range 1/2 to 5Hz
        
        self.max_count = max_count
        self.window_start = time.time()

        
    def batch_is_ready(self, count):
       
        now = time.time()
        elapsed = now - self.window_start
        over_count = count >= self.max_count 
        
        if  over_count:
            greenMsg(f'batch is ready: elapsed: {elapsed} count: {count}  over_count: {over_count}')
            self.window_start = now
            return True
        else:
            #msg(f'batch is not ready: elapsed: {elapsed} count: {count}  over_count: {over_count}')
            return False

'''

def has_nested_list(lst):
    for elem in lst:
        #greenMsg(f'elem {json.dumps(elem)}')
        if isinstance(elem, list):
            return True
        elif isinstance(elem, (tuple, set)):
            return True
            # check nested tuples and sets too
            #if has_nested_list(list(elem)):
            #    return True
    return False


