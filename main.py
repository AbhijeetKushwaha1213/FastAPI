import json
from fastapi import FastAPI, HTTPException,Path,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel ,Field,computed_field
from typing import Annotated, Literal, Optional


app=FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of Patient',examples=['P001'])]
    name:Annotated[str,Field(...,max_length=50,title='Name of Patient',examples=['Abhijeet','Rohit'])]
    city:Annotated[str,Field(...,max_length=50,title='City of Patient',examples=['Mumbai','Delhi'])]
    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the patient')]
    gender:Annotated[Literal['Male','Female','others'],Field(...,title='Gender of Patient')]
    height:Annotated[float,Field(...,gt=0,description='height of the patient')]
    weight:Annotated[float,Field(...,gt=0,description='weight of the patient')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if(self.bmi<18):
            return 'Under Weight'
        elif(self.bmi<25):
            return 'Normal'
        else:
            return 'Obese'
        
class Update_patient(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,gt=0)]
    gender:Annotated[Optional[Literal['Male','Female','Other']],Field(default=None)]
    height:Annotated[Optional[float],Field(default=None,gt=0)]
    weight:Annotated[Optional[float],Field(default=None,gt=0)]

#load the data    
def load_data():
    with open('patient.json','r') as f:
        data=json.load(f)
    return data
#covert dict into json
def save_data(data):
    with open('patient.json','w') as f:
        json.dump(data,f)

#get and view information
@app.get("/")
def index():
    return {"message":"Patient management system"}

@app.get("/about")
def index(): 
    return {"message":"A fully functional API to manage your patient record"}

@app.get("/view")
def view():
    data=load_data()
    return data

@app.get('/patient/{patient_id}')
def view(patient_id:str=Path(...,description='ID of the Patient',examples='P001')):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    #return {"error":"patient_id not exits"}
    raise HTTPException(status_code=404, detail='Patient no found')

@app.get("/sort")
def sort_patient(sort_by:str=Query(..., description='sort on the basis of height ,weight or bmi'),order:str=Query('asc',description='sort in asc or desc order')):
    valid_field=['height','weight','bmi']

    if sort_by not in valid_field:
        raise HTTPException(status_code=400,detail=f'Invalid field selected from {valid_field}')

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='Invalid field selected between asc,desc')

    data=load_data()

    sort_order=True if order=='desc' else False

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient:Patient):
    #load the existing data
    data=load_data()
    #check if the patient already exits
    if(patient.id in data):
        raise HTTPException(status_code=400,detail='Patient already exists')
     #new patient added to database
    data[patient.id]=patient.model_dump(exclude=['id'])
    #save
    save_data(data)

    return JSONResponse(status_code=201,content={'message':'patiend created sucssfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient_update:Update_patient):
    data=load_data()
    #check if the patient already exits
    if(patient_id not in data):
        raise HTTPException(status_code=404,detail='Patient not found')
    
    existing_patient_info=data[patient_id]
    #json to dict
    update_patient_info=patient_update.model_dump(exclude_unset=True)
    for key ,value in update_patient_info.items():  
        existing_patient_info[key]=value
    #exitisting patient_info->pydantic_object->update bmi+verdict->pydantic object->dict->save
    existing_patient_info['id']=patient_id
    patient_pydantic_obj=Patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_obj.model_dump(exclude='id')

    data[patient_id]=existing_patient_info
    #save
    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient updated sucssfully'})

@app.delete('/delete/{Patient_id}')
def delete_patient(patient_id:str):
    data=load_data()
    if(patient_id not in data):
        raise HTTPException(status_code=404,detail='Patient not found')
    
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient deleted sucssfully'})