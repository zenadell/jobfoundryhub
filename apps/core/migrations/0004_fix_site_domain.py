from django.db import migrations

def fix_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Use update_or_create for robustness
    Site.objects.update_or_create(
        id=1,
        defaults={
            'domain': 'www.jobfoundryhub.com',
            'name': 'Job Foundry Hub'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_alter_faq_answer_alter_sitesettings_about_intro_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(fix_site_domain),
    ]
