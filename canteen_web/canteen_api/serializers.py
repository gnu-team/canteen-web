from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import Point
from rest_framework import serializers
from canteen.models import Report, PurityReport, Profile

class BaseReportSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    date = serializers.ReadOnlyField()
    creator = serializers.HyperlinkedRelatedField(read_only=True, view_name='user-detail')
    creator_name = serializers.ReadOnlyField(source='creator.username')
    latitude = serializers.FloatField(source='loc.get_y')
    longitude = serializers.FloatField(source='loc.get_x')

    class Meta:
        fields = ('id', 'date', 'creator', 'creator_name', 'latitude',
                  'longitude', 'description')

    def create(self, validated_data):
        validated_data['loc'] = Point(validated_data['loc']['get_x'],
                                      validated_data['loc']['get_y'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'loc' in validated_data:
            new_loc = Point(*instance.loc.get_coords())
            if 'get_x' in validated_data['loc']:
                new_loc.set_x(validated_data['loc']['get_x'])
            if 'get_y' in validated_data['loc']:
                new_loc.set_y(validated_data['loc']['get_y'])
            validated_data['loc'] = new_loc

        return super().update(instance, validated_data)

class ReportSerializer(BaseReportSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = BaseReportSerializer.Meta.fields + ('type', 'condition')

class PurityReportSerializer(BaseReportSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PurityReport
        fields = BaseReportSerializer.Meta.fields + ('virusPPM', 'contaminantPPM', 'condition')

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
