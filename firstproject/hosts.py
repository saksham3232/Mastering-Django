from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'www', 'firstapp.urls', name='www'),
    host(r'services', 'seller.urls', name='services'),
)