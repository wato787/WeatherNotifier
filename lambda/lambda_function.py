# lambda_function.py
import json
import os
import requests
from datetime import datetime

def get_weather(city="Tokyo", api_key=None):
    """天気情報を取得する"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    api_key = api_key or os.environ.get('OPENWEATHER_API_KEY')
    
    if not api_key:
        raise ValueError("API key is required")
    
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ja'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        return {
            'weather': weather_data['weather'][0]['description'],
            'temp': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except requests.exceptions.RequestException as e:
        print(f"Failed to get weather info: {e}")
        raise

def send_line_notification(message, line_token=None):
    """LINEに通知を送信する"""
    line_token = line_token or os.environ.get('LINE_NOTIFY_TOKEN')
    if not line_token:
        raise ValueError("LINE Notify Token is required")
    
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_token}'}
    data = {'message': message}
    
    try:
        response = requests.post(line_notify_api, headers=headers, data=data)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Failed to send LINE notification: {e}")
        raise

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        # 天気情報の取得
        weather_info = get_weather()
        
        # 通知メッセージの作成
        message = (
            f"\n【天気通知】{weather_info['timestamp']}\n"
            f"場所: Tokyo\n"
            f"天気: {weather_info['weather']}\n"
            f"気温: {weather_info['temp']}°C\n"
            f"湿度: {weather_info['humidity']}%"
        )
        
        # LINE通知の送信
        send_line_notification(message)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Weather notification sent successfully',
                'weather_info': weather_info
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }