from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json

app = FastAPI()

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Define a Pydantic model for our item
class Item(BaseModel):
    name: str
    description: str

# Create
@app.post("/items/{item_id}")
def create_item(item_id: str, item: Item):
    if r.exists(item_id):
        raise HTTPException(status_code=400, detail="Item already exists")
    r.set(item_id, item.json())
    return {"message": "Item created successfully"}

# Read
@app.get("/items/{item_id}")
def read_item(item_id: str):
    item_data = r.get(item_id)
    if item_data is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item.parse_raw(item_data)

# Update
@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    if not r.exists(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    r.set(item_id, item.json())
    return {"message": "Item updated successfully"}

# Delete
@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    if not r.exists(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    r.delete(item_id)
    return {"message": "Item deleted successfully"}

# List all items
@app.get("/items")
def list_items():
    keys = r.keys("*")
    items = []
    for key in keys:
        item_data = r.get(key)
        item = Item.parse_raw(item_data)
        items.append({"id": key.decode(), "item": item})
    return items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
