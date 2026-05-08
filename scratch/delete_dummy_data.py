from apps.blog.models import Post
from apps.jobs.models import Job

# Delete dummy posts
dummy_post_slugs = [
    'how-to-ace-your-next-interview',
    'remote-work-the-future-of-recruitment',
    '5-tips-for-building-a-great-resume',
    'the-rise-of-ai-in-the-workplace'
]

posts_deleted = Post.objects.filter(slug__in=dummy_post_slugs).delete()
print(f"Deleted posts: {posts_deleted}")

# Delete dummy jobs
jobs_deleted = Job.objects.filter(slug__endswith='-1234').delete()
print(f"Deleted jobs: {jobs_deleted}")
