from .base import app
from utils.filetransfer import *
import services.result
from fastapi import APIRouter
from .schemas import *

result_router = APIRouter(prefix='/result')

@app.get('/results')
async def results():
    return 'api: results'

@app.post('/create_result')
async def create_result(details:ResultInfo):
    response = await services.result.create_result(
        details.name,
        details.creator,
        details.details)
    print(response)
    if response != 'ok':
        return {
            'error': f'{response} already exists'
        }, 400

    
    else:
        return {
            'name': details.name,
            'creator': details.creator,
            'details': details.details,
        }, 200
@app.post('/delete_result')
async def delete_result(details:ID):
    response = await services.result.delete_result(details.id)
    if response[0]['status'] != 'ok':
        return {
            'error' : f'delete failed'
        },400
    else :
        return {
            'id':details.id
        },200
@app.post('/edit_result')
async def edit_result(details:ResultDetails):
    response = await services.result.edit_result(
        details.id,
        details.details
    )
    if response[0]['status'] != 'ok':
        return {
            'error': 'edit failed'
        },400
    else:
        return {
            'id':response[0]['id'],
            'name':response[0]['name'],
            'creator':response[0]['creator'],
            'details':response[0]['details']
            
        }
@app.post('/get_result')
async def get_result(details:ID):
    response = await services.result.get_result(details.id)
    if response[0]["status"] != "ok":
        return {
            'error' : f'not found id {details.id}'
        },400
    else :
        return {
            'id':response[0]['id'],
            'name':response[0]['name'],
            'creator':response[0]['creator'],
            'details':response[0]['details'],
            'questions':response[0]['questions']
        },200
@result_router.get('/')
def result(id):
    return 'requested result with id ' + str(id)
