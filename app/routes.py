from flask import Blueprint, jsonify, Response, stream_with_context,request  # Added request import
from pydantic import BaseModel, ValidationError, Field  # Added Field for better validation
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from asgiref.sync import sync_to_async  
import json

from app.Utils.truthfinder import run_scraper as run_truthfinder
from app.Utils.infotracer import run_scraper as run_infotracer
from app.Utils.skype import run_scraper as run_skype_scraper
from app.Utils.boardreader import run_scraper as run_boardreader_scraper
from app.Utils.xss import run_scraper as run_xss_scraper
from app.Utils.search_email import run_scraper as run_email_scraper
from app.Utils.search_phone import run_scraper as run_phone_scraper

def run_async_scraper(scraper_func, user_data):
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(scraper_func(user_data))
        return result
    finally:
        loop.close()

def run_scraper(user_data):
    # Create a thread pool
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both scrapers to run in separate threads
        future_info = executor.submit(run_async_scraper, run_infotracer, user_data)
        # future_truth = executor.submit(run_async_scraper, run_truthfinder, user_data)
        
        # Handle results and exceptions
        scrapers = []
        if user_data.input_type == "License":
            scrapers = [('Info Scraper', future_info)]
        else:
            # scrapers = [('Info Scraper', future_info)]
            scrapers = [('Info Scraper', future_info), ('Truth Scraper', future_truth)]

        results = []
        for name, future in scrapers:
            try:
                result = future.result()
                results.append(result)
                print(f"{name} completed successfully")
            except Exception as e:
                print(f"{name} failed with error: {e}")
        
        # print(results)

        return results



# Create a Blueprint  
main = Blueprint('main', __name__)  

class Input(BaseModel):
    input_type: str = ""
    first_name: str = ""
    second_name: str = ""
    middle_name: str = ""  # Fixed type hints
    city: str = ""
    state: str = ""
    age: int = 0
    phone: str = ""
    email: str = ""
    street_address: str = ""
    zip_code: str = ""
    license: str = ""

class SkypeInput(BaseModel):
    input_type: str = ""
    input_value: str = ""

class SingleKeywordInput(BaseModel):
    keyword: str = ""

# Define the first route  
@main.route('/search', methods=['POST'])  
async def search_router():
    result = ""
    try:
        user_data = Input(**request.get_json())  # Fixed class name
        print(user_data)
    except Exception as e:
        print(e)
        return "error"
    try:
        result = run_scraper(user_data)
    except Exception as e:
        print(e)

    response_data = {
        "status": "success",
        "message": "Data validated successfully",
        "data": result  # Convert Pydantic model to dict
    }
    
    return jsonify(response_data), 200

@main.route('/skype', methods=['POST'])
async def skype_router():
    result = ""
    try:
        user_data = SkypeInput(**request.get_json())  # Fixed class name
        print(user_data)
    except Exception as e:
        print(e)
        return "error"

    try:
        result = await run_skype_scraper(user_data.input_value, user_data.input_type)
    except Exception as e:
        print(e)

    response_data = {
        "status": "success",
        "message": "Data validated successfully",
        "data": result  # Convert Pydantic model to dict
    }
    
    return jsonify(response_data), 200

@main.route('/boardreader', methods=['POST'])
def iboardreader_router():
    result = ""
    try:
        user_data = SingleKeywordInput(**request.get_json())  # Fixed class name
        print(user_data)
        result = run_boardreader_scraper(user_data.keyword)
        response_data = {
            "status": "success",
            "message": "Data validated successfully",
            "data": result  # Convert Pydantic model to dict
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print(e)
        return "error"

@main.route('/xss', methods=['POST'])
async def xss_router():
    result = ""
    try:
        user_data = SingleKeywordInput(**request.get_json())  # Fixed class name
        print(user_data)
        result = await run_xss_scraper(user_data.keyword)
        response_data = {
            "status": "success",
            "message": "Data validated successfully",
            "data": result  # Convert Pydantic model to dict
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print(e)
        return "error"
    
def async_generator_to_sync(generator):  
    """Helper function to convert async generator to sync generator."""  
    loop = asyncio.new_event_loop()  
    asyncio.set_event_loop(loop)  
    
    try:  
        while True:  
            try:  
                result = loop.run_until_complete(generator.__anext__())  
                yield jsonify({  
                    "status": "success",  
                    "message": "Scraper result",  
                    "data": result  
                }).data.decode() + '\n'  
            except StopAsyncIteration:  
                break  
    finally:  
        loop.close()  
 

@main.route('/search-email', methods=['POST'])
def email_router():  
    try:  
        user_data = SingleKeywordInput(**request.get_json())  
        email = user_data.keyword  
        # Create an async generator
        async_gen = run_email_scraper(email)  # Changed to use the correct scraper function
        
        # Use stream_with_context to handle the generator
        return Response(
            stream_with_context(async_generator_to_sync(async_gen)),
            content_type='application/json'
        )
        
    except Exception as e:  
        print(e)  
        response_data = {  
            "status": "error",  
            "message": str(e),  
        }  
        return jsonify(response_data), 500
    
@main.route('/search-phone', methods=['POST'])
async def phone_router():
    result = ""
    try:
        user_data = SingleKeywordInput(**request.get_json())  # Fixed class name
        print(user_data)
        result = await run_phone_scraper(user_data.keyword)
        response_data = {
            "status": "success",
            "message": "Data validated successfully",
            "data": result  # Convert Pydantic model to dict
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print(e)
        return "error"