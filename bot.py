import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from datetime import datetime, timedelta
from colorama import Fore, Style  # Jika Anda ingin menggunakan warna

def load_tokens(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return []

def check_in(token, session):
    url = 'https://api.x.ink/v1/check-in'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
        'origin': 'https://x.ink',
        'referer': 'https://x.ink/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    
    try:
        response = session.post(url, headers=headers, json={}, timeout=10)
        response.raise_for_status()
        result = response.json()
        return response.status_code, result
    except requests.exceptions.RequestException as e:
        return None, str(e)

def process_check_ins(session):
    # Load tokens
    tokens = load_tokens('tokens.txt')
    if not tokens:
        print("No tokens found in tokens.txt")
        return
    
    print(f"Found {len(tokens)} tokens")
    print(f"Starting check-ins at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Process each token
    for i, token in enumerate(tokens, 1):
        print(f"\nProcessing account {i}/{len(tokens)}")
        status_code, result = check_in(token, session)
        
        if status_code:
            print(Fore.GREEN + f"Status Code: {status_code}" + Style.RESET_ALL)  # Output sukses berwarna hijau
            print(f"Response: {result}")
        else:
            print(Fore.RED + f"Failed: {result}" + Style.RESET_ALL)  # Output kesalahan berwarna merah
        
        # Add delay between requests to avoid rate limiting
        if i < len(tokens):
            time.sleep(2)
    
    print("\nAll check-ins completed!")

def main():
    # Banner
    print(Fore.GREEN + "=== Daily Claim XOS by Cuan Segar ===" + Style.RESET_ALL)
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    # Create session
    session = requests.Session()
    session.mount('https://', adapter)
    
    print("Bot started! Will check in every 24 hours.")
    print("Press Ctrl+C to stop the bot.")
    print("-" * 50)
    
    last_run = None
    
    try:
        while True:
            current_time = datetime.now()
            
            # Run if it's the first time or if 24 hours have passed since last run
            if last_run is None or (current_time - last_run) >= timedelta(hours=24):
                process_check_ins(session)
                last_run = current_time
                next_run = current_time + timedelta(hours=24)
                print(f"\nNext check-in scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                # Hitung mundur waktu hingga check-in berikutnya
                remaining_time = next_run - current_time
                print(f"Countdown until next check-in: {remaining_time}")
            
            # Sleep for 5 minutes before checking again
            time.sleep(300)
    
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        print("Goodbye!")

if __name__ == '__main__':
    main()