from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User, Group
from canteen.models import Report, PurityReport, Profile
from rest_framework import serializers

class ReportSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    date = serializers.ReadOnlyField()
    creator = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    creator_name = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Report
        fields = ('id', 'date', 'creator', 'creator_name', 'latitude',
                  'longitude', 'type', 'condition', 'description')

class PurityReportSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    date = serializers.ReadOnlyField()
    creator = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    creator_name = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = PurityReport
        fields = ('id', 'date', 'creator', 'creator_name', 'latitude',
                  'longitude', 'virusPPM', 'contaminantPPM', 'condition',
                  'description')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, validators=(validate_password,), style={'input_type': 'password'})
    group = serializers.ChoiceField(('Users', 'Workers', 'Managers', 'Administrators'), source='profile.get_group')
    reports = serializers.HyperlinkedRelatedField(view_name='report-detail', many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'group', 'reports')

    def create(self, validated_data):
        u = User.objects.create_user(username=validated_data['username'],
                                     password=validated_data['password'])
        profile = Profile.objects.create(user=u)
        profile.set_group(validated_data['profile']['get_group'])
        profile.save()

        return u

    def update(self, instance, validated_data):
        new_password = validated_data.pop('password', None)

        if new_password:
            instance.set_password(new_password)

        # XXX Make this less horrible
        new_profile = validated_data.pop('profile', None)
        new_group = validated_data.pop('get_group', None) if new_profile else None

        if new_group:
            instance.profile.set_group(new_group)

        return super().update(instance, validated_data)
