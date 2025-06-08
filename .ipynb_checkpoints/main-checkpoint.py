from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

# Pydantic models for request/response validation
class ItemBase(BaseModel):
    name: str = Field(..., description="Name of the item", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Description of the item")
    price: float = Field(..., description="Price of the item", gt=0)
    tax: Optional[float] = Field(None, description="Tax applied to the item", ge=0)
    tags: List[str] = Field(default=[], description="List of tags for the item")

class ItemCreate(ItemBase):
    """Model for creating a new item"""
    pass

class ItemUpdate(BaseModel):
    """Model for updating an existing item"""
    name: Optional[str] = Field(None, description="Name of the item", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Description of the item")
    price: Optional[float] = Field(None, description="Price of the item", gt=0)
    tax: Optional[float] = Field(None, description="Tax applied to the item", ge=0)
    tags: Optional[List[str]] = Field(None, description="List of tags for the item")

class Item(ItemBase):
    """Model for a complete item with ID"""
    id: str = Field(..., description="Unique identifier for the item")
    created_at: datetime = Field(..., description="Timestamp when the item was created")
    updated_at: datetime = Field(..., description="Timestamp when the item was last updated")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Sample Item",
                "description": "This is a sample item for demonstration",
                "price": 29.99,
                "tax": 5.99,
                "tags": ["sample", "demo"],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }

# Create FastAPI application
app = FastAPI(
    title="FastAPI Demo",
    description="A sample FastAPI application with CRUD endpoints",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory database for demonstration
items_db: Dict[str, Item] = {}

# Dependency for getting the current time
def get_current_time():
    return datetime.now()

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint to check if the API is running
    
    Returns:
        dict: A welcome message
    """
    return {"message": "Welcome to the FastAPI application!"}

# CRUD operations for items

@app.get("/items", response_model=List[Item], tags=["Items"])
async def read_items():
    """
    Get all items
    
    Returns:
        List[Item]: A list of all items
    """
    return list(items_db.values())

@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def read_item(item_id: str):
    """
    Get a specific item by ID
    
    Args:
        item_id (str): The ID of the item to retrieve
        
    Returns:
        Item: The requested item
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return items_db[item_id]

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: ItemCreate, current_time: datetime = Depends(get_current_time)):
    """
    Create a new item
    
    Args:
        item (ItemCreate): The item data
        current_time (datetime): The current timestamp from dependency
        
    Returns:
        Item: The created item with generated ID and timestamps
    """
    item_id = str(uuid.uuid4())
    item_dict = item.dict()
    
    new_item = Item(
        id=item_id,
        created_at=current_time,
        updated_at=current_time,
        **item_dict
    )
    
    items_db[item_id] = new_item
    return new_item

@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(
    item_id: str, 
    item_update: ItemUpdate, 
    current_time: datetime = Depends(get_current_time)
):
    """
    Update an existing item
    
    Args:
        item_id (str): The ID of the item to update
        item_update (ItemUpdate): The updated item data
        current_time (datetime): The current timestamp from dependency
        
    Returns:
        Item: The updated item
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    
    item_data = items_db[item_id]
    update_data = item_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(item_data, field, value)
    
    # Update the 'updated_at' timestamp
    item_data.updated_at = current_time
    
    items_db[item_id] = item_data
    return item_data

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: str):
    """
    Delete an item
    
    Args:
        item_id (str): The ID of the item to delete
        
    Raises:
        HTTPException: If the item is not found
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    
    del items_db[item_id]
    return None

# Error handling

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "error": str(exc)
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

