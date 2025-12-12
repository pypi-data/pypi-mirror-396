
'''
        where_uri
        where_type
        
        where_property(predicate)
             matches_condition
             matches_uri
                      matches_value
                      matches_query(rangeObject)  

        where_property_element
                      matches_condition(operator, value, value_type)
                      matches_uri(uri)
                      matches_value(value, value_type)
                      matches_query(rangeObject)


        
                  

        where_reverse_property
                      matches_query(domainObject) 

    type_definition = 'semantic.fera.types.fera_type_constructors'


    subject_object = query_object(type_definition, type1)
    range_object = query_object(type_definition, type2)
    domain_object = query_object(type_definition, type3)



    subject_object.whereProperty(predicate).matchesCondition(operator, value)
                                   .matchesUri(uri)
                                   .matchesValue(value)
                                   .matchesQuery(range_object)

          .wherePropertyElement(predicate, index).matchesXXX
          .whereType(type)
          .whereReverseProperty(domain_object)   

    

    request = query_constructor(options)

    result = await semantic.chain( subject_object.query() , request, frame, flatten, process, out  )

    subject_object.query() returns array of TripleType

             matches_condition.
             matches_uri
                      matches_value
                      matches_query(rangeObject)  

        where_property_element
                      matches_condition
                      matches_uri
                      matches_value
                      matches_query(rangeObject)


        WhereType
                      matches_value

        WhereReversePropery
                      matches_query(domainObject) 
'''

- [X]  subject.where_property(predicate: str).matches_value(timeStamp: "xsd:string") 
- [X]  subject.where_property(predicate: str).matches_value(timeStamp substring: "xsd:string") 

- [X]  subject.where_property(predicate: str).matches_value(value: "xsd:double") 
- [X]  subject.where_property(predicate: str).matches_value(value: "xsd:integer") 

- [X]  subject.where_property(predicate: str).matches_uri(uri: str)

- [X]  subject.where_property(predicate: str).matches_condition.('<', value: "xsd:double")
- [X]  subject.where_property(predicate: str).matches_condition.('>', value: "xsd:double")
- [X]  subject.where_property(predicate: str).matches_condition.('==', value: "xsd:double")

- [x]  subject.where_property_element(predicate: str, index: int).matches_value(value: "xsd:double")

- [x]  subject.where_property_element(predicate: str, index: int).matches_condition('==', value: "xsd:double")
- [x]  subject.where_property_element(predicate: str, index: int).matches_condition('<', value: "xsd:double")
- [x]  subject.where_property_element(predicate: str, index: int).matches_condition('>', value: "xsd:double")

- [x]  subject.where_property(predicate: str).matches_object(range: query_object)

- [x]  subject.where_reverse_property_element(predicate: str).matches_object(range: query_object)
- [x]  subject.where_reverse_property_element(predicate: str).matches_object(range: query_object)




### Chain (Pipe) Functions

| chain function | origin | input pre-condition | output post-condition |
|:--- |:--- |:--- |:--- |
| **query** |  semantic.query_constructor | raw frame object (chain seed or returned by previous function) | query result in JSON-LD format as Promised Either |
| **select** | semantic.select_constructor |input object as Promised Either and function with closure on frame | framed input object as Promised Either|
| **flatten** | imported from semantic | input object as Promised Either| flattend array of values  as Promised Either|
| *user-defined-function* | semantic.function_constructor and user defined function | input in format of preceding function output |  return Promise(lambda resolve, reject: resolve(Right(processed))) |
| **chain_out** | imported from semantic | input object as Promised Either| raw object or array if flattened |
| *type-constructor* | imported from fera | data input from preceding function, or partial function with closure on static variables with returned function taking one arg for use with chain input data |  return  of a function (thunk) that returns an **Either**, i.e. a function of no arguments (potentially one for data streaming in chain) that when invoked, returns either a validated dictionary for the type or an error in a function of one argument |
| **update_map** |  previous function is a *type-constructor* |  updates semantic.typeMap with object freom *type-constructor* |

The chain of async functions allows users flexibility in defining sequential processing of data as it allows a mix of functions for:

 -  frame formulation: functions for simplifying construction of frames 
 -  query response formatting: secondary (or a sequence of) frame to select and format pipeline data derived from db or sample streams
 -  user defined data processing functions to analyze data in the pipeline
 -  semantic data creation and database insertion
 -  functions as policy guards operating on conditions defined on semantic data
 -  function return as Promised Either to allow a mix of async and synchronous pipeline with error handling
 

A common use-case takes the form of:

```
    result = await semantic.chain( object , query, frame, flatten, process, out  )
```

The input is typically an object representing a JSON-LD frame that forms a declarative query against the database when followed by the query function. 

The query function takes the frame object as input which it uses to query the database.

The frame-db-response function is a partial function that has previously been defined with a frame that it will use to process the output of the query.

The flatten function will take its input object and return a value-only array.

The out function resolves the promised Either for the returned result.


### Frame node primitives

the API provides a function **frame(seed, *functions)** takes a seed frame dictionary as input to a chain of functions that operate on the seed.
One common use-case is a seed that is the desired frame and no helper **functions** are requied.
Another common use-case is a seed that is an empty dict '''{}''' and a series of helper **functions** to build up the desired frame.

are query (declarative data framing) and data processing functions that form a data processing pipeline.
The processing pipeline is defined by the function sequence: **func-1, func-2, ...func-i**.

| frame primitive functions | input pre-condition | output post-condition |
|:--- |:--- |:--- |
| **findByType(type)** |  frame and type name | **'@type': type** added to frame|
| **findByName(name)** |  frame and name | **'name': name** added to frame|
| **findByPair(key, value)** |  frame and key value | **key: value** added to frame |
| **findByCondition(key, operator, value)** |  frame and start timestamp | **key: {operator: value}** added to frame |


### Frame graph primitives

To frame the graph in either the range or domain, recurse and walk the graph using the following:

| functions for recursive framing in the range or domain of a node | input pre-condition | output post-condition |
|:--- |:--- |:--- |
| **frameRange(key, frame)** |  frame providing parent scope and key for range scope | **key: { }** added range frame on key |
| **frameDomain(key, frame)** |  frame providing parent scope and key for domain scope  | **"@reverse":{key: [{}]}** added domain frame on key |


example:

```
joint_state_frame = frame({}, findByType('JointState'), findByName('shoulder_pan_joint', findByPair('first', 'now')))

print(json.dumps(joint_state_frame(), indent=6))

    {
    "@type": "JointState",
    "name": "shoulder_pan_joint",
    "first": "now"
    }
```

to pull in the UsdPrim that that joint state is an an attribute of, you can either choose to have the graph's named node be **JointState** or the named node be **UsdPrim** with **typeName** **PhysicsRevoluteJoint**. 

```
joint_state_range = frame(joint_state_frame, frameRange('parentObject'), frame({}, findByType('UsdPrim'), findByPair('segmentName', 'shoulder_pan_joint')))

print(json.dumps(joint_state_range, indent=6))

    {
    "@type": "JointState",
    "name": "shoulder_pan_joint",
    "first": "now",
    "parentObject": 
        { 
            "@type": "UsdPrim",
            "segmentName": "shoulder_pan_joint"
        }
    }
```

```
joint_state_domain = frame({}, findByType('UsdPrim'), findByPair('segmentName', 'shoulder_pan_joint'), frameDomain(joint_state_frame))

print(json.dumps(joint_state_domain, indent=6))

    {
    "@type": "UsdPrim",
    "segmentName": "shoulder_pan_joint",
    "@reverse" : {
        "parentObject": [
        { 
            "@type": "JointState",
            "name": "shoulder_pan_joint",
            "first": "now"
        }
        ]
    }
    }
```

The playground should be used to develop frames as it can be used incrementally to explore what is in the database as for example with the frame joint_state_domain() and verify that it matches the equivalent operation via semantic.chain:

```
print(json.sdumps( await semantic.chain( joint_state_domain(), query, out )))

{
  "@context": {
    "@base": "terminusdb:///data/",
    "@vocab": "terminusdb:///schema#"
  },
  "@id": "UsdPrim/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef",
  "@type": "UsdPrim",
  "active": true,
  "apiSchemas": [
    "PhysicsDriveAPI:angular",
    "PhysicsJointStateAPI:angular",
    "PhysxJointAPI"
  ],
  "definedIn": "usd",
  "name": "UR10+ur10+base_link+shoulder_pan_joint",
  "parentObject": "UsdPrim/UR10%2Bur10%2Bbase_link+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef",
  "path": "/ur10/base_link/shoulder_pan_joint",
  "relationships": [
    "UsdRelationship/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint%2Bphysics%3Abody0",
    "UsdRelationship/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint%2Bphysics%3Abody1"
  ],
  "segmentName": "shoulder_pan_joint",
  "specializesName": "shoulder_pan_joint",
  "specifier": "SpecifierDef",
  "typeName": "PhysicsRevoluteJoint",
  "@graph": [
    {
      "@id": "JointState/shoulder_pan_joint+now",
      "@type": "JointState",
      "count": 1,
      "first": "now",
      "hasJointEffort": 0.11,
      "hasJointPosition": 0.22,
      "hasJointVelocity": 0.33,
      "last": "now",
      "name": "shoulder_pan_joint",
      "parentObject": "UsdPrim/UR10%2Bur10%2Bbase_link%2Bshoulder_pan_joint+terminusdb%3A%2F%2F%2Fschema%23UsdSpecifier%2FSpecifierDef"
    }
  ]
}
```




### Use-case specific framing functions

Use-case specific functions are defined in user code in terms of the previous function primitives.

TODO: provide function set for the following questions. Note, the answers given in the following are early concepts only.

<!-- 
Give me all images after the insertion of all unsuccessful insertions for object A

note: image.insertion requires that camera and image instances are modeled with insertion.

Question: is 'A' a type or an instance of a type? i.e. a 'CartridgeHolder' or a specific CartridgeHolder instance named A?

 ``` findBy(object('CartidgeHolder, 'A')).findBy(insertion('success',0).uriSelectBy(insertion.image) ```

 Question: how are objects typed? as ```WorkItem```s of type  ```PenBody, PenCap, BodyLiner, CartridgeHolder, PistonRod```? 

 Give me the force profile for all insertions for all objects
 ``` findBy(insertion.all).uri(force-profile) ```

 Implies task:  select functions ```uriSelectBy, literalSelectBy```


Give me the force profile for all insertions for all objects.

``` findBy(insertion.all).uriSelectBy(insertion.force-profile) ```
	
Question: how is force profile defined? as the forces on the tool end effector during the insertion process?

Give me the force profile for all insertions for all objects at the end effector.
``` findBy(insertion.all).uriSelectBy(insertion.force-profile) ```

Give me all images of camera B and the force profile at the end effector after the insertion of all unsuccessful insertions for object A.
``` findBy(workItem.A).findBy(insertion.failure).uriSelectBy(cameraB.images, insertion.force-profile) ```

Show me all instances of the insertion where the force at the end effector was larger than 5 newtons.
``` findBy(insertion.all).findCondition(endEffector.force, '>', 5).literalSelectBy(insertion) ```

What the names of the different phases for task A.
    NB!: need to discuss modeling of this! Currently:

``` 
PenAssemblyTask:
    BinPickTask
    GraspTask
    GraspValidationTask
    PoseEstimationTask
    ProcessingTask
    InsertionTask
    InsertionInspectionTask
```
``` findBy(task.).literalSelect```


What tasks have been performed with object A.
	
Give me all the point clouds and objects poses where the objects expected grasp pose matches the in-hand pose for object A.
	

Give me all the point clouds and objects poses where the objects expected grasp pose is within a translation of 1 cm with the in-hand pose for object A.

Give me the complete information you have available for one instance of a false grasp for object A.
	

Give me all joint information at a frequency of one hour for robot A over the last five years.

Give me the timestamps each failed grasping.

How many times today were no pose estimations obtained on object A. 
	

User: Give me all the instances were the grasping resulted in imprecise poses.
System: Define imprecise poses.
User: Were the in-hand pose differs with the expected grasp pose with more than 5mm. 
	Are you asking for the ability to define pose tolerances for use in a query, and if so, 




``` 
   jointstate_1 = semantic.by_type('JointState')
   name_1 = semantic.by_name('elbow-joint')
   status_1 = semantic.by_predicate_value('status', 'failure')
   first_1 = semantic.by_predicate_condition('first', '>', t1)
   last_1 = semantic.by_predicate_condition('last', '<', t1)

   semantic.query(jointstate_1, name_1, status_1, first_1, last_1).select('JointState','hasJointForce')

   semantic.query_joint_force(name_1, status_1, first_1, last_1)
   
``` 
-->
