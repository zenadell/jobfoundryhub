import json
import logging
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)
User = get_user_model()

# List of models to export/import, in dependency order for insertion.
# For deletion, we will process this list in reverse.
MODELS_CONFIG = [
    {
        "app_label": "auth",
        "model_name": "User",
        "key": "users",
    },
    {
        "app_label": "accounts",
        "model_name": "UserProfile",
        "key": "user_profiles",
    },
    {
        "app_label": "core",
        "model_name": "SiteSettings",
        "key": "site_settings",
    },
    {
        "app_label": "core",
        "model_name": "FAQ",
        "key": "faqs",
    },
    {
        "app_label": "core",
        "model_name": "HowItWorksStep",
        "key": "how_it_works_steps",
    },
    {
        "app_label": "core",
        "model_name": "ContactMessage",
        "key": "contact_messages",
    },
    {
        "app_label": "jobs",
        "model_name": "JobCategory",
        "key": "job_categories",
    },
    {
        "app_label": "jobs",
        "model_name": "Company",
        "key": "companies",
    },
    {
        "app_label": "jobs",
        "model_name": "Job",
        "key": "jobs",
    },
    {
        "app_label": "jobs",
        "model_name": "JobAlert",
        "key": "job_alerts",
    },
    {
        "app_label": "jobs",
        "model_name": "ResumeSubmission",
        "key": "resume_submissions",
    },
    {
        "app_label": "jobs",
        "model_name": "JobPostingRequest",
        "key": "job_posting_requests",
    },
    {
        "app_label": "blog",
        "model_name": "BlogCategory",
        "key": "blog_categories",
    },
    {
        "app_label": "blog",
        "model_name": "Tag",
        "key": "tags",
    },
    {
        "app_label": "blog",
        "model_name": "Post",
        "key": "posts",
    },
    {
        "app_label": "newsletter",
        "model_name": "NewsletterSubscriber",
        "key": "newsletter_subscribers",
    },
]

class DataVaultEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetimes, dates, and decimals."""
    def default(self, obj):
        if isinstance(obj, (datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def serialize_model_instance(instance):
    """Serialize a single model instance into a dictionary of primitive types."""
    data = {}
    opts = instance._meta
    
    # 1. Standard fields and ForeignKeys (use attname to capture raw foreign keys like user_id)
    for f in opts.fields:
        val = f.value_from_object(instance)
        # If ForeignKey, value_from_object returns the ID value itself.
        if val is not None:
            if isinstance(val, (datetime, Decimal)):
                val = str(val)
            else:
                # Safely check for FileField/ImageField without raising ValueErrors
                # by catching ValueError on accessing .url or name.
                try:
                    # In Django, if it has a file name, val has a name attribute.
                    # If it's a FieldFile descriptor and is truthy, we want its string name.
                    if hasattr(val, 'field') and hasattr(val, 'name'):
                        if bool(val):
                            val = val.name
                        else:
                            val = ""
                except (ValueError, AttributeError):
                    pass
        data[f.attname] = val
        
    # 2. Many-to-Many fields
    for m2m in opts.many_to_many:
        # Get the primary keys of the related objects
        related_pks = list(getattr(instance, m2m.name).values_list('pk', flat=True))
        data[f"_m2m_{m2m.name}"] = related_pks
        
    return data

def deserialize_and_save(model_class, data_list):
    """Restore a list of serialized instances into the database, preserving PKs."""
    opts = model_class._meta
    m2m_data_to_save = []
    
    for item in data_list:
        fields = {}
        m2m_fields = {}
        
        # Separate M2M data and standard fields
        for k, v in item.items():
            if k.startswith("_m2m_"):
                field_name = k[5:]
                m2m_fields[field_name] = v
            else:
                fields[k] = v
                
        # Parse datetimes and decimals appropriately
        for f in opts.fields:
            if f.name in fields and fields[f.name] is not None:
                field_type = f.get_internal_type()
                if "DateTime" in field_type:
                    fields[f.name] = parse_datetime(fields[f.name])
                elif "Decimal" in field_type:
                    fields[f.name] = Decimal(fields[f.name])
                    
        # Check if password is present (for User model)
        is_user_model = (model_class == User)
        
        # Build the model instance
        instance = model_class(**fields)
        
        # If user model, save password directly without rehashing (it's already hashed in the JSON!)
        if is_user_model:
            instance.password = fields.get('password')
            
        instance.save(force_insert=True)
        
        if m2m_fields:
            m2m_data_to_save.append((instance, m2m_fields))
            
    # Set Many-to-Many relations after standard instances are saved
    for instance, m2m_fields in m2m_data_to_save:
        for field_name, pks in m2m_fields.items():
            getattr(instance, field_name).set(pks)

def export_all_data():
    """Exports all site data to a Python dictionary, serializing each configured model."""
    export_dict = {
        "export_meta": {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "total_records": 0
        }
    }
    
    total_records = 0
    for cfg in MODELS_CONFIG:
        model_class = apps.get_model(cfg["app_label"], cfg["model_name"])
        queryset = model_class.objects.all()
        
        records = []
        for instance in queryset:
            records.append(serialize_model_instance(instance))
            
        export_dict[cfg["key"]] = records
        count = len(records)
        total_records += count
        logger.info(f"Exported {count} records from {cfg['app_label']}.{cfg['model_name']}")
        
    export_dict["export_meta"]["total_records"] = total_records
    return export_dict

def import_all_data(data_dict, clear_existing=True):
    """Imports site data from a dictionary under a single atomic transaction."""
    summary = {}
    
    with transaction.atomic():
        # 1. Optional: Clear existing data in reverse dependency order
        if clear_existing:
            logger.info("Clearing existing database tables...")
            for cfg in reversed(MODELS_CONFIG):
                model_class = apps.get_model(cfg["app_label"], cfg["model_name"])
                # Bypass delete() signals/cascades to keep database clear and fast
                count, _ = model_class.objects.all().delete()
                logger.info(f"Cleared {count} records from {cfg['app_label']}.{cfg['model_name']}")
                
        # 2. Import in forward dependency order
        for cfg in MODELS_CONFIG:
            model_class = apps.get_model(cfg["app_label"], cfg["model_name"])
            key = cfg["key"]
            records = data_dict.get(key, [])
            
            if records:
                deserialize_and_save(model_class, records)
                summary[key] = len(records)
                logger.info(f"Imported {len(records)} records into {cfg['app_label']}.{cfg['model_name']}")
            else:
                summary[key] = 0
                
    return summary
