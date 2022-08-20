from posts.models import Post

MIN_POSTS = 5

class LAI619Grader:
    def get_grades(self, user):
        has_min_posts = self.count_posts(user) >= MIN_POSTS
        return {
            "total": "PASS" if has_min_posts else "FAIL",
            "items": [
                {
                    "name": "posts", 
                    "description": "Did you post enough?", 
                    "score": self.count_posts(user)
                }
            ]
        }

    def count_posts(self, user):
        return Post.objects.filter(author=user).count()
