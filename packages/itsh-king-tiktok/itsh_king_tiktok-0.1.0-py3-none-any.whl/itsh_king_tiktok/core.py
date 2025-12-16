import requests
import random
uu = 'qwertyuiopasdfghjklzxcvbnm1234567890'

class TikTokChecker:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def check_user(self, username):
        try:
            response = requests.get(f'https://www.tiktok.com/@{username}', headers=self.headers, timeout=10)

            if response.status_code == 404:
                return {
                    "available": True,
                    "message": f"@{username} is available"
                }

            if response.status_code == 200:
                text = response.text

                if '"followerCount":' in text:
                    followers = self._extract(text, '"followerCount":', ",")
                    following = self._extract(text, '"followingCount":', ",")
                    likes = self._extract(text, '"heartCount":', ",")

                    return {
                        "available": False,
                        "followers": followers,
                        "following": following,
                        "likes": likes,
                        "message": f"@{username} is taken"
                    }

                return {
                    "available": False,
                    "message": f"@{username} taken but stats unavailable"
                }

            return {
                "available": None,
                "message": f"Unexpected status: {response.status_code}"
            }

        except requests.exceptions.RequestException as e:
            return {
                "available": None,
                "message": f"Connection error: {e}"
            }

    def _extract(self, text, key, end_char):
        start = text.find(key) + len(key)
        end = text.find(end_char, start)
        return text[start:end].strip()


def run_cli():
    checker = TikTokChecker()

    while True:
        print("" + "=" * 40)
        user = ''.join(random.choice(uu) for i in range(4))
        username = user.strip().replace("@", "")

        if username.lower() == "exit":
            print("Goodbye 👋")
            break

        if not username:
            print("⚠️ Enter a valid username")
            continue

        info = checker.check_user(username)

        print(info["message"])
        if info.get("followers"): print("Followers:", info["followers"])
        if info.get("following"): print("Following:", info["following"])
        if info.get("likes"): print("Likes:", info["likes"])
TikTokChecker()
run_cli()