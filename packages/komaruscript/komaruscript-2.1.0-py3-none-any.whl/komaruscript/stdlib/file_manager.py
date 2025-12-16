import os

class FileManager:
    def создать_папку(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            
    def получить_список_файлов(self, path="."):
        results = []
        if os.path.exists(path):
            for entry in os.scandir(path):
                results.append({
                    "имя": entry.name,
                    "это_папка": entry.is_dir()
                })
        return results

def создать_менеджер_файлов():
    return FileManager()
