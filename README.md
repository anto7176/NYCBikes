# NYCBikes

---

## To install dependencies for the backend:

cd backend
poetry config virtualenvs.in-project true
poetry env use python3.13
poetry install

When needed to add one use poetry add <package> instead of pip install <package>

---

##To run backend:

cd backend
./run (Because it runs uvicorn that handles fastapi)

---

## To install dependencies for the frontend:

cd frontend
npm install

---

## To run frontend:

ng serve