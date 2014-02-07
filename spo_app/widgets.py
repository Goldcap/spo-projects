from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.utils.safestring import mark_safe

class SpoCheckboxSelectMultiple(CheckboxSelectMultiple):
    
    def __init__(self, attrs=None):
        
        self.size = 'two-up'
        if attrs and 'size' in attrs:
            self.size = attrs['size']
        
        super(SpoCheckboxSelectMultiple, self).__init__(attrs)
        
    def render(self, name, value, attrs=None, choices=()):
        html = super(SpoCheckboxSelectMultiple, self).render(name, value, attrs, choices)

        return mark_safe(html.replace('<ul>', '<ul class="display block-grid usm-zebra-block-%s %s ">' % (self.size,self.size)))
        