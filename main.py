# Purpose: Start fastapi server for the app
# Author: ABHISHEK GUPTA <abhishek@quantgrade.com>

from src.get_webhook_data import *
import uvicorn

if __name__ == '__main__':
    # Run fastapi app
    uvicorn.run(app, port=8080)
