from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel
import subprocess
import tempfile
import os
import asyncio
import uuid
import signal
import sys
import logging
import secrets
import json
import threading
import socket
from typing import Optional, Dict
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta

# デバッグモードの有効化フラグ（-dオプションで設定）
DEBUG_MODE = '-d' in sys.argv or '--debug' in sys.argv

# ロギング設定
if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# sudo機能の有効化フラグ（-sオプションで設定）
SUDO_ENABLED = '-s' in sys.argv or '--sudo' in sys.argv

# トークン認証の設定（URLアクセス制御用）
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", secrets.token_urlsafe(32))

# セッション管理
SESSION_COOKIE_NAME = "m21_session"
SESSION_TTL_SECONDS = 60 * 60 * 8  # 8時間
sessions: Dict[str, Dict] = {}

# CORS設定は動的ポートに合わせてmain()関数内で設定



# 静的ファイルのパス
STATIC_DIR = Path(__file__).parent / "static"
IMAGE_DIR = Path.cwd() / "images"

# Markdownファイルの保存ベースディレクトリ（実行時のカレントディレクトリ）
FILES_DIR = Path.cwd()
BASE_DIR = FILES_DIR.resolve()


def resolve_safe_path(rel_path: str) -> Path:
    """相対パスをベースディレクトリ内の安全な絶対パスへ解決"""
    rel_path = (rel_path or "").strip()
    # 絶対パスとパストラバーサルを拒否
    if rel_path.startswith(("/", "\\")):
        rel_path = rel_path.lstrip("/\\")
    rel_parts = Path(rel_path).parts
    if ".." in rel_parts:
        raise HTTPException(status_code=400, detail="Invalid path")

    candidate = (BASE_DIR / rel_path).resolve()
    base_resolved = BASE_DIR
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise HTTPException(status_code=400, detail="Path escapes base directory")
    return candidate


def to_relative_path(path: Path) -> str:
    """ベースディレクトリからの相対パスを返す（POSIX形式）"""
    rel = path.resolve().relative_to(BASE_DIR)
    rel_str = rel.as_posix()
    return "" if rel_str == "." else rel_str

# 最後に開いたファイル名（メモリ内で保持）
last_opened_file: Optional[str] = None

# 最後に開いたディレクトリパス（メモリ内で保持）
last_opened_directory: Optional[str] = None

# 作成された画像ファイル取得
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

@app.get("/images/{file_path:path}")
async def get_image(file_path: str):
    """画像ファイルを取得"""
    image_path = IMAGE_DIR / file_path
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

# 静的ファイル（JS, CSS, 画像など）を配信
if STATIC_DIR.exists():
    app.mount(
        "/notebook/assets",
        StaticFiles(directory=STATIC_DIR / "assets"),
        name="static_assets"
    )
    
    # faviconなどのルートレベルの静的ファイル
    @app.get("/notebook/favicon.ico")
    async def favicon():
        favicon_path = STATIC_DIR / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        raise HTTPException(status_code=404)
    
    @app.get("/notebook")
    @app.get("/notebook/{path:path}")
    async def serve_frontend(path: str = ""):
        """フロントエンドを配信（SPA用）"""
        # 静的ファイルのリクエスト（拡張子がある場合）
        if path and "." in path and not path.endswith(".html"):
            file_path = STATIC_DIR / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
        
        # SPA用: すべてのルートをindex.htmlにフォールバック
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            raise HTTPException(
                status_code=503,
                detail="Frontend not built. Run 'npm run build' first."
            )
else:
    @app.get("/notebook")
    @app.get("/notebook/{path:path}")
    async def frontend_not_built():
        raise HTTPException(
            status_code=503,
            detail="Frontend not built. Run 'npm run build' first."
        )

# Language configurations
LANGUAGE_CONFIGS = {
    'bash': {
        'command': lambda f: ['bash', f],
        'extension': 'sh',
    },
    'sh': {
        'command': lambda f: ['bash', f],
        'extension': 'sh',
    },
    'python': {
        'command': lambda f: ['python3', f],
        'extension': 'py',
    },
    'python3': {
        'command': lambda f: ['python3', f],
        'extension': 'py',
    },
    'javascript': {
        'command': lambda f: ['node', f],
        'extension': 'js',
    },
    'js': {
        'command': lambda f: ['node', f],
        'extension': 'js',
    },
    'node': {
        'command': lambda f: ['node', f],
        'extension': 'js',
    },
}

wrappers = {
    'uv': ['uv', 'run'],
    'poetry': ['poetry', 'run'],
    'pipenv': ['pipenv', 'run'],
}

TIMEOUT_SECONDS = 30

# 実行中のタスクを管理
running_tasks: Dict[str, Dict] = {}


def create_session(token: str) -> str:
    """セッションを生成し、メモリに保存"""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "token": token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(seconds=SESSION_TTL_SECONDS),
    }
    return session_id


def validate_session(session_id: Optional[str]) -> Optional[Dict]:
    """セッションIDから有効なセッションを取得"""
    if not session_id:
        return None
    session = sessions.get(session_id)
    if not session:
        return None
    if session["expires_at"] < datetime.utcnow():
        # 期限切れセッションをクリーンアップ
        sessions.pop(session_id, None)
        return None
    return session


def has_active_session() -> bool:
    """有効なセッションが存在するかを確認。期限切れは同時に掃除。"""
    expired_ids = [sid for sid, s in sessions.items() if s["expires_at"] < datetime.utcnow()]
    for sid in expired_ids:
        sessions.pop(sid, None)
    return any(sessions.values())


async def require_session(request: Request) -> Dict:
    """セッション認証が必要なエンドポイントで使用する依存関係"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    session = validate_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session not found or expired")
    return session


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecuteRequest(BaseModel):
    code: str
    language: str = "bash"
    task_id: Optional[str] = None
    sudo: bool = False
    password: Optional[str] = None
    wrap: Optional[str] = None
    timeout: int = TIMEOUT_SECONDS


class StopRequest(BaseModel):
    task_id: str


class FileRequest(BaseModel):
    path: str
    content: str
    sudo: bool = False
    password: Optional[str] = None


class MarkdownFileRequest(BaseModel):
    filename: str
    content: str


class DirectoryRequest(BaseModel):
    path: str


class DirectoryRenameRequest(BaseModel):
    new_name: str


async def execute_code_async(
    task_id: str,
    code: str,
    language: str,
    wrap: Optional[str] = None,
    sudo: bool = False,
    password: Optional[str] = None,
    timeout: int = TIMEOUT_SECONDS
):
    """非同期でコードを実行"""
    # sudo実行のチェック
    if sudo:
        if not SUDO_ENABLED:
            running_tasks[task_id]['status'] = ExecutionStatus.FAILED
            running_tasks[task_id]['error'] = 'Sudo execution is not enabled. Start server with -s option.'
            return
        
        if not password:
            running_tasks[task_id]['status'] = ExecutionStatus.FAILED
            running_tasks[task_id]['error'] = 'Password is required for sudo execution.'
            return
    
    lang_config = LANGUAGE_CONFIGS.get(language.lower())
    if not lang_config:
        running_tasks[task_id]['status'] = ExecutionStatus.FAILED
        running_tasks[task_id]['error'] = f'Unsupported language: {language}'
        return


    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{lang_config["extension"]}',
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name

        running_tasks[task_id]['status'] = ExecutionStatus.RUNNING

        base_cmd = lang_config['command'](temp_file)
        if wrap:
            wrapper_cmd = wrappers.get(wrap.lower(), None)
            logger.debug(f"Wrapper command: {wrapper_cmd}")
            if wrapper_cmd is None:
                raise ValueError(f'Unsupported wrapper: {wrap}')
            base_cmd = wrapper_cmd + base_cmd
        logger.debug(f"Running command: {' '.join(base_cmd)}")

        # Execute code in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def run_process():
            if sudo:
                # sudo -S で実行（パスワードをstdinから読み込む）
                cmd = ['sudo', '-S'] + base_cmd
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # 行バッファリング
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
                # パスワードをstdinに送信（communicate()が自動的にstdinを閉じる）
                process.stdin.write(password + '\n')
                process.stdin.flush()
                # stdin.close()は呼ばない - communicate()が自動的に閉じる
                return process
            else:
                return subprocess.Popen(
                    base_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # 行バッファリング
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )

        process = await loop.run_in_executor(None, run_process)
        running_tasks[task_id]['process'] = process
        stream_queue = running_tasks[task_id]['stream_queue']

        # ストリーミング用: stdoutとstderrを別スレッドで読み取る
        def read_stream_thread(stream, queue, is_error=False):
            """ストリームを読み取り、キューに書き込む（スレッドで実行）"""
            try:
                for line in iter(stream.readline, ''):
                    if not line:
                        break
                    # スレッドからasyncioキューに書き込む
                    asyncio.run_coroutine_threadsafe(
                        queue.put(('error' if is_error else 'output', line)),
                        loop
                    )
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    queue.put(('error', f"Stream read error: {e}\n")),
                    loop
                )

        # stdoutとstderrを別スレッドで読み取る
        stdout_thread = threading.Thread(target=read_stream_thread, args=(process.stdout, stream_queue, False), daemon=True)
        stderr_thread = threading.Thread(target=read_stream_thread, args=(process.stderr, stream_queue, True), daemon=True)
        stdout_thread.start()
        stderr_thread.start()

        # プロセスの完了を待つ
        try:
            returncode = await asyncio.wait_for(
                loop.run_in_executor(None, process.wait),
                timeout=timeout
            )

            # スレッドの完了を待つ
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

            # 残りの出力を収集
            stdout_lines = []
            stderr_lines = []
            while not stream_queue.empty():
                stream_type, line = await stream_queue.get()
                if stream_type == 'output':
                    stdout_lines.append(line)
                elif stream_type == 'error':
                    stderr_lines.append(line)

            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)

            if returncode != 0:
                running_tasks[task_id]['status'] = ExecutionStatus.FAILED
                running_tasks[task_id]['output'] = stdout
                running_tasks[task_id]['error'] = stderr
            else:
                running_tasks[task_id]['status'] = ExecutionStatus.COMPLETED
                running_tasks[task_id]['output'] = stdout
                running_tasks[task_id]['error'] = None

            # 完了を通知
            await stream_queue.put(('status', {'status': running_tasks[task_id]['status'], 'output': stdout, 'error': stderr}))

        except asyncio.TimeoutError:
            # Kill the process group
            if process:
                message = ""
                try:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                except Exception as e:
                    message = f"(Failed to terminate process: {e})"

            running_tasks[task_id]['status'] = ExecutionStatus.FAILED
            running_tasks[task_id]['error'] = f"Process timeout {message}"
            await stream_queue.put(('error', f"Process timeout {message}\n"))
            await stream_queue.put(('status', {'status': ExecutionStatus.FAILED, 'error': f"Process timeout {message}"}))

    except Exception as e:
        running_tasks[task_id]['status'] = ExecutionStatus.FAILED
        running_tasks[task_id]['error'] = str(e)

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.error(f"Failed to remove temporary file: {temp_file} : {e}")
        
        # Clean up process reference
        if task_id in running_tasks:
            running_tasks[task_id]['process'] = None


@app.get("/auth/login")
async def login_with_token(request: Request, token: str, redirect: Optional[str] = None):
    """
    トークンで認証し、セッションを発行してフロントエンドへリダイレクト
    無限ループ防止のため、既に有効なセッションがある場合はリダイレクトのみ行う
    """
    target_url = redirect or "/notebook/?session=1"
    existing_session = validate_session(request.cookies.get(SESSION_COOKIE_NAME))
    if existing_session:
        return RedirectResponse(url=target_url, status_code=302)

    # グローバルに有効なセッションが存在する場合は新規発行を拒否
    if has_active_session():
        raise HTTPException(status_code=403, detail="Another active session already exists")

    if token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    session_id = create_session(token)
    response = RedirectResponse(url=target_url, status_code=302)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=SESSION_TTL_SECONDS,
        secure=False,
        samesite="lax",
    )
    return response


@app.get("/auth/session")
async def session_status(request: Request):
    """セッションが有効かを確認"""
    session = validate_session(request.cookies.get(SESSION_COOKIE_NAME))
    if not session:
        raise HTTPException(status_code=401, detail="Session not found or expired")
    return {"status": "authenticated"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/execute")
async def execute_code(request: ExecuteRequest, session: Dict = Depends(require_session)):
    """コードを非同期で実行開始"""
    if not request.code:
        raise HTTPException(status_code=400, detail="Code is required")

    language = request.language.lower()
    if language not in LANGUAGE_CONFIGS:
        raise HTTPException(
            status_code=400,
            detail=f'Unsupported language: {language}. Supported languages: {", ".join(LANGUAGE_CONFIGS.keys())}'
        )

    python_path = os.environ.get("PYTHONPATH", None)
    if python_path is None:
        os.environ["PYTHONPATH"] = str(Path.cwd())

    # Generate task ID if not provided
    task_id = request.task_id or str(uuid.uuid4())

    # Initialize task status
    running_tasks[task_id] = {
        'status': ExecutionStatus.PENDING,
        'output': None,
        'error': None,
        'process': None,
        'stream_queue': asyncio.Queue(),
    }

    timeout = request.timeout or TIMEOUT_SECONDS
    wrap = request.wrap or None
    sudo = request.sudo or False
    password = request.password or None
    
    # Start execution in background
    asyncio.create_task(execute_code_async(
        task_id, 
        request.code, 
        language, 
        wrap=wrap,
        timeout=timeout,
        sudo=sudo,
        password=password
    ))

    return {
        "task_id": task_id,
        "status": ExecutionStatus.PENDING,
        "message": "Execution started"
    }


@app.get("/api/execute/{task_id}")
async def get_execution_status(task_id: str, session: Dict = Depends(require_session)):
    """実行状態を取得"""
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = running_tasks[task_id]
    response = {
        "task_id": task_id,
        "status": task['status'],
    }

    if task['status'] == ExecutionStatus.COMPLETED:
        response["output"] = task.get('output', '')
        response["result"] = task.get('output', '')
    elif task['status'] == ExecutionStatus.FAILED:
        response["error"] = task.get('error', '')
        response["output"] = task.get('output', '')

    return response


@app.get("/api/execute/stream/{task_id}")
async def stream_execution_output(task_id: str, session: Dict = Depends(require_session)):
    """実行中の出力をストリーミング（SSE）"""
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = running_tasks[task_id]
    stream_queue = task.get('stream_queue')

    if not stream_queue:
        raise HTTPException(status_code=400, detail="Streaming not available for this task")

    async def generate():
        """SSEイベントを生成"""
        try:
            while True:
                try:
                    # タイムアウト付きでキューから読み取る
                    stream_type, data = await asyncio.wait_for(stream_queue.get(), timeout=0.5)
                    
                    if stream_type == 'status':
                        # 最終状態を送信して終了
                        yield f"data: {json.dumps({'type': 'status', 'status': data['status'], 'output': data.get('output', ''), 'error': data.get('error', '')})}\n\n"
                        break
                    else:
                        # 出力データを送信
                        yield f"data: {json.dumps({'type': stream_type, 'data': data})}\n\n"
                        
                except asyncio.TimeoutError:
                    # タイムアウト時はタスクの状態を確認
                    if task['status'] in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                        # 残りの出力を処理
                        while not stream_queue.empty():
                            stream_type, data = await stream_queue.get()
                            if stream_type == 'status':
                                yield f"data: {json.dumps({'type': 'status', 'status': data['status'], 'output': data.get('output', ''), 'error': data.get('error', '')})}\n\n"
                                break
                            else:
                                yield f"data: {json.dumps({'type': stream_type, 'data': data})}\n\n"
                        # 最終状態を送信
                        yield f"data: {json.dumps({'type': 'status', 'status': task['status'], 'output': task.get('output', ''), 'error': task.get('error', '')})}\n\n"
                        break
                    continue

        except Exception as e:
            logger.exception(f"Error in stream generation: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/execute/stop")
async def stop_execution(request: StopRequest, session: Dict = Depends(require_session)):
    """実行を停止"""
    task_id = request.task_id

    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = running_tasks[task_id]

    if task['status'] not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        return {
            "task_id": task_id,
            "status": task['status'],
            "message": "Task is not running"
        }

    # Kill the process
    process = task.get('process')
    if process:
        try:
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            # Wait a bit for graceful termination
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Force kill if still running
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
        except Exception:
            pass

    task['status'] = ExecutionStatus.CANCELLED
    task['error'] = "Execution cancelled by user"

    return {
        "task_id": task_id,
        "status": ExecutionStatus.CANCELLED,
        "message": "Execution stopped"
    }


@app.delete("/api/execute/{task_id}")
async def cleanup_task(task_id: str, session: Dict = Depends(require_session)):
    """タスクをクリーンアップ"""
    if task_id in running_tasks:
        task = running_tasks[task_id]
        process = task.get('process')
        if process:
            message = "Task cleaned up"
            try:
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
            except Exception as e:
                message = f"Failed to terminate process: {e}"
        del running_tasks[task_id]
        return {"message": message}
    return {"message": "Task not found"}


@app.post("/api/file")
async def create_file(request: FileRequest, session: Dict = Depends(require_session)):
    """ファイルを作成"""
    logger.debug(f"create_file called: path={request.path}, sudo={request.sudo}, password={'*' * len(request.password) if request.password else None}")
    
    if not request.path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    if not request.content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    # sudo実行のチェック
    if request.sudo:
        logger.debug(f"SUDO_ENABLED={SUDO_ENABLED}")
        if not SUDO_ENABLED:
            raise HTTPException(status_code=403, detail="Sudo execution is not enabled. Start server with -s option.")
        
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required for sudo file creation.")
    
    try:
        # パスの正規化とセキュリティチェック
        file_path = Path(request.path).resolve()
        logger.debug(f"Resolved file_path: {file_path}")
        
        # 相対パスの場合、カレントディレクトリからの相対パスとして扱う
        # 絶対パスの場合はそのまま使用（セキュリティ上の注意が必要）
        
        if request.sudo:
            # sudoでファイルを作成
            # 一時ファイルに内容を書き込み、sudoでコピー
            tmp_file_path = None
            try:
                # 一時ファイルに内容を書き込む
                logger.debug("Creating temporary file")
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_file:
                    tmp_file.write(request.content)
                    tmp_file_path = tmp_file.name
                logger.debug(f"Temporary file created: {tmp_file_path}")
                
                # 親ディレクトリが存在しない場合は作成（常に実行、既に存在する場合はエラーにならない）
                parent_dir = file_path.parent
                logger.debug(f"Creating parent directory: {parent_dir}")
                mkdir_cmd = ['sudo', '-S', 'mkdir', '-p', str(parent_dir)]
                logger.debug(f"Running command: {' '.join(mkdir_cmd)}")
                mkdir_process = subprocess.Popen(
                    mkdir_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                mkdir_process.stdin.write(request.password + '\n')
                mkdir_stdout, mkdir_stderr = mkdir_process.communicate()
                logger.debug(f"mkdir returncode: {mkdir_process.returncode}, stdout: {mkdir_stdout}, stderr: {mkdir_stderr}")
                
                if mkdir_process.returncode != 0:
                    raise Exception(f"Failed to create directory: {mkdir_stderr}")
                
                # sudo cp でファイルをコピー
                logger.debug(f"Copying file from {tmp_file_path} to {file_path}")
                cp_cmd = ['sudo', '-S', 'cp', tmp_file_path, str(file_path)]
                logger.debug(f"Running command: {' '.join(cp_cmd)}")
                cp_process = subprocess.Popen(
                    cp_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                cp_process.stdin.write(request.password + '\n')
                cp_stdout, cp_stderr = cp_process.communicate()
                logger.debug(f"cp returncode: {cp_process.returncode}, stdout: {cp_stdout}, stderr: {cp_stderr}")
                
                if cp_process.returncode != 0:
                    raise Exception(f"Failed to create file: {cp_stderr}")
                
                # ファイルのパーミッションを設定（必要に応じて）
                logger.debug(f"Setting permissions on {file_path}")
                chmod_cmd = ['sudo', '-S', 'chmod', '644', str(file_path)]
                logger.debug(f"Running command: {' '.join(chmod_cmd)}")
                chmod_process = subprocess.Popen(
                    chmod_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                chmod_process.stdin.write(request.password + '\n')
                chmod_stdout, chmod_stderr = chmod_process.communicate()
                logger.debug(f"chmod returncode: {chmod_process.returncode}, stdout: {chmod_stdout}, stderr: {chmod_stderr}")
                
                if chmod_process.returncode != 0:
                    # chmodの失敗は警告として扱う（ファイルは作成されている）
                    logger.warning(f"chmod failed but file was created: {chmod_stderr}")
            finally:
                # 一時ファイルを削除
                if tmp_file_path and os.path.exists(tmp_file_path):
                    try:
                        logger.debug(f"Removing temporary file: {tmp_file_path}")
                        os.unlink(tmp_file_path)
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file: {e}")
        else:
            # 通常のファイル作成
            logger.debug("Creating file without sudo")
            # 親ディレクトリが存在することを確認
            parent_dir = file_path.parent
            if not parent_dir.exists():
                # 親ディレクトリを作成
                parent_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイルを作成
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(request.content)
        
        logger.debug(f"File created successfully: {file_path}")
        return {
            "message": "File created successfully",
            "path": str(file_path)
        }
    except Exception as e:
        logger.exception(f"Error creating file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create file: {str(e)}")


# MarkdownファイルのCRUD API
@app.get("/api/files")
async def list_files(path: str = "", session: Dict = Depends(require_session)):
    """指定パス直下のMarkdownファイルとディレクトリ一覧を取得"""
    try:
        target_dir = resolve_safe_path(path)
        if not target_dir.exists() or not target_dir.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")

        files = []
        directories = []

        for entry in target_dir.iterdir():
            if entry.is_dir():
                stat = entry.stat()
                directories.append({
                    "name": entry.name,
                    "path": to_relative_path(entry),
                    "modified": stat.st_mtime,
                })
            elif entry.is_file() and entry.suffix == ".md":
                stat = entry.stat()
                files.append({
                    "filename": entry.name,
                    "path": to_relative_path(entry),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                })

        directories.sort(key=lambda x: x["name"])
        files.sort(key=lambda x: x["filename"])
        return {"directories": directories, "files": files, "path": to_relative_path(target_dir)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.get("/api/files/last")
async def get_last_file(session: Dict = Depends(require_session)):
    """最後に開いたファイル名を取得"""
    global last_opened_file
    
    if last_opened_file:
        # ファイルが存在するか確認
        file_path = resolve_safe_path(last_opened_file)
        if file_path.exists():
            return {"filename": last_opened_file}
        else:
            # ファイルが存在しない場合はクリア
            last_opened_file = None
    
    return {"filename": None}


@app.post("/api/files/last")
async def set_last_file(request: dict, session: Dict = Depends(require_session)):
    """最後に開いたファイル名を保存"""
    global last_opened_file
    
    filename = request.get('filename')
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # パスを検証
    file_path = resolve_safe_path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    last_opened_file = filename
    return {
        "message": "Last file saved successfully",
        "filename": filename,
    }


@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str, session: Dict = Depends(require_session)):
    """Markdownファイルを読み込む"""
    resolved_path = resolve_safe_path(file_path)
    if resolved_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "filename": to_relative_path(resolved_path),
            "content": content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@app.post("/api/files")
async def save_file(request: MarkdownFileRequest, session: Dict = Depends(require_session)):
    """Markdownファイルを保存（作成または更新）"""
    if not request.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    filename = request.filename
    if not filename.endswith('.md'):
        filename += '.md'

    file_path = resolve_safe_path(filename)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
        return {
            "message": "File saved successfully",
            "filename": to_relative_path(file_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@app.put("/api/files/{file_path:path}")
async def update_file(file_path: str, request: MarkdownFileRequest, session: Dict = Depends(require_session)):
    """Markdownファイルを更新"""
    resolved_path = resolve_safe_path(file_path)
    if resolved_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
        return {
            "message": "File updated successfully",
            "filename": to_relative_path(resolved_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")


@app.delete("/api/files/{file_path:path}")
async def delete_file(file_path: str, session: Dict = Depends(require_session)):
    """Markdownファイルを削除"""
    global last_opened_file
    
    resolved_path = resolve_safe_path(file_path)
    if resolved_path.suffix != ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        resolved_path.unlink()
        
        # 削除したファイルが最後に開いたファイルの場合、キャッシュをクリア
        if last_opened_file == file_path or last_opened_file == to_relative_path(resolved_path):
            last_opened_file = None
        
        return {
            "message": "File deleted successfully",
            "filename": to_relative_path(resolved_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


# ディレクトリ CRUD
@app.get("/api/dirs")
async def list_directories(path: str = "", session: Dict = Depends(require_session)):
    """指定ディレクトリ直下のディレクトリ一覧を取得"""
    try:
        target_dir = resolve_safe_path(path)
        if not target_dir.exists() or not target_dir.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")

        directories = []
        for entry in target_dir.iterdir():
            if entry.is_dir():
                stat = entry.stat()
                directories.append({
                    "name": entry.name,
                    "path": to_relative_path(entry),
                    "modified": stat.st_mtime,
                })
        directories.sort(key=lambda x: x["name"])
        return {"directories": directories, "path": to_relative_path(target_dir)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list directories: {str(e)}")


@app.post("/api/dirs")
async def create_directory(request: DirectoryRequest, session: Dict = Depends(require_session)):
    """ディレクトリを作成"""
    if not request.path:
        raise HTTPException(status_code=400, detail="Path is required")
    
    dir_path = resolve_safe_path(request.path)
    try:
        dir_path.mkdir(parents=True, exist_ok=False)
        return {
            "message": "Directory created successfully",
            "path": to_relative_path(dir_path),
        }
    except FileExistsError:
        raise HTTPException(status_code=400, detail="Directory already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")


@app.put("/api/dirs/{dir_path:path}")
async def rename_directory(dir_path: str, request: DirectoryRenameRequest, session: Dict = Depends(require_session)):
    """ディレクトリ名を変更"""
    if not request.new_name:
        raise HTTPException(status_code=400, detail="New name is required")

    target_dir = resolve_safe_path(dir_path)
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    # 新しい名前にパストラバーサルを含めない
    if any(part in ("..", "") for part in Path(request.new_name).parts) or "/" in request.new_name or "\\" in request.new_name:
        raise HTTPException(status_code=400, detail="Invalid directory name")

    new_path = target_dir.parent / request.new_name
    new_path_resolved = resolve_safe_path(to_relative_path(new_path))

    if new_path_resolved.exists():
        raise HTTPException(status_code=400, detail="Target directory already exists")

    try:
        target_dir.rename(new_path_resolved)
        return {
            "message": "Directory renamed successfully",
            "path": to_relative_path(new_path_resolved),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename directory: {str(e)}")


@app.delete("/api/dirs/{dir_path:path}")
async def delete_directory(dir_path: str, session: Dict = Depends(require_session)):
    """ディレクトリを削除（空ディレクトリのみ）"""
    target_dir = resolve_safe_path(dir_path)
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")

    if any(target_dir.iterdir()):
        raise HTTPException(status_code=400, detail="Directory is not empty")

    try:
        target_dir.rmdir()
        return {
            "message": "Directory deleted successfully",
            "path": to_relative_path(target_dir),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete directory: {str(e)}")


@app.get("/api/dirs/last")
async def get_last_directory(session: Dict = Depends(require_session)):
    """最後に開いたディレクトリパスを取得"""
    global last_opened_directory
    
    if last_opened_directory is not None:
        # ディレクトリが存在するか確認
        try:
            dir_path = resolve_safe_path(last_opened_directory)
            if dir_path.exists() and dir_path.is_dir():
                return {"path": last_opened_directory}
            else:
                # ディレクトリが存在しない場合はクリア
                last_opened_directory = None
        except HTTPException:
            # パスが無効な場合はクリア
            last_opened_directory = None
    
    return {"path": None}


@app.post("/api/dirs/last")
async def set_last_directory(request: dict, session: Dict = Depends(require_session)):
    """最後に開いたディレクトリパスを保存"""
    global last_opened_directory
    
    path = request.get('path')
    if path is None:
        raise HTTPException(status_code=400, detail="Path is required")
    
    # 空文字列の場合はNoneとして保存（ルートディレクトリ）
    if path == "":
        last_opened_directory = ""
        return {
            "message": "Last directory saved successfully",
            "path": "",
        }
    
    # パスを検証
    try:
        dir_path = resolve_safe_path(path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        last_opened_directory = path
        return {
            "message": "Last directory saved successfully",
            "path": path,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save last directory: {str(e)}")


def is_port_available(host: str, port: int) -> bool:
    """ポートが使用可能かどうかをチェック"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(host: str, start_port: int, max_attempts: int = 100) -> int:
    """使用可能なポートを見つける（npmのようにポート番号を加算）"""
    port = start_port
    attempts = 0
    
    while attempts < max_attempts:
        if is_port_available(host, port):
            return port
        port += 1
        attempts += 1
    
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts (starting from {start_port})")


def main():
    """Main entry point for the application"""
    import uvicorn
    start_port = int(os.environ.get("PORT", 8000))
    # ホストはlocalhostのみを許可
    host = "localhost"
    
    # 使用可能なポートを見つける
    try:
        port = find_available_port(host, start_port)
        if port != start_port:
            print(f"⚠️  Port {start_port} is already in use, trying port {port}...")
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # 動的ポートに合わせてCORS設定を更新
    # 既存のCORSミドルウェアを削除（存在する場合）
    cors_middleware_index = None
    for i, middleware in enumerate(app.user_middleware):
        if middleware.cls == CORSMiddleware:
            cors_middleware_index = i
            break
    
    if cors_middleware_index is not None:
        app.user_middleware.pop(cors_middleware_index)
    
    # 動的に見つかったポートとlocalhostに合わせてCORSを制限
    base_url = f"http://{host}:{port}"
    allowed_origins = [
        base_url,
        #"http://localhost:5173",  # Vite開発サーバー
        #"http://127.0.0.1:5173",
    ]
    
    # 環境変数で追加のオリジンを指定可能
    cors_origins_env = os.environ.get("CORS_ORIGINS", None)
    if cors_origins_env:
        allowed_origins.extend([origin.strip() for origin in cors_origins_env.split(",")])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Cookie"],
        expose_headers=["Content-Type"],
    )
    
    # トークンを含むURLを生成
    token_url = f"{base_url}/notebook/?token={ACCESS_TOKEN}"
    
    print(f"📓 Notebook UI: {token_url}")
    if DEBUG_MODE:
        print("🐛 Debug mode is ENABLED (-d option)")
    if SUDO_ENABLED:
        print("⚠️  Sudo execution is ENABLED (-s option)")
    else:
        print("ℹ️  Sudo execution is disabled. Use -s option to enable.")
    if not STATIC_DIR.exists():
        print("⚠️  Frontend not built. Run 'npm run build' first.")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
