# mock-api-server-py-flask
Python-Flask using Mock-API-Server

# Documentation of Mock API Server
This is the documentation for Mock API Server, which is hosted on Heroku.

> This is implemented using Flask and Python.

## EndPoints

 1. `/jsonGetter` returns a JSON object containing Users' data.
	 

>     {   "members": [
>     {
>       "activity_periods": [
>         {
>           "end_time": "Feb 1 2020 1:54PM", 
>           "start_time": "Feb 1 2020  1:33PM"
>         }, 
>         {
>           "end_time": "Mar 1 2020 2:00PM", 
>           "start_time": "Mar 1 2020  11:11AM"
>         }, 
>         {
>           "end_time": "Mar 16 2020 8:02PM", 
>           "start_time": "Mar 16 2020  5:33PM"
>         }
>       ], 
>       "id": "W012A3CDE", 
>       "real_name": "Egon Spengler", 
>       "tz": "America/Los_Angeles"
>     }, ...
>     ],    
>       "ok": true
>   }
