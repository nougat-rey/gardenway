from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_mb = 4
    if file.size > max_size_mb * pow(10, 6):
        raise ValidationError(f'Files cannot be larger than {max_size_mb} Mb.')
