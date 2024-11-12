# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# import pandas as pd
# import os
# import pymysql
# import uvicorn
#
# app = FastAPI()
#
# # Connection parameters for the database
# db_config = {
#     "host": "148.113.1.101",
#     "user": "root",
#     "password": "actowiz",
#     "database": "indiamart_seller",
#     "port": 3306
# }
#
# # keyword="epoxy"
# # city="tamil"
#
# @app.get("/")
# async def get_data(keyword, city):
#     # Establish a new database connection
#     connection = pymysql.connect(**db_config)
#     try:
#         cursor = connection.cursor()
#
#         # Define the SQL query with placeholders for the parameters
#         query = """
#         SELECT * FROM seller2
#         WHERE product_name LIKE %s AND company_basic_information_registered_address LIKE %s
#         """
#
#         # Execute the query with keyword and city parameters, allowing for partial matches
#         cursor.execute(query, (f"%{keyword}%", f"%{city}%"))
#         result = cursor.fetchall()  # Fetch all occurrences
#
#         # Check if any data is found
#         if not result:
#             return {"message": "No matching data found."}
#
#         # Convert the result to a Pandas DataFrame
#         columns = [desc[0] for desc in cursor.description]  # Get column names from the cursor
#         df = pd.DataFrame(result, columns=columns)
#
#         # Define the path where you want to save the file
#         file_save_path = r"C:\Users\Admin\PycharmProjects\csv_files\to\path"
#         os.makedirs(file_save_path, exist_ok=True)  # Ensure directory exists
#         file_name="output_17.xlsx"
#         file_path = os.path.join(file_save_path, file_name)
#         df.to_excel(file_path, index=False)
#         print({"message": "Data saved successfully.",
#                 "download_url": f"http://127.0.0.1:8000/download-file?file_path={file_name}"})#file_name
#         # Return a message with a download URL
#         return {"message": "Data saved successfully.",
#                 "download_url": f"http://127.0.0.1:8000/download-file?file_path={file_name}"}         #download_url": f"http://127.0.0.1:8000/download-file?file_path={file_path}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
#
#     finally:
#         cursor.close()
#         connection.close()
#
#
#
#
# @app.get("/download-file")
# async def download_file(file_path:str):
#     # Check if the file exists
#     if os.path.exists(file_path):
#         return FileResponse(
#             path=file_path,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             filename=os.path.basename(file_path),
#             headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
#         )
#     else:
#         raise HTTPException(status_code=404, detail="File not found")
#
#
#
#
# # Run the FastAPI app with Uvicorn in the terminal, NOT by directly calling get_data.
# if __name__ == '__main__':
#     uvicorn.run(app,host="0.0.0.0",port=8000,reload=False)#172.28.151.65





from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
import pymysql
import uvicorn

app = FastAPI()

# Connection parameters for the database
db_config = {
    "host": "148.113.1.101",
    "user": "root",
    "password": "actowiz",
    "database": "indiamart_seller",
    "port": 3306
}
file_save_path = r"C:\Users\Admin\PycharmProjects\csv_files\indiamart_seller_file\path"

app.mount("C:/Users/Admin/PycharmProjects/fast_api/indiamart_seller_api/static", StaticFiles(directory="static"), name="static")


@app.get("/",response_class=HTMLResponse)
async def read_root():
    # Serve the index.html file
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Index file not found")

@app.get("/get-data")
async def get_data(keyword: str, city: str):
    # Establish a new database connection
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

    except Exception as db_connect_error:
        raise HTTPException(status_code=500, detail=f"Database connection error: {db_connect_error}")

    try:
        # cursor = connection.cursor()

        # Define the SQL query with placeholders for the parameters
        query = """
        SELECT * FROM seller2
        WHERE product_name LIKE %s AND company_basic_information_registered_address LIKE %s
        """

        # Execute the query with keyword and city parameters, allowing for partial matches
        cursor.execute(query, (f"%{keyword}%", f"%{city}%"))
        result = cursor.fetchall()  # Fetch all occurrences
        print("result  :", result)

        # Check if any data is found
        if not result:
            return {"message": "No matching data found."}

        # Convert the result to a Pandas DataFrame
        columns = [desc[0] for desc in cursor.description]  # Get column names from the cursor
        df = pd.DataFrame(result, columns=columns)

        # Define the path where you want to save the file

        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path)

        file_name = "output_27.xlsx"
        file_path = os.path.join(file_save_path, file_name) #file_save_path + file_name
        df.to_excel(file_path, index=False)

        # file_name = "output_14.xlsx"
        # file_path = os.path.join(file_save_path, file_name)
        # df.to_excel(file_path, index=False)

        # Return a message with a download URL

        return {
            "message": "Data saved successfully.",
            "download_url": f"http://127.0.0.1:8000/download-file?file_name={file_name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

@app.get("/download-file")
async def download_file(file_name: str):
    # Construct the full file path using the filename
    file_path = os.path.join(file_save_path, file_name)

    # Check if the file exists
    if os.path.exists(file_path):       #it gives True  if path exist
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(file_path),
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Run the FastAPI app with Uvicorn in the terminal, NOT by directly calling get_data.
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)









