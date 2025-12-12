
import os
import sys
import time
import datetime
import base64
import copy
import asyncio
import json
from itertools import chain  

from semantic.api.semantic_api import semantic
from semantic.common.utils import msg, redMsg, greenMsg, chain_out
from semantic.api.queries import query_object

class sample_set:
    def __init__(self, api: semantic, situation: str, *types: str):
      self.api = api
      self.module = module
      self.types = tuple(types)
      self.situation
      '''


      '''
      
    
    async def match_time_stamp(self, value, limit, order):
      msg(f'no of types specified {len(self.types)}')
      msg(f'types[0] {self.types}')
    
     
      cluster = [ await self.api.chain(
                              query_object(self.module, type).where_property('timeStamp').matches_sub_string(value).where_type(type=type).query(),
                              self.api.query_constructor(limit=limit, order=order), 
                              chain_out
                              ) for type in iter(self.types) ]

      #greenMsg('cluster '+json.dumps(cluster, indent=6))

      '''
            query for meta-data (DUL State.hasSetting to DUL Situation)
      '''
     
      meta_data = cluster[0]['@graph'][0][self.situation]
      

      result = await self.api.chain(
                              query_object().where_uri(meta_data).query(),
                              self.api.query_constructor(), 
                              chain_out
                              )
    
      '''
        poor flattening capabilities in python
      '''
     
      result['@graph'].extend(list(chain(*[obj['@graph']  for obj in cluster])))

      #greenMsg('result '+json.dumps(result, indent=6))
      return result


    async def has_setting(self, obj: dict):
      msg(f'no of types specified {len(self.types)}')
      msg(f'types[0] {self.types}')
    
     
      cluster = [await self.api.chain(
                              query_object(self.module, type).where_property('timeStamp').matches_sub_string(value).where_type(type=type).query(),
                              self.api.query_constructor(limit=limit, order=order), 
                              chain_out
                              ) for type in iter(self.types)]

      result = { 
                  '@context' : cluster[0]['@context'],
                  '@graph': []
                }
    
      '''
        poor flattening capabilities in python
      '''
     
      result['@graph'].extend(list(chain(*[obj['@graph']  for obj in cluster])))

      #greenMsg('result '+json.dumps(result, indent=6))
      return result