from django.contrib.auth.models import User, Group
from canteen.models import Report, PurityReport
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
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    group = serializers.ChoiceField(('Users', 'Workers', 'Managers', 'Administrators'), write_only=True)
    reports = serializers.HyperlinkedRelatedField(view_name='report-detail', many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password', 'group', 'reports')

    def create(self, validated_data):
        u = User.objects.create_user(username=validated_data['username'],
                                     password=validated_data['password'])

        group = validated_data['group']
        if group == 'Administrators':
            # Don't do anything for now; granting admin permissions to
            # anyone is too dangerous
            pass
        else:
            Group.objects.get(name=group).user_set.add(u)

        return u

    def update(self, instance, validated_data):
        new_password = validated_data.pop('password', None)

        if new_password:
            instance.set_password(new_password)

        return super().update(instance, validated_data)
