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
    # Profile attributes stored in the 1:1 Profile model rather than the
    # default Django User model
    phone = serializers.CharField(source='profile.phone', allow_blank=True, required=False)
    address = serializers.CharField(source='profile.address', allow_blank=True, required=False)
    bio = serializers.CharField(source='profile.bio', allow_blank=True, required=False)

    class Meta:
        model = User
        _profile_fields = ('phone', 'address', 'bio')
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'group', 'reports') + _profile_fields

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
        if new_profile:
            if 'get_group' in new_profile:
                instance.profile.set_group(new_profile['get_group'])

            for attr in self.Meta._profile_fields:
                if attr in new_profile:
                    setattr(instance.profile, attr, new_profile[attr])

            instance.profile.save()

        return super().update(instance, validated_data)
