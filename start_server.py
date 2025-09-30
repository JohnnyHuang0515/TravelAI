#!/usr/bin/env python3
"""啟動修復的服務器"""

import sys
sys.path.append('.')

if __name__ == "__main__":
    from src.itinerary_planner.main import app
    import uvicorn
    
    print("檢查應用程式路由...")
    print(f"路由數量: {len(app.routes)}")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"- {route.path} {route.methods}")
    
    openapi = app.openapi()
    print(f"OpenAPI 路徑數量: {len(openapi['paths'])}")
    for path in openapi['paths'].keys():
        print(f"- {path}")
    
    print("\\n啟動服務器...")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
