from rest_framework import serializers
from .models import WorkExperience, Education, Project, SkillCategory

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'title', 'company', 'period', 'achievements', 'created_at', 'updated_at']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'major', 'school', 'period', 'degree', 'description', 'created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'techStack', 'details', 'created_at', 'updated_at']

class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'skills', 'created_at', 'updated_at']

class UpdateAboutMeSerializer(serializers.Serializer):
    work = WorkExperienceSerializer(many=True)
    education = EducationSerializer(many=True)
    projects = ProjectSerializer(many=True)
    skills = SkillCategorySerializer(many=True)

    def validate_work(self, value):
        """验证工作经历数据"""
        if len(value) > 2:
            raise serializers.ValidationError("工作经历最多只能有2条")
        
        for work in value:
            if len(work.get('achievements', [])) > 3:
                raise serializers.ValidationError(f"工作 '{work.get('title', '')}' 的成就最多只能有3条")
        return value

    def validate_education(self, value):
        """验证教育背景数据"""
        if len(value) > 2:
            raise serializers.ValidationError("教育背景最多只能有2条")
        return value

    def validate(self, data):
        """验证所有数据"""
        # 确保所有必需字段都有数据
        required_fields = ['work', 'education', 'projects', 'skills']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} 不能为空")
        return data
