from typing_extensions import TypedDict
from typing_extensions import TypeAliasType
from pydantic import BaseModel
from pymonad.either import Either
from pymonad.promise import Promise

'''
  Typing issue in defining type classes or TypedDicts for an  ontology under python:

  Python class members cannot have special characters such as @
  which means that pydantic's BaseModel cannot be used for validating json-ld derived objects
  However, this is contradicted by the following example of using a TypedDict to instantiate a class 
  (have not investigated how this is achieved and what are the limitiations, would be a starting point for going further)
  A second issue is encountered with multi inheritenace from both BaseModel and TypedDict.

      Typed = TypedDict('Typed', {"@type": str})

      class NamedType(Typed): 
        name: str

      # would like the following which results in the multi-inheritance issue with basemodel and typedicts
      class JointState(BaseModel, NamedType)

      note that union is possible but what is the point to carry both type defs around?
      class JointState(BaseModel | NamedType)
        ... 
          if not isinstance(object, BaseModel):
               validated = JointState(**object)
        ...

  Assuming the use of BaseModel for runtime checking of semantic data, and the multi inheritence issue
  with BaseModel and TypeDict is not resolved, the implication is that
  all @ keys must be stripped from the data prior to validation

  https://github.com/pydantic/pydantic/discussions/2574
  https://github.com/pydantic/pydantic/discussions/6517
  https://www.speakeasy.com/post/pydantic-vs-dataclasses

  This could be an opensource mypy/pydantic effort to resolve, out of scope here, instead:

  TypedDicts are more syntatically elegant and efficient (note runtime validation cost when performance is an issue)

  However the pratical choice is pydantic (class over TypedDict) for now without @ data members, 
'''

# TerminusRef = TypedDict('TerminusRef', {"@id": str})
TerminusId = TypedDict('TerminusId', {"@id": str})
TerminusRef = TypeAliasType('TerminusRef', str)
#TerminusRef = TypedDict('TerminusRef', str)
#class TerminusRef(BaseModel):
 # ref: str

class Typed(BaseModel):
  type: str          # @type

class NamedType(Typed):
  '''
    union of type with None does not work with BaseObject validation
    method for declaring optional fields is tbd
  '''
  #id: str | None     # @id
  #type: str          # @type
  name: str



class SchemaId(TypedDict):
  schemaName: str
  schemaVersion: str
  instanceName: str
  dbUri: str
  
class PipeArgBase(TypedDict):
   pass

class PipeArg(PipeArgBase, total=False):
  schema: SchemaId  
  doc: Either
  frame: any
  topic: str
  mqttClient: any
  requestId: int | str
  clientId: str
  serviceId: str
  objectFormat: str
  #pipeType: str believe pipeType is  not being used on server side


class SemanticConfigBase(Typed):
   dispatch: str 

class SemanticConfig(PipeArgBase, total=False):
  args: str #| list[str]


class TripleType(TypedDict, total=False):
    '''
      type is type WOQL query type
      triple type is passed as a predicate
    '''
    type: str
    use: str
    where: str              # could be enum for WhereType, WhereProperty, WherePropertyElement, WhereReverseProperty 
    matches: str #| None     # could be enum for MatchesUri, MatchesValue, MatchesCondition, MatchesCondition
    predicate: str
    value: any #| None           # value is an array of TripleType for query matchType (recurse for range or domain objects)
    valueType: str #| None
    operand: str #| None     # could be enum
    index: int #| None
    selects: tuple[str]
  

class TripleVars(TypedDict):
    '''
      WOQL vars for triple and rhs value
    '''
    subject: str     
    predicate: str #| None
    object: str #| None
    rhs: any #| None
  
class QueryOptions(TypedDict):
    '''
      WOQL Options
    '''
    limit: int     
    order: bool
  
class WoqlValue(TypedDict):
    woqlclass: str
    woqltype: str | None