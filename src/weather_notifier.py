import requests
import schedule
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# .envファイルから環境変数を読み込む
load_dotenv()

class WeatherNotifier:
    def __init__(self, city="Tokyo", api_key=None):
        """
        天気通知システムの初期化
        
        Parameters:
        city (str): 天気を取得したい都市名（デフォルト: Tokyo）
        api_key (str): OpenWeatherMap APIキー
        """
        self.city = city
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("API keyが必要です")
        
        # APIのベースURL
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self):
        """天気情報を取得する"""
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': 'metric',  # 摂氏温度で取得
            'lang': 'ja'        # 日本語で取得
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # エラーチェック
            weather_data = response.json()
            
            return {
                'weather': weather_data['weather'][0]['description'],
                'temp': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except requests.exceptions.RequestException as e:
            print(f"天気情報の取得に失敗しました: {e}")
            return None
            
    def send_notification(self, weather_info):
        """
        天気情報を通知する
        実際の通知方法（LINE, メール等）に応じてこのメソッドを修正してください
        """
        if weather_info:
            message = (
                f"【天気通知】{weather_info['timestamp']}\n"
                f"場所: {self.city}\n"
                f"天気: {weather_info['weather']}\n"
                f"気温: {weather_info['temp']}°C\n"
                f"湿度: {weather_info['humidity']}%"
            )
            print(message)  # コンソールに出力
            # ここに実際の通知処理を追加
            
    def run_daily_notification(self):
        """毎日の天気通知を実行"""
        weather_info = self.get_weather()
        self.send_notification(weather_info)

def main():
    # 通知システムの初期化
    notifier = WeatherNotifier()
    
    # 毎朝8時に実行するようにスケジュール設定
    schedule.every().day.at("08:00").do(notifier.run_daily_notification)
    
    # 初回実行
    notifier.run_daily_notification()
    
    # スケジュールされたタスクを継続的に実行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにチェック

if __name__ == "__main__":
    main()