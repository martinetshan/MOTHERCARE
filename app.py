import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Depends, Query, requests
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
import requests
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from models import add_nutrition_entry, create_users_table, add_user, check_user_credentials, get_nutrition_data

load_dotenv()

API_KEY = os.getenv("API_KEY")
FOOD_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

with open("FoodData_Central_survey_food_json_2022-10-28.json", "r") as f:
    food_data = json.load(f)
    
# Initialize FastAPI app
app = FastAPI()

# Load templates
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Add session management
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")


# Create users table on startup
@app.on_event("startup")
def startup():
    create_users_table()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/landing")
    return RedirectResponse(url="/login")


@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
async def signup(request: Request, firstname: str = Form(...), lastname: str = Form(...), dob: str = Form(...), gender: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        is_authenticated, user_details = add_user(firstname, lastname, dob, gender, email, password)
        request.session["user"] = user_details
    except ValueError as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error_message": str(e)})
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error_message": "User already exists."})
    return RedirectResponse(url="/landing", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/landing")
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    is_authenticated, user_details = check_user_credentials(email, password)
    if is_authenticated:
        # Store user information in the session
        request.session["user"] = user_details
        return RedirectResponse(url="/landing", status_code=303)

    # Return the login form with an error message
    return templates.TemplateResponse("login.html", {"request": request, "error_message": "Invalid credentials"})


@app.get("/landing", response_class=HTMLResponse)
async def landing(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("landing.html", {"request": request, "user": user})


@app.get("/logout", response_class=RedirectResponse)
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/login")


@app.get("/nutrition-tracker", response_class=HTMLResponse)
async def serve_nutrition_tracker(request: Request):
    return templates.TemplateResponse("nutrition_tracker.html", {"request": request})


@app.get("/child-developement", response_class=HTMLResponse)
async def serve_nutrition_tracker(request: Request):
    return templates.TemplateResponse("child_development.html", {"request": request})


@app.get("/search-food", response_class=JSONResponse)
async def search_food(query: str = Query(...)):
    params = {"query": query, "api_key": API_KEY, "pageSize": 20}  # Limit the number of results for simplicity
    response = requests.get(FOOD_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data")

# @app.get("/search-food", response_class=JSONResponse)
# async def search_food(query: str = Query(...)):
#     results = []
#     for food in food_data['SurveyFoods']:
#         if query.lower() in food["description"].lower():
#             results.append(food)
#         if len(results) >= 20:  # Limit to 20 results for simplicity
#             break
#     if results:
#         return JSONResponse({"foods": results})
#     else:
#         raise HTTPException(status_code=404, detail="No food items found")

@app.get("/nutrition-analytics", response_class=HTMLResponse)
async def serve_nutrition_tracker(request: Request):
    return templates.TemplateResponse("nutrition_analytics.html", {"request": request})

@app.post("/add-nutrition", response_class=HTMLResponse)
async def add_nutrition(request: Request, food_name: str = Form(...), calories: float = Form(...), protein: float = Form(...), carbohydrates: float = Form(...), fat: float = Form(...)):
    user = request.session.get("user")
    print(user)
    if not user:
        return RedirectResponse(url="/login")
    add_nutrition_entry(user["id"], food_name, calories, protein, carbohydrates, fat)
    return RedirectResponse(url="/nutrition-tracker", status_code=200)


@app.get("/nutrition-data", response_class=JSONResponse)
async def fetch_nutrition_data(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user["id"]
    query = """
        SELECT food_name, calories, protein, carbohydrates, fat, consumed_at
        FROM nutrition
        WHERE user_id = %s
    """
    data = get_nutrition_data(query, (user_id,))

    result = [{"food_name": row[0], "calories": row[1], "protein": row[2], "carbohydrates": row[3], "fat": row[4], "consumed_at": row[5].strftime("%Y-%m-%d %H:%M:%S")} for row in data]

    return JSONResponse(result)

@app.get("/user-analytics", response_class=HTMLResponse)
async def serve_user_tracker(request: Request):
    return templates.TemplateResponse("user_level_analytics.html", {"request": request})

@app.get("/get-users", response_class=JSONResponse)
async def get_users():
    query = """
        SELECT id, firstname, lastname
        FROM users
    """
    data = get_nutrition_data(query, ())

    result = [{"id": row[0], "firstname": row[1], "lastname": row[2]} for row in data]

    return JSONResponse(result)


@app.get("/user-nutrition-data", response_class=JSONResponse)
async def fetch_user_nutrition_data(user_id: int = Query(...)):
    query = """
        SELECT food_name, calories, protein, carbohydrates, fat, consumed_at
        FROM nutrition
        WHERE user_id = %s
    """
    data = get_nutrition_data(query, (user_id,))

    result = [{"food_name": row[0], "calories": row[1], "protein": row[2], "carbohydrates": row[3], "fat": row[4], "consumed_at": row[5].strftime("%Y-%m-%d %H:%M:%S")} for row in data]

    return JSONResponse(result)

@app.get("/average-intake", response_class=JSONResponse)
async def average_intake():
    query = """
        SELECT AVG(calories) as avg_calories, AVG(protein) as avg_protein, AVG(carbohydrates) as avg_carbohydrates, AVG(fat) as avg_fat
        FROM nutrition
    """
    data = get_nutrition_data(query, ())

    if data:
        result = {
            "avg_calories": data[0][0],
            "avg_protein": data[0][1],
            "avg_carbohydrates": data[0][2],
            "avg_fat": data[0][3]
        }
        return JSONResponse(result)
    else:
        raise HTTPException(status_code=404, detail="No data found")