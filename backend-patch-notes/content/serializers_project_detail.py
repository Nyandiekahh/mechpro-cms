"""ADD to content/serializers.py: a detail serializer with the fuller body."""
ADDITIONS = '''
class ProjectDetailSerializer(ProjectSerializer):
    fullDescription = serializers.SerializerMethodField()

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["fullDescription"]

    def get_fullDescription(self, obj):
        text = obj.full_description or obj.summary
        return [p.strip() for p in text.split("\\n\\n") if p.strip()]
'''
print(ADDITIONS)
