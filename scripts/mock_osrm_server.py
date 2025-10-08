#!/usr/bin/env python3
"""
模擬 OSRM 服務器
用於測試前端 OSRM 整合功能
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app)

# 模擬路由響應數據
def create_mock_route_response(start_lat, start_lon, end_lat, end_lon):
    """創建模擬的路由響應"""
    
    # 簡單的距離計算（直線距離 * 1.3 作為實際距離）
    import math
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371000  # 地球半徑（米）
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    distance = haversine_distance(start_lat, start_lon, end_lat, end_lon) * 1.3
    duration = distance / 30 * 60  # 假設平均速度 30 km/h
    
    return {
        "code": "Ok",
        "routes": [
            {
                "distance": distance,
                "duration": duration,
                "geometry": {
                    "coordinates": [
                        [start_lon, start_lat],
                        [end_lon, end_lat]
                    ],
                    "type": "LineString"
                },
                "legs": [
                    {
                        "distance": distance,
                        "duration": duration,
                        "summary": "",
                        "steps": []
                    }
                ]
            },
            # 替代路線
            {
                "distance": distance * 1.2,
                "duration": duration * 1.1,
                "geometry": {
                    "coordinates": [
                        [start_lon, start_lat],
                        [end_lon, end_lat]
                    ],
                    "type": "LineString"
                },
                "legs": [
                    {
                        "distance": distance * 1.2,
                        "duration": duration * 1.1,
                        "summary": "",
                        "steps": []
                    }
                ]
            }
        ],
        "waypoints": [
            {
                "hint": "mock_hint_start",
                "distance": 0,
                "name": "起點",
                "location": [start_lon, start_lat]
            },
            {
                "hint": "mock_hint_end",
                "distance": 0,
                "name": "終點",
                "location": [end_lon, end_lat]
            }
        ]
    }

@app.route('/health', methods=['GET'])
def health():
    """健康檢查端點"""
    return jsonify({
        "status": "ok",
        "service": "mock-osrm-server",
        "version": "1.0.0",
        "timestamp": time.time()
    })

@app.route('/route/v1/driving/<path:coordinates>', methods=['GET'])
def route(coordinates):
    """路由計算端點"""
    try:
        # 解析座標
        coord_pairs = coordinates.split(';')
        if len(coord_pairs) != 2:
            return jsonify({"error": "Invalid coordinates format"}), 400
        
        start_coords = coord_pairs[0].split(',')
        end_coords = coord_pairs[1].split(',')
        
        start_lon, start_lat = float(start_coords[0]), float(start_coords[1])
        end_lon, end_lat = float(end_coords[0]), float(end_coords[1])
        
        # 獲取請求參數
        alternatives = request.args.get('alternatives', 'false').lower() == 'true'
        steps = request.args.get('steps', 'false').lower() == 'true'
        geometries = request.args.get('geometries', 'polyline')
        overview = request.args.get('overview', 'simplified')
        
        # 創建模擬響應
        response = create_mock_route_response(start_lat, start_lon, end_lat, end_lon)
        
        # 根據參數調整響應
        if not alternatives:
            response["routes"] = response["routes"][:1]
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/isochrone/v1/driving/<path:coordinates>', methods=['GET'])
def isochrone(coordinates):
    """等時線計算端點"""
    try:
        # 解析座標
        coord_pairs = coordinates.split(',')
        if len(coord_pairs) != 2:
            return jsonify({"error": "Invalid coordinates format"}), 400
        
        lon, lat = float(coord_pairs[0]), float(coord_pairs[1])
        
        # 獲取請求參數
        contours = request.args.get('contours', '900,1800,3600').split(',')
        geometries = request.args.get('geometries', 'geojson')
        
        # 創建模擬等時線響應
        response = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for i, contour in enumerate(contours):
            time_seconds = int(contour)
            radius_km = time_seconds / 60 * 0.8  # 假設平均速度 48 km/h
            
            # 創建圓形等時線
            feature = {
                "type": "Feature",
                "properties": {
                    "contour": time_seconds,
                    "metric": "duration",
                    "color": f"hsl({120 + i * 30}, 70%, 50%)"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon - radius_km/111, lat - radius_km/111],
                        [lon + radius_km/111, lat - radius_km/111],
                        [lon + radius_km/111, lat + radius_km/111],
                        [lon - radius_km/111, lat + radius_km/111],
                        [lon - radius_km/111, lat - radius_km/111]
                    ]]
                }
            }
            response["features"].append(feature)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/trip/v1/driving/<path:coordinates>', methods=['GET'])
def trip(coordinates):
    """行程規劃端點"""
    try:
        # 解析座標
        coord_pairs = coordinates.split(';')
        if len(coord_pairs) < 2:
            return jsonify({"error": "At least 2 waypoints required"}), 400
        
        # 創建模擬行程響應
        response = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 15000,  # 15 km
                    "duration": 1800,   # 30 minutes
                    "geometry": {
                        "coordinates": [[float(coord.split(',')[0]), float(coord.split(',')[1])] for coord in coord_pairs],
                        "type": "LineString"
                    },
                    "legs": []
                }
            ],
            "waypoints": []
        }
        
        for i, coord_pair in enumerate(coord_pairs):
            lon, lat = coord_pair.split(',')
            waypoint = {
                "hint": f"mock_hint_{i}",
                "distance": 0,
                "name": f"點 {i+1}",
                "location": [float(lon), float(lat)]
            }
            response["waypoints"].append(waypoint)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 啟動模擬 OSRM 服務器...")
    print(f"🌐 服務地址: http://localhost:{port}")
    print(f"📊 健康檢查: http://localhost:{port}/health")
    print(f"🗺️ 路由 API: http://localhost:{port}/route/v1/driving/{{coordinates}}")
    print(f"⏰ 等時線 API: http://localhost:{port}/isochrone/v1/driving/{{coordinates}}")
    print(f"🚗 行程 API: http://localhost:{port}/trip/v1/driving/{{coordinates}}")
    print("")
    print("💡 使用 Ctrl+C 停止服務")
    
    app.run(host='0.0.0.0', port=port, debug=True)
