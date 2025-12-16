import sys
import os
import subprocess
from .transpiler import KomaruTranspiler

def print_help():
    print("🐱 KomaruScript V2")
    print("Использование:")
    print("  komaru <файл.ks>        # Запустить скрипт")
    print("  komaru install <пакет>  # Установить пакет через pip")
    print("  komaru compile <файл.ks> # Скомпилировать в .EXE")
    print("  komaru --debug <файл.ks> # Режим отладки (показать код Python)")
    print("  komaru                  # Запустить интерактивную консоль")

def install_package(package_name):
    print(f"🐱 Установка {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Успешно установлено: {package_name}!")
    except subprocess.CalledProcessError:
        print(f"❌ Ошибка установки {package_name}")

def run_script(file_path, debug=False):
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    transpiler = KomaruTranspiler()
    py_code = transpiler.transpile(code)

    # Add stdlib to sys.path so imports work
    stdlib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stdlib')
    if stdlib_path not in sys.path:
        sys.path.append(stdlib_path)

    if debug:
        print("--- 🐱 Транслированный Python код 🐍 ---")
        print(py_code)
        print("----------------------------------------")

    # Create a temporary environment to execute the code
    # We pass __file__ as the script path so os.path.dirname works correctly in the script
    env = {
        '__file__': os.path.abspath(file_path),
        '__name__': '__main__'
    }
    
    try:
        exec(py_code, env)
    except Exception as e:
        try:
            print(f"❌ Ошибка выполнения: {e}")
        except UnicodeEncodeError:
            print(f"[ERROR] Ошибка выполнения: {e}")

def compile_script(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return

    print(f"🔨 Компиляция {file_path} в EXE...")
    
    # 1. Transpile to Python
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    transpiler = KomaruTranspiler()
    py_code = transpiler.transpile(code)
    
    # Add path configuration for the standalone exe
    # Basically we want sys.path to be correct in the built exe too.
    # PyInstaller usually handles stdlib, but we need to ensure our custom stdlib is picked up if we want to bundle it.
    # For simplicity v1: Just try to compile the script logic.
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    py_file = f"{base_name}.py"
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write(py_code)
        
    # 2. Run PyInstaller
    try:
        # Check if pyinstaller is installed
        subprocess.check_call([sys.executable, "-m", "pyinstaller", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller не найден. Установите его: komaru install pyinstaller")
        os.remove(py_file)
        return

    try:
        # Build onefile
        cmd = [sys.executable, "-m", "pyinstaller", "--onefile", "--name", base_name, py_file]
        subprocess.check_call(cmd)
        print(f"✅ Успешно скомпилировано! Проверьте папку dist/{base_name}.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка компиляции: {e}")
    finally:
        if os.path.exists(py_file):
            os.remove(py_file)
        if os.path.exists(f"{base_name}.spec"):
            os.remove(f"{base_name}.spec")

def main():
    # Force UTF-8 for emoji support on Windows
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
             pass 

    if len(sys.argv) < 2:
        print("🐱 KomaruScript REPL (v2.0.0)")
        print("Напишите 'exit' или 'escape' для выхода.")
        
        transpiler = KomaruTranspiler()
        env = {'__name__': '__main__'}
        
        # Pre-load stdlib for REPL
        stdlib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stdlib')
        if stdlib_path not in sys.path:
            sys.path.append(stdlib_path)
            
        while True:
            try:
                line = input(">>> ")
                if line.strip() in ["exit", "escape", "quit"]:
                    break
                
                # Transpile line-by-line
                py_code = transpiler.transpile(line)
                
                try:
                    exec(py_code, env)
                except Exception as e:
                    print(f"❌ {e}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ {e}")
        return

    command = sys.argv[1]

    if command == "install":
        if len(sys.argv) < 3:
            print("❌ Укажите имя пакета для установки")
            return
        install_package(sys.argv[2])
    elif command == "compile":
        if len(sys.argv) < 3:
            print("❌ Укажите файл для компиляции")
            return
        compile_script(sys.argv[2])
    elif command == "--debug":
        if len(sys.argv) < 3:
            print("❌ Укажите файл для отладки")
            return
        run_script(sys.argv[2], debug=True)
    elif command.endswith(".ks"):
        run_script(command)
    else:
        # Assume it's a file if it doesn't match other commands, or show help
        if os.path.exists(command):
             run_script(command)
        else:
            print(f"❌ Неизвестная команда или файл: {command}")
            print_help()

if __name__ == "__main__":
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass # Python < 3.7
    main()
