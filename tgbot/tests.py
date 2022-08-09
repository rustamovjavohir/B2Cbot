from django.test import TestCase
from models import B2CCommandText

a = B2CCommandText.objects.filter(text_code=4)

# commands = [for]
print(a)

if __name__ == '__main__':
    pass
