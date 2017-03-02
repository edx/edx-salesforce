DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wwc',
        'USER': 'read_only',
        'PASSWORD': 'gwrpRpi28kUYxBksd1Tb1KaLCO2hri',
        'HOST': 'prod-edx-replica-rds.edx.org',
        'PORT': '3306',
    },
    'ecommerce': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecommerce',
        'USER': 'read_only',
        'PASSWORD': 'gwrpRpi28kUYxBksd1Tb1KaLCO2hri',
        'HOST': 'prod-edx-ecommerce-replica-001.ciqreuddjk02.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}
