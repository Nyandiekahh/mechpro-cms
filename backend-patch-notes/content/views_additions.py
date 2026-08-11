"""
ADD to content/views.py: a ProjectDetail view (RetrieveAPIView by slug),
mirroring the pattern already used for Service/Industry detail views.
"""
ADDITIONS = '''
class ProjectDetailView(RetrieveAPIView):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectDetailSerializer
    lookup_field = "slug"
'''
print(ADDITIONS)
