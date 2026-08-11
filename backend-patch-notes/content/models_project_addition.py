"""
ADDITIVE field for content/models.py Project class — add this one field
inside the existing Project class body (anywhere after existing fields).
Existing project rows simply get blank/empty value for it; nothing else
changes.
"""
PROJECT_NEW_FIELD = '''
    full_description = models.TextField(
        blank=True,
        help_text="Longer write-up shown on the project's own detail page. "
                  "Leave blank to just show the summary there too.")
'''
print(PROJECT_NEW_FIELD)
