import os
import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.blog.models import Post, BlogCategory
from django.conf import settings

class Command(BaseCommand):
    help = 'Loads initial blog posts from MASTER_PROJECT.md'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'MASTER_PROJECT.md')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by POST marker anywhere in the file
        raw_posts = content.split('### POST ')[1:]
        
        # Get or create author
        author, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            author.set_password('admin123')
            author.save()

        count = 0
        for raw_post in raw_posts:
            lines = raw_post.strip().split('\n')
            
            title = ''
            slug = ''
            category_name = ''
            meta_title = ''
            meta_desc = ''
            focus_keyword = ''
            read_time = 5
            
            content_lines = []
            parsing_content = False
            
            for line in lines:
                if line.startswith('**Title:**'):
                    title = line.replace('**Title:**', '').strip()
                elif line.startswith('**Slug:**'):
                    slug = line.replace('**Slug:**', '').strip()
                elif line.startswith('**Category:**'):
                    category_name = line.replace('**Category:**', '').strip()
                elif line.startswith('**Meta Title:**'):
                    meta_title = line.replace('**Meta Title:**', '').strip()
                elif line.startswith('**Meta Description:**'):
                    meta_desc = line.replace('**Meta Description:**', '').strip()
                elif line.startswith('**Focus Keyword:**'):
                    focus_keyword = line.replace('**Focus Keyword:**', '').strip()
                elif line.startswith('**Read Time:**'):
                    rt_str = line.replace('**Read Time:**', '').strip().replace('min', '').strip()
                    try:
                        read_time = int(rt_str)
                    except ValueError:
                        pass
                elif line.startswith('**Content:**'):
                    parsing_content = True
                elif parsing_content:
                    if line.strip() == '---':
                        break
                    content_lines.append(line)
            
            if not title or not category_name:
                continue

            # Join content and wrap paragraphs
            raw_body = '\n'.join(content_lines).strip()
            
            # Very basic markdown to HTML for this specific format
            html_body = []
            for p in raw_body.split('\n\n'):
                p = p.strip()
                if not p:
                    continue
                # Replace **bold**
                p = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p)
                # Replace *italic*
                p = re.sub(r'\*(.*?)\*', r'<em>\1</em>', p)
                
                # Check if it's a heading
                if p.isupper() and len(p.split()) < 10:
                    html_body.append(f'<h3>{p}</h3>')
                else:
                    html_body.append(f'<p>{p}</p>')
            
            final_html = '\n'.join(html_body)

            # Create Category
            category, _ = BlogCategory.objects.get_or_create(
                name=category_name,
                defaults={'slug': category_name.lower().replace(' ', '-')}
            )

            # Create Post
            post, created = Post.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'category': category,
                    'author': author,
                    'content': final_html,
                    'excerpt': meta_desc,
                    'status': 'published',
                    'meta_title': meta_title,
                    'meta_description': meta_desc,
                    'focus_keyword': focus_keyword,
                    'read_time': read_time
                }
            )
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} blog posts.'))
