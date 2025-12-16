try:
    import requests
except ImportError:
    print("❌ Error: 'requests' module not found. Please run 'komaru install requests'")
    requests = None

class WebClient:
    def __init__(self):
        self.session = requests.Session() if requests else None

    def получить_страницу(self, url):
        if not self.session: return None
        return self.session.get(url)

def создать_веб_клиент():
    return WebClient()
