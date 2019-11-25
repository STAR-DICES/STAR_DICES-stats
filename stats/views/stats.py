import json

from jsonschema import validate, ValidationError
from flask import request, jsonify, abort
from flask import current_app as app
from flakon import SwaggerBlueprint


stats = SwaggerBlueprint('stats', 'stats', swagger_spec='stats-specs.yaml')

"""
This endpoint returns the stats for the specified user
"""
@stats.operation('get_stats')
def _stats(user_id):
    # Maybe not needed.
    if not general_validator('get_stats', user_id):
        abort(400)

    r = app.request.get_stories(user_id)
    if r.status_code != 200:
        abort(500)

    stories = json.loads(r.json())
    return jsonify({'score': compute_score(stories['stories'])})

def general_validator(op_id, request):
    schema = stats.spec['paths']
    for endpoint in schema.keys():
        for method in schema[endpoint].keys():
            if schema[endpoint][method]['operationId'] != op_id:
                continue

            op_schema = schema[endpoint][method]['parameters'][0]
            if 'schema' not in op_schema:
                return True

            definition= op_schema['schema']['$ref'].split("/")[2]
            schema= stats.spec['definitions'][definition]
            try:
                validate(request.get_json(), schema=schema)
            except ValidationError as error:
                return False
            return True

"""
This function returns the score of the user taking the sum of all likes received over the number of dislikes,
divided by the number of published stories.
"""
def compute_score(stories):
    tot_stories = 0
    tot_likes = 0
    tot_dislikes = 0
    for story in stories:
        tot_stories += 1
        tot_likes += story.likes
        tot_dislikes += story.dislikes
    if tot_stories == 0:
        return 0
    if tot_likes == 0:
        tot_likes = 1
    if tot_dislikes == 0:
        tot_dislikes = 1
    return round((tot_likes / tot_dislikes) / tot_stories, 2)
