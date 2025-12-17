import re
import argparse
import requests
import time
import sys
import json
import os
import getpass
from pathlib import Path
from typing import Optional, List, Dict

class RunnerCli:
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None, cookie_file: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session_cookie = None
        
        # クッキーファイルのパスを決定
        if cookie_file:
            self.cookie_file = Path(cookie_file)
        else:
            self.cookie_file = Path.cwd() / 'cookie.json'
        
        # 既存のクッキーを読み込む
        self.load_cookie()

    def load_cookie(self) -> bool:
        """保存されたクッキーを読み込む"""
        if not self.cookie_file.exists():
            return False
        
        try:
            with open(self.cookie_file, 'r') as f:
                cookie_data = json.load(f)
                base_url = cookie_data.get('base_url')
                session_cookie = cookie_data.get('session_cookie')
                
                # 同じベースURLのクッキーのみ使用
                if base_url == self.base_url and session_cookie:
                    self.session_cookie = session_cookie
                    self.session.cookies.set('m21_session', session_cookie)
                    return True
        except Exception as e:
            # クッキーファイルの読み込みエラーは無視
            pass
        
        return False
    
    def save_cookie(self) -> bool:
        """クッキーをファイルに保存"""
        if not self.session_cookie:
            return False
        
        try:
            cookie_data = {
                'base_url': self.base_url,
                'session_cookie': self.session_cookie
            }
            
            # ディレクトリが存在しない場合は作成
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cookie_file, 'w') as f:
                json.dump(cookie_data, f)
            
            return True
        except Exception as e:
            print(f"Warning: Failed to save cookie: {e}")
            return False
    
    def login(self, force: bool = False) -> bool:
        """トークンでログインしてセッションを取得"""
        # 既に有効なクッキーがある場合はスキップ（force=Trueの場合は再ログイン）
        if not force and self.session_cookie:
            # セッションの有効性を確認
            try:
                response = self.session.get(f"{self.base_url}/auth/session")
                if response.status_code == 200:
                    print("✓ Using existing session")
                    return True
            except:
                # セッション確認に失敗した場合は再ログイン
                pass
        
        if not self.token:
            print("Error: Token is required for authentication")
            return False
        
        try:
            # /auth/login エンドポイントでログイン
            response = self.session.get(
                f"{self.base_url}/auth/login",
                params={"token": self.token},
                allow_redirects=False
            )
            
            if response.status_code == 302:
                # リダイレクトレスポンスからクッキーを取得
                cookies = response.cookies
                if 'm21_session' in cookies:
                    self.session_cookie = cookies['m21_session']
                    # セッションにクッキーを設定
                    self.session.cookies.set('m21_session', self.session_cookie)
                    # クッキーを保存
                    self.save_cookie()
                    print("✓ Authentication successful")
                    return True
                else:
                    print("Error: Session cookie not found in response")
                    return False
            elif response.status_code == 403:
                print("Error: Another active session already exists")
                return False
            elif response.status_code == 401:
                print("Error: Invalid token")
                return False
            else:
                print(f"Error: Login failed with status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def create_file(self, file_path: str, content: str, sudo: bool = False, password: Optional[str] = None) -> bool:
        """ファイルを作成"""
        try:
            payload = {
                "path": file_path,
                "content": content,
            }
            if sudo:
                payload["sudo"] = True
                if password:
                    payload["password"] = password
            
            response = self.session.post(
                f"{self.base_url}/api/file",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ File created: {result.get('path')}")
                return True
            elif response.status_code == 401:
                print("Error: Authentication required. Please login first.")
                return False
            else:
                print(f"Error: Failed to create file: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def run(self, code: str, language: str = "bash", task_id: Optional[str] = None, 
            sudo: bool = False, password: Optional[str] = None) -> Optional[str]:
        """コードを実行開始し、task_idを返す"""
        try:
            payload = {
                "code": code,
                "language": language,
            }
            if task_id:
                payload["task_id"] = task_id
            if sudo:
                payload["sudo"] = True
                if password:
                    payload["password"] = password
            
            response = self.session.post(
                f"{self.base_url}/api/execute",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("task_id")
            elif response.status_code == 401:
                print("Error: Authentication required. Please login first.")
                return None
            else:
                print(f"Error: Failed to start execution: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return None

    def get_status(self, task_id: str) -> Optional[Dict]:
        """実行状態を取得"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/execute/{task_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Error: Task {task_id} not found")
                return None
            elif response.status_code == 401:
                print("Error: Authentication required. Please login first.")
                return None
            else:
                print(f"Error: Failed to get status: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return None

    def wait_for_completion(self, task_id: str, poll_interval: float = 0.5, stream: bool = True) -> Optional[Dict]:
        """タスクの完了を待つ（ストリーミング対応）"""
        if stream:
            return self.wait_for_completion_stream(task_id)
        
        # フォールバック: ポーリング方式
        while True:
            status = self.get_status(task_id)
            if not status:
                return None
            
            current_status = status.get("status")
            
            if current_status == "completed":
                return status
            elif current_status == "failed":
                return status
            elif current_status == "cancelled":
                return status
            elif current_status in ["pending", "running"]:
                time.sleep(poll_interval)
            else:
                print(f"Unknown status: {current_status}")
                return status

    def wait_for_completion_stream(self, task_id: str) -> Optional[Dict]:
        """ストリーミングでタスクの完了を待つ"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/execute/stream/{task_id}",
                stream=True,
                headers={'Accept': 'text/event-stream'}
            )
            
            if response.status_code == 404:
                print(f"Error: Task {task_id} not found")
                return None
            elif response.status_code == 401:
                print("Error: Authentication required. Please login first.")
                return None
            elif response.status_code != 200:
                print(f"Error: Failed to stream execution: {response.status_code}")
                return None
            
            final_status = None
            
            # SSEストリームを処理
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])  # 'data: 'を除去
                        event_type = data.get('type')
                        
                        if event_type == 'output':
                            # 標準出力をリアルタイムで表示
                            output_data = data.get('data', '')
                            if output_data:
                                print(output_data, end='', flush=True)
                        elif event_type == 'error':
                            # エラー出力をリアルタイムで表示
                            error_data = data.get('data', '')
                            if error_data:
                                print(error_data, end='', flush=True, file=sys.stderr)
                        elif event_type == 'status':
                            # 最終状態を取得
                            final_status = {
                                'task_id': task_id,
                                'status': data.get('status'),
                                'output': data.get('output', ''),
                                'error': data.get('error', '')
                            }
                            break
                    except json.JSONDecodeError:
                        continue
            
            return final_status
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return None

    def stop(self, task_id: str) -> bool:
        """実行を停止"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/execute/stop",
                json={"task_id": task_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Execution stopped: {result.get('message')}")
                return True
            elif response.status_code == 404:
                print(f"Error: Task {task_id} not found")
                return False
            elif response.status_code == 401:
                print("Error: Authentication required. Please login first.")
                return False
            else:
                print(f"Error: Failed to stop execution: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def cleanup(self, task_id: str) -> bool:
        """タスクをクリーンアップ"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/execute/{task_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Task cleaned up: {result.get('message')}")
                return True
            elif response.status_code == 404:
                print(f"Error: Task {task_id} not found")
                return False
            elif response.status_code == 401:
                print("Error: Authentication required. Please login first.")
                return False
            else:
                print(f"Error: Failed to cleanup task: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def run_all(self, code_blocks: List[Dict], default_sudo_password: Optional[str] = None) -> List[Optional[str]]:
        """複数のコードブロックを順次実行"""
        task_ids = []
        
        for i, block in enumerate(code_blocks, 1):
            language = block.get('language', 'bash')
            code = '\n'.join(block.get('code', []))
            options = block.get('language_options', {})
            
            if not code.strip():
                continue
                        
            # オプションからsudoとpasswordを取得
            sudo = options.get('sudo', False)
            if isinstance(sudo, str):
                sudo = sudo.lower() in ('yes', 'true', '1')
            
            # passwordの優先順位: オプションで指定 > デフォルトパスワード
            password = options.get('password') or default_sudo_password
            
            # file=オプションがある場合は、ファイルを作成
            file_path = options.get('file')
            if file_path:
                print(f"\nCreating file: {file_path}")
                print("=" * 60)
                if not self.create_file(file_path, code, sudo=sudo, password=password):
                    print(f"✗ Failed to create file: {file_path}")
                    task_ids.append(None)
                print("=" * 60)
                continue

            print(f"\n[{i}/{len(code_blocks)}] Running {options.get('run', 'unknown task')}...")
            print("=" * 60)

            task_id = self.run(code, language, sudo=sudo, password=password)
            if not task_id:
                print(f"✗ Failed to start execution for block {i}")
                task_ids.append(None)
                continue
            
            task_ids.append(task_id)
            
            result = self.wait_for_completion(task_id)
            if result:
                status = result.get('status')
                if status == 'completed':
                    output = result.get('output', '')
                    if output:
                        print(output[:-1])  # 末尾の改行を削除
                elif status == 'failed':
                    error = result.get('error', '')
                    output = result.get('output', '')
                    print(f"✗ Task failed: {task_id}")
                    if error:
                        print(f"Error: {error}")
                    if output:
                        print(output[:-1])  # 末尾の改行を削除
                elif status == 'cancelled':
                    print(f"⚠ Task cancelled: {task_id}")
            else:
                print(f"✗ Failed to get result for task {task_id}")
            
            print("=" * 60)
        
        return task_ids

class ParseMardown:
    def __init__(self, input_file):
        self.input_file = input_file

    def get_code_blocks(self):
        code_blocks = []
        current_block = None
        current_language = None
        current_options = {}

        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('```'):
                        # コードブロックの開始または終了
                        rest = stripped[3:].strip()  # ``` を除去
                        
                        if current_block is not None:
                            # コードブロックの終了
                            if current_block:  # 空でない場合のみ追加
                                code_blocks.append({
                                    'language': current_language or 'bash',
                                    'language_options': current_options,
                                    'code': current_block
                                })
                            current_block = None
                            current_language = None
                            current_options = {}
                        else:
                            # コードブロックの開始
                            if rest:
                                # 言語とオプションを解析
                                # Example: bash{run="create a user",file=/tmp/new-file.sh,sudo=yes}
                                lang_match = re.match(r'^([a-zA-Z0-9_+-]+)(\{.*\})?$', rest)
                                if lang_match:
                                    current_language = lang_match.group(1)
                                    opts_str = lang_match.group(2)
                                    if opts_str:
                                        # Remove braces
                                        opts_str = opts_str[1:-1]
                                        for opt in opts_str.split(','):
                                            opt = opt.strip()
                                            if '=' in opt:
                                                k, v = opt.split('=', 1)
                                                v = v.strip()
                                                if v.startswith('"') and v.endswith('"'):
                                                    v = v[1:-1]
                                                elif v.startswith("'") and v.endswith("'"):
                                                    v = v[1:-1]
                                                current_options[k.strip()] = v
                                            else:
                                                current_options[opt] = True
                                else:
                                    current_language = rest
                            current_block = []
                    else:
                        # コードブロック内の行
                        if current_block is not None:
                            current_block.append(line.rstrip('\n'))
                
                # ファイル終端で開いたままのコードブロックを処理
                if current_block is not None and current_block:
                    code_blocks.append({
                        'language': current_language or 'bash',
                        'language_options': current_options,
                        'code': current_block
                    })

        except FileNotFoundError:
            print(f"File not found: {self.input_file}")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []

        return code_blocks



def main():
    parser = argparse.ArgumentParser(description='Parse and run Markdown file')
    parser.add_argument('input_file', type=str, help='The input Markdown file')
    parser.add_argument('--base-url', type=str, default='http://localhost:8000',
                        help='Base URL of the backend server (default: http://localhost:8000)')
    parser.add_argument('--token', type=str, default=None,
                        help='Access token for authentication (required if no valid session exists)')
    parser.add_argument('-s', '--sudo', action='store_true',
                        help='Prompt for sudo password for code blocks that require sudo')
    parser.add_argument('--cookie-file', type=str, default=None,
                        help='Path to cookie file (default: cookie.json)')
    args = parser.parse_args()

    # Parse Markdown file
    parse_markdown = ParseMardown(args.input_file)
    code_blocks = parse_markdown.get_code_blocks()
    
    if not code_blocks:
        print("No code blocks found in the Markdown file")
        return

    print(f"Found {len(code_blocks)} code block(s)")
    
    # sudoパスワードを取得（-sオプションが指定された場合）
    sudo_password = None
    if args.sudo:
        sudo_password = getpass.getpass("Enter sudo password: ")
    
    # Initialize runner
    runner = RunnerCli(base_url=args.base_url, token=args.token, cookie_file=args.cookie_file)
    
    # Login (既存のクッキーがある場合は自動的に使用される)
    if not runner.login():
        if not args.token:
            print("Error: Token is required for authentication. Use --token option.")
            sys.exit(1)
        print("Failed to authenticate. Exiting.")
        sys.exit(1)
    
    # Run all code blocks
    runner.run_all(code_blocks, default_sudo_password=sudo_password)

if __name__ == "__main__":
    main()