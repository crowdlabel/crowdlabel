from fastapi import Depends, UploadFile, status
from fastapi.routing import APIRouter
from utils.filetransfer import download_file, upload_file
from .auth import get_current_user
import services.tasks
import services.users
from .jsondocumentedresponse import JSONDocumentedResponse, create_documentation, forbidden_jdr, not_found_jdr
import schemas.tasks
from utils.datetime_str import datetime_now_str
from typing import Optional

router = APIRouter()
task_service = services.tasks.Tasks()


###############################################################################
get_task_success_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Successfully queried tasks.',
    schemas.tasks.TaskSearchResponse
)
get_task_failed_hdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Task query failed.',
    schemas.tasks.ErrorResponse
)
@router.put('/',
    **create_documentation([get_task_success_jdr, get_task_failed_hdr])
)
async def search_tasks(query: schemas.tasks.TaskSearchRequest, current_user=Depends(get_current_user(['respondent']))):
    """
    Task search
    """
    print(query)
    print(query.dict())

    # TODO: complete arguments
    tasks = await task_service.search(current_user)

    if isinstance(tasks, str):
        return get_task_failed_hdr.response(schemas.tasks.ErrorResponse(tasks))

    response = schemas.tasks.TaskSearchResponse(**query.dict())
    response.tasks, response.total = tasks
    # TODO: exclude tasks.questions
    return get_task_success_jdr.response(response)
###############################################################################
upload_success_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Task uploaded and created successfully',
    schemas.tasks.Task
)
upload_failed_jdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Task not created',
    schemas.tasks.ErrorResponse
)
@router.post('/upload',
    **create_documentation([upload_success_jdr, upload_failed_jdr])
)
async def upload_task(in_file: UploadFile, current_user=Depends(get_current_user(['requester']))):
    filename = 'upload_' + current_user.username + '_' + datetime_now_str() + '.zip'
    await upload_file(in_file, filename)
    response = await task_service.process_task_archive(filename)
    if isinstance(response, str):
        return upload_failed_jdr(schemas.tasks.ErrorResponse('Error'))
    return upload_success_jdr.response(response)
###############################################################################




create_task_success_jdr = JSONDocumentedResponse(
    status.HTTP_201_CREATED,
    'Task created successfully',
    schemas.tasks.Task
)
create_task_failed_jdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Task not created',
)
async def create_task(task: schemas.tasks.CreateTaskRequest, cover: Optional[UploadFile]=None,
    current_user=Depends(get_current_user(['requester']))
):

    cover_filename = 'cover_' + current_user.username + datetime_now_str() + '.png'

    result = await task_service.create_task(
        creator=current_user,
        name=task.name,
        description=task.description,
        introduction=task.introduction,
        cover_filename=cover_filename if cover else None,
        responses_required=task.responses_required,
        credits=task.credits
    )

    if cover:
        await upload_file(cover, 'cover_' + current_user.username + datetime_now_str() + '.png')









###############################################################################

@router.get('/{task_id}')
async def get_task(task_id: int, current_user=Depends(get_current_user())):
    task = await task_service.get_task(task_id=task_id)
    if not task:
        return {'description': 'Task not found'}, status.HTTP_404_NOT_FOUND

    return task

###############################################################################
task_delete_success_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Task deleted successfully',
)
@router.delete('/{task_id}',
    **create_documentation([task_delete_success_jdr, forbidden_jdr, not_found_jdr])
)
async def delete_task(task_id: int, current_user=Depends(get_current_user(['requester']))):
    response = await task_service.delete_task(task_id)
    if response == 'forbidden':
        return forbidden_jdr.response()
    if response == 'not_found':
        return not_found_jdr.response()
    return task_delete_success_jdr.response()
###############################################################################



""" @app.post('/create_task')
async def create_task(details:TaskInfo):
    response = await services.task.create_task(
        details.name,
        details.creator,
        details.type,
        details.details,
        details.introduction,
        details.path)
    if response['status'] != 'ok':
        return {
            'error': f'already exists'
        }, 400

    
    else:
        return {
            'name': details.name,
            'creator': details.creator,
            'details': details.details,
            'introduction':details.introduction,
            'type':details.type,
            'path':details.path
        }, 200 """


""" @router.patch('/{task_id}')
async def edit_task(details: TaskDetails):
    response = await ts.edit_task(
        details.id,
        details.details,
        details.introduction

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
            'details':response[0]['details'],
            'introduction':response[0]['introduction']
        } """



""" 
    
    response = await services.task.get_task(details.id)
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
            'questions':response[0]['questions'],
            'results':response[0]['results'],
            'type':response[0]['type'],
            'introduction':response[0]['introduction'],
            'path':response[0]['path']
        },200

    """

###############################################################################
claim_success_jdr = JSONDocumentedResponse(
    status.HTTP_200_OK,
    'Task claimed successfully.',
    schemas.tasks.Task,
)
claim_failed_jdr = JSONDocumentedResponse(
    status.HTTP_400_BAD_REQUEST,
    'Task claim failed.',
    schemas.tasks.ErrorResponse,
)
@router.post('/{task_id}/claim',
    **create_documentation([claim_success_jdr, claim_failed_jdr])
)
async def claim_task(task_id: int, current_user=Depends(get_current_user(['respondent']))):
    task = await task_service.claim_task(current_user.username,task_id)

    return claim_success_jdr.response(task)
###############################################################################

@router.get('/{task_id}/download',)
async def download_task_results(task_id: int, current_user=Depends(get_current_user(['requester']))):
    filename = await task_service.create_task_results_file(task_id)
    return await download_file(filename)
###############################################################################

@router.patch('/{task_id}')
async def edit_task(task_id: int, current_user=Depends(get_current_user)):
    return 'editing task ' + str(task_id)
###############################################################################
