from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
import pymysql
import uvicorn


app = FastAPI()

# Connection parameters for the database
db_config = {
    "host": "localhost",#148.113.1.101
    "user": "root",
    "password": "actowiz",
    "database": "scraped_data",
    "port": 3306
}

file_save_path = r"C:\Users\Admin\PycharmProjects\csv_files\hyundai_csv\path"

app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Serve the index.html file
    index_path = "./static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Index file not found")


@app.get("/get-data")
async def get_data(keyword: str, city: str):
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        # Define SQL query with placeholders for parameters
        query = """
         SELECT * FROM hundai_car_new
        WHERE city  LIKE %s
        """

        query = """
               SELECT * FROM hundai_car_new
               WHERE city  LIKE %s
               """

        # Execute the query with keyword and city parameters, allowing for partial matches
        cursor.execute(query, (f"%{city}%"))
        result = cursor.fetchall()  # Fetch all occurrences
        print("result  :", result)

        # Check if any data is found
        if not result:
            return {"message": "No matching data found."}

        # Convert the result to a Pandas DataFrame
        columns = [desc[0] for desc in cursor.description]  # Get column names from the cursor
        df = pd.DataFrame(result, columns=columns)
        record_count = df.shape[0]

        # Define the path where you want to save the file

        if not os.path.exists(file_save_path):
            os.makedirs(file_save_path)

        file_name = "hy_output_2.xlsx"
        file_path = os.path.join(file_save_path, file_name)  # file_save_path + file_name
        df.to_excel(file_path, index=False)

        # Return a message with a download URL

        return {
            "message": "Data saved successfully.",
            "download_url": f"http://127.0.0.1:8000/download-file?file_name={file_name}",
            "record_count": record_count
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



# New endpoint to get city suggestions
@app.get("/suggest-city")
async def suggest_city(partial_city: str):
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
    except Exception as db_connect_error:
        raise HTTPException(status_code=500, detail=f"Database connection error: {db_connect_error}")

    try:
        query = """
        SELECT DISTINCT city
        FROM hundai_car_new
        WHERE city LIKE %s
        LIMIT 100
        """
        cursor.execute(query, (f"%{partial_city}%",))
        suggestions = [row[0] for row in cursor.fetchall()]
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()




if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)



# Run the FastAPI app with Uvicorn in the terminal, NOT by directly calling get_data.
# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)