"""
Custom template filters for company data
"""
from django import template
import os
import re

register = template.Library()

# Country name to flag emoji mapping
COUNTRY_FLAGS = {
    'afghanistan': '🇦🇫', 'albania': '🇦🇱', 'algeria': '🇩🇿', 'andorra': '🇦🇩', 'angola': '🇦🇴',
    'argentina': '🇦🇷', 'armenia': '🇦🇲', 'australia': '🇦🇺', 'austria': '🇦🇹', 'azerbaijan': '🇦🇿',
    'bahamas': '🇧🇸', 'bahrain': '🇧🇭', 'bangladesh': '🇧🇩', 'barbados': '🇧🇧', 'belarus': '🇧🇾',
    'belgium': '🇧🇪', 'belize': '🇧🇿', 'benin': '🇧🇯', 'bhutan': '🇧🇹', 'bolivia': '🇧🇴',
    'bosnia': '🇧🇦', 'botswana': '🇧🇼', 'brazil': '🇧🇷', 'brunei': '🇧🇳', 'bulgaria': '🇧🇬',
    'burkina': '🇧🇫', 'burundi': '🇧🇮', 'cambodia': '🇰🇭', 'cameroon': '🇨🇲', 'canada': '🇨🇦',
    'chad': '🇹🇩', 'chile': '🇨🇱', 'china': '🇨🇳', 'colombia': '🇨🇴', 'congo': '🇨🇬',
    'costa rica': '🇨🇷', 'croatia': '🇭🇷', 'cuba': '🇨🇺', 'cyprus': '🇨🇾', 'czech': '🇨🇿',
    'denmark': '🇩🇰', 'djibouti': '🇩🇯', 'dominica': '🇩🇲', 'ecuador': '🇪🇨', 'egypt': '🇪🇬',
    'el salvador': '🇸🇻', 'estonia': '🇪🇪', 'ethiopia': '🇪🇹', 'fiji': '🇫🇯', 'finland': '🇫🇮',
    'france': '🇫🇷', 'gabon': '🇬🇦', 'gambia': '🇬🇲', 'georgia': '🇬🇪', 'germany': '🇩🇪',
    'ghana': '🇬🇭', 'greece': '🇬🇷', 'grenada': '🇬🇩', 'guatemala': '🇬🇹', 'guinea': '🇬🇳',
    'guyana': '🇬🇾', 'haiti': '🇭🇹', 'honduras': '🇭🇳', 'hungary': '🇭🇺', 'iceland': '🇮🇸',
    'india': '🇮🇳', 'indonesia': '🇮🇩', 'iran': '🇮🇷', 'iraq': '🇮🇶', 'ireland': '🇮🇪',
    'israel': '🇮🇱', 'italy': '🇮🇹', 'jamaica': '🇯🇲', 'japan': '🇯🇵', 'jordan': '🇯🇴',
    'kazakhstan': '🇰🇿', 'kenya': '🇰🇪', 'kuwait': '🇰🇼', 'kyrgyzstan': '🇰🇬', 'laos': '🇱🇦',
    'latvia': '🇱🇻', 'lebanon': '🇱🇧', 'lesotho': '🇱🇸', 'liberia': '🇱🇷', 'libya': '🇱🇾',
    'liechtenstein': '🇱🇮', 'lithuania': '🇱🇹', 'luxembourg': '🇱🇺', 'madagascar': '🇲🇬', 'malawi': '🇲🇼',
    'malaysia': '🇲🇾', 'maldives': '🇲🇻', 'mali': '🇲🇱', 'malta': '🇲🇹', 'mauritania': '🇲🇷',
    'mauritius': '🇲🇺', 'mexico': '🇲🇽', 'moldova': '🇲🇩', 'monaco': '🇲🇨', 'mongolia': '🇲🇳',
    'montenegro': '🇲🇪', 'morocco': '🇲🇦', 'mozambique': '🇲🇿', 'myanmar': '🇲🇲', 'namibia': '🇳🇦',
    'nepal': '🇳🇵', 'netherlands': '🇳🇱', 'new zealand': '🇳🇿', 'nicaragua': '🇳🇮', 'niger': '🇳🇪',
    'nigeria': '🇳🇬', 'norway': '🇳🇴', 'oman': '🇴🇲', 'pakistan': '🇵🇰', 'panama': '🇵🇦',
    'papua': '🇵🇬', 'paraguay': '🇵🇾', 'peru': '🇵🇪', 'philippines': '🇵🇭', 'poland': '🇵🇱',
    'portugal': '🇵🇹', 'qatar': '🇶🇦', 'romania': '🇷🇴', 'russia': '🇷🇺', 'rwanda': '🇷🇼',
    'saudi arabia': '🇸🇦', 'senegal': '🇸🇳', 'serbia': '🇷🇸', 'seychelles': '🇸🇨', 'singapore': '🇸🇬',
    'slovakia': '🇸🇰', 'slovenia': '🇸🇮', 'somalia': '🇸🇴', 'south africa': '🇿🇦', 'south korea': '🇰🇷',
    'spain': '🇪🇸', 'sri lanka': '🇱🇰', 'sudan': '🇸🇩', 'suriname': '🇸🇷', 'sweden': '🇸🇪',
    'switzerland': '🇨🇭', 'syria': '🇸🇾', 'taiwan': '🇹🇼', 'tajikistan': '🇹🇯', 'tanzania': '🇹🇿',
    'thailand': '🇹🇭', 'togo': '🇹🇬', 'tonga': '🇹🇴', 'trinidad': '🇹🇹', 'tunisia': '🇹🇳',
    'turkey': '🇹🇷', 'turkmenistan': '🇹🇲', 'uganda': '🇺🇬', 'ukraine': '🇺🇦', 'united arab emirates': '🇦🇪',
    'united kingdom': '🇬🇧', 'uk': '🇬🇧', 'england': '🇬🇧', 'scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'united states': '🇺🇸', 'usa': '🇺🇸', 'america': '🇺🇸', 'uruguay': '🇺🇾', 'uzbekistan': '🇺🇿',
    'vanuatu': '🇻🇺', 'venezuela': '🇻🇪', 'vietnam': '🇻🇳', 'yemen': '🇾🇪', 'zambia': '🇿🇲',
    'zimbabwe': '🇿🇼'
}


@register.filter
def get_country_flag(address):
    """
    Extract country from address (last word) and return its flag emoji
    """
    if not address:
        return ''
    
    # Get the last word from the address (the country)
    parts = address.split()
    if not parts:
        return '🌍'
    
    last_word = parts[-1].lower().strip()
    
    # Check if the last word matches a country
    if last_word in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[last_word]
    
    # If not found, check each country name in the address (fallback)
    address_lower = address.lower()
    for country, flag in COUNTRY_FLAGS.items():
        if country in address_lower:
            return flag
    
    return '🌍'  # Default globe emoji if country not found


@register.filter
def get_country_name(address):
    """
    Extract country name from address (last word)
    """
    if not address:
        return ''
    
    # Get the last word from the address (the country)
    parts = address.split()
    if not parts:
        return ''
    
    return parts[-1].strip()


@register.filter
def split_technologies(tech_string):
    """
    Split comma-separated technologies and return a clean list
    """
    if not tech_string:
        return []
    
    # Split by comma and strip whitespace from each item
    technologies = [tech.strip() for tech in tech_string.split(',') if tech.strip()]
    return technologies


@register.filter
def get_tech_icon(tech_name):
    """
    Get the icon path for a technology.
    Icons are stored in static/icons/ as lowercase filenames (svg, png, or jpg)
    Returns the static URL if icon exists, otherwise returns None
    """
    from django.conf import settings
    from django.templatetags.static import static
    
    if not tech_name:
        return None
    
    # Convert tech name to lowercase and remove spaces/dots
    clean_name = tech_name.lower().strip().replace(' ', '-').replace('.', '')
    
    # Technology name mappings for common variations
    tech_mappings = {
        # CMS
        'fork-cms': 'fork-cms.png',
        'october-cms': 'october-cms.png', 
        'octobercms': 'octobercms.svg',
        'craft-cms': 'craftcms.svg',
        'craftcms': 'craftcms.svg',
        'dato-cms': 'dato-cms.svg',
        'datocms': 'dato-cms.svg',
        'wordpress': 'wordpress.svg',
        'wp': 'wordpress.svg',
        'drupal': 'drupal.svg',
        'joomla': 'joomla.svg',
        'webflow': 'webflow.svg',
        'wix': 'wix.svg',
        'weebly': 'weebly.svg',
        'storyblok': 'storyblok.svg',
        'prismic': 'prismic.svg',
        
        # Programming Languages
        'php': 'php.svg',
        'python': 'python.svg',
        'javascript': 'vanillajs.svg',
        'js': 'vanillajs.svg',
        'typescript': 'typescript.svg',
        'ts': 'typescript.svg',
        'css': 'css.svg',
        
        # Frameworks
        'symfony': 'symfony.svg',
        'laravel': 'laravel.svg',
        'django': 'django.svg',
        'codeigniter': 'codeigniter.svg',
        'vue': 'vue.svg',
        'vuejs': 'vue.svg',
        'next-js': 'next-js.svg',
        'nextjs': 'next-js.svg',
        'next': 'next-js.svg',
        'nuxt': 'nuxt.svg',
        'nuxtjs': 'nuxt.svg',
        'gatsby': 'gatsby.svg',
        'gatsbyjs': 'gatsby.svg',
        'preact': 'preact.svg',
        'threejs': 'threejs.svg',
        'three-js': 'threejs.svg',
        'gsap': 'gsap.svg',
        'alpine-js': 'alpine-tjs.svg',
        'alpinejs': 'alpine-tjs.svg',
        
        # Libraries
        'jquery': 'jquery.svg',
        'sass': 'sass.svg',
        'scss': 'sass.svg',
        'tailwind': 'tailwind.svg',
        'tailwindcss': 'tailwind.svg',
        'webpack': 'webpack.svg',
        
        # Databases
        'mysql': 'mysql.svg',
        'mongodb': 'mongo-db.svg',
        'mongo-db': 'mongo-db.svg',
        'mongo': 'mongo-db.svg',
        'postgresql': 'postgree.svg',
        'postgres': 'postgree.svg',
        'postgree': 'postgree.svg',
        
        # Cloud/Hosting
        'aws': 'aws.svg',
        'amazon': 'aws.svg',
        'azure': 'azure.svg',
        'google-cloud': 'google-cloud.svg',
        'gcp': 'google-cloud.svg',
        'netlify': 'netlify.svg',
        'heroku': 'heroku.svg',
        'cloudflare': 'cloudflare.svg',
        'apache': 'apache.svg',
        'nginx': 'nginx.svg',
        'plesk': 'plesk.svg',
        'gunicorn': 'gunicorn.svg',
        
        # Tools/Services
        'github': 'github.svg',
        'git': 'github.svg',
        'figma': 'figma.svg',
        'photoshop': 'photoshop.svg',
        'illustrator': 'illustrator.svg',
        'adobe': 'adobe.svg',
        'hubspot': 'hubspot.svg',
        'mapbox': 'mapbox.svg',
        'zendesk': 'zendesk.svg',
        'asana': 'asana.svg',
        'monday': 'monday.svg',
        'jira': 'jira.svg',
        'sendinblue': 'sendinblue.svg',
        
        # WordPress Plugins
        'elementor': 'elementor.svg',
        'woocommerce': 'woocommerce.svg',
        'woo-commerce': 'woocommerce.svg',
        'yoast': 'yoast.svg',
        'wpml': 'wpml.svg',
        
        # Social Media
        'instagram': 'instagram.svg',
        'twitter': 'twitter.svg',
        'linkedin': 'linkedin.svg',
        
        # Other
        'pwa': 'pwa.svg',
        'node': 'nodejs.svg',
        'nodejs': 'nodejs.svg',
        'express': 'nodejs.svg',
        's3': 's3.svg'
    }
    
    # Check if we have a direct mapping
    if clean_name in tech_mappings:
        icon_file = tech_mappings[clean_name]
        full_path = os.path.join(settings.BASE_DIR, 'static', 'icons', icon_file)
        if os.path.exists(full_path):
            return static(f'icons/{icon_file}')
    
    # If no direct mapping, try exact filename match with extensions
    for ext in ['svg', 'png', 'jpg']:
        icon_path = f'icons/{clean_name}.{ext}'
        full_path = os.path.join(settings.BASE_DIR, 'static', icon_path)
        if os.path.exists(full_path):
            return static(icon_path)
    
    return None


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ my_dict|get_item:my_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)



